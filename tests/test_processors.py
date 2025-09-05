"""
Tests pour les modules de traitement
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.prospect_qualifier import ProspectQualifier
from src.processors.mistral_personalizer import MistralPersonalizer
from src.processors.data_enricher import DataEnricher

class TestProspectQualifier:
    """Tests pour la classe ProspectQualifier"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.qualifier = ProspectQualifier()
    
    def test_initialization(self):
        """Test d'initialisation du qualificateur de prospects"""
        assert self.qualifier is not None
        assert hasattr(self.qualifier, 'qualify_prospect')
        assert hasattr(self.qualifier, 'calculate_qualification_score')
    
    def test_calculate_qualification_score(self):
        """Test de calcul du score de qualification"""
        # Test avec un prospect de haute qualité
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'email': 'contact@testcompany.com',
            'website': 'https://testcompany.com',
            'sector': 'Technology',
            'country': 'France',
            'problem_detected': 'Need for e-commerce optimization',
            'specificity': 'B2B SaaS company'
        }
        
        score = self.qualifier.calculate_qualification_score(prospect_data)
        
        # Vérifier que le score est élevé
        assert score > 7.0
    
    def test_calculate_qualification_score_low(self):
        """Test de calcul du score de qualification avec un prospect de faible qualité"""
        # Test avec un prospect de faible qualité
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'email': '',  # Pas d'email
            'website': '',  # Pas de site web
            'sector': 'Other',  # Secteur non ciblé
            'country': 'Other',  # Pays non ciblé
            'problem_detected': '',  # Pas de problème détecté
            'specificity': ''  # Pas de spécificité
        }
        
        score = self.qualifier.calculate_qualification_score(prospect_data)
        
        # Vérifier que le score est faible
        assert score < 3.0
    
    def test_qualify_prospect(self):
        """Test de qualification d'un prospect"""
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'email': 'contact@testcompany.com',
            'website': 'https://testcompany.com',
            'sector': 'Technology',
            'country': 'France'
        }
        
        result = self.qualifier.qualify_prospect(prospect_data)
        
        # Vérifier les résultats
        assert result['prospect_id'] == prospect_data.get('id', 0)
        assert isinstance(result['qualified'], bool)
        assert isinstance(result['score'], float)
        assert isinstance(result['reasons'], list)
        assert isinstance(result['detected_problems'], list)
        assert isinstance(result['specificities'], list)
    
    def test_detect_problems(self):
        """Test de détection de problèmes"""
        website_content = '''
        <html>
            <body>
                <p>Our e-commerce site is slow and has high cart abandonment.</p>
                <p>We need help with digital marketing.</p>
            </body>
        </html>
        '''
        
        problems = self.qualifier._detect_problems(website_content)
        
        # Vérifier que des problèmes ont été détectés
        assert len(problems) > 0
        assert any('slow' in problem.lower() for problem in problems)
        assert any('cart abandonment' in problem.lower() for problem in problems)
    
    def test_detect_specificities(self):
        """Test de détection de spécificités"""
        website_content = '''
        <html>
            <body>
                <p>We are a B2B SaaS company specializing in e-commerce solutions.</p>
                <p>Founded in 2010, we have 50+ employees.</p>
            </body>
        </html>
        '''
        
        specificities = self.qualifier._detect_specificities(website_content)
        
        # Vérifier que des spécificités ont été détectées
        assert len(specificities) > 0
        assert any('b2b' in specificity.lower() for specificity in specificities)
        assert any('saas' in specificity.lower() for specificity in specificities)

class TestMistralPersonalizer:
    """Tests pour la classe MistralPersonalizer"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.personalizer = MistralPersonalizer()
    
    def test_initialization(self):
        """Test d'initialisation du personnaliseur Mistral"""
        assert self.personalizer is not None
        assert hasattr(self.personalizer, 'generate_email')
        assert hasattr(self.personalizer, '_create_prompt')
    
    @patch('src.processors.mistral_personalizer.openai.ChatCompletion.create')
    def test_generate_email_success(self, mock_create):
        """Test de génération d'email réussie"""
        # Simuler une réponse de l'API Mistral
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Subject: Test Email\n\nDear Test Prospect,\n\nThis is a personalized email.\n\nBest regards,\nTest Sender'))]
        mock_create.return_value = mock_response
        
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'sector': 'Technology',
            'problem_detected': 'Need for e-commerce optimization',
            'specificity': 'B2B SaaS company'
        }
        
        result = self.personalizer.generate_email(prospect_data)
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'subject' in result
        assert 'content' in result
        assert result['subject'] == 'Test Email'
        assert 'Dear Test Prospect' in result['content']
    
    @patch('src.processors.mistral_personalizer.openai.ChatCompletion.create')
    def test_generate_email_failure(self, mock_create):
        """Test de génération d'email avec échec"""
        # Simuler une erreur de l'API Mistral
        mock_create.side_effect = Exception("API Error")
        
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'sector': 'Technology',
            'problem_detected': 'Need for e-commerce optimization',
            'specificity': 'B2B SaaS company'
        }
        
        result = self.personalizer.generate_email(prospect_data)
        
        # Vérifier les résultats
        assert result['success'] == False
        assert 'error' in result
        assert result['error'] == "API Error"
    
    def test_create_prompt(self):
        """Test de création de prompt"""
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'sector': 'Technology',
            'problem_detected': 'Need for e-commerce optimization',
            'specificity': 'B2B SaaS company'
        }
        
        prompt = self.personalizer._create_prompt(prospect_data)
        
        # Vérifier que le prompt contient les informations du prospect
        assert 'Test Prospect' in prompt
        assert 'Test Company' in prompt
        assert 'Technology' in prompt
        assert 'Need for e-commerce optimization' in prompt
        assert 'B2B SaaS company' in prompt
    
    def test_extract_email_parts(self):
        """Test d'extraction des parties d'un email"""
        email_content = '''
        Subject: Test Subject
        
        Dear Test Prospect,
        
        This is the email content.
        
        Best regards,
        Test Sender
        '''
        
        parts = self.personalizer._extract_email_parts(email_content)
        
        # Vérifier les parties extraites
        assert 'subject' in parts
        assert 'content' in parts
        assert parts['subject'] == 'Test Subject'
        assert 'Dear Test Prospect' in parts['content']

class TestDataEnricher:
    """Tests pour la classe DataEnricher"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.enricher = DataEnricher()
    
    def test_initialization(self):
        """Test d'initialisation de l'enrichisseur de données"""
        assert self.enricher is not None
        assert hasattr(self.enricher, 'enrich_prospect')
        assert hasattr(self.enricher, '_get_company_info')
    
    @patch('src.processors.data_enricher.requests.get')
    def test_enrich_prospect_success(self, mock_get):
        """Test d'enrichissement de prospect réussie"""
        # Simuler une réponse HTTP réussie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Test Company',
            'description': 'Test company description',
            'category': 'Technology',
            'employees': 100,
            'founded': 2010,
            'headquarters': 'Paris, France'
        }
        mock_get.return_value = mock_response
        
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'website': 'https://testcompany.com'
        }
        
        result = self.enricher.enrich_prospect(prospect_data)
        
        # Vérifier les résultats
        assert result['success'] == True
        assert 'enriched_data' in result
        assert result['enriched_data']['description'] == 'Test company description'
        assert result['enriched_data']['category'] == 'Technology'
        assert result['enriched_data']['employees'] == 100
        assert result['enriched_data']['founded'] == 2010
        assert result['enriched_data']['headquarters'] == 'Paris, France'
    
    @patch('src.processors.data_enricher.requests.get')
    def test_enrich_prospect_failure(self, mock_get):
        """Test d'enrichissement de prospect avec échec"""
        # Simuler une réponse HTTP échouée
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        prospect_data = {
            'name': 'Test Prospect',
            'company': 'Test Company',
            'website': 'https://testcompany.com'
        }
        
        result = self.enricher.enrich_prospect(prospect_data)
        
        # Vérifier les résultats
        assert result['success'] == False
        assert 'error' in result
    
    def test_extract_domain(self):
        """Test d'extraction de domaine"""
        # Test avec une URL valide
        domain = self.enricher._extract_domain('https://www.testcompany.com/page')
        assert domain == 'testcompany.com'
        
        # Test avec une URL sans sous-domaine
        domain = self.enricher._extract_domain('https://testcompany.com')
        assert domain == 'testcompany.com'
        
        # Test avec une URL invalide
        domain = self.enricher._extract_domain('invalid-url')
        assert domain is None
    
    def test_clean_company_name(self):
        """Test de nettoyage de nom d'entreprise"""
        # Test avec un nom contenant des termes juridiques
        clean_name = self.enricher._clean_company_name('Test Company Inc.')
        assert clean_name == 'Test Company'
        
        # Test avec un nom contenant des ponctuations
        clean_name = self.enricher._clean_company_name('Test-Company, LLC')
        assert clean_name == 'Test Company'
    
    def test_estimate_company_size(self):
        """Test d'estimation de la taille d'entreprise"""
        # Test avec une petite entreprise
        size = self.enricher._estimate_company_size(10)
        assert size == 'Petite'
        
        # Test avec une moyenne entreprise
        size = self.enricher._estimate_company_size(150)
        assert size == 'Moyenne'
        
        # Test avec une grande entreprise
        size = self.enricher._estimate_company_size(1000)
        assert size == 'Grande'
