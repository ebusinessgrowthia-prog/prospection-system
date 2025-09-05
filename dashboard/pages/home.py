"""
Page d'accueil du dashboard
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
from src.core.utils import format_number

def render_home():
    """Affiche la page d'accueil"""
    st.title("🏠 Tableau de Bord")
    
    # Statistiques principales
    stats = db_manager.get_system_stats()
    
    if stats:
        # Cartes de statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Prospects", 
                format_number(stats.get('prospects', {}).get('total', 0)),
                delta=None
            )
            
        with col2:
            st.metric(
                "Prospects Qualifiés", 
                format_number(stats.get('prospects', {}).get('qualified', 0)),
                delta=None
            )
            
        with col3:
            st.metric(
                "Emails Envoyés", 
                format_number(stats.get('emails', {}).get('total', 0)),
                delta=None
            )
            
        with col4:
            st.metric(
                "Audits Réservés", 
                format_number(stats.get('prospects', {}).get('audit_booked', 0)),
                delta=None
            )
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prospects par Pays")
            country_data = stats.get('by_country', {})
            if country_data:
                df_country = pd.DataFrame(list(country_data.items()), columns=['Pays', 'Nombre'])
                fig_country = px.bar(df_country, x='Pays', y='Nombre', color='Pays')
                st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            st.subheader("Prospects par Secteur")
            sector_data = stats.get('by_sector', {})
            if sector_data:
                df_sector = pd.DataFrame(list(sector_data.items()), columns=['Secteur', 'Nombre'])
                fig_sector = px.pie(df_sector, values='Nombre', names='Secteur')
                st.plotly_chart(fig_sector, use_container_width=True)
        
        # Activité récente
        st.subheader("Activité Récente")
        prospects_df = db_manager.get_prospects()
        
        if prospects_df:
            # Convertir en DataFrame
            prospects_data = [prospect.to_dict() for prospect in prospects_df]
            prospects_df = pd.DataFrame(prospects_data)
            
            # Convertir les dates
            prospects_df['date_added'] = pd.to_datetime(prospects_df['date_added'])
            prospects_df['date_added_date'] = prospects_df['date_added'].dt.date
            
            # Regrouper par date
            activity_df = prospects_df.groupby('date_added_date').size().reset_index(name='count')
            
            # Créer le graphique
            fig_activity = px.line(
                activity_df, 
                x='date_added_date', 
                y='count',
                labels={'date_added_date': 'Date', 'count': 'Nombre de Prospects'},
                title='Prospects Ajoutés par Jour'
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        # Derniers prospects
        st.subheader("Derniers Prospects Ajoutés")
        if prospects_df:
            # Trier par date et prendre les 10 derniers
            latest_prospects = prospects_df.sort_values('date_added', ascending=False).head(10)
            
            # Sélectionner les colonnes pertinentes
            display_cols = ['name', 'company', 'sector', 'country', 'status']
            latest_prospects_display = latest_prospects[display_cols]
            
            # Afficher le tableau
            st.dataframe(latest_prospects_display, use_container_width=True)
        
        # Performance des emails
        st.subheader("Performance des Emails")
        email_stats = stats.get('emails', {})
        if email_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Taux d'Ouverture", 
                    f"{email_stats.get('open_rate', 0)}%"
                )
                
            with col2:
                st.metric(
                    "Taux de Clic", 
                    f"{email_stats.get('click_rate', 0)}%"
                )
                
            with col3:
                st.metric(
                    "Emails Envoyés", 
                    format_number(email_stats.get('total', 0))
                )
    else:
        st.warning("Impossible de charger les statistiques système.")
