"""
Google Dorks Scraper pour EBUSINESS AI
Recherche automatisée de prospects e-commerce via Google Dorks
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup

from src.config import get_config
from src.core.models import ScrapingResult, ProspectData, ProspectSource
from src.core.utils import clean_text, extract_domain_from_url, is_valid_website

logger = logging.getLogger(__name__)
config = get_config()

class GoogleDorksScraper:
    """Scraper pour les Google Dorks"""
    
    def __init__(self):
        self.serpapi_key = config.serpapi_api_key
        self.base_url = "https://serpapi.com/search"
        
    def search_prospects(self, dorks: List[str] = None, max_results_per_dork: int = 10) -> ScrapingResult:
        """
        Recherche des prospects en utilisant les Google Dorks
        
        Args:
            dorks: Liste des dorks à utiliser (si None, utilise les dorks de la config)
            max_results_per_dork: Nombre maximum de résultats par dork
            
        Returns:
            ScrapingResult: Résultats de la recherche
        """
        try:
            if not dorks:
                dorks = config.get_google_dorks()
            
            all_prospects = []
            total_searched = 0
            
            logger.info(f"🔍 Début de la recherche Google Dorks avec {len(dorks)} dorks")
            
            for i, dork in enumerate(dorks):
                try:
                    logger.info(f"Recherche {i+1}/{len(dorks)}: {dork}")
                    
                    # Effectuer la recherche
                    results = self._search_single_dork(dork, max_results_per_dork)
                    
                    if results:
                        all_prospects.extend(results)
                        total_searched += len(results)
                        logger.info(f"✅ {len(results)} prospects trouvés pour: {dork}")
                    
                    # Délai pour éviter de surcharger l'API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la recherche du dork '{dork}': {e}")
                    continue
            
            # Éliminer les doublons
            unique_prospects = self._remove_duplicates(all_prospects)
            
            logger.info(f"🎯 Recherche terminée: {len(unique_prospects)} prospects uniques trouvés")
            
            return ScrapingResult(
                success=True,
                data=[prospect.to_dict() for prospect in unique_prospects],
                source="google_dorks",
                scraped_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur critique lors de la recherche Google Dorks: {e}")
            return ScrapingResult(
                success=False,
                error=str(e),
                source="google_dorks",
                scraped_at=datetime.now()
            )
    
    def _search_single_dork(self, dork: str, max_results: int) -> List[ProspectData]:
        """
        Recherche les résultats pour un seul dork
        
        Args:
            dork: Le dork à rechercher
            max_results: Nombre maximum de résultats
            
        Returns:
            List[ProspectData]: Liste des prospects trouvés
        """
        try:
            # Configuration de la recherche SerpAPI
            params = {
                "engine": "google",
                "q": dork,
                "api_key": self.serpapi_key,
                "num": max_results,
                "gl": "fr",  # France
                "hl": "fr"   # Français
            }
            
            # Effectuer la recherche
            search = GoogleSearch(params)
            results = search.get_dict()
            
            prospects = []
            
            # Traiter les résultats organiques
            if "organic_results" in results:
                for result in results["organic_results"][:max_results]:
                    prospect = self._extract_prospect_from_result(result, dork)
                    if prospect:
                        prospects.append(prospect)
            
            return prospects
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche du dork '{dork}': {e}")
            return []
    
    def _extract_prospect_from_result(self, result: Dict[str, Any], dork: str) -> Optional[ProspectData]:
        """
        Extrait les informations d'un prospect à partir d'un résultat Google
        
        Args:
            result: Résultat Google
            dork: Dork utilisé pour la recherche
            
        Returns:
            ProspectData: Prospect extrait ou None si invalide
        """
        try:
            # Extraire l'URL
            url = result.get("link", "")
            if not url or not is_valid_website(url):
                return None
            
            # Extraire le titre
            title = result.get("title", "")
            if not title:
                return None
            
            # Extraire le snippet
            snippet = result.get("snippet", "")
            
            # Détecter le nom de l'entreprise et le domaine
            company, domain = self._extract_company_info(url, title, snippet)
            
            if not company:
                return None
            
            # Détecter le secteur
            sector = self._detect_sector(title, snippet, dork)
            
            # Détecter le pays
            country = self._detect_country(title, snippet, url)
            
            # Créer le prospect
            prospect = ProspectData(
                name=company,  # Utiliser le nom de l'entreprise comme nom par défaut
                company=company,
                website=url,
                sector=sector,
                country=country,
                source=ProspectSource.GOOGLE_DORKS,
                raw_data={
                    "dork": dork,
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "searched_at": datetime.now().isoformat()
                }
            )
            
            return prospect
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction du prospect: {e}")
            return None
    
    def _extract_company_info(self, url: str, title: str, snippet: str) -> tuple:
        """
        Extrait le nom de l'entreprise et le domaine à partir des informations disponibles
        
        Args:
            url: URL du site
            title: Titre du résultat
            snippet: Snippet du résultat
            
        Returns:
            tuple: (company_name, domain)
        """
        try:
            # Extraire le domaine de l'URL
            domain = extract_domain_from_url(url)
            if not domain:
                return None, None
            
            # Nettoyer le domaine pour obtenir un nom d'entreprise potentiel
            company_candidates = []
            
            # 1. Utiliser le titre
            if title:
                clean_title = clean_text(title)
                company_candidates.append(clean_title)
            
            # 2. Utiliser le domaine
            domain_parts = domain.split('.')
            if len(domain_parts) > 1:
                company_name = domain_parts[0].title()
                company_candidates.append(company_name)
            
            # 3. Chercher des noms d'entreprise dans le snippet
            if snippet:
                # Chercher des patterns comme "Nom de l'entreprise" ou "Entreprise X"
                import re
                company_patterns = [
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:boutique|shop|store|e-commerce|ecommerce)',
                    r'(?:boutique|shop|store|e-commerce|ecommerce)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:en ligne|online)',
                ]
                
                for pattern in company_patterns:
                    matches = re.findall(pattern, snippet, re.IGNORECASE)
                    if matches:
                        company_candidates.extend(matches)
            
            # Choisir le meilleur candidat
            if company_candidates:
                # Préférer les noms plus longs (plus spécifiques)
                best_candidate = max(company_candidates, key=len)
                
                # Nettoyer le nom
                best_candidate = clean_text(best_candidate)
                
                # Limiter la longueur
                if len(best_candidate) > 100:
                    best_candidate = best_candidate[:100]
                
                return best_candidate, domain
            
            return domain.split('.')[0].title(), domain
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des infos entreprise: {e}")
            return None, None
    
    def _detect_sector(self, title: str, snippet: str, dork: str) -> Optional[str]:
        """
        Détecte le secteur d'activité à partir des informations disponibles
        
        Args:
            title: Titre du résultat
            snippet: Snippet du résultat
            dork: Dork utilisé
            
        Returns:
            str: Secteur détecté ou None
        """
        try:
            text = f"{title} {snippet} {dork}".lower()
            
            # Mots-clés par secteur
            sector_keywords = {
                "Mode": ["mode", "vetements", "vêtements", "fashion", "clothing", "boutique", "style", "tendance"],
                "Électronique": ["électronique", "electronique", "high-tech", "tech", "informatique", "smartphone", "ordinateur"],
                "Services": ["service", "services", "consulting", "conseil", "expertise", "formation", "accompagnement"],
                "Digital": ["digital", "numérique", "online", "web", "internet", "e-commerce", "ecommerce"],
                "Retail": ["retail", "magasin", "store", "shop", "vente", "commerce", "distribution"]
            }
            
            # Compter les occurrences de mots-clés par secteur
            sector_scores = {}
            for sector, keywords in sector_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    sector_scores[sector] = score
            
            # Retourner le secteur avec le score le plus élevé
            if sector_scores:
                return max(sector_scores, key=sector_scores.get)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la détection du secteur: {e}")
            return None
    
    def _detect_country(self, title: str, snippet: str, url: str) -> Optional[str]:
        """Détecte le pays à partir des informations disponibles"""
        try:
            text = f"{title} {snippet} {url}".lower()
            
            # Mots-clés par pays
            country_keywords = {
                "France": ["france", "français", "paris", "lyon", "marseille", ".fr"],
                "Belgique": ["belgique", "belge", "bruxelles", "anvers", ".be"],
                "Suisse": ["suisse", "suisse", "zurich", "genève", "lausanne", ".ch"],
                "Luxembourg": ["luxembourg", "luxembourgeois", ".lu"],
                "Monaco": ["monaco", "monégasque", ".mc"],
                "Canada (Québec)": ["québec", "quebec", "canada", "montréal", "toronto", ".ca"]
            }
            
            # Compter les occurrences de mots-clés par pays
            country_scores = {}
            for country, keywords in country_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    country_scores[country] = score
            
            # Retourner le pays avec le score le plus élevé
            if country_scores:
                return max(country_scores, key=country_scores.get)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la détection du pays: {e}")
            return None
    
    def _remove_duplicates(self, prospects: List[ProspectData]) -> List[ProspectData]:
        """
        Élimine les doublons de la liste des prospects
        
        Args:
            prospects: Liste des prospects
            
        Returns:
            List[ProspectData]: Liste sans doublons
        """
        try:
            unique_prospects = []
            seen_websites = set()
            seen_companies = set()
            
            for prospect in prospects:
                # Vérifier par website
                if prospect.website and prospect.website in seen_websites:
                    continue
                
                # Vérifier par nom d'entreprise
                if prospect.company and prospect.company.lower() in seen_companies:
                    continue
                
                # Ajouter le prospect
                unique_prospects.append(prospect)
                
                # Ajouter aux ensembles de vérification
                if prospect.website:
                    seen_websites.add(prospect.website)
                if prospect.company:
                    seen_companies.add(prospect.company.lower())
            
            return unique_prospects
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'élimination des doublons: {e}")
            return prospects

# Instance globale du scraper
google_dorks_scraper = GoogleDorksScraper()

# Fonction pour l'import facile
def search_prospects_with_google_dorks(dorks: List[str] = None, max_results_per_dork: int = 10) -> ScrapingResult:
    """
    Fonction wrapper pour la recherche de prospects avec Google Dorks
    
    Args:
        dorks: Liste des dorks à utiliser
        max_results_per_dork: Nombre maximum de résultats par dork
        
    Returns:
        ScrapingResult: Résultats de la recherche
    """
    return google_dorks_scraper.search_prospects(dorks, max_results_per_dork)
