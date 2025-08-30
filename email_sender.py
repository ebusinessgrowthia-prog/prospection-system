import sendgrid
from sendgrid.helpers.mail import Mail
import logging
from config import SENDGRID_API_KEY, UNSUBSCRIBE_LINK

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    
    def send_email(self, to_email, subject, content, from_email, from_name):
        """Envoie un email via SendGrid"""
        try:
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content.replace('\n', '<br>')
            )
            
            # Ajouter le lien de désinscription
            message.add_custom_arg('unsubscribe_link', UNSUBSCRIBE_LINK)
            
            response = self.sg.client.mail.send.post(request_body=message.get())
            
            if response.status_code == 202:
                logger.info(f"Email envoyé avec succès à {to_email}")
                return True
            else:
                logger.error(f"Échec de l'envoi à {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {e}")
            return False
    
    def check_daily_limits(self):
        """Vérifie les limites d'envoi quotidiennes"""
        try:
            # Obtenir les statistiques d'envoi du jour
            today = datetime.now().strftime('%Y-%m-%d')
            response = self.sg.client.stats.get(query_params={
                'start_date': today,
                'end_date': today
            })
            
            stats = response.to_dict()
            delivered = stats.get('stats', [{}])[0].get('metrics', {}).get('delivered', 0)
            
            # Retourner les informations sur les limites
            return {
                'delivered_today': delivered,
                'remaining': max(0, 100 - delivered)  # Limite SendGrid gratuite
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des limites: {e}")
            return {'delivered_today': 0, 'remaining': 100}
