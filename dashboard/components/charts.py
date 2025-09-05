"""
Composants pour l'affichage des graphiques
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any, Optional, Union

def render_bar_chart(data: pd.DataFrame, x: str, y: str, title: str = "", 
                    color: Optional[str] = None, color_discrete_sequence: Optional[List[str]] = None):
    """
    Affiche un graphique à barres
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X
        y: Colonne pour l'axe Y
        title: Titre du graphique
        color: Colonne pour la couleur (optionnel)
        color_discrete_sequence: Séquence de couleurs (optionnel)
    """
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        color_discrete_sequence=color_discrete_sequence
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_line_chart(data: pd.DataFrame, x: str, y: str, title: str = "", 
                    color: Optional[str] = None, line_group: Optional[str] = None):
    """
    Affiche un graphique linéaire
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X
        y: Colonne pour l'axe Y
        title: Titre du graphique
        color: Colonne pour la couleur (optionnel)
        line_group: Colonne pour grouper les lignes (optionnel)
    """
    fig = px.line(
        data, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        line_group=line_group
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_pie_chart(data: pd.DataFrame, values: str, names: str, title: str = "", 
                    color_discrete_sequence: Optional[List[str]] = None):
    """
    Affiche un graphique circulaire
    
    Args:
        data: DataFrame contenant les données
        values: Colonne pour les valeurs
        names: Colonne pour les noms
        title: Titre du graphique
        color_discrete_sequence: Séquence de couleurs (optionnel)
    """
    fig = px.pie(
        data, 
        values=values, 
        names=names, 
        title=title,
        color_discrete_sequence=color_discrete_sequence
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_scatter_chart(data: pd.DataFrame, x: str, y: str, title: str = "", 
                        color: Optional[str] = None, size: Optional[str] = None):
    """
    Affiche un graphique de dispersion
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X
        y: Colonne pour l'axe Y
        title: Titre du graphique
        color: Colonne pour la couleur (optionnel)
        size: Colonne pour la taille (optionnel)
    """
    fig = px.scatter(
        data, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        size=size
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_histogram(data: pd.DataFrame, x: str, title: str = "", nbins: int = 20, 
                   color: Optional[str] = None):
    """
    Affiche un histogramme
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'histogramme
        title: Titre du graphique
        nbins: Nombre de bins
        color: Colonne pour la couleur (optionnel)
    """
    fig = px.histogram(
        data, 
        x=x, 
        title=title,
        nbins=nbins,
        color=color
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_box_plot(data: pd.DataFrame, y: str, title: str = "", x: Optional[str] = None, 
                   color: Optional[str] = None):
    """
    Affiche un graphique en boîte
    
    Args:
        data: DataFrame contenant les données
        y: Colonne pour l'axe Y
        title: Titre du graphique
        x: Colonne pour l'axe X (optionnel)
        color: Colonne pour la couleur (optionnel)
    """
    fig = px.box(
        data, 
        y=y, 
        x=x, 
        title=title,
        color=color
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_heatmap(data: pd.DataFrame, x: str, y: str, z: str, title: str = "", 
                 color_continuous_scale: Optional[str] = None):
    """
    Affiche une carte thermique
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X
        y: Colonne pour l'axe Y
        z: Colonne pour la couleur
        title: Titre du graphique
        color_continuous_scale: Échelle de couleurs (optionnel)
    """
    fig = px.density_heatmap(
        data, 
        x=x, 
        y=y, 
        z=z, 
        title=title,
        color_continuous_scale=color_continuous_scale
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_choropleth_map(data: pd.DataFrame, locations: str, locationmode: str = "country names", 
                         color: str, title: str = "", hover_name: Optional[str] = None, 
                         color_continuous_scale: Optional[str] = None):
    """
    Affiche une carte choroplèthe
    
    Args:
        data: DataFrame contenant les données
        locations: Colonne pour les localisations
        locationmode: Mode de localisation
        color: Colonne pour la couleur
        title: Titre du graphique
        hover_name: Colonne pour le nom au survol (optionnel)
        color_continuous_scale: Échelle de couleurs (optionnel)
    """
    fig = px.choropleth(
        data, 
        locations=locations,
        locationmode=locationmode,
        color=color,
        hover_name=hover_name,
        title=title,
        color_continuous_scale=color_continuous_scale
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_time_series_chart(data: pd.DataFrame, x: str, y: str, title: str = "", 
                           color: Optional[str] = None, line_group: Optional[str] = None):
    """
    Affiche un graphique de série temporelle
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X (dates)
        y: Colonne pour l'axe Y
        title: Titre du graphique
        color: Colonne pour la couleur (optionnel)
        line_group: Colonne pour grouper les lignes (optionnel)
    """
    fig = px.line(
        data, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        line_group=line_group
    )
    
    # Mettre en forme l'axe X pour les dates
    fig.update_xaxes(
        tickformat="%Y-%m-%d",
        tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_multi_axis_chart(data: pd.DataFrame, x: str, y1: str, y2: str, 
                           title: str = "", y1_title: str = "", y2_title: str = ""):
    """
    Affiche un graphique avec deux axes Y
    
    Args:
        data: DataFrame contenant les données
        x: Colonne pour l'axe X
        y1: Colonne pour le premier axe Y
        y2: Colonne pour le deuxième axe Y
        title: Titre du graphique
        y1_title: Titre du premier axe Y
        y2_title: Titre du deuxième axe Y
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Ajouter la première série
    fig.add_trace(
        go.Scatter(
            x=data[x], 
            y=data[y1], 
            name=y1_title or y1,
            line=dict(color="royalblue")
        ),
        secondary_y=False
    )
    
    # Ajouter la deuxième série
    fig.add_trace(
        go.Scatter(
            x=data[x], 
            y=data[y2], 
            name=y2_title or y2,
            line=dict(color="firebrick")
        ),
        secondary_y=True
    )
    
    # Définir les titres des axes
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y1_title or y1, secondary_y=False)
    fig.update_yaxes(title_text=y2_title or y2, secondary_y=True)
    
    fig.update_layout(title=title)
    
    st.plotly_chart(fig, use_container_width=True)

def render_gauge_chart(value: float, title: str, min_val: float = 0, max_val: float = 100):
    """
    Affiche un graphique de type jauge
    
    Args:
        value: Valeur actuelle
        title: Titre du graphique
        min_val: Valeur minimale
        max_val: Valeur maximale
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * 0.5], 'color': "lightgray"},
                {'range': [max_val * 0.5, max_val * 0.8], 'color': "gray"},
                {'range': [max_val * 0.8, max_val], 'color': "lightblue"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
