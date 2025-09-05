"""
Mistral Personalizer pour EBUSINESS AI
Génération d'emails ultra-personnalisés avec Mistral AI
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import mistralai
from mistralai import MistralClient

from src.config import get_config
from src.core.models import EmailGenerationResult

logger = logging.getLogger(__name__)
config = get_config()

class MistralPersonalizer:
    """Générateur d'emails personnalisés avec Mistral AI"""

    def __init__(self):
        self.client = MistralClient(api_key=config.mistral_api_key)
        self.email_prompt_template = config.get_email_prompt_template()
        
        # Templates de base pour différents types de prospects
        self.email_templates = {
            "mode": {
                "accroche": "J'ai remarqué que votre boutique de mode en ligne génère déjà un beau chiffre d'affaires.",
                "probleme": "Avez-vous déjà mesuré combien vos données clients non exploitées pourraient augmenter votre taux de conversion ?",
                "solution": "J'ai conçu un framework d'audit gratuit qui pourrait vous révéler des opportunités cachées dans vos données."
            },
            "électronique": {
                "accroche": "Votre site d'électronique semble bien établi dans votre secteur.",
                "probleme": "Avez-vous déjà analysé comment vos données de vente pourraient optimiser votre chaîne logistique ?",
                "solution": "Mon audit gratuit pourrait identifier des leviers de performance dans votre exploitation des données."
            },
            "digital": {
                "accroche": "Votre activité digitale montre un bon potentiel de croissance.",
                "probleme": "Avez-vous déjà évalué comment vos données utilisateurs pourraient améliorer votre expérience client ?",
                "solution": "Je vous propose un audit gratuit pour explorer comment exploiter au mieux vos données numériques."
            },
            "services": {
                "accroche": "Votre entreprise de services semble avoir une base solide.",
                "probleme": "Avez-vous déjà mesuré l'impact de vos données sur l'optimisation de vos processus ?",
                "solution": "Mon audit gratuit pourrait vous aider à transformer vos données en décisions stratégiques."
            },
            "retail": {
                "accroche": "Votre activité de retail en ligne présente des opportunités intéressantes.",
                "probleme": "Avez-vous déjà exploité vos données de vente pour optimiser votre gestion des stocks ?",
                "solution": "Je vous propose un audit gratuit pour analyser comment vos données peuvent améliorer votre performance."
            }
        }

    def generate_personalized_email(self, prospect_data: Dict[str, Any]) -> EmailGenerationResult:
        """
        Génère un email ultra-personnalisé pour un prospect
        
        Args:
            prospect_data: Données complètes du prospect
            
        Returns:
            EmailGenerationResult: Résultat de la génération
        """
        try:
            prospect_id = prospect_data.get('id', 0)
            
            # Préparer les données pour le prompt
            prompt_data = {
                'name': prospect_data.get('name', ''),
                'company': prospect_data.get('company', ''),
                'sector': prospect_data.get('sector', ''),
                'problem': self._extract_main_problem(prospect_data),
                'specificity': self._extract_specificity(prospect_data),
                'landing_page': config.landing_page_url
            }
            
            # Générer le prompt
            prompt = self.email_prompt_template.format(**prompt_data)
            
            # Appeler Mistral AI
            response = self.client.chat.complete(
                model="mistral-medium",
                messages=[
                    {"role": "system", "content": "Tu es un expert en neurosciences comportementales et psychologie cognitive spécialisé dans la rédaction d'emails de prospection pour e-commerçants."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            generated_content = response.choices[0].message.content
            
            # Extraire le sujet et le contenu
            subject, content = self._extract_subject_and_content(generated_content)
            
            # Valider le contenu
            validation_result = self._validate_generated_email(content, prospect_data)
            
            if not validation_result['valid']:
                logger.warning(f"⚠️ Email généré non valide pour le prospect {prospect_id}: {validation_result['errors']}")
                return EmailGenerationResult(
                    success=False,
                    prospect_id=prospect_id,
                    subject="",
                    content="",
                    error=f"Validation échouée: {', '.join(validation_result['errors'])}"
                )
            
            logger.info(f"✅ Email généré avec succès pour le prospect {prospect_id}")
            
            return EmailGenerationResult(
                success=True,
                prospect_id=prospect_id,
                subject=subject,
                content=content,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de l'email pour le prospect {prospect_data.get('id', 0)}: {e}")
            return EmailGenerationResult(
                success=False,
                prospect_id=prospect_data.get('id', 0),
                subject="",
                content="",
                error=str(e)
            )

    def _extract_main_problem(self, prospect_data: Dict[str, Any]) -> str:
        """Extrait le problème principal du prospect"""
        problems = prospect_data.get('problem_detected', [])
        
        if isinstance(problems, list) and problems:
            return problems[0]  # Prendre le premier problème
        
        # Essayer de détecter un problème dans les données brutes
        raw_data = prospect_data.get('raw_data', {})
        if isinstance(raw_data, dict):
            # Chercher des indices dans le titre ou la description
            title = raw_data.get('title', '').lower()
            description = raw_data.get('description', '').lower()
            
            text = f"{title} {description}"
            
            if 'conversion' in text:
                return "Conversion faible"
            elif 'coût' in text or 'cher' in text:
                return "Acquisition coûteuse"
            elif 'données' in text or 'analytics' in text:
                return "Données inexploitées"
            elif 'fidélisation' in text or 'client' in text:
                return "Fidélisation faible"
        
        return "Optimisation des performances"

    def _extract_specificity(self, prospect_data: Dict[str, Any]) -> str:
        """Extrait la spécificité du prospect"""
        specificities = prospect_data.get('specificity', [])
        
        if isinstance(specificities, list) and specificities:
            return specificities[0]  # Prendre la première spécificité
        
        # Utiliser le secteur comme spécificité par défaut
        sector = prospect_data.get('sector', '')
        if sector:
            return f"Secteur {sector}"
        
        return "Activité en ligne"

    def _extract_subject_and_content(self, generated_content: str) -> tuple:
        """Extrait le sujet et le contenu de l'email généré"""
        lines = generated_content.strip().split('\n')
        
        subject = ""
        content_lines = []
        
        # Chercher la ligne sujet (généralement la première ligne non vide)
        for line in lines:
            line = line.strip()
            if line and not subject:
                # Nettoyer le sujet
                subject = line.replace('Subject:', '').replace('Objet:', '').strip()
                if subject and not subject.endswith('.'):
                    subject += '.'
                continue
            
            if line:
                content_lines.append(line)
        
        content = '\n'.join(content_lines)
        
        # Si pas de sujet trouvé, en générer un
        if not subject:
            subject = "Opportunités pour votre e-commerce"
        
        return subject, content

    def _validate_generated_email(self, content: str, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide l'email généré selon les directives"""
        errors = []
        
        # Vérifier la présence du CTA
        if config.landing_page_url not in content:
            errors.append("CTA manquant")
        
        # Vérifier la présence de la signature
        if "EBUSINESS AI" not in content:
            errors.append("Signature manquante")
        
        # Vérifier l'absence d'URLs brutes
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content)
        
        # Compter les URLs (le CTA devrait être le seul)
        if len(urls) > 1:
            errors.append("Trop d'URLs dans le contenu")
        
        # Vérifier le ton (utilisation du conditionnel)
        conditionnel_words = ['pourrait', 'serait', 'pourrait-il', 'serait-il', 'pourriez', 'seriez']
        content_lower = content.lower()
        
        if not any(word in content_lower for word in conditionnel_words):
            errors.append("Ton trop affirmatif")
        
        # Vérifier la longueur
        if len(content) < 200:
            errors.append("Email trop court")
        elif len(content) > 2000:
            errors.append("Email trop long")
        
        # Vérifier la personnalisation
        name = prospect_data.get('name', '')
        company = prospect_data.get('company', '')
        
        if name and name.lower() not in content_lower:
            errors.append("Nom du prospect non mentionné")
        
        if company and company.lower() not in content_lower:
            errors.append("Entreprise du prospect non mentionnée")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def generate_batch_emails(self, prospects: List[Dict[str, Any]]) -> List[EmailGenerationResult]:
        """
        Génère des emails pour une liste de prospects
        
        Args:
            prospects: Liste des prospects
            
        Returns:
            List[EmailGenerationResult]: Résultats de génération
        """
        results = []
        
        for prospect in prospects:
            result = self.generate_personalized_email(prospect)
            results.append(result)
            
            # Petit délai pour éviter de surcharger l'API
            import time
            time.sleep(0.5)
        
        logger.info(f"✅ Génération batch terminée: {len(results)} emails générés")
        return results

    def get_email_template_for_sector(self, sector: str) -> Dict[str, str]:
        """
        Retourne le template d'email pour un secteur donné
        
        Args:
            sector: Secteur du prospect
            
        Returns:
            Dict[str, str]: Template pour le secteur
        """
        sector_lower = sector.lower()
        
        # Chercher une correspondance exacte
        if sector_lower in self.email_templates:
            return self.email_templates[sector_lower]
        
        # Chercher une correspondance partielle
        for key, template in self.email_templates.items():
            if key in sector_lower:
                return template
        
        # Template par défaut
        return {
            "accroche": "Votre activité en ligne semble prometteuse.",
            "probleme": "Avez-vous déjà mesuré comment vos données pourraient optimiser votre performance ?",
            "solution": "Je vous propose un audit gratuit pour explorer vos opportunités de croissance."
        }

# Instance globale du personnalisateur
mistral_personalizer = MistralPersonalizer()

# Fonction pour l'import facile
def generate_personalized_email_for_prospect(prospect_data: Dict[str, Any]) -> EmailGenerationResult:
    """
    Fonction wrapper pour la génération d'email personnalisé
    
    Args:
        prospect_data: Données du prospect
        
    Returns:
        EmailGenerationResult: Résultat de la génération
    """
    return mistral_personalizer.generate_personalized_email(prospect_data)
