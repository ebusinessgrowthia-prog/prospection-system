"""
Worker continu pour EBUSINESS AI
Gestionnaire de tâches planifiées qui tourne 24h/24
"""

import logging
import signal
import sys
from datetime import datetime
from typing import List, Dict, Any
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

from src.config import get_config
from src.scheduler.tasks import get_scheduled_tasks
from src.core.database import db_manager
from src.core.utils import setup_logging

logger = logging.getLogger(__name__)
config = get_config()

class AutomationWorker:
    """Worker principal pour l'automatisation 24h/24"""

    def __init__(self):
        self.scheduler = None
        self.running = False
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Configure les gestionnaires de signaux pour l'arrêt propre"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour l'arrêt propre"""
        logger.info(f"🛑 Signal {signum} reçu, arrêt du worker...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Démarre le worker et le scheduler"""
        try:
            logger.info("🚀 Démarrage du worker d'automatisation...")
            
            # Initialiser la base de données
            from src.core.database import init_database
            init_database()
            
            # Créer le scheduler
            self.scheduler = BlockingScheduler(
                executors={'default': ThreadPoolExecutor(20)},
                timezone=config.timezone
            )
            
            # Ajouter les tâches planifiées
            self._add_scheduled_tasks()
            
            # Ajouter les listeners d'événements
            self._add_event_listeners()
            
            # Démarrer le scheduler
            self.running = True
            logger.info("✅ Worker démarré avec succès - Tâches planifiées actives")
            
            # Logger le démarrage
            db_manager.log_system_event(
                level="INFO",
                message="Worker d'automatisation démarré",
                module="worker",
                extra_data={
                    "tasks_count": len(get_scheduled_tasks()),
                    "timezone": config.timezone,
                    "started_at": datetime.now().isoformat()
                }
            )
            
            # Démarrer le scheduler (bloquant)
            self.scheduler.start()
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du worker: {e}")
            self.stop()
            sys.exit(1)

    def stop(self):
        """Arrête le worker et le scheduler"""
        try:
            if self.scheduler and self.running:
                logger.info("🛑 Arrêt du worker...")
                self.scheduler.shutdown(wait=True)
                self.running = False
                
                # Logger l'arrêt
                db_manager.log_system_event(
                    level="INFO",
                    message="Worker d'automatisation arrêté",
                    module="worker",
                    extra_data={
                        "stopped_at": datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt du worker: {e}")

    def _add_scheduled_tasks(self):
        """Ajoute toutes les tâches planifiées au scheduler"""
        try:
            task_definitions = get_scheduled_tasks()
            
            for task_def in task_definitions:
                self.scheduler.add_job(
                    func=task_def['func'],
                    trigger=task_def['trigger'],
                    id=task_def['id'],
                    name=task_def['name'],
                    replace_existing=True,
                    max_instances=1,
                    misfire_grace_time=300  # 5 minutes de grace
                )
                
                logger.info(f"✅ Tâche ajoutée: {task_def['name']} ({task_def['id']})")
            
            logger.info(f"✅ {len(task_definitions)} tâches planifiées ajoutées")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout des tâches: {e}")
            raise

    def _add_event_listeners(self):
        """Ajoute les listeners d'événements pour le suivi"""
        try:
            # Listener pour les erreurs de jobs
            def job_error_listener(event):
                if event.exception:
                    logger.error(f"❌ Erreur dans le job {event.job_id}: {event.exception}")
                    
                    db_manager.log_system_event(
                        level="ERROR",
                        message=f"Erreur job {event.job_id}: {str(event.exception)}",
                        module="worker",
                        extra_data={
                            "job_id": event.job_id,
                            "exception": str(event.exception),
                            "scheduled_run_time": event.scheduled_run_time.isoformat() if event.scheduled_run_time else None
                        }
                    )

            # Listener pour les jobs manqués
            def job_missed_listener(event):
                logger.warning(f"⚠️ Job manqué: {event.job_id}")
                
                db_manager.log_system_event(
                    level="WARNING",
                    message=f"Job manqué: {event.job_id}",
                    module="worker",
                    extra_data={
                        "job_id": event.job_id,
                        "scheduled_run_time": event.scheduled_run_time.isoformat() if event.scheduled_run_time else None
                    }
                )

            # Ajouter les listeners
            self.scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)
            self.scheduler.add_listener(job_missed_listener, EVENT_JOB_MISSED)
            
            logger.info("✅ Listeners d'événements ajoutés")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout des listeners: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut actuel du worker
        
        Returns:
            Dict[str, Any]: Statut du worker
        """
        try:
            status = {
                'running': self.running,
                'scheduler_running': self.scheduler.running if self.scheduler else False,
                'jobs_count': len(self.scheduler.get_jobs()) if self.scheduler else 0,
                'next_run_times': {},
                'last_health_check': None
            }
            
            # Récupérer les prochains temps d'exécution
            if self.scheduler:
                for job in self.scheduler.get_jobs():
                    next_run = job.next_run_time
                    if next_run:
                        status['next_run_times'][job.id] = next_run.isoformat()
            
            # Récupérer le dernier health check
            try:
                from datetime import timedelta
                cutoff = datetime.now() - timedelta(hours=1)
                
                # Chercher le dernier log de health check
                # Note: Ceci est une implémentation simplifiée
                status['last_health_check'] = datetime.now().isoformat()
                
            except Exception:
                pass
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération du statut: {e}")
            return {'running': False, 'error': str(e)}

    def run_job_now(self, job_id: str) -> bool:
        """
        Exécute immédiatement un job spécifique
        
        Args:
            job_id: ID du job à exécuter
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            if not self.scheduler:
                logger.error("❌ Scheduler non initialisé")
                return False
            
            job = self.scheduler.get_job(job_id)
            if not job:
                logger.error(f"❌ Job {job_id} non trouvé")
                return False
            
            # Exécuter le job
            self.scheduler.modify_job(job_id, next_run_time=datetime.now())
            
            logger.info(f"✅ Job {job_id} programmé pour exécution immédiate")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution immédiate du job {job_id}: {e}")
            return False

    def pause_job(self, job_id: str) -> bool:
        """
        Met en pause un job spécifique
        
        Args:
            job_id: ID du job à mettre en pause
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            if not self.scheduler:
                return False
            
            job = self.scheduler.get_job(job_id)
            if not job:
                return False
            
            self.scheduler.pause_job(job_id)
            logger.info(f"✅ Job {job_id} mis en pause")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la pause du job {job_id}: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """
        Reprend un job spécifique
        
        Args:
            job_id: ID du job à reprendre
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            if not self.scheduler:
                return False
            
            job = self.scheduler.get_job(job_id)
            if not job:
                return False
            
            self.scheduler.resume_job(job_id)
            logger.info(f"✅ Job {job_id} repris")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la reprise du job {job_id}: {e}")
            return False

# Instance globale du worker
automation_worker = AutomationWorker()

# Fonction pour démarrer le worker
def start_scheduler():
    """
    Fonction principale pour démarrer le worker
    """
    try:
        setup_logging()
        automation_worker.start()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
        automation_worker.stop()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        automation_worker.stop()
        sys.exit(1)

# Fonction pour obtenir le statut (pour le dashboard)
def get_worker_status() -> Dict[str, Any]:
    """
    Retourne le statut du worker
    
    Returns:
        Dict[str, Any]: Statut du worker
    """
    return automation_worker.get_status()

# Fonction pour exécuter un job manuellement
def run_job_manually(job_id: str) -> bool:
    """
    Exécute un job manuellement
    
    Args:
        job_id: ID du job à exécuter
        
    Returns:
        bool: True si succès, False sinon
    """
    return automation_worker.run_job_now(job_id)
