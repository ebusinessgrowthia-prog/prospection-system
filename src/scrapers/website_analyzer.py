"""
Website Analyzer pour EBUSINESS AI
Analyse approfondie des sites web pour détecter des e-commerces et extraire des informations
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import json

from src.config import get_config
from src.core.utils import is_valid_website, clean_text, extract_domain_from_url

logger = logging.getLogger(__name__)
config = get_config()

class WebsiteAnalyzer:
    """Analyseur de sites web pour détecter des e-commerces"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Analyse un site web pour détecter s'il s'agit d'un e-commerce et extraire des informations
        
        Args:
            url: URL du site web à analyser
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        try:
            logger.info(f"🔍 Analyse du site web: {url}")
            
            # Normaliser l'URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Récupérer le contenu de la page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parser le contenu
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les informations de base
            analysis_result = {
                'url': url,
                'domain': extract_domain_from_url(url),
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'is_ecommerce': self._is_ecommerce(soup, url),
                'ecommerce_platform': self._detect_ecommerce_platform(soup),
                'contact_info': self._extract_contact_info(soup, url),
                'social_links': self._extract_social_links(soup, url),
                'products_count': self._estimate_products_count(soup),
                'has_blog': self._has_blog(soup),
                'has_testimonials': self._has_testimonials(soup),
                'has_prices': self._has_prices(soup),
                'has_cart': self._has_cart(soup),
                'has_checkout': self._has_checkout(soup),
                'business_info': self._extract_business_info(soup),
                'technologies': self._detect_technologies(soup),
                'content_quality': self._analyze_content_quality(soup),
                'mobile_friendly': self._check_mobile_friendly(soup),
                'load_time': response.elapsed.total_seconds(),
                'status_code': response.status_code,
                'analyzed_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Analyse terminée pour {url}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse du site {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrait le titre de la page"""
        title_tag = soup.find('title')
        return clean_text(title_tag.text) if title_tag else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrait la description de la page"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return clean_text(meta_desc['content'])
        
        # Chercher aussi dans og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return clean_text(og_desc['content'])
        
        return ""

    def _is_ecommerce(self, soup: BeautifulSoup, url: str) -> bool:
        """Détecte si le site est un e-commerce"""
        ecommerce_indicators = [
            # Mots-clés dans le contenu
            r'\b(panier|cart|commande|order|achat|buy|prix|price|produit|product|shop|boutique|store|checkout|paiement|payment)\b',
            
            # Éléments HTML typiques
            r'class=["\']?(cart|basket|shop|product|price|checkout|add-to-cart|buy-now|purchase)["\']?',
            r'id=["\']?(cart|basket|shop|product|price|checkout)["\']?',
            
            # URLs typiques
            r'/(cart|checkout|shop|products?|boutique|commande|paiement)',
            
            # Boutons d'action
            r'<button[^>]*(ajouter|acheter|commander|payer|buy|add|cart|order)[^>]*>',
            r'<a[^>]*(acheter|commander|payer|buy|order)[^>]*>'
        ]
        
        content = str(soup).lower()
        url_lower = url.lower()
        
        for pattern in ecommerce_indicators:
            if re.search(pattern, content) or re.search(pattern, url_lower):
                return True
        
        return False

    def _detect_ecommerce_platform(self, soup: BeautifulSoup) -> Optional[str]:
        """Détecte la plateforme e-commerce utilisée"""
        platform_indicators = {
            'Shopify': [
                r'shopify\.com',
                r'cdn\.shopify\.com',
                r'myshopify\.com',
                r'shopify-pay',
                r'shopify-checkout'
            ],
            'WooCommerce': [
                r'woocommerce',
                r'wp-content/plugins/woocommerce',
                r'add_to_cart',
                r'woocommerce-products'
            ],
            'PrestaShop': [
                r'prestashop',
                r'prestashop\.com',
                r'prestashop-theme'
            ],
            'Magento': [
                r'magento',
                r'magento\.com',
                r'magento-theme'
            ],
            'BigCommerce': [
                r'bigcommerce',
                r'bigcommerce\.com'
            ],
            'Wix': [
                r'wix\.com',
                r'wixstatic',
                r'wixstores'
            ],
            'Squarespace': [
                r'squarespace\.com',
                r'squarespace-cdn'
            ]
        }
        
        content = str(soup).lower()
        
        for platform, patterns in platform_indicators.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    return platform
        
        return None

    def _extract_contact_info(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extrait les informations de contact"""
        contact_info = {
            'email': None,
            'phone': None,
            'address': None,
            'contact_page': None,
            'social_media': {}
        }
        
        # Chercher les emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, str(soup))
        if emails:
            contact_info['email'] = emails[0]  # Prendre le premier email trouvé
        
        # Chercher les numéros de téléphone
        phone_pattern = r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. )]*(\d{4})'
        phones = re.findall(phone_pattern, str(soup))
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # Chercher la page de contact
        contact_link = soup.find('a', href=re.compile(r'contact', re.I))
        if contact_link and contact_link.get('href'):
            contact_info['contact_page'] = urljoin(base_url, contact_link['href'])
        
        return contact_info

    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extrait les liens vers les réseaux sociaux"""
        social_links = {}
        
        social_platforms = {
            'facebook': r'facebook\.com',
            'twitter': r'twitter\.com|x\.com',
            'linkedin': r'linkedin\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com',
            'pinterest': r'pinterest\.com',
            'tiktok': r'tiktok\.com'
        }
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            for platform, pattern in social_platforms.items():
                if re.search(pattern, href):
                    social_links[platform] = href
        
        return social_links

    def _estimate_products_count(self, soup: BeautifulSoup) -> int:
        """Estime le nombre de produits sur le site"""
        # Chercher des indicateurs de nombre de produits
        count_patterns = [
            r'(\d+)\s*(?:produits?|products?|articles?|items?)',
            r'affich(?:er|ing)\s*(\d+)\s*(?:produits?|products?|articles?|items?)',
            r'(\d+)\s*(?:résultats?|results?)'
        ]
        
        content = str(soup)
        max_count = 0
        
        for pattern in count_patterns:
            matches = re.findall(pattern, content, re.I)
            for match in matches:
                try:
                    count = int(match)
                    max_count = max(max_count, count)
                except ValueError:
                    continue
        
        return max_count

    def _has_blog(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site a un blog"""
        blog_indicators = [
            r'blog',
            r'actualités?',
            r'news',
            r'articles?',
            r'journal'
        ]
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            for indicator in blog_indicators:
                if indicator in href or indicator in text:
                    return True
        
        return False

    def _has_testimonials(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site a des témoignages"""
        testimonial_indicators = [
            r'témoignage',
            r'avis',
            r'review',
            r'testimonial',
            r'client',
            r'feedback',
            r'rating'
        ]
        
        content = str(soup).lower()
        
        for indicator in testimonial_indicators:
            if indicator in content:
                return True
        
        return False

    def _has_prices(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site affiche des prix"""
        price_patterns = [
            r'\$\d+',
            r'€\d+',
            r'£\d+',
            r'\d+\s*€',
            r'\d+\s*\$',
            r'\d+\s*£',
            r'prix\s*:\s*\d+',
            r'price\s*:\s*\d+'
        ]
        
        content = str(soup)
        
        for pattern in price_patterns:
            if re.search(pattern, content):
                return True
        
        return False

    def _has_cart(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site a un panier"""
        cart_indicators = [
            r'cart',
            r'panier',
            r'basket',
            r'add-to-cart',
            r'ajouter-au-panier'
        ]
        
        content = str(soup).lower()
        
        for indicator in cart_indicators:
            if indicator in content:
                return True
        
        return False

    def _has_checkout(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site a une page de checkout"""
        checkout_indicators = [
            r'checkout',
            r'commande',
            r'paiement',
            r'payment',
            r'finaliser'
        ]
        
        content = str(soup).lower()
        
        for indicator in checkout_indicators:
            if indicator in content:
                return True
        
        return False

    def _extract_business_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extrait les informations sur l'entreprise"""
        business_info = {
            'name': None,
            'slogan': None,
            'description': None,
            'founded': None,
            'employees': None,
            'location': None
        }
        
        # Extraire le nom de l'entreprise
        name_patterns = [
            r'<h1[^>]*>([^<]+)</h1>',
            r'<title[^>]*>([^<]+)</title>',
            r'class=["\']?(company-name|business-name|site-name)["\']?[^>]*>([^<]+)<'
        ]
        
        content = str(soup)
        for pattern in name_patterns:
            match = re.search(pattern, content, re.I)
            if match:
                business_info['name'] = clean_text(match.group(1))
                break
        
        # Extraire la description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            business_info['description'] = clean_text(meta_desc['content'])
        
        return business_info

    def _detect_technologies(self, soup: BeautifulSoup) -> List[str]:
        """Détecte les technologies utilisées sur le site"""
        technologies = []
        content = str(soup).lower()
        
        tech_indicators = {
            'WordPress': r'wp-content|wordpress',
            'Drupal': r'drupal',
            'Joomla': r'joomla',
            'React': r'react',
            'Vue.js': r'vue\.js|vuejs',
            'Angular': r'angular',
            'Bootstrap': r'bootstrap',
            'jQuery': r'jquery',
            'Google Analytics': r'google-analytics|gtag',
            'Facebook Pixel': r'facebook\.net|fbq',
            'Hotjar': r'hotjar',
            'Intercom': r'intercom',
            'Zendesk': r'zendesk',
            'HubSpot': r'hubspot'
        }
        
        for tech, pattern in tech_indicators.items():
            if re.search(pattern, content):
                technologies.append(tech)
        
        return technologies

    def _analyze_content_quality(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyse la qualité du contenu"""
        content_quality = {
            'word_count': 0,
            'readability_score': 0,
            'has_meta_description': False,
            'has_alt_tags': False,
            'has_headings': False,
            'has_structured_data': False
        }
        
        # Compter les mots
        text = soup.get_text()
        words = text.split()
        content_quality['word_count'] = len(words)
        
        # Vérifier la présence de meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        content_quality['has_meta_description'] = meta_desc is not None
        
        # Vérifier les alt tags
        images = soup.find_all('img')
        alt_tags = [img.get('alt') for img in images if img.get('alt')]
        content_quality['has_alt_tags'] = len(alt_tags) > 0
        
        # Vérifier les headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        content_quality['has_headings'] = len(headings) > 0
        
        # Vérifier les données structurées
        structured_data = soup.find_all(['script', 'noscript'], type=re.compile(r'application/ld\+json', re.I))
        content_quality['has_structured_data'] = len(structured_data) > 0
        
        # Calculer un score de lisibilité simple
        if content_quality['word_count'] > 0:
            score = 0
            if content_quality['has_meta_description']:
                score += 20
            if content_quality['has_alt_tags']:
                score += 20
            if content_quality['has_headings']:
                score += 30
            if content_quality['has_structured_data']:
                score += 30
            
            content_quality['readability_score'] = score
        
        return content_quality

    def _check_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site est mobile-friendly"""
        mobile_indicators = [
            r'viewport',
            r'responsive',
            r'mobile-friendly',
            r'bootstrap',
            r'flexbox',
            r'grid'
        ]
        
        content = str(soup).lower()
        
        for indicator in mobile_indicators:
            if indicator in content:
                return True
        
        return False

# Instance globale de l'analyseur
website_analyzer = WebsiteAnalyzer()

# Fonction pour l'import facile
def analyze_website_for_ecommerce(url: str) -> Dict[str, Any]:
    """
    Fonction wrapper pour l'analyse de site web
    
    Args:
        url: URL du site web à analyser
        
    Returns:
        Dict[str, Any]: Résultats de l'analyse
    """
    return website_analyzer.analyze_website(url)
