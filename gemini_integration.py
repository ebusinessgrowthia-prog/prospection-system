import google.generativeai as genai
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class GeminiIntegration:
    def __init__(self, api_key: str):
        """Initialize Gemini integration"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate_dorks(self, agence_info: Dict[str, Any]) -> List[str]:
        """Generate Google Dorks based on agence information"""
        prompt = f"""
        Génère 10 requêtes Google Dorks optimisées pour trouver des prospects B2B pour une agence.
        
        Informations de l'agence:
        - Nom: {agence_info.get('nom_agence', '')}
        - Secteur: {agence_info.get('secteur', '')}
        - Cible: {agence_info.get('cible_principale', '')}
        - Localisation: {agence_info.get('localisation', 'France')}
        
        Les Dorks doivent:
        1. Être spécifiques au secteur
        2. Inclure des mots-clés de prospection
        3. Cibler les décideurs
        4. Être adaptés à la localisation
        
        Retourne uniquement une liste JSON des 10 Dorks, sans explication.
        """
        
        try:
            response = self.model.generate_content(prompt)
            dorks_text = response.text.strip()
            
            # Try to parse as JSON
            if dorks_text.startswith('[') and dorks_text.endswith(']'):
                return json.loads(dorks_text)
            else:
                # Fallback: extract lines
                return [line.strip() for line in dorks_text.split('\n') if line.strip()]
                
        except Exception as e:
            logger.error(f"Error generating Dorks: {e}")
            return self._get_default_dorks(agence_info)
    
    def analyze_prospect(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prospect data to extract insights"""
        prompt = f"""
        Analyse ce prospect pour personnaliser l'approche commerciale:
        
        Données du prospect:
        {json.dumps(prospect_data, indent=2, ensure_ascii=False)}
        
        Extrais:
        1. Pain points probables
        2. Opportunités d'amélioration
        3. Angle d'approche personnalisé
        4. Ton recommandé
        
        Retourne un JSON structuré avec ces informations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error analyzing prospect: {e}")
            return {
                "pain_points": ["Besoin de visibilité en ligne"],
                "opportunities": ["Amélioration SEO possible"],
                "approach_angle": "Approche consultative",
                "recommended_tone": "professionnel et amical"
            }
    
    def generate_personalized_email(self, prospect_analysis: Dict[str, Any], 
                                  agence_info: Dict[str, Any], 
                                  prospect_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate personalized email content"""
        prompt = f"""
        Rédige un email de prospection ultra-personnalisé.
        
        Analyse du prospect:
        {json.dumps(prospect_analysis, indent=2, ensure_ascii=False)}
        
        Informations de l'agence:
        {json.dumps(agence_info, indent=2, ensure_ascii=False)}
        
        Données du prospect:
        {json.dumps(prospect_data, indent=2, ensure_ascii=False)}
        
        Structure:
        1. Objet accrocheur et personnalisé
        2. Corps du message (max 150 mots)
        3. CTA clair
        4. Signature professionnelle
        
        Retourne un JSON avec "objet" et "corps".
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return {
                "objet": f"Boostez votre {prospect_data.get('secteur', 'activité')} avec notre expertise",
                "corps": f"Bonjour {prospect_data.get('nom_complet', '')},\n\nJ'ai remarqué que votre entreprise {prospect_data.get('entreprise', '')} pourrait bénéficier de notre expertise en {agence_info.get('secteur', 'marketing digital')}.\n\nSeriez-vous ouvert à un échange rapide ?\n\nCordialement,\n{agence_info.get('nom_agence', 'Notre agence')}"
            }
    
    def optimize_campaign(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize campaign based on performance data"""
        prompt = f"""
        Optimise cette campagne de prospection basée sur les données de performance:
        
        {json.dumps(performance_data, indent=2, ensure_ascii=False)}
        
        Recommande:
        1. Ajustements des Dorks
        2. Amélioration des messages
        3. Changements de stratégie
        4. Nouvelles opportunités
        
        Retourne un JSON avec les recommandations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error optimizing campaign: {e}")
            return {
                "dork_adjustments": ["Ajouter des mots-clés spécifiques"],
                "message_improvements": ["Rendre les sujets plus accrocheurs"],
                "strategy_changes": ["Cibler des sous-secteurs"],
                "new_opportunities": ["LinkedIn outreach"]
            }
    
    def _get_default_dorks(self, agence_info: Dict[str, Any]) -> List[str]:
        """Fallback default Dorks"""
        secteur = agence_info.get('secteur', '').lower()
        cible = agence_info.get('cible_principale', '').lower()
        
        return [
            f'site:linkedin.com "{cible}" "{secteur}" email',
            f'intitle:"contact" "{cible}" "{secteur}"',
            f'inurl:contact "{cible}" "{secteur}"',
            f'"@{cible.replace(" ", "")}" "{secteur}"',
            f'site:fr.linkedin.com "{cible}" "{secteur}"',
            f'intitle:"à propos" "{cible}" "{secteur}"',
            f'inurl:equipe "{cible}" "{secteur}"',
            f'"contact@" "{cible}" "{secteur}"',
            f'site:entreprises.fr "{cible}" "{secteur}"',
            f'intitle:"nous contacter" "{cible}" "{secteur}"'
        ]