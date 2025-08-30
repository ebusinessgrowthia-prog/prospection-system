import google.generativeai as genai
import logging
from config import GEMINI_API_KEY, AGENCES_CONFIG

logger = logging.getLogger(__name__)

class GoogleDorksGenerator:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_dorks(self, agency_config):
        """Génère des Google Dorks pour une agence"""
        try:
            agency_name = agency_config["nom"]
            sector = agency_config["secteur"]
            target = agency_config["cible"]
            base_dorks = agency_config["dorks_base"]
            
            # Utiliser Gemini pour générer des Dorks supplémentaires
            prompt = f"""
            Génère 10 Google Dorks supplémentaires pour trouver des prospects dans le secteur {sector}.
            Cible: {target}
            
            Les Dorks doivent être similaires à ces exemples:
            {chr(10).join(base_dorks[:3])}
            
            Retourne uniquement la liste des Dorks, un par ligne.
            """
            
            response = self.model.generate_content(prompt)
            additional_dorks = response.text.split('\n')
            
            # Combiner les Dorks de base et les nouveaux
            all_dorks = base_dorks + [dork.strip() for dork in additional_dorks if dork.strip()]
            
            logger.info(f"Généré {len(all_dorks)} Dorks pour {agency_name}")
            return all_dorks[:20]  # Limiter à 20 Dorks
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des Dorks: {e}")
            return agency_config["dorks_base"]
