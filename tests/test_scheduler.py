"""
Tests pour les modules de planification
"""

import pytest
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler.tasks import ScheduledTasks
from src.scheduler.worker import Worker

class TestScheduledTasks:
    """Tests pour la classe ScheduledTasks"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.tasks = ScheduledTasks()
    
    def test_initialization(self):
        """Test d'initialisation des tâches planifiées"""
        assert self.tasks is not None
        assert hasattr(self.tasks, 'search_prospects_task')
        assert hasattr(self.tasks, 'qualify_prospects_task')
        assert hasattr(self.tasks, 'send_emails_task')
    
    @patch('src.scheduler.tasks.GoogleDorksScraper')
    def test_search_prospects_task_success(self, mock_scraper):
        """Test de la tâche de recherche de prospects réussie"""
        # Simuler un scraper qui retourne des prospects
        mock_scraper_instance = Mock()
        mock_scraper_instance.search_companies.return_value = [
            {'name': 'Company 1', 'website': 'https://company1.com'},
            {'name': 'Company 2', 'website': 'https://company2.com'}
        ]
        mock_scraper.return_value = mock_scraper_instance
        
        # Appeler la tâche
        result = self.tasks.search_prospects_task()
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'prospects_found' in result
        assert result['prospects_found'] == 2
    
    @patch('src.scheduler.tasks.GoogleDorksScraper')
    def test_search_prospects_task_failure(self, mock_scraper):
        """Test de la tâche de recherche de prospects avec échec"""
        # Simuler une erreur
        mock_scraper.side_effect = Exception("Scraper Error")
        
        # Appeler la tâche
        result = self.tasks.search_prospects_task()
        
        # Vérifier les résultats
        assert result['success'] == False
        assert 'error' in result
        assert "Scraper Error" in result['error']
    
    @patch('src.scheduler.tasks.ProspectQualifier')
    def test_qualify_prospects_task_success(self, mock_qualifier):
        """Test de la tâche de qualification de prospects réussie"""
        # Simuler un qualificateur qui qualifie des prospects
        mock_qualifier_instance = Mock()
        mock_qualifier_instance.qualify_prospects.return_value = [
            {'prospect_id': 1, 'qualified': True, 'score': 8.5},
            {'prospect_id': 2, 'qualified': False, 'score': 4.2}
        ]
        mock_qualifier.return_value = mock_qualifier_instance
        
        # Appeler la tâche
        result = self.tasks.qualify_prospects_task()
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'qualified_prospects' in result
        assert result['qualified_prospects'] == 1
    
    @patch('src.scheduler.tasks.EmailSender')
    def test_send_emails_task_success(self, mock_sender):
        """Test de la tâche d'envoi d'emails réussie"""
        # Simuler un envoyeur d'emails qui envoie des emails
        mock_sender_instance = Mock()
        mock_sender_instance.send_emails.return_value = [
            {'prospect_id': 1, 'email_sent': True, 'message_id': 'msg123'},
            {'prospect_id': 2, 'email_sent': False, 'error': 'Invalid email'}
        ]
        mock_sender.return_value = mock_sender_instance
        
        # Appeler la tâche
        result = self.tasks.send_emails_task()
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'emails_sent' in result
        assert result['emails_sent'] == 1
    
    def test_get_prospects_to_contact(self):
        """Test d'obtention des prospects à contacter"""
        # Simuler un appel à la base de données
        with patch.object(self.tasks, '_get_prospects_to_contact_from_db') as mock_get:
            mock_prospects = [
                {'id': 1, 'name': 'Prospect 1', 'email': 'prospect1@example.com'},
                {'id': 2, 'name': 'Prospect 2', 'email': 'prospect2@example.com'}
            ]
            mock_get.return_value = mock_prospects
            
            prospects = self.tasks.get_prospects_to_contact()
            
            # Vérifier les prospects
            assert len(prospects) == 2
            assert prospects[0]['id'] == 1
            assert prospects[1]['id'] == 2
    
    def test_is_business_hours(self):
        """Test de vérification des heures de bureau"""
        # Test pendant les heures de bureau (mardi à vendredi, 9h-17h)
        tuesday_10am = datetime(2023, 1, 3, 10, 0, 0)  # Mardi 10h
        assert self.tasks._is_business_hours(tuesday_10am) == True
        
        # Test en dehors des heures de bureau (samedi)
        saturday_10am = datetime(2023, 1, 7, 10, 0, 0)  # Samedi 10h
        assert self.tasks._is_business_hours(saturday_10am) == False
        
        # Test en dehors des heures de bureau (trop tôt)
        tuesday_8am = datetime(2023, 1, 3, 8, 0, 0)  # Mardi 8h
        assert self.tasks._is_business_hours(tuesday_8am) == False
    
    def test_get_next_run_time(self):
        """Test d'obtention de la prochaine heure d'exécution"""
        # Test avec une heure actuelle pendant les heures de bureau
        tuesday_10am = datetime(2023, 1, 3, 10, 0, 0)  # Mardi 10h
        next_run = self.tasks._get_next_run_time(tuesday_10am)
        
        # Vérifier que la prochaine heure d'exécution est dans le futur
        assert next_run > tuesday_10am
        
        # Test avec une heure actuelle en dehors des heures de bureau
        saturday_10am = datetime(2023, 1, 7, 10, 0, 0)  # Samedi 10h
        next_run = self.tasks._get_next_run_time(saturday_10am)
        
        # Vérifier que la prochaine heure d'exécution est le prochain jour ouvrable à 9h
        assert next_run.weekday() < 5  # Lundi à vendredi
        assert next_run.hour == 9
        assert next_run.minute == 0

class TestWorker:
    """Tests pour la classe Worker"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.worker = Worker()
    
    def test_initialization(self):
        """Test d'initialisation du worker"""
        assert self.worker is not None
        assert hasattr(self.worker, 'start')
        assert hasattr(self.worker, 'stop')
        assert hasattr(self.worker, 'is_running')
    
    @patch('src.scheduler.worker.ScheduledTasks')
    def test_run_tasks_success(self, mock_tasks):
        """Test d'exécution des tâches réussie"""
        # Simuler des tâches qui s'exécutent avec succès
        mock_tasks_instance = Mock()
        mock_tasks_instance.search_prospects_task.return_value = {'success': True, 'prospects_found': 2}
        mock_tasks_instance.qualify_prospects_task.return_value = {'success': True, 'qualified_prospects': 1}
        mock_tasks_instance.send_emails_task.return_value = {'success': True, 'emails_sent': 1}
        mock_tasks.return_value = mock_tasks_instance
        
        # Appeler la méthode d'exécution des tâches
        result = self.worker._run_tasks()
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'tasks_executed' in result
        assert result['tasks_executed'] == 3
    
    @patch('src.scheduler.worker.ScheduledTasks')
    def test_run_tasks_partial_failure(self, mock_tasks):
        """Test d'exécution des tâches avec échec partiel"""
        # Simuler des tâches avec des succès et des échecs
        mock_tasks_instance = Mock()
        mock_tasks_instance.search_prospects_task.return_value = {'success': True, 'prospects_found': 2}
        mock_tasks_instance.qualify_prospects_task.return_value = {'success': False, 'error': 'Qualification error'}
        mock_tasks_instance.send_emails_task.return_value = {'success': True, 'emails_sent': 1}
        mock_tasks.return_value = mock_tasks_instance
        
        # Appeler la méthode d'exécution des tâches
        result = self.worker._run_tasks()
        
        # Vérifier les résultats
        assert result['success'] == True  # Le worker est considéré comme succès même si une tâche échoue
        assert 'tasks_executed' in result
        assert result['tasks_executed'] == 3
        assert 'failed_tasks' in result
        assert result['failed_tasks'] == 1
    
    def test_start_worker(self):
        """Test de démarrage du worker"""
        # Simuler l'exécution des tâches
        with patch.object(self.worker, '_run_tasks') as mock_run:
            mock_run.return_value = {'success': True, 'tasks_executed': 3}
            
            # Démarrer le worker
            self.worker.start()
            
            # Vérifier que le worker est en cours d'exécution
            assert self.worker.is_running() == True
    
    def test_stop_worker(self):
        """Test d'arrêt du worker"""
        # Démarrer le worker
        self.worker.start()
        
        # Vérifier que le worker est en cours d'exécution
        assert self.worker.is_running() == True
        
        # Arrêter le worker
        self.worker.stop()
        
        # Vérifier que le worker n'est plus en cours d'exécution
        assert self.worker.is_running() == False
    
    def test_worker_loop(self):
        """Test de la boucle du worker"""
        # Simuler l'exécution des tâches
        with patch.object(self.worker, '_run_tasks') as mock_run:
            mock_run.return_value = {'success': True, 'tasks_executed': 3}
            
            # Simuler la boucle du worker
            with patch.object(self.worker, '_should_continue') as mock_continue:
                # Simuler 2 itérations avant d'arrêter
                mock_continue.side_effect = [True, True, False]
                
                # Exécuter la boucle du worker
                self.worker._worker_loop()
                
                # Vérifier que les tâches ont été exécutées 2 fois
                assert mock_run.call_count == 2
    
    def test_get_worker_stats(self):
        """Test d'obtention des statistiques du worker"""
        # Simuler des exécutions de tâches
        with patch.object(self.worker, '_run_tasks') as mock_run:
            mock_run.return_value = {'success': True, 'tasks_executed': 3}
            
            # Exécuter quelques tâches
            self.worker._run_tasks()
            self.worker._run_tasks()
            
            # Obtenir les statistiques
            stats = self.worker.get_worker_stats()
            
            # Vérifier les statistiques
            assert 'total_executions' in stats
            assert 'successful_executions' in stats
            assert 'failed_executions' in stats
            assert 'last_execution_time' in stats
            assert stats['total_executions'] == 2
            assert stats['successful_executions'] == 2
            assert stats['failed_executions'] == 0
    
    def test_handle_task_exception(self):
        """Test de gestion des exceptions de tâches"""
        # Simuler une exception lors de l'exécution des tâches
        with patch.object(self.worker, '_run_tasks') as mock_run:
            mock_run.side_effect = Exception("Task Error")
            
            # Exécuter la gestion d'exception
            result = self.worker._handle_task_exception(Exception("Task Error"))
            
            # Vérifier les résultats
            assert result['success'] == False
            assert 'error' in result
            assert "Task Error" in result['error']
