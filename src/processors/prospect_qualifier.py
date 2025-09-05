"""
Prospect Qualifier pour EBUSINESS AI
Qualification automatique des prospects selon des critères prédéfinis
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.config import get_config
from src.core.models import QualificationResult, ProspectStatus, ProspectSource
from src.core.utils import calculate_qualification_score, extract_keywords, clean_text

logger = logging.getLogger(__name__)
config = get_config()

class ProspectQualifier:
    """Qualificateur de prospects basé sur des règles métier"""

    def __init__(self):
        self.target_sectors = config.target_sectors
        self.target_countries = config.target_countries
        self.min_company_size = config.min_company_size
        self.max_company_size = config.max_company_size
        
        # Mots-clés pour détecter les e-commerces
        self.ecommerce_keywords = [
            "e-commerce", "ecommerce", "boutique en ligne", "shop", "store",
            "vendre en ligne", "commerce en ligne", "site e-commerce",
            "plateforme e-commerce", "solution e-commerce", "logiciel e-commerce",
            "gestion e-commerce", "optimisation e-commerce", "audit e-commerce"
        ]
        
        # Mots-clés pour détecter les problèmes
        self.problem_keywords = [
            "problème", "difficulté", "défi", "obstacle", "frein",
            "coûteux", "cher", "complexe", "difficile", "lent",
            "conversion", "trafic", "ventes", "chiffre d'affaires", "ca",
            "données", "analytics", "performance", "optimisation",
            "acquisition", "fidélisation", "référencement", "seo"
        ]
        
        # Mots-clés pour la taille d'entreprise
        self.size_keywords = {
            "small": ["petite", "pme", "tpe", "start-up", "startup"],
            "medium": ["moyenne", "entreprise", "société", "business"],
            "large": ["grande", "groupe", "international", "multinational"]
        }

    def qualify_prospect(self, prospect_data: Dict[str, Any]) -> QualificationResult:
        """
        Qualifie un prospect selon les critères définis
        
        Args:
            prospect_data: Données du prospect à qualifier
            
        Returns:
            QualificationResult: Résultat de la qualification
        """
        try:
            prospect_id = prospect_data.get('id', 0)
            
            # Critères de qualification
            sector_match = self._check_sector_match(prospect_data)
            country_match = self._check_country_match(prospect_data)
            has_website = self._check_website(prospect_data)
            has_email = self._check_email(prospect_data)
            is_ecommerce = self._check_is_ecommerce(prospect_data)
            size_appropriate = self._check_size_appropriate(prospect_data)
            
            # Calculer le score
            score = self._calculate_qualification_score(
                sector_match, country_match, has_website, has_email, 
                is_ecommerce, size_appropriate, prospect_data
            )
            
            # Déterminer si le prospect est qualifié
            qualified = score >= 5.0  # Score minimum pour être qualifié
            
            # Extraire les raisons
            reasons = []
            detected_problems = []
            specificities = []
            
            if sector_match:
                reasons.append("Secteur cible")
            
            if country_match:
                reasons.append("Pays cible")
            
            if has_website:
                reasons.append("Site web présent")
            
            if has_email:
                reasons.append("Email professionnel disponible")
            
            if is_ecommerce:
                reasons.append("E-commerce détecté")
                specificities.append("Activité e-commerce confirmée")
            
            if size_appropriate:
                reasons.append("Taille d'entreprise appropriée")
            
            # Détecter les problèmes spécifiques
            detected_problems = self._detect_problems(prospect_data)
            specificities.extend(self._extract_specificities(prospect_data))
            
            logger.info(f"✅ Prospect {prospect_id} qualifié: {qualified} (score: {score})")
            
            return QualificationResult(
                prospect_id=prospect_id,
                qualified=qualified,
                score=score,
                reasons=reasons,
                detected_problems=detected_problems,
                specificities=specificities
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la qualification du prospect: {e}")
            return QualificationResult(
                prospect_id=prospect_data.get('id', 0),
                qualified=False,
                score=0.0,
                reasons=[],
                detected_problems=[],
                specificities=[]
            )

    def _check_sector_match(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si le secteur du prospect correspond aux secteurs cibles"""
        sector = prospect_data.get('sector', '').lower()
        
        if not sector:
            return False
        
        return any(target_sector.lower() in sector for target_sector in self.target_sectors)

    def _check_country_match(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si le pays du prospect correspond aux pays cibles"""
        country = prospect_data.get('country', '').lower()
        
        if not country:
            return False
        
        return any(target_country.lower() in country for target_country in self.target_countries)

    def _check_website(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si le prospect a un site web"""
        website = prospect_data.get('website', '')
        
        if not website:
            return False
        
        # Vérifier que le site web semble valide
        return website.startswith(('http://', 'https://')) and len(website) > 10

    def _check_email(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si le prospect a un email professionnel"""
        email = prospect_data.get('email', '')
        
        if not email:
            return False
        
        # Vérifier que l'email est valide et professionnel
        return '@' in email and not email.endswith(('@gmail.com', '@yahoo.com', '@hotmail.com', '@outlook.com'))

    def _check_is_ecommerce(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si le prospect est un e-commerce"""
        # Vérifier dans plusieurs champs
        text_to_check = ""
        
        for field in ['company', 'sector', 'website', 'raw_data']:
            value = prospect_data.get(field, '')
            if isinstance(value, str):
                text_to_check += f" {value.lower()}"
        
        # Chercher des mots-clés e-commerce
        return any(keyword in text_to_check for keyword in self.ecommerce_keywords)

    def _check_size_appropriate(self, prospect_data: Dict[str, Any]) -> bool:
        """Vérifie si la taille de l'entreprise est appropriée"""
        # Pour l'instant, on considère que c'est approprié si on a les infos de base
        # Cette méthode pourrait être améliorée avec des données plus précises
        return (
            prospect_data.get('company') and 
            prospect_data.get('website') and
            prospect_data.get('sector')
        )

    def _calculate_qualification_score(self, *args, **kwargs) -> float:
        """Calcule le score de qualification"""
        sector_match, country_match, has_website, has_email, is_ecommerce, size_appropriate, prospect_data = args
        
        score = 0.0
        
        # Critères de base
        if sector_match:
            score += 2.0
        
        if country_match:
            score += 2.0
        
        if has_website:
            score += 1.5
        
        if has_email:
            score += 1.5
        
        if is_ecommerce:
            score += 2.0
        
        if size_appropriate:
            score += 1.0
        
        # Bonus pour les informations complémentaires
        if prospect_data.get('phone'):
            score += 0.5
        
        if prospect_data.get('specificity'):
            score += 0.5
        
        # Bonus pour les problèmes détectés
        if self._detect_problems(prospect_data):
            score += 0.5
        
        return min(score, 10.0)  # Score maximum de 10

    def _detect_problems(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Détecte les problèmes potentiels du prospect"""
        problems = []
        
        # Analyser plusieurs champs
        text_to_check = ""
        for field in ['company', 'sector', 'website', 'raw_data']:
            value = prospect_data.get(field, '')
            if isinstance(value, str):
                text_to_check += f" {value.lower()}"
        
        # Détecter des problèmes spécifiques
        problem_patterns = {
            "Conversion faible": [
                "conversion", "taux de conversion", "transformer", "optimiser conversion"
            ],
            "Acquisition coûteuse": [
                "acquisition", "coût", "cher", "trafic payant", "publicité", "roi"
            ],
            "Données inexploitées": [
                "données", "analytics", "statistiques", "mesurer", "analyser", "tracking"
            ],
            "Fidélisation faible": [
                "fidélisation", "rétention", "clients", "abandon", "churn"
            ],
            "Performance technique": [
                "lent", "performance", "vitesse", "optimisation", "technique"
            ],
            "Référencement": [
                "seo", "référencement", "visibilité", "google", "moteur de recherche"
            ]
        }
        
        for problem, keywords in problem_patterns.items():
            if any(keyword in text_to_check for keyword in keywords):
                problems.append(problem)
        
        return problems

    def _extract_specificities(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extrait les spécificités du prospect"""
        specificities = []
        
        # Spécificités basées sur le secteur
        sector = prospect_data.get('sector', '').lower()
        if 'mode' in sector:
            specificities.append("Secteur de la mode")
        elif 'électronique' in sector:
            specificities.append("Secteur électronique")
        elif 'digital' in sector:
            specificities.append("Secteur numérique")
        
        # Spécificités basées sur la présence d'éléments
        if prospect_data.get('phone'):
            specificities.append("Téléphone disponible")
        
        if prospect_data.get('email'):
            specificities.append("Email professionnel disponible")
        
        if prospect_data.get('website'):
            specificities.append("Site web identifié")
        
        # Spécificités basées sur les données brutes
        raw_data = prospect_data.get('raw_data', {})
        if isinstance(raw_data, dict):
            if raw_data.get('title'):
                specificities.append("Titre identifié")
            
            if raw_data.get('description'):
                specificities.append("Description disponible")
        
        return specificities

    def batch_qualify_prospects(self, prospects: List[Dict[str, Any]]) -> List[QualificationResult]:
        """
        Qualifie une liste de prospects
        
        Args:
            prospects: Liste des prospects à qualifier
            
        Returns:
            List[QualificationResult]: Résultats de qualification
        """
        results = []
        
        for prospect in prospects:
            result = self.qualify_prospect(prospect)
            results.append(result)
        
        logger.info(f"✅ Qualification batch terminée: {len(results)} prospects traités")
        return results

# Instance globale du qualificateur
prospect_qualifier = ProspectQualifier()

# Fonction pour l'import facile
def qualify_prospect_data(prospect_data: Dict[str, Any]) -> QualificationResult:
    """
    Fonction wrapper pour la qualification d'un prospect
    
    Args:
        prospect_data: Données du prospect à qualifier
        
    Returns:
        QualificationResult: Résultat de la qualification
    """
    return prospect_qualifier.qualify_prospect(prospect_data)
