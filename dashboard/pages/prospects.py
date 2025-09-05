"""
Page de gestion des prospects
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

def render_prospects(status_filter=None, country_filter=None, sector_filter=None):
    """Affiche la page des prospects"""
    st.title("👥 Prospects")
    
    # Charger les données
    prospects = db_manager.get_prospects()
    
    if not prospects:
        st.warning("Aucun prospect trouvé dans la base de données.")
        return
    
    # Convertir en DataFrame
    prospects_data = [prospect.to_dict() for prospect in prospects]
    prospects_df = pd.DataFrame(prospects_data)
    
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
