"""
Gestionnaire d'exports pour EBUSINESS AI
Permet d'exporter les données vers des fichiers Excel de manière automatique
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import zipfile
from pathlib import Path

# Import des modules locaux
from src.core.database import db_manager
from src.core.utils import get_logger, format_date_for_display, format_number

# Configuration du logging
logger = get_logger(__name__)

class ExportManager:
    """
    Gestionnaire pour l'export des données vers des fichiers Excel
    """
    
    def __init__(self):
        """Initialisation du gestionnaire d'exports"""
        # S'assurer que le répertoire exports existe
        self.exports_dir = Path("data/exports")
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des exports
        self.max_rows_per_file = 10000  # Maximum de lignes par fichier
        self.include_metadata = True    # Inclure les métadonnées dans les exports
        
    def export_prospects_to_excel(self, 
                               prospects: Optional[List[Dict[str, Any]]] = None,
                               filters: Optional[Dict[str, Any]] = None,
                               filename: Optional[str] = None) -> str:
        """
        Exporte les prospects vers un fichier Excel
        
        Args:
            prospects: Liste des prospects à exporter (si None, utilise la base de données)
            filters: Filtres à appliquer
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin vers le fichier Excel créé
        """
        logger.info("Export des prospects vers Excel")
        
        try:
            # Si aucune liste de prospects n'est fournie, récupérer depuis la base de données
            if prospects is None:
                prospects_data = db_manager.get_prospects()
                prospects = [prospect.to_dict() for prospect in prospects_data]
            
            # Appliquer les filtres si fournis
            if filters:
                prospects = self._apply_prospect_filters(prospects, filters)
            
            # Créer un DataFrame pandas
            df = pd.DataFrame(prospects)
            
            # Nettoyer et formater les données
            df = self._clean_prospect_data(df)
            
            # Générer le nom du fichier si non fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"prospects_export_{timestamp}.xlsx"
            
            # S'assurer que le fichier a l'extension .xlsx
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Chemin complet du fichier
            file_path = self.exports_dir / filename
            
            # Créer le writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Feuille principale avec les prospects
                df.to_excel(writer, sheet_name='Prospects', index=False)
                
                # Feuille de résumé
                self._add_prospects_summary_sheet(writer, df)
                
                # Feuille de métadonnées si activé
                if self.include_metadata:
                    self._add_metadata_sheet(writer, {
                        'type': 'prospects',
                        'export_date': datetime.now().isoformat(),
                        'total_records': len(df),
                        'filters': filters or {}
                    })
            
            logger.info(f"Export des prospects terminé: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des prospects: {e}")
            raise
    
    def export_campaigns_to_excel(self,
                                campaigns: Optional[List[Dict[str, Any]]] = None,
                                filters: Optional[Dict[str, Any]] = None,
                                filename: Optional[str] = None) -> str:
        """
        Exporte les campagnes email vers un fichier Excel
        
        Args:
            campaigns: Liste des campagnes à exporter (si None, utilise la base de données)
            filters: Filtres à appliquer
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin vers le fichier Excel créé
        """
        logger.info("Export des campagnes vers Excel")
        
        try:
            # Si aucune liste de campagnes n'est fournie, récupérer depuis la base de données
            if campaigns is None:
                campaigns_data = db_manager.SessionLocal().query(db_manager.EmailCampaign).all()
                campaigns = [campaign.to_dict() for campaign in campaigns_data]
            
            # Appliquer les filtres si fournis
            if filters:
                campaigns = self._apply_campaign_filters(campaigns, filters)
            
            # Créer un DataFrame pandas
            df = pd.DataFrame(campaigns)
            
            # Nettoyer et formater les données
            df = self._clean_campaign_data(df)
            
            # Générer le nom du fichier si non fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"campaigns_export_{timestamp}.xlsx"
            
            # S'assurer que le fichier a l'extension .xlsx
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Chemin complet du fichier
            file_path = self.exports_dir / filename
            
            # Créer le writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Feuille principale avec les campagnes
                df.to_excel(writer, sheet_name='Campagnes', index=False)
                
                # Feuille de résumé
                self._add_campaigns_summary_sheet(writer, df)
                
                # Feuille de métadonnées si activé
                if self.include_metadata:
                    self._add_metadata_sheet(writer, {
                        'type': 'campaigns',
                        'export_date': datetime.now().isoformat(),
                        'total_records': len(df),
                        'filters': filters or {}
                    })
            
            logger.info(f"Export des campagnes terminé: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des campagnes: {e}")
            raise
    
    def export_statistics_to_excel(self,
                                 stats: Optional[Dict[str, Any]] = None,
                                 filename: Optional[str] = None) -> str:
        """
        Exporte les statistiques vers un fichier Excel
        
        Args:
            stats: Statistiques à exporter (si None, utilise la base de données)
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin vers le fichier Excel créé
        """
        logger.info("Export des statistiques vers Excel")
        
        try:
            # Si aucune statistique n'est fournie, récupérer depuis la base de données
            if stats is None:
                stats = db_manager.get_system_stats()
            
            # Créer des DataFrames pandas à partir des statistiques
            dfs = self._create_stats_dataframes(stats)
            
            # Générer le nom du fichier si non fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"statistics_export_{timestamp}.xlsx"
            
            # S'assurer que le fichier a l'extension .xlsx
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Chemin complet du fichier
            file_path = self.exports_dir / filename
            
            # Créer le writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Feuille avec les statistiques des prospects
                if 'prospects_df' in dfs:
                    dfs['prospects_df'].to_excel(writer, sheet_name='Prospects', index=False)
                
                # Feuille avec les statistiques des emails
                if 'emails_df' in dfs:
                    dfs['emails_df'].to_excel(writer, sheet_name='Emails', index=False)
                
                # Feuille avec les données par pays
                if 'by_country_df' in dfs:
                    dfs['by_country_df'].to_excel(writer, sheet_name='Par Pays', index=False)
                
                # Feuille avec les données par secteur
                if 'by_sector_df' in dfs:
                    dfs['by_sector_df'].to_excel(writer, sheet_name='Par Secteur', index=False)
                
                # Feuille de métadonnées si activé
                if self.include_metadata:
                    self._add_metadata_sheet(writer, {
                        'type': 'statistics',
                        'export_date': datetime.now().isoformat(),
                        'stats_date': datetime.now().isoformat()
                    })
            
            logger.info(f"Export des statistiques terminé: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des statistiques: {e}")
            raise
    
    def export_complete_report(self,
                             filters: Optional[Dict[str, Any]] = None,
                             filename: Optional[str] = None) -> str:
        """
        Exporte un rapport complet (prospects + campagnes + statistiques) vers un fichier Excel
        
        Args:
            filters: Filtres à appliquer
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin vers le fichier Excel créé
        """
        logger.info("Export d'un rapport complet vers Excel")
        
        try:
            # Générer le nom du fichier si non fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"complete_report_{timestamp}.xlsx"
            
            # S'assurer que le fichier a l'extension .xlsx
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Chemin complet du fichier
            file_path = self.exports_dir / filename
            
            # Créer le writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Exporter les prospects
                prospects_df = self._get_prospects_dataframe(filters)
                prospects_df.to_excel(writer, sheet_name='Prospects', index=False)
                
                # Exporter les campagnes
                campaigns_df = self._get_campaigns_dataframe(filters)
                campaigns_df.to_excel(writer, sheet_name='Campagnes', index=False)
                
                # Exporter les statistiques
                stats_dfs = self._create_stats_dataframes(db_manager.get_system_stats())
                
                if 'prospects_df' in stats_dfs:
                    stats_dfs['prospects_df'].to_excel(writer, sheet_name='Stats Prospects', index=False)
                
                if 'emails_df' in stats_dfs:
                    stats_dfs['emails_df'].to_excel(writer, sheet_name='Stats Emails', index=False)
                
                if 'by_country_df' in stats_dfs:
                    stats_dfs['by_country_df'].to_excel(writer, sheet_name='Stats par Pays', index=False)
                
                if 'by_sector_df' in stats_dfs:
                    stats_dfs['by_sector_df'].to_excel(writer, sheet_name='Stats par Secteur', index=False)
                
                # Feuille de résumé
                self._add_complete_summary_sheet(writer, prospects_df, campaigns_df)
                
                # Feuille de métadonnées si activé
                if self.include_metadata:
                    self._add_metadata_sheet(writer, {
                        'type': 'complete_report',
                        'export_date': datetime.now().isoformat(),
                        'total_prospects': len(prospects_df),
                        'total_campaigns': len(campaigns_df),
                        'filters': filters or {}
                    })
            
            logger.info(f"Export du rapport complet terminé: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export du rapport complet: {e}")
            raise
    
    def create_auto_export(self, 
                           export_type: str = 'prospects',
                           schedule: str = 'daily') -> str:
        """
        Crée un export automatique selon un planning
        
        Args:
            export_type: Type d'export ('prospects', 'campaigns', 'statistics', 'complete')
            schedule: Planning ('daily', 'weekly', 'monthly')
            
        Returns:
            Chemin vers le fichier Excel créé
        """
        logger.info(f"Création d'un export automatique: {export_type} ({schedule})")
        
        try:
            # Déterminer le nom du fichier selon le planning
            if schedule == 'daily':
                date_str = datetime.now().strftime("%Y%m%d")
                filename = f"{export_type}_auto_{date_str}.xlsx"
            elif schedule == 'weekly':
                # Obtenir le début de la semaine (lundi)
                today = datetime.now()
                start_of_week = today - pd.Timedelta(days=today.weekday())
                date_str = start_of_week.strftime("%Y%m%d")
                filename = f"{export_type}_auto_weekly_{date_str}.xlsx"
            elif schedule == 'monthly':
                date_str = datetime.now().strftime("%Y%m")
                filename = f"{export_type}_auto_monthly_{date_str}.xlsx"
            else:
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_type}_auto_{date_str}.xlsx"
            
            # Créer l'export selon le type
            if export_type == 'prospects':
                return self.export_prospects_to_excel(filename=filename)
            elif export_type == 'campaigns':
                return self.export_campaigns_to_excel(filename=filename)
            elif export_type == 'statistics':
                return self.export_statistics_to_excel(filename=filename)
            elif export_type == 'complete':
                return self.export_complete_report(filename=filename)
            else:
                raise ValueError(f"Type d'export inconnu: {export_type}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'export automatique: {e}")
            raise
    
    def cleanup_old_exports(self, days_to_keep: int = 30) -> List[str]:
        """
        Nettoie les anciens fichiers d'export
        
        Args:
            days_to_keep: Nombre de jours à conserver
            
        Returns:
            Liste des fichiers supprimés
        """
        logger.info(f"Nettoyage des exports plus anciens que {days_to_keep} jours")
        
        try:
            from datetime import timedelta
            
            deleted_files = []
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Parcourir tous les fichiers d'export
            for file_path in self.exports_dir.glob("*.xlsx"):
                # Vérifier la date de modification du fichier
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mod_time < cutoff_date:
                    # Supprimer le fichier
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                    logger.info(f"Fichier supprimé: {file_path}")
            
            logger.info(f"Nettoyage terminé: {len(deleted_files)} fichiers supprimés")
            return deleted_files
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des exports: {e}")
            raise
    
    def create_export_archive(self, 
                            export_files: List[str],
                            archive_name: Optional[str] = None) -> str:
        """
        Crée une archive ZIP contenant plusieurs fichiers d'export
        
        Args:
            export_files: Liste des chemins vers les fichiers à archiver
            archive_name: Nom de l'archive
            
        Returns:
            Chemin vers l'archive ZIP créée
        """
        logger.info(f"Création d'une archive avec {len(export_files)} fichiers")
        
        try:
            # Générer le nom de l'archive si non fourni
            if not archive_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"exports_archive_{timestamp}.zip"
            
            # S'assurer que l'archive a l'extension .zip
            if not archive_name.endswith('.zip'):
                archive_name += '.zip'
            
            # Chemin complet de l'archive
            archive_path = self.exports_dir / archive_name
            
            # Créer l'archive ZIP
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in export_files:
                    # Ajouter le fichier à l'archive
                    zipf.write(file_path, os.path.basename(file_path))
            
            logger.info(f"Archive créée: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'archive: {e}")
            raise
    
    # Méthodes privées
    
    def _clean_prospect_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et formate les données des prospects
        
        Args:
            df: DataFrame des prospects à nettoyer
            
        Returns:
            DataFrame nettoyé
        """
        # Convertir les dates en format lisible
        date_columns = ['date_added', 'date_contacted', 'date_responded', 'date_audit_booked']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: format_date_for_display(x) if pd.notnull(x) else '')
        
        # Formater les nombres
        if 'qualification_score' in df.columns:
            df['qualification_score'] = df['qualification_score'].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else '')
        
        # Remplacer les valeurs booléennes par des chaînes
        bool_columns = ['email_sent', 'email_opened', 'email_clicked']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: 'Oui' if x else 'Non')
        
        return df
    
    def _clean_campaign_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et formate les données des campagnes
        
        Args:
            df: DataFrame des campagnes à nettoyer
            
        Returns:
            DataFrame nettoyé
        """
        # Convertir les dates en format lisible
        date_columns = ['sent_at', 'opened_at', 'clicked_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: format_date_for_display(x) if pd.notnull(x) else '')
        
        return df
    
    def _apply_prospect_filters(self, prospects: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Applique des filtres à une liste de prospects
        
        Args:
            prospects: Liste des prospects
            filters: Dictionnaire de filtres
            
        Returns:
            Liste des prospects filtrés
        """
        filtered_prospects = prospects.copy()
        
        # Filtrer par statut
        if 'status' in filters:
            status_filter = filters['status']
            if isinstance(status_filter, list):
                filtered_prospects = [p for p in filtered_prospects if p.get('status') in status_filter]
            else:
                filtered_prospects = [p for p in filtered_prospects if p.get('status') == status_filter]
        
        # Filtrer par pays
        if 'country' in filters:
            country_filter = filters['country']
            if isinstance(country_filter, list):
                filtered_prospects = [p for p in filtered_prospects if p.get('country') in country_filter]
            else:
                filtered_prospects = [p for p in filtered_prospects if p.get('country') == country_filter]
        
        # Filtrer par secteur
        if 'sector' in filters:
            sector_filter = filters['sector']
            if isinstance(sector_filter, list):
                filtered_prospects = [p for p in filtered_prospects if p.get('sector') in sector_filter]
            else:
                filtered_prospects = [p for p in filtered_prospects if p.get('sector') == sector_filter]
        
        # Filtrer par score de qualification
        if 'min_score' in filters:
            min_score = filters['min_score']
            filtered_prospects = [p for p in filtered_prospects if p.get('qualification_score', 0) >= min_score]
        
        if 'max_score' in filters:
            max_score = filters['max_score']
            filtered_prospects = [p for p in filtered_prospects if p.get('qualification_score', 0) <= max_score]
        
        return filtered_prospects
    
    def _apply_campaign_filters(self, campaigns: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Applique des filtres à une liste de campagnes
        
        Args:
            campaigns: Liste des campagnes
            filters: Dictionnaire de filtres
            
        Returns:
            Liste des campagnes filtrées
        """
        filtered_campaigns = campaigns.copy()
        
        # Filtrer par statut de livraison
        if 'delivery_status' in filters:
            status_filter = filters['delivery_status']
            if isinstance(status_filter, list):
                filtered_campaigns = [c for c in filtered_campaigns if c.get('delivery_status') in status_filter]
            else:
                filtered_campaigns = [c for c in filtered_campaigns if c.get('delivery_status') == status_filter]
        
        # Filtrer par date d'envoi
        if 'sent_after' in filters:
            sent_after = filters['sent_after']
            filtered_campaigns = [c for c in filtered_campaigns if c.get('sent_at') and c['sent_at'] >= sent_after]
        
        if 'sent_before' in filters:
            sent_before = filters['sent_before']
            filtered_campaigns = [c for c in filtered_campaigns if c.get('sent_at') and c['sent_at'] <= sent_before]
        
        return filtered_campaigns
    
    def _create_stats_dataframes(self, stats: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Crée des DataFrames pandas à partir des statistiques
        
        Args:
            stats: Dictionnaire de statistiques
            
        Returns:
            Dictionnaire de DataFrames
        """
        dataframes = {}
        
        # DataFrame pour les statistiques des prospects
        if 'prospects' in stats:
            prospects_stats = stats['prospects']
            prospects_df = pd.DataFrame([
                {
                    'Métrique': 'Total',
                    'Valeur': prospects_stats.get('total', 0)
                },
                {
                    'Métrique': 'Qualifiés',
                    'Valeur': prospects_stats.get('qualified', 0)
                },
                {
                    'Métrique': 'Contactés',
                    'Valeur': prospects_stats.get('contacted', 0)
                },
                {
                    'Métrique': 'Répondu',
                    'Valeur': prospects_stats.get('responded', 0)
                },
                {
                    'Métrique': 'Audits Réservés',
                    'Valeur': prospects_stats.get('audit_booked', 0)
                }
            ])
            dataframes['prospects_df'] = prospects_df
        
        # DataFrame pour les statistiques des emails
        if 'emails' in stats:
            emails_stats = stats['emails']
            emails_df = pd.DataFrame([
                {
                    'Métrique': 'Total',
                    'Valeur': emails_stats.get('total', 0)
                },
                {
                    'Métrique': 'Ouverts',
                    'Valeur': emails_stats.get('opened', 0)
                },
                {
                    'Métrique': 'Cliqués',
                    'Valeur': emails_stats.get('clicked', 0)
                },
                {
                    'Métrique': 'Taux d\'Ouverture',
                    'Valeur': f"{emails_stats.get('open_rate', 0):.1f}%"
                },
                {
                    'Métrique': 'Taux de Clic',
                    'Valeur': f"{emails_stats.get('click_rate', 0):.1f}%"
                }
            ])
            dataframes['emails_df'] = emails_df
        
        # DataFrame pour les données par pays
        if 'by_country' in stats:
            by_country = stats['by_country']
            by_country_df = pd.DataFrame([
                {'Pays': country, 'Nombre': count}
                for country, count in by_country.items()
            ])
            dataframes['by_country_df'] = by_country_df
        
        # DataFrame pour les données par secteur
        if 'by_sector' in stats:
            by_sector = stats['by_sector']
            by_sector_df = pd.DataFrame([
                {'Secteur': sector, 'Nombre': count}
                for sector, count in by_sector.items()
            ])
            dataframes['by_sector_df'] = by_sector_df
        
        return dataframes
    
    def _get_prospects_dataframe(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Récupère un DataFrame des prospects depuis la base de données
        
        Args:
            filters: Filtres à appliquer
            
        Returns:
            DataFrame des prospects
        """
        prospects = db_manager.get_prospects()
        prospects_data = [prospect.to_dict() for prospect in prospects]
        
        if filters:
            prospects_data = self._apply_prospect_filters(prospects_data, filters)
        
        df = pd.DataFrame(prospects_data)
        return self._clean_prospect_data(df)
    
    def _get_campaigns_dataframe(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Récupère un DataFrame des campagnes depuis la base de données
        
        Args:
            filters: Filtres à appliquer
            
        Returns:
            DataFrame des campagnes
        """
        campaigns = db_manager.SessionLocal().query(db_manager.EmailCampaign).all()
        campaigns_data = [campaign.to_dict() for campaign in campaigns]
        
        if filters:
            campaigns_data = self._apply_campaign_filters(campaigns_data, filters)
        
        df = pd.DataFrame(campaigns_data)
        return self._clean_campaign_data(df)
    
    def _add_prospects_summary_sheet(self, writer, df: pd.DataFrame):
        """
        Ajoute une feuille de résumé pour les prospects
        
        Args:
            writer: Excel writer
            df: DataFrame des prospects
        """
        # Calculer les statistiques
        stats = {
            'Total': len(df),
            'Par Statut': df['status'].value_counts().to_dict(),
            'Par Pays': df['country'].value_counts().to_dict(),
            'Par Secteur': df['sector'].value_counts().to_dict(),
            'Score Moyen': df['qualification_score'].astype(float).mean()
        }
        
        # Créer un DataFrame pour le résumé
        summary_df = pd.DataFrame([
            {'Métrique': 'Total Prospects', 'Valeur': stats['Total']},
            {'Métrique': 'Score Moyen', 'Valeur': f"{stats['Score Moyen']:.1f}"}
        ])
        
        # Ajouter la feuille de résumé
        summary_df.to_excel(writer, sheet_name='Résumé Prospects', index=False)
        
        # Ajouter les détails par statut
        status_df = pd.DataFrame(list(stats['Par Statut'].items()), columns=['Statut', 'Nombre'])
        status_df.to_excel(writer, sheet_name='Par Statut', index=False)
        
        # Ajouter les détails par pays
        country_df = pd.DataFrame(list(stats['Par Pays'].items()), columns=['Pays', 'Nombre'])
        country_df.to_excel(writer, sheet_name='Par Pays', index=False)
        
        # Ajouter les détails par secteur
        sector_df = pd.DataFrame(list(stats['Par Secteur'].items()), columns=['Secteur', 'Nombre'])
        sector_df.to_excel(writer, sheet_name='Par Secteur', index=False)
    
    def _add_campaigns_summary_sheet(self, writer, df: pd.DataFrame):
        """
        Ajoute une feuille de résumé pour les campagnes
        
        Args:
            writer: Excel writer
            df: DataFrame des campagnes
        """
        # Calculer les statistiques
        stats = {
            'Total': len(df),
            'Par Statut de Livraison': df['delivery_status'].value_counts().to_dict()
        }
        
        # Créer un DataFrame pour le résumé
        summary_df = pd.DataFrame([
            {'Métrique': 'Total Campagnes', 'Valeur': stats['Total']}
        ])
        
        # Ajouter la feuille de résumé
        summary_df.to_excel(writer, sheet_name='Résumé Campagnes', index=False)
        
        # Ajouter les détails par statut de livraison
        status_df = pd.DataFrame(list(stats['Par Statut de Livraison'].items()), columns=['Statut', 'Nombre'])
        status_df.to_excel(writer, sheet_name='Par Statut de Livraison', index=False)
    
    def _add_complete_summary_sheet(self, writer, prospects_df, campaigns_df):
        """
        Ajoute une feuille de résumé pour un rapport complet
        
        Args:
            writer: Excel writer
            prospects_df: DataFrame des prospects
            campaigns_df: DataFrame des campagnes
        """
        # Calculer les statistiques
        stats = {
            'Total Prospects': len(prospects_df),
            'Total Campagnes': len(campaigns_df),
            'Prospects Qualifiés': len(prospects_df[prospects_df['status'] == 'qualifié']),
            'Campagnes Envoyées': len(campaigns_df[campaigns_df['delivery_status'] == 'sent'])
        }
        
        # Créer un DataFrame pour le résumé
        summary_df = pd.DataFrame([
            {'Métrique': 'Total Prospects', 'Valeur': stats['Total Prospects']},
            {'Métrique': 'Total Campagnes', 'Valeur': stats['Total Campagnes']},
            {'Métrique': 'Prospects Qualifiés', 'Valeur': stats['Prospects Qualifiés']},
            {'Métrique': 'Campagnes Envoyées', 'Valeur': stats['Campagnes Envoyées']}
        ])
        
        # Ajouter la feuille de résumé
        summary_df.to_excel(writer, sheet_name='Résumé Complet', index=False)
    
    def _add_metadata_sheet(self, writer, metadata: Dict[str, Any]):
        """
        Ajoute une feuille de métadonnées
        
        Args:
            writer: Excel writer
            metadata: Dictionnaire de métadonnées
        """
        # Créer un DataFrame pour les métadonnées
        metadata_df = pd.DataFrame([
            {'Propriété': 'Type', 'Valeur': metadata.get('type', '')},
            {'Propriété': 'Date d\'Export', 'Valeur': metadata.get('export_date', '')},
            {'Propriété': 'Total Enregistrements', 'Valeur': metadata.get('total_records', 0)}
        ])
        
        # Ajouter les filtres si présents
        if 'filters' in metadata and metadata['filters']:
            filters = metadata['filters']
            for key, value in filters.items():
                metadata_df = pd.concat([
                    metadata_df,
                    pd.DataFrame([{'Propriété': f'Filtre: {key}', 'Valeur': str(value)}])
                ], ignore_index=True)
        
        # Ajouter la feuille de métadonnées
        metadata_df.to_excel(writer, sheet_name='Métadonnées', index=False)


# Instance globale du gestionnaire d'exports
export_manager = ExportManager()
