"""
Page de gestion des campagnes email
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import db_manager
from src.core.utils import format_date_for_display

def render_campaigns():
    """Affiche la page des campagnes email"""
    st.title("📧 Campagnes Email")
    
    # Charger les données
    campaigns = db_manager.SessionLocal().query(db_manager.EmailCampaign).all()
    
    if not campaigns:
        st.warning("Aucune campagne trouvée dans la base de données.")
        return
    
    # Convertir en DataFrame
    campaigns_data = [campaign.to_dict() for campaign in campaigns]
    campaigns_df = pd.DataFrame(campaigns_data)
    
    # Afficher le nombre de campagnes
    st.write(f"Affichage de {len(campaigns_df)} campagnes")
    
    # Options d'affichage
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Rechercher une campagne", "")
    
    with col2:
        view_option = st.selectbox(
            "Vue",
            ["Tableau", "Performance", "Analyse"]
        )
    
    # Appliquer la recherche
    if search_term:
        campaigns_df = campaigns_df[
            campaigns_df['subject'].str.contains(search_term, case=False) |
            campaigns_df['content'].str.contains(search_term, case=False)
        ]
    
    # Afficher selon l'option sélectionnée
    if view_option == "Tableau":
        # Sélectionner les colonnes à afficher
        display_cols = ['prospect_id', 'subject', 'sent_at', 'opened_at', 'clicked_at']
        display_df = campaigns_df[display_cols]
        
        # Renommer les colonnes pour l'affichage
        display_df = display_df.rename(columns={
            'prospect_id': 'ID Prospect',
            'subject': 'Sujet',
            'sent_at': 'Envoyé le',
            'opened_at': 'Ouvert le',
            'clicked_at': 'Cliqué le'
        })
        
        # Formater les dates
        for col in ['Envoyé le', 'Ouvert le', 'Cliqué le']:
            display_df[col] = display_df[col].apply(lambda x: format_date_for_display(x) if x else '')
        
        # Afficher le tableau
        st.dataframe(display_df, use_container_width=True)
        
        # Bouton pour exporter
        if st.button("Exporter les campagnes filtrées"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name=f'campagnes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    elif view_option == "Performance":
        st.subheader("Performance des Campagnes")
        
        # Calculer les taux d'ouverture et de clic
        total_emails = len(campaigns_df)
        opened_emails = len(campaigns_df[campaigns_df['opened_at'].notna()])
        clicked_emails = len(campaigns_df[campaigns_df['clicked_at'].notna()])
        
        open_rate = (opened_emails / total_emails * 100) if total_emails > 0 else 0
        click_rate = (clicked_emails / opened_emails * 100) if opened_emails > 0 else 0
        
        # Afficher les métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Taux d'Ouverture", 
                f"{open_rate:.2f}%"
            )
            
        with col2:
            st.metric(
                "Taux de Clic", 
                f"{click_rate:.2f}%"
            )
            
        with col3:
            st.metric(
                "Emails Envoyés", 
                total_emails
            )
        
        # Graphique d'ouverture par jour
        campaigns_df['sent_at'] = pd.to_datetime(campaigns_df['sent_at'])
        campaigns_df['sent_date'] = campaigns_df['sent_at'].dt.date
        
        # Compter les emails envoyés par jour
        daily_sent = campaigns_df.groupby('sent_date').size().reset_index(name='count')
        
        # Compter les emails ouverts par jour
        opened_df = campaigns_df[campaigns_df['opened_at'].notna()].copy()
        opened_df['opened_at'] = pd.to_datetime(opened_df['opened_at'])
        opened_df['opened_date'] = opened_df['opened_at'].dt.date
        daily_opened = opened_df.groupby('opened_date').size().reset_index(name='count')
        
        # Fusionner les données
        daily_data = pd.merge(daily_sent, daily_opened, on='sent_date', how='left', suffixes=('_sent', '_opened'))
        daily_data = daily_data.rename(columns={'sent_date': 'date'})
        daily_data['count_opened'] = daily_data['count_opened'].fillna(0)
        
        # Créer le graphique
        fig_daily = go.Figure()
        
        fig_daily.add_trace(go.Bar(
            x=daily_data['date'],
            y=daily_data['count_sent'],
            name='Emails Envoyés',
            marker_color='lightblue'
        ))
        
        fig_daily.add_trace(go.Bar(
            x=daily_data['date'],
            y=daily_data['count_opened'],
            name='Emails Ouverts',
            marker_color='darkblue'
        ))
        
        fig_daily.update_layout(
            title='Performance Quotidienne des Emails',
            xaxis_title='Date',
            yaxis_title='Nombre d\'Emails',
            barmode='group'
        )
        
        st.plotly_chart(fig_daily, use_container_width=True)
    
    elif view_option == "Analyse":
        st.subheader("Analyse Détaillée des Campagnes")
        
        # Sélectionner une campagne spécifique
        campaign_ids = campaigns_df['id'].tolist()
        selected_campaign_id = st.selectbox(
            "Sélectionner une campagne",
            campaign_ids,
            format_func=lambda x: f"Campagne {x}"
        )
        
        if selected_campaign_id:
            # Récupérer les détails de la campagne
            campaign_details = campaigns_df[campaigns_df['id'] == selected_campaign_id].iloc[0]
            
            # Afficher les détails
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Sujet:**")
                st.write(campaign_details['subject'])
                
                st.write("**Envoyé le:**")
                st.write(format_date_for_display(campaign_details['sent_at']))
                
                st.write("**Ouvert le:**")
                st.write(format_date_for_display(campaign_details['opened_at']))
                
                st.write("**Cliqué le:**")
                st.write(format_date_for_display(campaign_details['clicked_at']))
            
            with col2:
                st.write("**Contenu de l'email:**")
                st.text_area("Email", campaign_details['content'], height=300)
            
            # Afficher le prospect associé
            prospect_id = campaign_details['prospect_id']
            prospects = db_manager.get_prospects()
            
            if prospects:
                prospect = next((p for p in prospects if p.id == prospect_id), None)
                if prospect:
                    st.write("**Prospect Associé:**")
                    prospect_data = [prospect.to_dict()]
                    prospect_df = pd.DataFrame(prospect_data)
                    st.dataframe(prospect_df, use_container_width=True)
