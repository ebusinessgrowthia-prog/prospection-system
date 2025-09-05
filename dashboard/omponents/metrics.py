"""
Composants pour l'affichage des métriques
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

def render_metric_card(title: str, value: Any, delta: Optional[str] = None, delta_color: str = "normal"):
    """
    Affiche une carte de métrique personnalisée
    
    Args:
        title: Titre de la métrique
        value: Valeur de la métrique
        delta: Variation (optionnel)
        delta_color: Couleur de la variation
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def render_progress_bar(value: float, title: str, color: str = "#667eea"):
    """
    Affiche une barre de progression
    
    Args:
        value: Valeur de progression (0-100)
        title: Titre de la barre
        color: Couleur de la barre
    """
    st.write(f"**{title}**")
    st.progress(value / 100)
    st.write(f"{value:.1f}%")

def render_gauge_chart(value: float, title: str, min_val: float = 0, max_val: float = 100, 
                      threshold: Optional[float] = None, threshold_color: str = "red"):
    """
    Affiche un graphique de type jauge
    
    Args:
        value: Valeur actuelle
        title: Titre du graphique
        min_val: Valeur minimale
        max_val: Valeur maximale
        threshold: Seuil (optionnel)
        threshold_color: Couleur du seuil
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': max_val / 2},
        gauge={
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * 0.5], 'color': "lightgray"},
                {'range': [max_val * 0.5, max_val * 0.8], 'color': "gray"},
                {'range': [max_val * 0.8, max_val], 'color': "lightblue"}
            ],
            'threshold': {
                'line': {'color': threshold_color, 'width': 4},
                'thickness': 0.75,
                'value': threshold if threshold else max_val * 0.9
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

def render_kpi_cards(kpi_data: List[Dict[str, Any]], columns: int = 4):
    """
    Affiche plusieurs cartes KPI
    
    Args:
        kpi_data: Liste de dictionnaires avec 'title', 'value', 'delta'
        columns: Nombre de colonnes
    """
    cols = st.columns(columns)
    
    for i, kpi in enumerate(kpi_data):
        with cols[i % columns]:
            render_metric_card(
                title=kpi.get('title', ''),
                value=kpi.get('value', 0),
                delta=kpi.get('delta'),
                delta_color=kpi.get('delta_color', 'normal')
            )

def render_funnel_chart(values: List[float], labels: List[str], title: str = "Funnel"):
    """
    Affiche un graphique en entonnoir
    
    Args:
        values: Liste des valeurs
        labels: Liste des étiquettes
        title: Titre du graphique
    """
    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#667eea", "#764ba2", "#f093fb", "#f5576c"]}
    ))
    
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

def render_waterfall_chart(values: List[float], labels: List[str], title: str = "Waterfall"):
    """
    Affiche un graphique en cascade
    
    Args:
        values: Liste des valeurs
        labels: Liste des étiquettes
        title: Titre du graphique
    """
    fig = go.Figure(go.Waterfall(
        name="Waterfall",
        orientation="v",
        measure=["relative"] * (len(values) - 1) + ["total"],
        x=labels,
        y=values,
        textposition="outside",
        textinfo="value",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

def render_indicator_chart(value: float, title: str, icon: str = "📊"):
    """
    Affiche un indicateur simple avec icône
    
    Args:
        value: Valeur de l'indicateur
        title: Titre de l'indicateur
        icon: Icône à afficher
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {title}")
        st.markdown(f"<div style='font-size: 2rem; font-weight: bold; color: #667eea;'>{value}</div>", unsafe_allow_html=True)
