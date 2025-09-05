"""
Email Tracker pour EBUSINESS AI
Tracking des ouvertures et clics des emails
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import unquote
import json

from src.config import get_config
from src.core.database import db_manager
from src.core.utils import generate_tracking_id

logger = logging.getLogger(__name__)
config = get_config()

class EmailTracker:
    """Gestionnaire de tracking des emails"""

    def __init__(self):
        self.base_url = config.landing_page_url

    def generate_tracking_urls(self, prospect_id: int, email_content: str) -> Dict[str, str]:
        """
        Génère les URLs de tracking pour un email
        
        Args:
            prospect_id: ID du prospect
            email_content: Contenu de l'email
            
        Returns:
            Dict[str, str]: URLs de tracking
        """
        tracking_id = generate_tracking_id()
        
        tracking_urls = {
            'open_pixel': f"{self.base_url}/track/open/{tracking_id}",
            'click_tracker': f"{self.base_url}/track/click/{tracking_id}",
            'unsubscribe': f"{self.base_url}/unsubscribe/{tracking_id}",
            'tracking_id': tracking_id
        }
        
        # Sauvegarder le tracking ID dans la base de données
        self._save_tracking_id(prospect_id, tracking_id)
        
        return tracking_urls

    def _save_tracking_id(self, prospect_id: int, tracking_id: str):
        """
        Sauvegarde le tracking ID dans la base de données
        
        Args:
            prospect_id: ID du prospect
            tracking_id: ID de tracking
        """
        try:
            # Mettre à jour le prospect avec le tracking ID
            db_manager.update_prospect(
                prospect_id=prospect_id,
                updates={'tracking_id': tracking_id}
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde du tracking ID: {e}")

    def track_open(self, tracking_id: str) -> bool:
        """
        Enregistre l'ouverture d'un email
        
        Args:
            tracking_id: ID de tracking
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Trouver la campagne email correspondante
            campaign = db_manager.session.query(db_manager.EmailCampaign).filter(
                db_manager.EmailCampaign.tracking_id == tracking_id
            ).first()
            
            if not campaign:
                logger.warning(f"⚠️ Campagne non trouvée pour le tracking ID: {tracking_id}")
                return False
            
            # Vérifier si l'ouverture n'a pas déjà été enregistrée
            if campaign.opened_at:
                logger.info(f"ℹ️ Ouverture déjà enregistrée pour: {tracking_id}")
                return True
            
            # Enregistrer l'ouverture
            update_data = {
                'opened_at': datetime.now(),
                'opened': True
            }
            
            success = db_manager.update_email_campaign(tracking_id, update_data)
            
            if success:
                # Mettre à jour le prospect
                db_manager.update_prospect(
                    prospect_id=campaign.prospect_id,
                    updates={
                        'email_opened': True,
                        'email_opened_at': datetime.now()
                    }
                )
                
                logger.info(f"✅ Ouverture enregistrée pour: {tracking_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du tracking d'ouverture: {e}")
            return False

    def track_click(self, tracking_id: str) -> Optional[str]:
        """
        Enregistre le clic sur un email et retourne l'URL de redirection
        
        Args:
            tracking_id: ID de tracking
            
        Returns:
            Optional[str]: URL de redirection ou None si erreur
        """
        try:
            # Trouver la campagne email correspondante
            campaign = db_manager.session.query(db_manager.EmailCampaign).filter(
                db_manager.EmailCampaign.tracking_id == tracking_id
            ).first()
            
            if not campaign:
                logger.warning(f"⚠️ Campagne non trouvée pour le tracking ID: {tracking_id}")
                return None
            
            # Enregistrer le clic
            update_data = {
                'clicked_at': datetime.now(),
                'clicked': True
            }
            
            success = db_manager.update_email_campaign(tracking_id, update_data)
            
            if success:
                # Mettre à jour le prospect
                db_manager.update_prospect(
                    prospect_id=campaign.prospect_id,
                    updates={
                        'email_clicked': True,
                        'email_clicked_at': datetime.now()
                    }
                )
                
                logger.info(f"✅ Clic enregistré pour: {tracking_id}")
                
                # Retourner l'URL de la landing page
                return config.landing_page_url
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du tracking de clic: {e}")
            return None

    def get_tracking_stats(self, prospect_id: int) -> Dict[str, Any]:
        """
        Retourne les statistiques de tracking pour un prospect
        
        Args:
            prospect_id: ID du prospect
            
        Returns:
            Dict[str, Any]: Statistiques de tracking
        """
        try:
            prospect = db_manager.session.query(db_manager.Prospect).filter(
                db_manager.Prospect.id == prospect_id
            ).first()
            
            if not prospect:
                return {}
            
            campaigns = db_manager.session.query(db_manager.EmailCampaign).filter(
                db_manager.EmailCampaign.prospect_id == prospect_id
            ).all()
            
            stats = {
                'emails_sent': len(campaigns),
                'emails_opened': sum(1 for c in campaigns if c.opened_at),
                'emails_clicked': sum(1 for c in campaigns if c.clicked_at),
                'open_rate': 0,
                'click_rate': 0,
                'last_opened': None,
                'last_clicked': None
            }
            
            if stats['emails_sent'] > 0:
                stats['open_rate'] = (stats['emails_opened'] / stats['emails_sent']) * 100
            
            if stats['emails_opened'] > 0:
                stats['click_rate'] = (stats['emails_clicked'] / stats['emails_opened']) * 100
            
            # Dernières interactions
            if prospect.email_opened_at:
                stats['last_opened'] = prospect.email_opened_at.isoformat()
            
            if prospect.email_clicked_at:
                stats['last_clicked'] = prospect.email_clicked_at.isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des stats de tracking: {e}")
            return {}

    def get_campaign_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Retourne les performances des campagnes sur une période
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dict[str, Any]: Performances des campagnes
        """
        try:
            from datetime import timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            campaigns = db_manager.session.query(db_manager.EmailCampaign).filter(
                db_manager.EmailCampaign.sent_at >= start_date
            ).all()
            
            if not campaigns:
                return {
                    'total_sent': 0,
                    'total_opened': 0,
                    'total_clicked': 0,
                    'open_rate': 0,
                    'click_rate': 0,
                    'period_days': days
                }
            
            total_sent = len(campaigns)
            total_opened = sum(1 for c in campaigns if c.opened_at)
            total_clicked = sum(1 for c in campaigns if c.clicked_at)
            
            open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
            click_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
            
            # Performances par jour
            daily_stats = {}
            for i in range(days):
                day = start_date + timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                
                day_campaigns = [c for c in campaigns if c.sent_at.date() == day.date()]
                
                daily_stats[day_str] = {
                    'sent': len(day_campaigns),
                    'opened': sum(1 for c in day_campaigns if c.opened_at),
                    'clicked': sum(1 for c in day_campaigns if c.clicked_at)
                }
            
            return {
                'total_sent': total_sent,
                'total_opened': total_opened,
                'total_clicked': total_clicked,
                'open_rate': round(open_rate, 2),
                'click_rate': round(click_rate, 2),
                'period_days': days,
                'daily_stats': daily_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des performances: {e}")
            return {}

    def create_tracking_pixel(self, tracking_id: str) -> str:
        """
        Crée un pixel de tracking invisible
        
        Args:
            tracking_id: ID de tracking
            
        Returns:
            str: HTML du pixel de tracking
        """
        tracking_url = f"{self.base_url}/track/open/{tracking_id}"
        return f'<img src="{tracking_url}" width="1" height="1" border="0" style="display:none;">'

    def create_tracking_link(self, tracking_id: str, url: str, link_text: str) -> str:
        """
        Crée un lien de tracking
        
        Args:
            tracking_id: ID de tracking
            url: URL de destination
            link_text: Texte du lien
            
        Returns:
            str: HTML du lien de tracking
        """
        tracking_url = f"{self.base_url}/track/click/{tracking_id}"
        return f'<a href="{tracking_url}" style="color: #667eea; text-decoration: none;">{link_text}</a>'

# Instance globale du tracker
email_tracker = EmailTracker()

# Fonctions pour l'import facile
def track_email_open(tracking_id: str) -> bool:
    """
    Fonction wrapper pour le tracking d'ouverture
    
    Args:
        tracking_id: ID de tracking
        
    Returns:
        bool: True si succès, False sinon
    """
    return email_tracker.track_open(tracking_id)

def track_email_click(tracking_id: str) -> Optional[str]:
    """
    Fonction wrapper pour le tracking de clic
    
    Args:
        tracking_id: ID de tracking
        
    Returns:
        Optional[str]: URL de redirection ou None si erreur
    """
    return email_tracker.track_click(tracking_id)
