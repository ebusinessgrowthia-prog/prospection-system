"""
Tests pour les modules d'email
"""

import pytest
import os
import sys
import smtplib
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.email.sender import EmailSender
from src.email.tracker import EmailTracker

class TestEmailSender:
    """Tests pour la classe EmailSender"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.sender = EmailSender()
    
    def test_initialization(self):
        """Test d'initialisation de l'envoyeur d'email"""
        assert self.sender is not None
        assert hasattr(self.sender, 'send_email')
        assert hasattr(self.sender, '_create_email_message')
    
    @patch('src.email.sender.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test d'envoi d'email réussie"""
        # Simuler une connexion SMTP réussie
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Données de test
        email_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        
        # Appeler la méthode
        result = self.sender.send_email(email_data)
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'message_id' in result
        
        # Vérifier que les méthodes SMTP ont été appelées
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('src.email.sender.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test d'envoi d'email avec échec"""
        # Simuler une erreur SMTP
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        # Données de test
        email_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        
        # Appeler la méthode
        result = self.sender.send_email(email_data)
        
        # Vérifier les résultats
        assert result['success'] == False
        assert 'error' in result
        assert "SMTP Error" in result['error']
    
    def test_create_email_message(self):
        """Test de création de message email"""
        # Données de test
        email_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'content': 'Test Content',
            'from_name': 'Test Sender',
            'from_email': 'sender@example.com'
        }
        
        # Appeler la méthode
        message = self.sender._create_email_message(email_data)
        
        # Vérifier le message
        assert message['To'] == 'test@example.com'
        assert message['Subject'] == 'Test Subject'
        assert message['From'] == 'Test Sender <sender@example.com>'
        assert 'Test Content' in message.get_payload()
    
    def test_is_business_hours(self):
        """Test de vérification des heures de bureau"""
        # Test pendant les heures de bureau (mardi à vendredi, 9h-17h)
        import datetime
        tuesday_10am = datetime.datetime(2023, 1, 3, 10, 0, 0)  # Mardi 10h
        assert self.sender._is_business_hours(tuesday_10am) == True
        
        # Test en dehors des heures de bureau (samedi)
        saturday_10am = datetime.datetime(2023, 1, 7, 10, 0, 0)  # Samedi 10h
        assert self.sender._is_business_hours(saturday_10am) == False
        
        # Test en dehors des heures de bureau (trop tôt)
        tuesday_8am = datetime.datetime(2023, 1, 3, 8, 0, 0)  # Mardi 8h
        assert self.sender._is_business_hours(tuesday_8am) == False
    
    def test_schedule_email(self):
        """Test de planification d'email"""
        # Données de test
        email_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        
        # Appeler la méthode
        result = self.sender.schedule_email(email_data)
        
        # Vérifier les résultats
        assert 'scheduled' in result
        assert 'scheduled_time' in result
        
        # Vérifier que l'email est planifié pour une heure future
        import datetime
        scheduled_time = result['scheduled_time']
        assert scheduled_time > datetime.datetime.now()
    
    def test_validate_email_data(self):
        """Test de validation des données d'email"""
        # Données valides
        valid_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        
        assert self.sender._validate_email_data(valid_data) == True
        
        # Données invalides (destinataire manquant)
        invalid_data = {
            'subject': 'Test Subject',
            'content': 'Test Content'
        }
        
        assert self.sender._validate_email_data(invalid_data) == False
        
        # Données invalides (sujet manquant)
        invalid_data = {
            'to': 'test@example.com',
            'content': 'Test Content'
        }
        
        assert self.sender._validate_email_data(invalid_data) == False
        
        # Données invalides (contenu manquant)
        invalid_data = {
            'to': 'test@example.com',
            'subject': 'Test Subject'
        }
        
        assert self.sender._validate_email_data(invalid_data) == False

class TestEmailTracker:
    """Tests pour la classe EmailTracker"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.tracker = EmailTracker()
    
    def test_initialization(self):
        """Test d'initialisation du tracker d'email"""
        assert self.tracker is not None
        assert hasattr(self.tracker, 'create_tracking_pixel')
        assert hasattr(self.tracker, 'generate_tracking_id')
    
    def test_generate_tracking_id(self):
        """Test de génération d'ID de suivi"""
        tracking_id = self.tracker.generate_tracking_id()
        
        # Vérifier que l'ID est une chaîne non vide
        assert isinstance(tracking_id, str)
        assert len(tracking_id) > 0
        
        # Vérifier que deux IDs sont différents
        tracking_id2 = self.tracker.generate_tracking_id()
        assert tracking_id != tracking_id2
    
    def test_create_tracking_pixel(self):
        """Test de création de pixel de suivi"""
        tracking_id = "test-tracking-id"
        
        pixel_html = self.tracker.create_tracking_pixel(tracking_id)
        
        # Vérifier que le pixel HTML contient l'ID de suivi
        assert tracking_id in pixel_html
        assert '<img' in pixel_html
        assert 'width="1"' in pixel_html
        assert 'height="1"' in pixel_html
    
    def test_create_tracking_link(self):
        """Test de création de lien de suivi"""
        tracking_id = "test-tracking-id"
        url = "https://example.com"
        
        tracking_link = self.tracker.create_tracking_link(url, tracking_id)
        
        # Vérifier que le lien contient l'URL et l'ID de suivi
        assert url in tracking_link
        assert tracking_id in tracking_link
        assert 'track' in tracking_link
    
    def test_extract_tracking_id(self):
        """Test d'extraction d'ID de suivi"""
        # Test avec une URL de suivi valide
        tracking_url = "https://example.com/track?tracking_id=test-tracking-id&other=value"
        tracking_id = self.tracker._extract_tracking_id(tracking_url)
        
        assert tracking_id == "test-tracking-id"
        
        # Test avec une URL sans ID de suivi
        normal_url = "https://example.com/page"
        tracking_id = self.tracker._extract_tracking_id(normal_url)
        
        assert tracking_id is None
    
    def test_track_open(self):
        """Test de suivi d'ouverture"""
        tracking_id = "test-tracking-id"
        
        # Simuler un appel à la base de données
        with patch.object(self.tracker, '_update_email_open') as mock_update:
            mock_update.return_value = True
            
            result = self.tracker.track_open(tracking_id)
            
            # Vérifier les résultats
            assert result['success'] == True
            mock_update.assert_called_once_with(tracking_id)
    
    def test_track_click(self):
        """Test de suivi de clic"""
        tracking_id = "test-tracking-id"
        
        # Simuler un appel à la base de données
        with patch.object(self.tracker, '_update_email_click') as mock_update:
            mock_update.return_value = True
            
            result = self.tracker.track_click(tracking_id)
            
            # Vérifier les résultats
            assert result['success'] == True
            mock_update.assert_called_once_with(tracking_id)
    
    def test_get_tracking_stats(self):
        """Test d'obtention des statistiques de suivi"""
        # Simuler un appel à la base de données
        mock_stats = {
            'total_emails': 100,
            'opened_emails': 50,
            'clicked_emails': 25
        }
        
        with patch.object(self.tracker, '_get_tracking_stats_from_db') as mock_get:
            mock_get.return_value = mock_stats
            
            stats = self.tracker.get_tracking_stats()
            
            # Vérifier les statistiques
            assert stats['total_emails'] == 100
            assert stats['opened_emails'] == 50
            assert stats['clicked_emails'] == 25
            assert stats['open_rate'] == 50.0
            assert stats['click_rate'] == 50.0
