"""
Page d'analyse avancée
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

def render_analytics():
    """Affiche la page d'analyse avancée"""
    st.title("📊 Analytics")
    
    # Charger les données
    prospects = db_manager.get_prospects()
    campaigns = db_manager.SessionLocal().query(db_manager.EmailCampaign).all()
    
    # Options d'analyse
    analysis_type = st.selectbox(
        "Type d'Analyse",
        ["Performance Globale", "Tendances Temporelles", "Analyse par Secteur", "Analyse par Pays"]
    )
    
    if analysis_type == "Performance Globale":
        st.subheader("Performance Globale du Système")
        
        # Statistiques système
        stats = db_manager.get_system_stats()
        
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
                if prospects:
                    prospects_data = [prospect.to_dict() for prospect in prospects]
                    prospects_df = pd.DataFrame(prospects_data)
                    
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
        
        if prospects:
            # Convertir en DataFrame
            prospects_data = [prospect.to_dict() for prospect in prospects]
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
        
        if campaigns:
            # Convertir en DataFrame
            campaigns_data = [campaign.to_dict() for campaign in campaigns]
            campaigns_df = pd.DataFrame(campaigns_data)
            
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
        
        if prospects:
            # Convertir en DataFrame
            prospects_data = [prospect.to_dict() for prospect in prospects]
            prospects_df = pd.DataFrame(prospects_data)
            
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
        
        if prospects:
            # Convertir en DataFrame
            prospects_data = [prospect.to_dict() for prospect in prospects]
            prospects_df = pd.DataFrame(prospects_data)
            
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
