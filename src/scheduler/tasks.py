"""
Scheduled Tasks pour EBUSINESS AI
Définition des tâches planifiées pour l'automatisation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.config import get_config
from src.core.database import db_manager
from src.scrapers.google_dorks_scraper import search_prospects_with_google_dorks
from src.processors.prospect_qualifier import qualify_prospect_data
from src.processors.mistral_personalizer import generate_personalized_email_for_prospect
from src.processors.data_enricher import enrich_prospect
from src.email.sender import send_email_to_prospect
from src.core.utils import is_business_hours, get_next_business_hour

logger = logging.getLogger(__name__)
config = get_config()

class ScheduledTasks:
    """Gestionnaire des tâches planifiées"""

    def __init__(self):
        self.db_manager = db_manager

    def search_prospects_task(self):
        """Tâche de recherche de prospects (toutes les 2 heures)"""
        try:
            logger.info("🔍 Démarrage de la tâche de recherche de prospects...")
            
            # Récupérer les Google Dorks
            dorks = config.get_google_dorks()
            
            # Lancer la recherche
            result = search_prospects_with_google_dorks(dorks, max_results_per_dork=20)
            
            if result.success:
                prospects_added = 0
                
                # Ajouter les prospects à la base de données
                for prospect_data in result.data:
                    prospect = self.db_manager.add_prospect(prospect_data)
                    if prospect:
                        prospects_added += 1
                
                logger.info(f"✅ Recherche terminée: {prospects_added} prospects ajoutés")
                
                # Logger l'événement
                self.db_manager.log_system_event(
                    level="INFO",
                    message=f"Recherche prospects terminée: {prospects_added} ajoutés",
                    module="search_prospects_task",
                    extra_data={
                        "dorks_used": len(dorks),
                        "prospects_found": len(result.data),
                        "prospects_added": prospects_added
                    }
                )
            else:
                logger.error(f"❌ Échec de la recherche: {result.error}")
                
                self.db_manager.log_system_event(
                    level="ERROR",
                    message=f"Échec recherche prospects: {result.error}",
                    module="search_prospects_task"
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche de recherche: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur recherche prospects: {str(e)}",
                module="search_prospects_task"
            )

    def qualify_prospects_task(self):
        """Tâche de qualification des prospects (toutes les heures)"""
        try:
            logger.info("🎯 Démarrage de la tâche de qualification des prospects...")
            
            # Récupérer les prospects non qualifiés
            prospects = self.db_manager.get_prospects(status='nouveau', limit=50)
            
            qualified_count = 0
            
            for prospect in prospects:
                try:
                    # Qualifier le prospect
                    qualification_result = qualify_prospect_data(prospect.to_dict())
                    
                    if qualification_result.qualified:
                        # Mettre à jour le prospect
                        update_data = {
                            'status': 'qualifié',
                            'qualification_score': qualification_result.score,
                            'problem_detected': qualification_result.detected_problems,
                            'specificity': qualification_result.specificities
                        }
                        
                        success = self.db_manager.update_prospect(prospect.id, update_data)
                        
                        if success:
                            qualified_count += 1
                            
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la qualification du prospect {prospect.id}: {e}")
                    continue
            
            logger.info(f"✅ Qualification terminée: {qualified_count} prospects qualifiés")
            
            # Logger l'événement
            self.db_manager.log_system_event(
                level="INFO",
                message=f"Qualification prospects terminée: {qualified_count} qualifiés",
                module="qualify_prospects_task",
                extra_data={
                    "prospects_processed": len(prospects),
                    "prospects_qualified": qualified_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche de qualification: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur qualification prospects: {str(e)}",
                module="qualify_prospects_task"
            )

    def enrich_prospects_task(self):
        """Tâche d'enrichissement des prospects (toutes les 3 heures)"""
        try:
            logger.info("🔧 Démarrage de la tâche d'enrichissement des prospects...")
            
            # Récupérer les prospects qualifiés non enrichis
            prospects = self.db_manager.get_prospects(status='qualifié', limit=30)
            
            enriched_count = 0
            
            for prospect in prospects:
                try:
                    # Enrichir le prospect
                    enriched_data = enrich_prospect(prospect.to_dict())
                    
                    # Mettre à jour le prospect avec les données enrichies
                    update_data = {
                        'raw_data': enriched_data.get('raw_data', {}),
                        'qualification_score': enriched_data.get('potential_score', prospect.qualification_score)
                    }
                    
                    success = self.db_manager.update_prospect(prospect.id, update_data)
                    
                    if success:
                        enriched_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Erreur lors de l'enrichissement du prospect {prospect.id}: {e}")
                    continue
            
            logger.info(f"✅ Enrichissement terminé: {enriched_count} prospects enrichis")
            
            # Logger l'événement
            self.db_manager.log_system_event(
                level="INFO",
                message=f"Enrichissement prospects terminé: {enriched_count} enrichis",
                module="enrich_prospects_task",
                extra_data={
                    "prospects_processed": len(prospects),
                    "prospects_enriched": enriched_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche d'enrichissement: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur enrichissement prospects: {str(e)}",
                module="enrich_prospects_task"
            )

    def generate_emails_task(self):
        """Tâche de génération d'emails (toutes les 30 minutes pendant les heures de bureau)"""
        try:
            if not is_business_hours():
                logger.info("⏰ Hors heures de bureau, génération d'emails suspendue")
                return
            
            logger.info("✏️ Démarrage de la tâche de génération d'emails...")
            
            # Récupérer les prospects qualifiés sans email généré
            prospects_to_contact = self.db_manager.get_prospects_to_contact(limit=10)
            
            generated_count = 0
            
            for prospect in prospects_to_contact:
                try:
                    # Générer l'email personnalisé
                    email_result = generate_personalized_email_for_prospect(prospect.to_dict())
                    
                    if email_result.success:
                        # Sauvegarder l'email généré dans les données brutes du prospect
                        raw_data = prospect.raw_data or {}
                        raw_data['generated_email'] = {
                            'subject': email_result.subject,
                            'content': email_result.content,
                            'generated_at': email_result.generated_at.isoformat()
                        }
                        
                        success = self.db_manager.update_prospect(
                            prospect.id,
                            {'raw_data': raw_data}
                        )
                        
                        if success:
                            generated_count += 1
                            
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la génération d'email pour le prospect {prospect.id}: {e}")
                    continue
            
            logger.info(f"✅ Génération terminée: {generated_count} emails générés")
            
            # Logger l'événement
            self.db_manager.log_system_event(
                level="INFO",
                message=f"Génération emails terminée: {generated_count} générés",
                module="generate_emails_task",
                extra_data={
                    "prospects_processed": len(prospects_to_contact),
                    "emails_generated": generated_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche de génération d'emails: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur génération emails: {str(e)}",
                module="generate_emails_task"
            )

    def send_emails_task(self):
        """Tâche d'envoi d'emails (toutes les 15 minutes pendant les heures de bureau)"""
        try:
            if not is_business_hours():
                logger.info("⏰ Hors heures de bureau, envoi d'emails suspendu")
                return
            
            logger.info("📧 Démarrage de la tâche d'envoi d'emails...")
            
            # Récupérer les prospects qualifiés avec email généré mais non envoyé
            prospects_to_email = self.db_manager.get_prospects_to_contact(limit=5)
            
            sent_count = 0
            
            for prospect in prospects_to_email:
                try:
                    # Récupérer l'email généré
                    raw_data = prospect.raw_data or {}
                    generated_email = raw_data.get('generated_email', {})
                    
                    if generated_email:
                        # Envoyer l'email
                        send_result = send_email_to_prospect(
                            prospect.to_dict(),
                            generated_email.get('content', '')
                        )
                        
                        if send_result.success:
                            # Mettre à jour le prospect
                            update_data = {
                                'status': 'contacté',
                                'email_sent': True,
                                'date_contacted': send_result.sent_at
                            }
                            
                            success = self.db_manager.update_prospect(prospect.id, update_data)
                            
                            if success:
                                sent_count += 1
                                
                except Exception as e:
                    logger.error(f"❌ Erreur lors de l'envoi d'email au prospect {prospect.id}: {e}")
                    continue
            
            logger.info(f"✅ Envoi terminé: {sent_count} emails envoyés")
            
            # Logger l'événement
            self.db_manager.log_system_event(
                level="INFO",
                message=f"Envoi emails terminé: {sent_count} envoyés",
                module="send_emails_task",
                extra_data={
                    "prospects_processed": len(prospects_to_email),
                    "emails_sent": sent_count
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche d'envoi d'emails: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur envoi emails: {str(e)}",
                module="send_emails_task"
            )

    def cleanup_task(self):
        """Tâche de nettoyage (tous les jours à minuit)"""
        try:
            logger.info("🧹 Démarrage de la tâche de nettoyage...")
            
            # Nettoyer les anciens logs
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Supprimer les anciens logs système
            # Note: Ceci est un exemple, à adapter selon votre système de logs
            
            logger.info("✅ Nettoyage terminé")
            
            # Logger l'événement
            self.db_manager.log_system_event(
                level="INFO",
                message="Nettoyage système terminé",
                module="cleanup_task"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche de nettoyage: {e}")
            
            self.db_manager.log_system_event(
                level="ERROR",
                message=f"Erreur nettoyage: {str(e)}",
                module="cleanup_task"
            )

    def health_check_task(self):
        """Tâche de vérification de santé (toutes les 5 minutes)"""
        try:
            # Vérifier que la base de données est accessible
            stats = self.db_manager.get_system_stats()
            
            if stats:
                logger.info("💚 Système en bonne santé")
            else:
                logger.warning("💛 Système en état dégradé")
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la tâche de santé: {e}")

    def get_task_definitions(self) -> List[Dict[str, Any]]:
        """
        Retourne la définition de toutes les tâches planifiées
        
        Returns:
            List[Dict[str, Any]]: Définition des tâches
        """
        return [
            {
                'id': 'search_prospects',
                'func': self.search_prospects_task,
                'trigger': IntervalTrigger(hours=config.search_frequency_hours),
                'name': 'Recherche de prospects',
                'description': 'Recherche de nouveaux prospects via Google Dorks'
            },
            {
                'id': 'qualify_prospects',
                'func': self.qualify_prospects_task,
                'trigger': IntervalTrigger(hours=1),
                'name': 'Qualification des prospects',
                'description': 'Qualification automatique des prospects trouvés'
            },
            {
                'id': 'enrich_prospects',
                'func': self.enrich_prospects_task,
                'trigger': IntervalTrigger(hours=3),
                'name': 'Enrichissement des prospects',
                'description': 'Enrichissement des données des prospects'
            },
            {
                'id': 'generate_emails',
                'func': self.generate_emails_task,
                'trigger': IntervalTrigger(minutes=30),
                'name': 'Génération d\'emails',
                'description': 'Génération d\'emails personnalisés'
            },
            {
                'id': 'send_emails',
                'func': self.send_emails_task,
                'trigger': IntervalTrigger(minutes=15),
                'name': 'Envoi d\'emails',
                'description': 'Envoi des emails générés'
            },
            {
                'id': 'cleanup',
                'func': self.cleanup_task,
                'trigger': CronTrigger(hour=0, minute=0),
                'name': 'Nettoyage',
                'description': 'Nettoyage des anciennes données'
            },
            {
                'id': 'health_check',
                'func': self.health_check_task,
                'trigger': IntervalTrigger(minutes=5),
                'name': 'Vérification de santé',
                'description': 'Vérification de l\'état du système'
            }
        ]

# Instance globale des tâches
scheduled_tasks = ScheduledTasks()

# Fonction pour l'import facile
def get_scheduled_tasks() -> List[Dict[str, Any]]:
    """
    Fonction wrapper pour obtenir les définitions des tâches
    
    Returns:
        List[Dict[str, Any]]: Définition des tâches
    """
    return scheduled_tasks.get_task_definitions()
