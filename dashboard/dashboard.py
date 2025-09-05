"""
Application principale du dashboard Streamlit pour EBUSINESS AI
Interface utilisateur pour le suivi des prospections
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
import sys
from datetime import datetime, timedelta
import json

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_config
from src.core.database import db_manager
from src.core.utils import format_date_for_display, format_number

# Configuration de la page
st.set_page_config(
    page_title="EBUSINESS AI - Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
config = get_config()

# CSS personnalisé
def local_css(file_name):
    """Charge un fichier CSS local"""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# JavaScript personnalisé
def local_js(file_name):
    """Charge un fichier JavaScript local"""
    with open(file_name) as f:
        components.html(f"<script>{f.read()}</script>", height=0)

# Appliquer le CSS personnalisé
local_css("static/css/style.css")

# Fonction pour charger les données
@st.cache_data(ttl=300)  # Cache de 5 minutes
def load_prospects_data():
    """Charge les données des prospects depuis la base de données"""
    try:
        prospects = db_manager.get_prospects()
        prospects_data = [prospect.to_dict() for prospect in prospects]
        return pd.DataFrame(prospects_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des prospects: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache de 5 minutes
def load_campaigns_data():
    """Charge les données des campagnes depuis la base de données"""
    try:
        campaigns = db_manager.SessionLocal().query(db_manager.EmailCampaign).all()
        campaigns_data = [campaign.to_dict() for campaign in campaigns]
        return pd.DataFrame(campaigns_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des campagnes: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache de 5 minutes
def load_system_stats():
    """Charge les statistiques système"""
    try:
        return db_manager.get_system_stats()
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {e}")
        return {}

# Barre latérale
def render_sidebar():
    """Affiche la barre latérale du dashboard"""
    with st.sidebar:
        st.image("static/img/logo.png", width=200)
        st.title("🚀 EBUSINESS AI")
        st.subheader("Automatisation de Prospection")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        page = st.selectbox(
            "Aller à",
            ["Accueil", "Prospects", "Campagnes", "Analytics"],
            key="navigation"
        )
        
        st.markdown("---")
        
        # Statistiques en temps réel
        st.subheader("Statistiques en Temps Réel")
        stats = load_system_stats()
        
        if stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Total Prospects", 
                    format_number(stats.get('prospects', {}).get('total', 0))
                )
                
            with col2:
                st.metric(
                    "Taux d'Ouverture", 
                    f"{stats.get('emails', {}).get('open_rate', 0)}%"
                )
        
        st.markdown("---")
        
        # Filtres
        st.subheader("Filtres")
        
        # Filtre par statut
        status_filter = st.multiselect(
            "Statut",
            ["nouveau", "qualifié", "contacté", "répondu", "audit_réservé"],
            default=["qualifié", "contacté"]
        )
        
        # Filtre par pays
        country_filter = st.multiselect(
            "Pays",
            ["France", "Belgique", "Suisse", "Luxembourg", "Monaco", "Canada (Québec)"],
            default=["France", "Belgique"]
        )
        
        # Filtre par secteur
        sector_filter = st.multiselect(
            "Secteur",
            ["Mode", "Électronique", "Services", "Digital", "Retail"],
            default=["Mode", "Électronique"]
        )
        
        st.markdown("---")
        
        # Export de données
        st.subheader("Export de Données")
        if st.button("Exporter les Prospects"):
            st.success("Export en cours...")
            # Logique d'export ici
        
        if st.button("Exporter les Campagnes"):
            st.success("Export en cours...")
            # Logique d'export ici
        
        st.markdown("---")
        
        # Informations système
        st.subheader("Informations Système")
        st.write(f"Version: 1.0.0")
        st.write(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Bouton de rafraîchissement
        if st.button("Rafraîchir les données"):
            st.rerun()
    
    return page, status_filter, country_filter, sector_filter

# Page d'accueil
def render_home_page():
    """Affiche la page d'accueil du dashboard"""
    st.title("🏠 Tableau de Bord")
    
    # Statistiques principales
    stats = load_system_stats()
    
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
        prospects_df = load_prospects_data()
        
        if not prospects_df.empty:
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
        if not prospects_df.empty:
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

# Page des prospects
def render_prospects_page(status_filter, country_filter, sector_filter):
    """Affiche la page des prospects"""
    st.title("👥 Prospects")
    
    # Charger les données
    prospects_df = load_prospects_data()
    
    if prospects_df.empty:
        st.warning("Aucun prospect trouvé dans la base de données.")
        return
    
    # Appliquer les filtres
    if status_filter:
        prospects_df = prospects_df[prospects_df['status'].isin(status_filter)]
    
    if country_filter:
        prospects_df = prospects_df[prospects_df['country'].isin(country_filter)]
    
    if sector_filter:
        prospects_df = prospects_df[prospects_df['sector'].isin(sector_filter)]
    
    # Afficher le nombre de prospects après filtrage
    st.write(f"Affichage de {len(prospects_df)} prospects")
    
    # Options d'affichage
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Rechercher un prospect", "")
    
    with col2:
        view_option = st.selectbox(
            "Vue",
            ["Tableau", "Carte", "Statistiques"]
        )
    
    # Appliquer la recherche
    if search_term:
        prospects_df = prospects_df[
            prospects_df['name'].str.contains(search_term, case=False) |
            prospects_df['company'].str.contains(search_term, case=False) |
            prospects_df['email'].str.contains(search_term, case=False)
        ]
    
    # Afficher selon l'option sélectionnée
    if view_option == "Tableau":
        # Sélectionner les colonnes à afficher
        display_cols = ['name', 'company', 'email', 'sector', 'country', 'status', 'qualification_score']
        display_df = prospects_df[display_cols]
        
        # Renommer les colonnes pour l'affichage
        display_df = display_df.rename(columns={
            'name': 'Nom',
            'company': 'Entreprise',
            'email': 'Email',
            'sector': 'Secteur',
            'country': 'Pays',
            'status': 'Statut',
            'qualification_score': 'Score'
        })
        
        # Afficher le tableau
        st.dataframe(display_df, use_container_width=True)
        
        # Bouton pour exporter
        if st.button("Exporter les prospects filtrés"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name=f'prospects_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    elif view_option == "Carte":
        st.subheader("Carte des Prospects")
        
        # Créer une carte avec les prospects
        # Note: Pour une vraie carte, il faudrait des coordonnées GPS
        # Ici, nous allons simuler avec des pays
        
        # Compter les prospects par pays
        country_counts = prospects_df['country'].value_counts().reset_index()
        country_counts.columns = ['Pays', 'Nombre']
        
        # Créer une carte mondiale simplifiée
        fig = px.choropleth(
            country_counts,
            locations="Pays",
            locationmode="country names",
            color="Nombre",
            hover_name="Pays",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Répartition des Prospects par Pays"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif view_option == "Statistiques":
        st.subheader("Statistiques des Prospects")
        
        # Statistiques par statut
        status_counts = prospects_df['status'].value_counts().reset_index()
        status_counts.columns = ['Statut', 'Nombre']
        
        fig_status = px.bar(
            status_counts, 
            x='Statut', 
            y='Nombre',
            color='Statut',
            title="Prospects par Statut"
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Statistiques par secteur
        sector_counts = prospects_df['sector'].value_counts().reset_index()
        sector_counts.columns = ['Secteur', 'Nombre']
        
        fig_sector = px.pie(
            sector_counts, 
            values='Nombre', 
            names='Secteur',
            title="Prospects par Secteur"
        )
        st.plotly_chart(fig_sector, use_container_width=True)
        
        # Distribution des scores
        fig_score = px.histogram(
            prospects_df, 
            x='qualification_score',
            nbins=20,
            title="Distribution des Scores de Qualification"
        )
        st.plotly_chart(fig_score, use_container_width=True)

# Page des campagnes
def render_campaigns_page():
    """Affiche la page des campagnes email"""
    st.title("📧 Campagnes Email")
    
    # Charger les données
    campaigns_df = load_campaigns_data()
    
    if campaigns_df.empty:
        st.warning("Aucune campagne trouvée dans la base de données.")
        return
    
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
        clicked_emails = len(campaigns_df[campaign_df_df['clicked_at'].notna()])
        
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
            prospects_df = load_prospects_data()
            
            if not prospects_df.empty:
                prospect = prospects_df[prospects_df['id'] == prospect_id]
                if not prospect.empty:
                    st.write("**Prospect Associé:**")
                    st.dataframe(prospect, use_container_width=True)

# Page d'analyse
def render_analytics_page():
    """Affiche la page d'analyse avancée"""
    st.title("📊 Analytics")
    
    # Charger les données
    prospects_df = load_prospects_data()
    campaigns_df = load_campaigns_data()
    
    # Options d'analyse
    analysis_type = st.selectbox(
        "Type d'Analyse",
        ["Performance Globale", "Tendances Temporelles", "Analyse par Secteur", "Analyse par Pays"]
    )
    
    if analysis_type == "Performance Globale":
        st.subheader("Performance Globale du Système")
        
        # Statistiques système
        stats = load_system_stats()
        
        if stats:
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Prospects", 
                    format_number(stats.get('prospects', {}).get('total', 0))
                )
                
            with col2:
                st.metric(
                    "Prospects Qualifiés", 
                    format_number(stats.get('prospects', {}).get('qualified', 0))
                )
                
            with col3:
                st.metric(
                    "Emails Envoyés", 
                    format_number(stats.get('emails', {}).get('total', 0))
                )
                
            with col4:
                st.metric(
                    "Audits Réservés", 
                    format_number(stats.get('prospects', {}).get('audit_booked', 0))
                )
            
            # Taux de conversion
            conversion_rate = (
                stats.get('prospects', {}).get('audit_booked', 0) / 
                stats.get('prospects', {}).get('total', 0) * 100
            ) if stats.get('prospects', {}).get('total', 0) > 0 else 0
            
            st.metric(
                "Taux de Conversion Global", 
                f"{conversion_rate:.2f}%"
            )
            
            # Graphiques de performance
            col1, col2 = st.columns(2)
            
            with col1:
                # Taux d'ouverture et de clic
                email_stats = stats.get('emails', {})
                if email_stats:
                    fig_email = go.Figure(data=[
                        go.Bar(name='Envoyés', x=['Emails'], y=[email_stats.get('total', 0)]),
                        go.Bar(name='Ouverts', x=['Emails'], y=[email_stats.get('opened', 0)]),
                        go.Bar(name='Cliqués', x=['Emails'], y=[email_stats.get('clicked', 0)])
                    ])
                    
                    fig_email.update_layout(
                        title='Performance des Emails',
                        xaxis_title='Type',
                        yaxis_title='Nombre'
                    )
                    
                    st.plotly_chart(fig_email, use_container_width=True)
            
            with col2:
                # Répartition par statut
                if not prospects_df.empty:
                    status_counts = prospects_df['status'].value_counts().reset_index()
                    status_counts.columns = ['Statut', 'Nombre']
                    
                    fig_status = px.pie(
                        status_counts, 
                        values='Nombre', 
                        names='Statut',
                        title='Répartition des Prospects par Statut'
                    )
                    
                    st.plotly_chart(fig_status, use_container_width=True)
    
    elif analysis_type == "Tendances Temporelles":
        st.subheader("Tendances Temporelles")
        
        if not prospects_df.empty:
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
        
        if not campaigns_df.empty:
            # Convertir les dates
            campaigns_df['sent_at'] = pd.to_datetime(campaigns_df['sent_at'])
            campaigns_df['sent_date'] = campaigns_df['sent_at'].dt.date
            
            # Compter les emails envoyés par jour
            daily_sent = campaigns_df.groupby('sent_date').size().reset_index(name='count')
            
            # Créer le graphique
            fig_sent = px.line(
                daily_sent, 
                x='sent_date', 
                y='count',
                labels={'sent_date': 'Date', 'count': 'Nombre d\'Emails'},
                title='Emails Envoyés par Jour'
            )
            
            st.plotly_chart(fig_sent, use_container_width=True)
    
    elif analysis_type == "Analyse par Secteur":
        st.subheader("Analyse par Secteur")
        
        if not prospects_df.empty:
            # Statistiques par secteur
            sector_stats = prospects_df.groupby('sector').agg({
                'id': 'count',  # Nombre de prospects
                'qualification_score': 'mean'  # Score moyen
            }).reset_index()
            
            sector_stats.columns = ['Secteur', 'Nombre de Prospects', 'Score Moyen']
            
            # Graphique du nombre de prospects par secteur
            fig_sector_count = px.bar(
                sector_stats, 
                x='Secteur', 
                y='Nombre de Prospects',
                color='Secteur',
                title='Nombre de Prospects par Secteur'
            )
            
            st.plotly_chart(fig_sector_count, use_container_width=True)
            
            # Graphique du score moyen par secteur
            fig_sector_score = px.bar(
                sector_stats, 
                x='Secteur', 
                y='Score Moyen',
                color='Secteur',
                title='Score de Qualification Moyen par Secteur'
            )
            
            st.plotly_chart(fig_sector_score, use_container_width=True)
    
    elif analysis_type == "Analyse par Pays":
        st.subheader("Analyse par Pays")
        
        if not prospects_df.empty:
            # Statistiques par pays
            country_stats = prospects_df.groupby('country').agg({
                'id': 'count',  # Nombre de prospects
                'qualification_score': 'mean'  # Score moyen
            }).reset_index()
            
            country_stats.columns = ['Pays', 'Nombre de Prospects', 'Score Moyen']
            
            # Graphique du nombre de prospects par pays
            fig_country_count = px.bar(
                country_stats, 
                x='Pays', 
                y='Nombre de Prospects',
                color='Pays',
                title='Nombre de Prospects par Pays'
            )
            
            st.plotly_chart(fig_country_count, use_container_width=True)
            
            # Graphique du score moyen par pays
            fig_country_score = px.bar(
                country_stats, 
                x='Pays', 
                y='Score Moyen',
                color='Pays',
                title='Score de Qualification Moyen par Pays'
            )
            
            st.plotly_chart(fig_country_score, use_container_width=True)
            
            # Carte des prospects
            fig_map = px.choropleth(
                country_stats,
                locations="Pays",
                locationmode="country names",
                color="Nombre de Prospects",
                hover_name="Pays",
                color_continuous_scale=px.colors.sequential.Plasma,
                title="Répartition des Prospects par Pays"
            )
            
            st.plotly_chart(fig_map, use_container_width=True)

# Fonction principale
def main():
    """Fonction principale du dashboard"""
    # Afficher la barre latérale
    page, status_filter, country_filter, sector_filter = render_sidebar()
    
    # Afficher la page sélectionnée
    if page == "Accueil":
        render_home_page()
    elif page == "Prospects":
        render_prospects_page(status_filter, country_filter, sector_filter)
    elif page == "Campagnes":
        render_campaigns_page()
    elif page == "Analytics":
        render_analytics_page()

# Point d'entrée
if __name__ == "__main__":
    main()
