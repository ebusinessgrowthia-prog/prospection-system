import google.generativeai as genai
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class AIEmailWriter:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_email(self, prospect, agency_name, agency_config, plan_message):
        """Génère un email personnalisé selon le plan de message"""
        try:
            # Extraire les informations du prospect
            prospect_name = prospect.get("name", "")
            prospect_company = prospect.get("company", "")
            prospect_sector = prospect.get("sector", "")
            
            # Obtenir les informations de l'agence
            agency_nom = agency_config["nom"]
            agency_secteur = agency_config["secteur"]
            agency_cible = agency_config["cible"]
            agency_objectif = agency_config["objectif"]
            agency_ton = agency_config["style_ton"]
            agency_cta = agency_config["cta_principal"]
            
            # Construire le prompt selon le plan de message
            prompt = f"""
            Tu es un expert en prospection pour l'agence {agency_nom}. Tu dois rédiger un email de prospection en suivant strictement le plan ci-dessous.
            
            PLAN DE MESSAGE À RESPECTER :
            
            1. NOUVEAU POSITIONNEMENT
            {agency_nom} se présente comme une agence spécialisée dans {plan_message["nouveau_positionnement"][agency_nom]}.
            Ce service est né d'un constat simple sur le marché :
            • Les entreprises investissent énormément dans l'acquisition,
            • mais leurs taux de conversion restent faibles, même pour les meilleures.
            • Les prospects non convertis ou inactifs représentent une mine d'opportunités inexploitées.
            Notre rôle : exploiter ce potentiel caché avec une approche méthodique, humaine et technologique.
            
            2. OBJECTIF DU SERVICE
            {plan_message["objectif_service"][agency_nom]}
            
            3. NOTRE APPROCHE
            • Collaborative et humaine : chaque mail doit donner l'impression d'un vrai échange personnel, pas d'un modèle robotique.
            • Le "je" avant tout : je parle en mon nom, en tant que consultant, pas en tant que "nous, la boîte".
            • Des questions ouvertes : l'objectif est de pousser le prospect à réfléchir sur ses propres blocages.
            • Faire émerger le besoin chez lui-même : le prospect doit se dire "c'est exactement mon problème".
            • Ultra-personnalisation : s'appuyer sur ce qu'on sait déjà de l'entreprise.
            
            4. TON ATTENDU
            • Humain : langage naturel, empathique, pas de jargon froid.
            • Concis mais précis : accrocher rapidement, donner envie de lire jusqu'à la fin.
            • Accroche forte : commencer avec une phrase qui interpelle ou qui touche directement le problème latent.
            • Émotionnel + rationnel : jouer sur la frustration de ne pas convertir assez → montrer que nous apportons une solution concrète.
            • Collaboratif : proposer de réfléchir ensemble à leur cas, plutôt que d'imposer une solution toute faite.
            
            5. OFFRE & URGENCE
            • Service tout juste lancé.
            • Offre limitée à 5 entreprises, avec un tarif symbolique ou gratuit (pour créer des cas clients).
            • Le prospect doit sentir qu'il est personnellement choisi parce que nous savons que ce service lui sera utile.
            
            6. STRUCTURE À RESPECTER DANS LES MAILS
            1. Accroche personnelle (phrase choc, humaine, centrée sur le problème de conversion)
            2. Constat partagé (je comprends ce que vivent les entreprises de votre secteur)
            3. La faille (vos coûts d'acquisition sont lourds, mais vos taux de conversion restent trop faibles)
            4. La solution (je propose un service précis pour résoudre votre problème)
            5. La preuve de rareté (offre limitée, service en lancement)
            6. La question ouverte (ex. "Est-ce que vous aimeriez qu'on explore ensemble vos pistes de conversion cachées ?")
            7. Clôture humaine et simple
            
            INFORMATIONS SUR LE PROSPECT :
            - Nom: {prospect_name}
            - Entreprise: {prospect_company}
            - Secteur: {prospect_sector}
            
            INFORMATIONS SUR L'AGENCE :
            - Nom: {agency_nom}
            - Secteur: {agency_secteur}
            - Cible: {agency_cible}
            - Objectif: {agency_objectif}
            - Ton: {agency_ton}
            - CTA: {agency_cta}
            
            INSTRUCTIONS SUPPLÉMENTAIRES :
            - Utilise le "je" et non le "nous"
            - Sois empathique et humain
            - Pose une seule question ouverte à la fin
            - Le CTA doit être un texte cliquable qui mène à l'objectif
            - Signature : "Merci,\\n{agency_nom}"
            
            Génère un email ultra-personnalisé qui respecte scrupuleusement ce plan de message.
            """
            
            # Générer l'email avec Gemini
            response = self.model.generate_content(prompt)
            email_content = response.text
            
            return email_content
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'email: {e}")
            return self.generate_fallback_email(prospect, agency_config)
    
    def generate_fallback_email(self, prospect, agency_config):
        """Génère un email de secours en cas d'échec"""
        return f"""
        Bonjour {prospect.get('name', '')},
        
        J'ai remarqué que votre entreprise {prospect.get('company', '')} pourrait bénéficier de nos services de {agency_config['secteur']}.
        
        {agency_config['objectif']}
        
        Souhaitez-vous en discuter ?
        
        Merci,
        {agency_config['nom']}
        """
    
    def generate_subject(self, prospect, agency_name):
        """Génère un objet d'email personnalisé"""
        try:
            prompt = f"""
            Génère un objet d'email court et percutant pour :
            - Prospect: {prospect.get('name', '')}
            - Entreprise: {prospect.get('company', '')}
            - Agence: {agency_name}
            
            L'objet doit susciter l'intérêt et l'ouverture de l'email.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'objet: {e}")
            return f"Opportunité pour {prospect.get('company', '')}"
