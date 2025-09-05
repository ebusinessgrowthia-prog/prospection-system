"""
Data Enricher pour EBUSINESS AI
Enrichissement des données des prospects avec des informations complémentaires
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re

from src.config import get_config
from src.core.utils import extract_domain_from_url, is_valid_website, clean_text

logger = logging.getLogger(__name__)
config = get_config()

class DataEnricher:
    """Enrichisseur de données pour les prospects"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Mots-clés pour détecter les tailles d'entreprise
        self.size_indicators = {
            'small': ['petite', 'pme', 'tpe', 'start-up', 'startup', 'freelance', 'indépendant'],
            'medium': ['moyenne', 'entreprise', 'société', 'business', 'group'],
            'large': ['grande', 'groupe', 'international', 'multinational', 'corporation']
        }

    def enrich_prospect_data(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données d'un prospect avec des informations complémentaires
        
        Args:
            prospect_data: Données brutes du prospect
            
        Returns:
            Dict[str, Any]: Données enrichies du prospect
        """
        try:
            enriched_data = prospect_data.copy()
            
            # Enrichissement à partir du site web
            if prospect_data.get('website'):
                website_data = self._enrich_from_website(prospect_data['website'])
                enriched_data.update(website_data)
            
            # Enrichissement à partir du nom de l'entreprise
            company_data = self._enrich_from_company_name(prospect_data.get('company', ''))
            enriched_data.update(company_data)
            
            # Détection de la taille d'entreprise
            size_info = self._detect_company_size(enriched_data)
            enriched_data.update(size_info)
            
            # Détection de la maturité e-commerce
            maturity_info = self._detect_ecommerce_maturity(enriched_data)
            enriched_data.update(maturity_info)
            
            # Calcul du score de potentiel
            potential_score = self._calculate_potential_score(enriched_data)
            enriched_data['potential_score'] = potential_score
            
            logger.info(f"✅ Données enrichies pour le prospect: {prospect_data.get('name', '')}")
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enrichissement des données: {e}")
            return prospect_data

    def _enrich_from_website(self, website: str) -> Dict[str, Any]:
        """
        Enrichit les données à partir de l'analyse du site web
        
        Args:
            website: URL du site web
            
        Returns:
            Dict[str, Any]: Données enrichies
        """
        try:
            if not is_valid_website(website):
                return {}
            
            # Récupérer le contenu de la page d'accueil
            response = self.session.get(website, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire les informations de base
            website_data = {
                'website_title': self._extract_title(soup),
                'website_description': self._extract_description(soup),
                'website_keywords': self._extract_keywords(soup),
                'has_contact_page': self._has_contact_page(soup, website),
                'has_blog': self._has_blog(soup),
                'has_ssl': website.startswith('https://'),
                'technologies': self._detect_technologies(soup),
                'social_media': self._extract_social_media(soup),
                'page_count_estimate': self._estimate_page_count(soup)
            }
            
            return website_data
            
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'analyser le site web {website}: {e}")
            return {}

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrait le titre du site web"""
        title_tag = soup.find('title')
        return clean_text(title_tag.text) if title_tag else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrait la description du site web"""
        # Chercher dans les meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return clean_text(meta_desc['content'])
        
        # Chercher dans le premier paragraphe
        first_p = soup.find('p')
        if first_p:
            return clean_text(first_p.text)[:200]
        
        return ""

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les mots-clés du site web"""
        keywords = []
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords['content'].split(',')])
        
        # Mots-clés dans le titre et la description
        title = self._extract_title(soup).lower()
        description = self._extract_description(soup).lower()
        
        # Mots-clés e-commerce
        ecommerce_keywords = [
            'boutique', 'shop', 'store', 'e-commerce', 'ecommerce', 'achat', 'vente',
            'panier', 'commande', 'livraison', 'paiement', 'catalogue', 'produit'
        ]
        
        for keyword in ecommerce_keywords:
            if keyword in title or keyword in description:
                keywords.append(keyword)
        
        return list(set(keywords))[:10]  # Limiter à 10 mots-clés

    def _has_contact_page(self, soup: BeautifulSoup, base_url: str) -> bool:
        """Vérifie si le site a une page de contact"""
        contact_links = soup.find_all('a', href=True)
        
        for link in contact_links:
            href = link['href'].lower()
            if any(keyword in href for keyword in ['contact', 'nous-contacter', 'contactez', 'about']):
                return True
        
        return False

    def _has_blog(self, soup: BeautifulSoup) -> bool:
        """Vérifie si le site a un blog"""
        blog_links = soup.find_all('a', href=True)
        
        for link in blog_links:
            href = link['href'].lower()
            if any(keyword in href for keyword in ['blog', 'actualite', 'news', 'article']):
                return True
        
        return False

    def _detect_technologies(self, soup: BeautifulSoup) -> List[str]:
        """Détecte les technologies utilisées sur le site"""
        technologies = []
        
        # Chercher des indices dans le code HTML
        html_content = str(soup).lower()
        
        # CMS populaires
        cms_indicators = {
            'WordPress': ['wp-content', 'wordpress', 'wp-json'],
            'Shopify': ['shopify', 'cdn.shopify'],
            'PrestaShop': ['prestashop', 'ps_'],
            'Magento': ['magento', 'skin/frontend'],
            'WooCommerce': ['woocommerce', 'wp-content/plugins/woocommerce'],
            'Drupal': ['drupal', 'sites/all'],
            'Joomla': ['joomla', 'com_content']
        }
        
        for cms, indicators in cms_indicators.items():
            if any(indicator in html_content for indicator in indicators):
                technologies.append(cms)
        
        # Frameworks JavaScript
        js_frameworks = {
            'React': ['react', 'reactjs'],
            'Vue.js': ['vue', 'vuejs'],
            'Angular': ['angular', 'ng-'],
            'jQuery': ['jquery', '$(']
        }
        
        for framework, indicators in js_frameworks.items():
            if any(indicator in html_content for indicator in indicators):
                technologies.append(framework)
        
        return technologies

    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrait les liens vers les réseaux sociaux"""
        social_media = {}
        
        social_links = soup.find_all('a', href=True)
        
        for link in social_links:
            href = link['href'].lower()
            
            if 'facebook.com' in href:
                social_media['facebook'] = href
            elif 'twitter.com' in href:
                social_media['twitter'] = href
            elif 'linkedin.com' in href:
                social_media['linkedin'] = href
            elif 'instagram.com' in href:
                social_media['instagram'] = href
            elif 'youtube.com' in href:
                social_media['youtube'] = href
        
        return social_media

    def _estimate_page_count(self, soup: BeautifulSoup) -> int:
        """Estime le nombre de pages sur le site"""
        # Compter les liens internes
        internal_links = soup.find_all('a', href=True)
        domain = extract_domain_from_url(str(soup))
        
        if not domain:
            return 1
        
        internal_count = 0
        for link in internal_links:
            href = link.get('href', '')
            if href and domain in href:
                internal_count += 1
        
        # Estimation basée sur le nombre de liens internes
        if internal_count < 10:
            return 1
        elif internal_count < 50:
            return 10
        elif internal_count < 100:
            return 50
        else:
            return 100

    def _enrich_from_company_name(self, company_name: str) -> Dict[str, Any]:
        """
        Enrichit les données à partir du nom de l'entreprise
        
        Args:
            company_name: Nom de l'entreprise
            
        Returns:
            Dict[str, Any]: Données enrichies
        """
        if not company_name:
            return {}
        
        enriched_data = {}
        
        # Détecter le type d'entreprise
        company_type = self._detect_company_type(company_name)
        if company_type:
            enriched_data['company_type'] = company_type
        
        # Extraire des mots-clés du nom
        name_keywords = self._extract_name_keywords(company_name)
        if name_keywords:
            enriched_data['name_keywords'] = name_keywords
        
        return enriched_data

    def _detect_company_type(self, company_name: str) -> Optional[str]:
        """Détecte le type d'entreprise à partir du nom"""
        company_lower = company_name.lower()
        
        type_indicators = {
            'SARL': ['sarl', 's.a.r.l'],
            'SAS': ['sas', 's.a.s'],
            'SA': ['sa', 's.a'],
            'EURL': ['eurl', 'e.u.r.l'],
            'Auto-entrepreneur': ['auto-entrepreneur', 'autoentrepreneur'],
            'Association': ['association', 'asso'],
            'Group': ['group', 'groupe'],
            'Holding': ['holding']
        }
        
        for company_type, indicators in type_indicators.items():
            if any(indicator in company_lower for indicator in indicators):
                return company_type
        
        return None

    def _extract_name_keywords(self, company_name: str) -> List[str]:
        """Extrait les mots-clés du nom de l'entreprise"""
        keywords = []
        
        # Nettoyer le nom
        clean_name = clean_text(company_name)
        
        # Diviser en mots
        words = clean_name.split()
        
        # Filtrer les mots communs
        common_words = {'et', 'de', 'la', 'le', 'les', 'des', 'du', 'en', 'pour', 'par', 'avec', 'sans'}
        
        for word in words:
            if len(word) > 2 and word.lower() not in common_words:
                keywords.append(word.lower())
        
        return keywords

    def _detect_company_size(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Détecte la taille de l'entreprise
        
        Args:
            enriched_data: Données déjà enrichies
            
        Returns:
            Dict[str, Any]: Informations sur la taille
        """
        size_info = {
            'estimated_size': 'unknown',
            'size_confidence': 0.0
        }
        
        # Analyser différents indicateurs
        indicators = []
        
        # Indicateurs du nom de l'entreprise
        company_name = enriched_data.get('company', '').lower()
        for size_type, keywords in self.size_indicators.items():
            if any(keyword in company_name for keyword in keywords):
                indicators.append((size_type, 0.3))
        
        # Indicateurs du site web
        website_title = enriched_data.get('website_title', '').lower()
        website_description = enriched_data.get('website_description', '').lower()
        
        for size_type, keywords in self.size_indicators.items():
            if any(keyword in website_title or keyword in website_description for keyword in keywords):
                indicators.append((size_type, 0.2))
        
        # Indicateurs du nombre de pages
        page_count = enriched_data.get('page_count_estimate', 1)
        if page_count <= 10:
            indicators.append(('small', 0.4))
        elif page_count <= 50:
            indicators.append(('medium', 0.3))
        else:
            indicators.append(('large', 0.2))
        
        # Indicateurs de technologies
        technologies = enriched_data.get('technologies', [])
        if 'Shopify' in technologies or 'PrestaShop' in technologies:
            indicators.append(('small', 0.2))
        elif 'Magento' in technologies or 'custom' in technologies:
            indicators.append(('medium', 0.2))
        
        # Agréger les résultats
        if indicators:
            # Calculer le score pour chaque taille
            size_scores = {'small': 0.0, 'medium': 0.0, 'large': 0.0}
            
            for size_type, confidence in indicators:
                size_scores[size_type] += confidence
            
            # Déterminer la taille la plus probable
            best_size = max(size_scores, key=size_scores.get)
            best_score = size_scores[best_size]
            
            size_info['estimated_size'] = best_size
            size_info['size_confidence'] = min(best_score, 1.0)
        
        return size_info

    def _detect_ecommerce_maturity(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Détecte la maturité e-commerce de l'entreprise
        
        Args:
            enriched_data: Données déjà enrichies
            
        Returns:
            Dict[str, Any]: Informations sur la maturité
        """
        maturity_info = {
            'maturity_level': 'basic',
            'maturity_score': 0.0
        }
        
        score = 0.0
        
        # Technologies e-commerce
        technologies = enriched_data.get('technologies', [])
        ecommerce_techs = ['Shopify', 'WooCommerce', 'PrestaShop', 'Magento', 'BigCommerce']
        
        for tech in ecommerce_techs:
            if tech in technologies:
                score += 0.3
        
        # Fonctionnalités e-commerce
        keywords = enriched_data.get('website_keywords', [])
        ecommerce_features = [
            'panier', 'commande', 'paiement', 'livraison', 'catalogue', 
            'produit', 'boutique', 'shop', 'store', 'ecommerce'
        ]
        
        for feature in ecommerce_features:
            if feature in keywords:
                score += 0.1
        
        # Présence sur les réseaux sociaux
        social_media = enriched_data.get('social_media', {})
        if len(social_media) >= 2:
            score += 0.2
        
        # Page de contact
        if enriched_data.get('has_contact_page'):
            score += 0.1
        
        # Blog
        if enriched_data.get('has_blog'):
            score += 0.1
        
        # SSL
        if enriched_data.get('has_ssl'):
            score += 0.1
        
        # Déterminer le niveau de maturité
        if score >= 0.8:
            maturity_info['maturity_level'] = 'advanced'
        elif score >= 0.5:
            maturity_info['maturity_level'] = 'intermediate'
        elif score >= 0.2:
            maturity_info['maturity_level'] = 'basic'
        else:
            maturity_info['maturity_level'] = 'emerging'
        
        maturity_info['maturity_score'] = min(score, 1.0)
        
        return maturity_info

    def _calculate_potential_score(self, enriched_data: Dict[str, Any]) -> float:
        """
        Calcule un score de potentiel pour le prospect
        
        Args:
            enriched_data: Données enrichies
            
        Returns:
            float: Score de potentiel (0-10)
        """
        score = 0.0
        
        # Taille de l'entreprise
        size = enriched_data.get('estimated_size', 'unknown')
        size_confidence = enriched_data.get('size_confidence', 0.0)
        
        if size == 'medium':
            score += 3.0 * size_confidence
        elif size == 'large':
            score += 2.0 * size_confidence
        elif size == 'small':
            score += 1.0 * size_confidence
        
        # Maturité e-commerce
        maturity_score = enriched_data.get('maturity_score', 0.0)
        score += maturity_score * 3.0
        
        # Présence de technologies avancées
        technologies = enriched_data.get('technologies', [])
        advanced_techs = ['Magento', 'custom', 'React', 'Vue.js', 'Angular']
        
        for tech in advanced_techs:
            if tech in technologies:
                score += 0.5
        
        # Présence sur les réseaux sociaux
        social_count = len(enriched_data.get('social_media', {}))
        score += social_count * 0.3
        
        # Nombre de pages
        page_count = enriched_data.get('page_count_estimate', 1)
        if page_count > 50:
            score += 1.0
        elif page_count > 10:
            score += 0.5
        
        # Contact et blog
        if enriched_data.get('has_contact_page'):
            score += 0.5
        
        if enriched_data.get('has_blog'):
            score += 0.5
        
        # SSL
        if enriched_data.get('has_ssl'):
            score += 0.5
        
        return min(score, 10.0)

    def batch_enrich_prospects(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrichit une liste de prospects
        
        Args:
            prospects: Liste des prospects à enrichir
            
        Returns:
            List[Dict[str, Any]]: Liste des prospects enrichis
        """
        enriched_prospects = []
        
        for prospect in prospects:
            try:
                enriched_prospect = self.enrich_prospect_data(prospect)
                enriched_prospects.append(enriched_prospect)
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'enrichissement du prospect: {e}")
                enriched_prospects.append(prospect)  # Ajouter le prospect non enrichi
        
        logger.info(f"✅ Enrichissement batch terminé: {len(enriched_prospects)} prospects traités")
        return enriched_prospects

# Instance globale de l'enrichisseur
data_enricher = DataEnricher()

# Fonction pour l'import facile
def enrich_prospect(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction wrapper pour l'enrichissement d'un prospect
    
    Args:
        prospect_data: Données du prospect
        
    Returns:
        Dict[str, Any]: Données enrichies
    """
    return data_enricher.enrich_prospect_data(prospect_data)
