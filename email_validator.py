import requests
import logging
from config import ABSTRACT_API_KEY, EMAIL_VALIDATION_THRESHOLD

logger = logging.getLogger(__name__)

class EmailValidator:
    def __init__(self):
        self.api_key = ABSTRACT_API_KEY
    
    def validate_emails(self, prospects):
        """Valide une liste d'emails prospects"""
        valid_prospects = []
        
        for prospect in prospects:
            try:
                # Valider l'email avec Abstract API
                is_valid, score = self.validate_email(prospect["email"])
                
                if is_valid and score >= EMAIL_VALIDATION_THRESHOLD:
                    prospect["validation_score"] = score
                    prospect["status"] = "Validé"
                    valid_prospects.append(prospect)
                else:
                    prospect["validation_score"] = score
                    prospect["status"] = "Invalide"
                    
            except Exception as e:
                logger.error(f"Erreur lors de la validation de l'email {prospect['email']}: {e}")
                prospect["validation_score"] = 0.0
                prospect["status"] = "Erreur"
        
        logger.info(f"Validation terminée: {len(valid_prospects)} emails valides sur {len(prospects)}")
        return valid_prospects
    
    def validate_email(self, email):
        """Valide un email individuel"""
        try:
            url = f"https://emailvalidation.abstractapi.com/v1/?api_key={self.api_key}&email={email}"
            response = requests.get(url)
            result = response.json()
            
            is_valid = result.get('deliverability') == "DELIVERABLE"
            score = result.get('quality_score', 0.0)
            
            return is_valid, score
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'email {email}: {e}")
            return False, 0.0
