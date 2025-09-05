"""
Composants pour l'affichage des tableaux
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
import io
import base64

def render_dataframe(data: pd.DataFrame, height: Optional[int] = None, 
                   use_container_width: bool = True, selection: Optional[str] = None):
    """
    Affiche un DataFrame avec des options de personnalisation
    
    Args:
        data: DataFrame à afficher
        height: Hauteur du tableau (optionnel)
        use_container_width: Utiliser la largeur du conteneur
        selection: Type de sélection ('single', 'multi', None)
    
    Returns:
        DataFrame sélectionné ou None
    """
    if selection == 'single':
        return st.dataframe(
            data,
            height=height,
            use_container_width=use_container_width,
            selection="single"
        )
    elif selection == 'multi':
        return st.dataframe(
            data,
            height=height,
            use_container_width=use_container_width,
            selection="multi"
        )
    else:
        return st.dataframe(
            data,
            height=height,
            use_container_width=use_container_width
        )

def render_data_editor(data: pd.DataFrame, height: Optional[int] = None, 
                      use_container_width: bool = True, num_rows: str = "dynamic"):
    """
    Affiche un DataFrame éditable
    
    Args:
        data: DataFrame à éditer
        height: Hauteur du tableau (optionnel)
        use_container_width: Utiliser la largeur du conteneur
        num_rows: Gestion des lignes ('dynamic', 'fixed')
    
    Returns:
        DataFrame édité
    """
    return st.data_editor(
        data,
        height=height,
        use_container_width=use_container_width,
        num_rows=num_rows
    )

def render_aggrid(data: pd.DataFrame, height: int = 400, 
                 fit_columns_on_grid_load: bool = True,
                 auto_height: bool = False,
                 enable_enterprise_modules: bool = False,
                 license_key: Optional[str] = None):
    """
    Affiche un DataFrame avec Ag-Grid (si installé)
    
    Args:
        data: DataFrame à afficher
        height: Hauteur du tableau
        fit_columns_on_grid_load: Ajuster les colonnes au chargement
        auto_height: Hauteur automatique
        enable_enterprise_modules: Activer les modules entreprise
        license_key: Clé de licence Ag-Grid
    
    Returns:
        Instance AgGridReturn ou None
    """
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
        
        gb = GridOptionsBuilder.from_dataframe(data)
        gb.configure_default_column(
            filterable=True, 
            sortable=True, 
            resizable=True,
            editable=False
        )
        
        if fit_columns_on_grid_load:
            gb.configure_grid_options(autoSizeColumns=True)
        
        gridOptions = gb.build()
        
        return AgGrid(
            data,
            gridOptions=gridOptions,
            height=height,
            fit_columns_on_grid_load=fit_columns_on_grid_load,
            auto_height=auto_height,
            enable_enterprise_modules=enable_enterprise_modules,
            license_key=license_key
        )
    except ImportError:
        st.warning("Ag-Grid n'est pas installé. Utilisation du tableau standard.")
        return st.dataframe(data, height=height, use_container_width=True)

def render_download_button(data: pd.DataFrame, filename: str = "data.csv", 
                          button_text: str = "Télécharger CSV"):
    """
    Affiche un bouton de téléchargement pour un DataFrame
    
    Args:
        data: DataFrame à télécharger
        filename: Nom du fichier
        button_text: Texte du bouton
    """
    csv = data.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label=button_text,
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

def render_excel_download(data: pd.DataFrame, filename: str = "data.xlsx", 
                         button_text: str = "Télécharger Excel"):
    """
    Affiche un bouton de téléchargement Excel pour un DataFrame
    
    Args:
        data: DataFrame à télécharger
        filename: Nom du fichier
        button_text: Texte du bouton
    """
    try:
        towrite = io.BytesIO()
        data.to_excel(towrite, index=False)  # write to BytesIO buffer
        towrite.seek(0)  # reset pointer
        
        b64 = base64.b64encode(towrite.read()).decode()  # encode to base64
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{button_text}</a>'
        
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de la création du fichier Excel: {e}")

def render_filterable_table(data: pd.DataFrame, key: str = "filterable_table"):
    """
    Affiche un tableau avec des filtres
    
    Args:
        data: DataFrame à afficher
        key: Clé unique pour le composant
    
    Returns:
        DataFrame filtré
    """
    # Créer des filtres pour chaque colonne
    filters = {}
    
    for col in data.columns:
        if data[col].dtype == 'object':
            # Pour les colonnes de texte, utiliser un sélecteur multiple
            unique_values = data[col].unique().tolist()
            selected_values = st.multiselect(
                f"Filtrer par {col}",
                options=unique_values,
                default=unique_values,
                key=f"{key}_{col}"
            )
            
            if selected_values:
                filters[col] = selected_values
        elif data[col].dtype in ['int64', 'float64']:
            # Pour les colonnes numériques, utiliser un curseur
            min_val, max_val = float(data[col].min()), float(data[col].max())
            selected_range = st.slider(
                f"Filtrer par {col}",
                min_val, max_val, (min_val, max_val),
                key=f"{key}_{col}"
            )
            
            filters[col] = selected_range
    
    # Appliquer les filtres
    filtered_data = data.copy()
    
    for col, filter_val in filters.items():
        if data[col].dtype == 'object':
            filtered_data = filtered_data[filtered_data[col].isin(filter_val)]
        elif data[col].dtype in ['int64', 'float64']:
            filtered_data = filtered_data[
                (filtered_data[col] >= filter_val[0]) & 
                (filtered_data[col] <= filter_val[1])
            ]
    
    # Afficher le tableau filtré
    st.dataframe(filtered_data, use_container_width=True)
    
    return filtered_data

def render_searchable_table(data: pd.DataFrame, search_columns: List[str], 
                           key: str = "searchable_table"):
    """
    Affiche un tableau avec une fonction de recherche
    
    Args:
        data: DataFrame à afficher
        search_columns: Colonnes à inclure dans la recherche
        key: Clé unique pour le composant
    
    Returns:
        DataFrame filtré
    """
    # Champ de recherche
    search_term = st.text_input("Rechercher", key=f"{key}_search")
    
    # Appliquer la recherche
    if search_term:
        mask = pd.Series([False] * len(data))
        
        for col in search_columns:
            if col in data.columns:
                mask |= data[col].astype(str).str.contains(search_term, case=False)
        
        filtered_data = data[mask]
    else:
        filtered_data = data
    
    # Afficher le tableau filtré
    st.dataframe(filtered_data, use_container_width=True)
    
    return filtered_data

def render_expandable_table(data: pd.DataFrame, expand_column: str, 
                          expanded_columns: List[str], key: str = "expandable_table"):
    """
    Affiche un tableau avec des lignes extensibles
    
    Args:
        data: DataFrame à afficher
        expand_column: Colonne contenant le contenu à développer
        expanded_columns: Colonnes à afficher dans la ligne développée
        key: Clé unique pour le composant
    """
    # Afficher le tableau principal
    display_data = data.drop(columns=expanded_columns)
    st.dataframe(display_data, use_container_width=True)
    
    # Sélectionner une ligne pour développer
    row_index = st.number_input(
        "Sélectionner une ligne à développer",
        min_value=0,
        max_value=len(data)-1,
        value=0,
        key=f"{key}_row_selector"
    )
    
    # Afficher les détails de la ligne sélectionnée
    st.subheader(f"Détails de la ligne {row_index}")
    
    for col in expanded_columns:
        if col in data.columns:
            st.write(f"**{col}:**")
            st.write(data.iloc[row_index][col])

def render_pivot_table(data: pd.DataFrame, index: List[str], columns: List[str], 
                      values: List[str], aggfunc: str = "sum", key: str = "pivot_table"):
    """
    Affiche un tableau croisé dynamique
    
    Args:
        data: DataFrame à utiliser
        index: Colonnes pour l'index
        columns: Colonnes pour les colonnes
        values: Colonnes pour les valeurs
        aggfunc: Fonction d'agrégation
        key: Clé unique pour le composant
    """
    # Créer le tableau croisé dynamique
    pivot_table = pd.pivot_table(
        data,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=0
    )
    
    # Afficher le tableau
    st.dataframe(pivot_table, use_container_width=True)
    
    return pivot_table
