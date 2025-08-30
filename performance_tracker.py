import logging
from datetime import datetime, timedelta
from config import RETENTION_DAYS

logger = logging.getLogger(__name__)

class PerformanceTracker:
    def __init__(self):
        self.campaign_metrics = {}
    
    def track_campaign(self, agency_name, emails_sent):
        """Suit les performances d'une campagne"""
        try:
            if agency_name not in self.campaign_metrics:
                self.campaign_metrics[agency_name] = {
                    'emails_sent': 0,
                    'opened': 0,
                    'replied': 0,
                    'converted': 0,
                    'start_date': datetime.now()
                }
            
            # Mettre à jour les métriques
            self.campaign_metrics[agency_name]['emails_sent'] += emails_sent
            
            # Calculer les taux
            metrics = self.campaign_metrics[agency_name]
            metrics['open_rate'] = (metrics['opened'] / metrics['emails_sent'] * 100) if metrics['emails_sent'] > 0 else 0
            metrics['reply_rate'] = (metrics['replied'] / metrics['emails_sent'] * 100) if metrics['emails_sent'] > 0 else 0
            metrics['conversion_rate'] = (metrics['converted'] / metrics['emails_sent'] * 100) if metrics['emails_sent'] > 0 else 0
            
            logger.info(f"Campagne {agency_name}: {emails_sent} emails envoyés")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors du suivi de la campagne {agency_name}: {e}")
            return {}
    
    def update_email_status(self, email_id, status):
        """Met à jour le statut d'un email"""
        try:
            # Cette méthode serait connectée aux webhooks de SendGrid
            # pour suivre les ouvertures, clics et réponses
            pass
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut de l'email: {e}")
    
    def cleanup_old_data(self):
        """Nettoie les anciennes données selon la politique de rétention"""
        try:
            cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
            # Supprimer les données antérieures à la date limite
            logger.info(f"Nettoyage des données antérieures à {cutoff_date}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
    
    def generate_report(self, agency_name):
        """Génère un rapport de performance pour une agence"""
        try:
            if agency_name in self.campaign_metrics:
                metrics = self.campaign_metrics[agency_name]
                return {
                    'agency': agency_name,
                    'period': f"{metrics['start_date'].strftime('%Y-%m-%d')} à {datetime.now().strftime('%Y-%m-%d')}",
                    'emails_sent': metrics['emails_sent'],
                    'opened': metrics['opened'],
                    'replied': metrics['replied'],
                    'converted': metrics['converted'],
                    'open_rate': metrics['open_rate'],
                    'reply_rate': metrics['reply_rate'],
                    'conversion_rate': metrics['conversion_rate']
                }
            else:
                return {'error': f'Aucune donnée trouvée pour {agency_name}'}
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {'error': str(e)}
