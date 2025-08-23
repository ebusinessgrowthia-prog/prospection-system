import sendgrid
from sendgrid.helpers.mail import Mail, Email, Content, Personalization
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, api_key: str, from_email: str, from_name: str):
        """Initialize SendGrid email sender"""
        self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        self.from_email = from_email
        self.from_name = from_name
        
    def send_single_email(self, to_email: str, subject: str, html_content: str, 
                         unsubscribe_url: str = None) -> Dict[str, Any]:
        """Send a single email"""
        try:
            # Create mail object
            mail = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add unsubscribe link if provided
            if unsubscribe_url:
                mail.add_custom_arg('unsubscribe_url', unsubscribe_url)
                
            # Send email
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_bulk_emails(self, recipients: List[Dict[str, Any]], 
                        template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send bulk emails with personalization"""
        results = []
        
        for recipient in recipients:
            try:
                # Personalize content
                personalized_content = self._personalize_content(
                    template_data['html_content'], 
                    recipient
                )
                
                # Send individual email
                result = self.send_single_email(
                    to_email=recipient['email'],
                    subject=template_data['subject'],
                    html_content=personalized_content,
                    unsubscribe_url=recipient.get('unsubscribe_url')
                )
                
                result['recipient'] = recipient['email']
                results.append(result)
                
            except Exception as e:
                results.append({
                    'success': False,
                    'recipient': recipient['email'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
        return results
    
    def _personalize_content(self, template: str, recipient: Dict[str, Any]) -> str:
        """Personalize email content with recipient data"""
        content = template
        
        # Replace placeholders
        placeholders = {
            '{{nom}}': recipient.get('nom_complet', '').split()[0] if recipient.get('nom_complet') else 'Cher client',
            '{{entreprise}}': recipient.get('entreprise', 'votre entreprise'),
            '{{secteur}}': recipient.get('secteur', 'votre secteur'),
            '{{url_site}}': recipient.get('url_site', ''),
            '{{date}}': datetime.now().strftime('%d/%m/%Y')
        }
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))
            
        return content
    
    def create_email_template(self, agence_info: Dict[str, Any], 
                            prospect_data: Dict[str, Any]) -> Dict[str, str]:
        """Create email template based on agence and prospect data"""
        subject = f"Boostez votre {prospect_data.get('secteur', 'activité')} avec notre expertise"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Bonjour {{nom}},</h2>
                
                <p>
                    J'ai remarqué que <strong>{{entreprise}}</strong> pourrait bénéficier 
                    de notre expertise en {agence_info.get('secteur', 'marketing digital')}.
                </p>
                
                <p>
                    Nous avons aidé des entreprises similaires à augmenter leurs résultats 
                    de manière significative grâce à nos stratégies personnalisées.
                </p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Ce que nous proposons :</h3>
                    <ul>
                        <li>Analyse gratuite de votre présence en ligne</li>
                        <li>Stratégie personnalisée selon vos objectifs</li>
                        <li>Accompagnement complet jusqu'aux résultats</li>
                    </ul>
                </div>
                
                <p>
                    Seriez-vous ouvert à un appel découverte de 15 minutes cette semaine ?
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://calendly.com/votre-agence" 
                       style="background: #3498db; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Réserver un appel gratuit
                    </a>
                </div>
                
                <p>
                    Au plaisir d'échanger,<br>
                    <strong>{agence_info.get('nom_agence', 'Votre agence')}</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    <a href="{{unsubscribe_url}}" style="color: #666;">
                        Se désinscrire de ces emails
                    </a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return {
            'subject': subject,
            'html_content': html_content
        }
    
    def check_email_limits(self) -> Dict[str, Any]:
        """Check daily email limits"""
        try:
            # Get SendGrid stats
            today = datetime.now().strftime('%Y-%m-%d')
            response = self.sg.client.stats.get(query_params={
                'start_date': today,
                'end_date': today
            })
            
            stats = response.to_dict()
            return {
                'daily_sent': stats.get('stats', [{}])[0].get('metrics', {}).get('delivered', 0),
                'daily_limit': 100,  # SendGrid free tier
                'remaining': max(0, 100 - stats.get('stats', [{}])[0].get('metrics', {}).get('delivered', 0))
            }
            
        except Exception as e:
            logger.error(f"Error checking email limits: {e}")
            return {
                'daily_sent': 0,
                'daily_limit': 100,
                'remaining': 100
            }
    
    def track_email_events(self, message_id: str) -> Dict[str, Any]:
        """Track email events (opens, clicks, etc.)"""
        try:
            response = self.sg.client.messages._(message_id).get()
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"Error tracking email {message_id}: {e}")
            return {'error': str(e)}