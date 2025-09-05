"""
Tests pour les modules de scraping
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.google_dorks_scraper import GoogleDorksScraper
from src.scrapers.email_finder import EmailFinder
from src.scrapers.website_analyzer import WebsiteAnalyzer

class TestGoogleDorksScraper:
    """Tests pour la classe GoogleDorksScraper"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.scraper = GoogleDorksScraper()
    
    def test_initialization(self):
        """Test d'initialisation du scraper"""
        assert self.scraper is not None
        assert hasattr(self.scraper, 'search_companies')
        assert hasattr(self.scraper, 'extract_company_data')
    
    @patch('src.scrapers.google_dorks_scraper.requests.Session.get')
    def test_search_companies_success(self, mock_get):
        """Test de recherche d'entreprises réussie"""
        # Simuler une réponse HTTP réussie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <div class="search-result__occluded-item">
                <a class="ember-view">Test Company</a>
                <p class="subline-level-1">E-commerce</p>
                <p class="subline-level-2">Technology</p>
                <span class="company-size">51-200 employees</span>
                <span class="location">Paris, France</span>
                <a class="link-without-visited-state">testcompany.com</a>
            </div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Appeler la méthode
        results = self.scraper.search_companies("e-commerce", "France")
        
        # Vérifier les résultats
        assert len(results) == 1
        assert results[0]['name'] == "Test Company"
        assert results[0]['industry'] == "Technology"
    
    @patch('src.scrapers.google_dorks_scraper.requests.Session.get')
    def test_search_companies_failure(self, mock_get):
        """Test de recherche d'entreprises avec échec"""
        # Simuler une réponse HTTP échouée
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Appeler la méthode
        results = self.scraper.search_companies("e-commerce", "France")
        
        # Vérifier les résultats
        assert len(results) == 0
    
    def test_extract_company_data(self):
        """Test d'extraction des données d'entreprise"""
        # Créer un élément HTML simulé
        from bs4 import BeautifulSoup
        html = '''
        <div class="search-result__occluded-item">
            <a class="ember-view" href="/company/test">Test Company</a>
            <p class="subline-level-1">E-commerce</p>
            <p class="subline-level-2">Technology</p>
            <span class="company-size">51-200 employees</span>
            <span class="location">Paris, France</span>
            <a class="link-without-visited-state">testcompany.com</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div', class_='search-result__occluded-item')
        
        # Appeler la méthode
        result = self.scraper._extract_company_data(card)
        
        # Vérifier les résultats
        assert result is not None
        assert result['name'] == "Test Company"
        assert result['industry'] == "Technology"
        assert result['employees'] == "51-200 employees"
        assert result['location'] == "Paris, France"
        assert result['domain'] == "testcompany.com"

class TestEmailFinder:
    """Tests pour la classe EmailFinder"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.finder = EmailFinder()
    
    def test_initialization(self):
        """Test d'initialisation du chercheur d'emails"""
        assert self.finder is not None
        assert hasattr(self.finder, 'find_emails')
        assert hasattr(self.finder, 'validate_email')
    
    @patch('src.scrapers.email_finder.requests.Session.get')
    def test_find_emails_success(self, mock_get):
        """Test de recherche d'emails réussie"""
        # Simuler une réponse HTTP réussie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <body>
                <a href="mailto:contact@testcompany.com">contact@testcompany.com</a>
                <div class="contact-info">contact@testcompany.com</div>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Appeler la méthode
        result = self.finder.find_emails("https://testcompany.com")
        
        # Vérifier les résultats
        assert result['status'] == 'success'
        assert len(result['emails']) > 0
        assert result['emails'][0]['email'] == 'contact@testcompany.com'
    
    def test_validate_email_format(self):
        """Test de validation du format d'email"""
        # Test avec un email valide
        assert self.finder._is_valid_email_format('contact@testcompany.com') == True
        
        # Test avec un email invalide
        assert self.finder._is_valid_email_format('invalid-email') == False
        
        # Test avec un email trop long
        long_email = 'a' * 255 + '@test.com'
        assert self.finder._is_valid_email_format(long_email) == False
    
    def test_clean_email(self):
        """Test de nettoyage d'email"""
        # Test avec un email obfusqué
        obfuscated_email = 'contact at testcompany com'
        cleaned_email = self.finder._clean_email(obfuscated_email)
        
        assert cleaned_email == 'contact@testcompany.com'
    
    def test_validate_email(self):
        """Test de validation d'email avec score de confiance"""
        # Test avec un email professionnel
        result = self.finder._validate_email('contact@testcompany.com', 'testcompany.com')
        
        assert result['valid'] == True
        assert result['confidence'] > 50
        
        # Test avec un email personnel
        result = self.finder._validate_email('contact@gmail.com', 'testcompany.com')
        
        assert result['valid'] == True
        assert 'Email personnel' in result['reasons']

class TestWebsiteAnalyzer:
    """Tests pour la classe WebsiteAnalyzer"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.analyzer = WebsiteAnalyzer()
    
    def test_initialization(self):
        """Test d'initialisation de l'analyseur de sites web"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'analyze_website')
        assert hasattr(self.analyzer, '_detect_technologies')
    
    @patch('src.scrapers.website_analyzer.requests.Session.get')
    def test_analyze_website_success(self, mock_get):
        """Test d'analyse de site web réussie"""
        # Simuler une réponse HTTP réussie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <head>
                <script src="https://cdn.shopify.com/assets.js"></script>
                <meta name="generator" content="Shopify" />
                <title>Test E-commerce</title>
                <meta name="description" content="Test e-commerce site" />
                <meta property="og:title" content="Test E-commerce" />
            </head>
            <body>
                <h1>Test E-commerce</h1>
                <div class="product">Product 1</div>
                <div class="product">Product 2</div>
                <div class="category">Category 1</div>
                <a href="mailto:contact@test.com">contact@test.com</a>
                <a href="https://facebook.com/test">Facebook</a>
            </body>
        </html>
        '''
        mock_response.headers = {
            'content-length': '5000',
            'x-cache': 'HIT'
        }
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response
        
        # Appeler la méthode
        result = self.analyzer.analyze_website("https://testecommerce.com")
        
        # Vérifier les résultats
        assert result['status'] == 'success'
        assert 'shopify' in result['technologies']
        assert result['products_count'] > 0
        assert result['categories_count'] > 0
        assert len(result['contact_info']['emails']) > 0
        assert 'facebook' in result['social_media']
    
    def test_detect_technologies(self):
        """Test de détection de technologies"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <head>
                <script src="https://cdn.shopify.com/assets.js"></script>
                <meta name="generator" content="Shopify" />
            </head>
            <body></body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Appeler la méthode
        technologies = self.analyzer._detect_technologies(soup, html)
        
        # Vérifier les résultats
        assert 'shopify' in technologies
    
    def test_extract_seo_data(self):
        """Test d'extraction des données SEO"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <head>
                <title>Test E-commerce</title>
                <meta name="description" content="Test e-commerce site" />
                <meta property="og:title" content="Test E-commerce" />
                <meta property="og:description" content="Test e-commerce description" />
                <meta name="twitter:card" content="summary" />
            </head>
            <body>
                <h1>Test E-commerce</h1>
                <h2>Category 1</h2>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Appeler la méthode
        seo_data = self.analyzer._extract_seo_data(soup)
        
        # Vérifier les résultats
        assert seo_data['title'] == 'Test E-commerce'
        assert seo_data['description'] == 'Test e-commerce site'
        assert seo_data['open_graph']['title'] == 'Test E-commerce'
        assert seo_data['twitter_card']['card'] == 'summary'
        assert seo_data['h1_tags'] == ['Test E-commerce']
        assert seo_data['h2_tags'] == ['Category 1']
    
    def test_count_products(self):
        """Test de comptage de produits"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <body>
                <div class="product">Product 1</div>
                <div class="product-item">Product 2</div>
                <div class="product-card">Product 3</div>
                <div class="item">Not a product</div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Appeler la méthode
        product_count = self.analyzer._count_products(soup)
        
        # Vérifier les résultats
        assert product_count == 3
    
    def test_extract_contact_info(self):
        """Test d'extraction des informations de contact"""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <body>
                <a href="mailto:contact@test.com">contact@test.com</a>
                <div class="contact-info">support@test.com</div>
                <a href="tel:+123456789">+123456789</a>
                <address>123 Test Street, Test City</address>
                <a href="/contact">Contact Page</a>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Appeler la méthode
        contact_info = self.analyzer._extract_contact_info(soup, "https://test.com")
        
        # Vérifier les résultats
        assert 'contact@test.com' in contact_info['emails']
        assert 'support@test.com' in contact_info['emails']
        assert '+123456789' in contact_info['phones']
        assert len(contact_info['addresses']) > 0
        assert len(contact_info['contact_links']) > 0
