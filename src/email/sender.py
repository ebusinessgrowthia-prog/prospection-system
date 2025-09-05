"""
Email Sender pour EBUSINESS AI
Envoi d'emails personnalisés avec tracking et gestion des horaires
"""

import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import ssl
import time
import threading
from jinja2 import Template

from src.config import get_config
from src.core.models import EmailSendingResult, EmailCampaignData
from src.core.utils import (
    validate_email_address, generate_tracking_id, 
    is_business_hours, get_next_business_hour, generate_random_delay
)

logger = logging.getLogger(__name__)
config = get_config()

class EmailSender:
    """Gestionnaire d'envoi d'emails avec tracking et respect des horaires"""

    def __init__(self):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.email_address = config.email_address
        self.email_password = config.email_password
        self.max_emails_per_day = config.max_emails_per_day
        self.delay_between_emails = config.delay_between_emails
        
        # Compteurs pour le suivi
        self.emails_sent_today = 0
        self.last_reset_date = datetime.now().date()
        
        # Verrou pour le thread-safe
        self.send_lock = threading.Lock()
        
        # Templates Jinja2
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Template]:
        """Charge les templates email"""
        templates = {}
        
        # Template HTML par défaut
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .content { margin-bottom: 30px; }
                .cta { 
                    display: inline-block; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 25px; 
                    font-weight: bold;
                }
                .footer { 
                    margin-top: 30px; 
                    padding-top: 20px; 
                    border-top: 1px solid #eee; 
                    font-size: 12px; 
                    color: #666; 
                }
                .tracking-pixel { width: 1px; height: 1px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 EBUSINESS AI</h1>
                </div>
                <div class="content">
                    {{ content | safe }}
                    <br><br>
                    <center>
                        <a href="{{ cta_url }}" class="cta">{{ cta_text }}</a>
                    </center>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé par {{ company_name }} - {{ your_name }}</p>
                    <p>{{ your_title }} | {{ your_location }}</p>
                    <p><a href="{{ unsubscribe_url }}">Se désabonner</a></p>
                    <img src="{{ tracking_pixel_url }}" class="tracking-pixel" alt="">
                </div>
            </div>
        </body>
        </html>
        """
        
        templates['default'] = Template(html_template)
        
        return templates

    def send_personalized_email(self, prospect_data: Dict[str, Any], email_content: str) -> EmailSendingResult:
        """
        Envoie un email personnalisé à un prospect
        
        Args:
            prospect_data: Données du prospect
            email_content: Contenu de l'email
            
        Returns:
            EmailSendingResult: Résultat de l'envoi
        """
        try:
            prospect_id = prospect_data.get('id', 0)
            recipient_email = prospect_data.get('email', '')
            
            if not recipient_email:
                return EmailSendingResult(
                    success=False,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    error="Email du prospect manquant"
                )
            
            if not validate_email_address(recipient_email):
                return EmailSendingResult(
                    success=False,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    error="Email invalide"
                )
            
            # Vérifier les horaires d'envoi
            if not is_business_hours():
                next_hour = get_next_business_hour()
                return EmailSendingResult(
                    success=False,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    error=f"Hors horaires de bureau. Prochain envoi à {next_hour.strftime('%H:%M')}"
                )
            
            # Vérifier la limite quotidienne
            if not self._check_daily_limit():
                return EmailSendingResult(
                    success=False,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    error="Limite quotidienne d'emails atteinte"
                )
            
            # Générer le tracking ID
            tracking_id = generate_tracking_id()
            
            # Préparer l'email
            subject = f"Opportunités pour {prospect_data.get('company', 'votre entreprise')}"
            
            # Créer le message
            message = self._create_email_message(
                recipient_email=recipient_email,
                subject=subject,
                content=email_content,
                tracking_id=tracking_id,
                prospect_data=prospect_data
            )
            
            # Envoyer l'email
            message_id = self._send_email_message(message, recipient_email)
            
            if message_id:
                # Enregistrer la campagne
                self._record_email_campaign(prospect_id, subject, email_content, tracking_id)
                
                # Mettre à jour les compteurs
                with self.send_lock:
                    self.emails_sent_today += 1
                
                logger.info(f"✅ Email envoyé avec succès à {recipient_email} (ID: {message_id})")
                
                return EmailSendingResult(
                    success=True,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    message_id=message_id,
                    sent_at=datetime.now()
                )
            else:
                return EmailSendingResult(
                    success=False,
                    prospect_id=prospect_id,
                    email_address=recipient_email,
                    error="Échec de l'envoi de l'email"
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de l'email au prospect {prospect_data.get('id', 0)}: {e}")
            return EmailSendingResult(
                success=False,
                prospect_id=prospect_data.get('id', 0),
                email_address=prospect_data.get('email', ''),
                error=str(e)
            )

    def _create_email_message(self, recipient_email: str, subject: str, content: str, 
                            tracking_id: str, prospect_data: Dict[str, Any]) -> MIMEMultipart:
        """
        Crée un message email avec tracking
        
        Args:
            recipient_email: Email du destinataire
            subject: Sujet de l'email
            content: Contenu de l'email
            tracking_id: ID de tracking
            prospect_data: Données du prospect
            
        Returns:
            MIMEMultipart: Message email prêt à envoyer
        """
        # Créer le message multipart
        message = MIMEMultipart('alternative')
        
        # Headers
        message['Subject'] = subject
        message['From'] = formataddr((f"{config.company_name}", self.email_address))
        message['To'] = recipient_email
        message['Reply-To'] = self.email_address
        message['Message-ID'] = f"<{tracking_id}@{config.company_name.lower().replace(' ', '')}>"
        
        # Préparer les URLs de tracking
        tracking_pixel_url = f"{config.landing_page_url}/track/open/{tracking_id}"
        cta_url = f"{config.landing_page_url}/track/click/{tracking_id}"
        
        # Préparer le contenu HTML
        html_content = self.templates['default'].render(
            subject=subject,
            content=content.replace('\n', '<br>'),
            cta_url=cta_url,
            cta_text="🚀 Découvre comment exploiter tes données e-commerce",
            company_name=config.company_name,
            your_name=config.your_name,
            your_title=config.your_title,
            your_location=config.your_location,
            unsubscribe_url=f"{config.landing_page_url}/unsubscribe/{tracking_id}",
            tracking_pixel_url=tracking_pixel_url
        )
        
        # Version texte brute
        text_content = f"""
{content}

🚀 Découvre comment exploiter tes données e-commerce: {cta_url}

---
Cet email a été envoyé par {config.company_name} - {config.your_name}
{config.your_title} | {config.your_location}
Pour vous désabonner: {config.landing_page_url}/unsubscribe/{tracking_id}
        """
        
        # Attacher les parties texte et HTML
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        return message

    def _send_email_message(self, message: MIMEMultipart, recipient_email: str) -> Optional[str]:
        """
        Envoie le message email via SMTP
        
        Args:
            message: Message à envoyer
            recipient_email: Email du destinataire
            
        Returns:
            Optional[str]: ID du message si succès, None sinon
        """
        try:
            # Créer le contexte SSL
            context = ssl.create_default_context()
            
            # Se connecter au serveur SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                
                # Envoyer l'email
                response = server.send_message(message)
                
                # Extraire l'ID du message de la réponse
                if response:
                    return response.split()[1].strip('<>')
                
                return str(int(time.time()))  # ID basé sur le timestamp
                
        except Exception as e:
            logger.error(f"❌ Erreur SMTP: {e}")
            return None

    def _check_daily_limit(self) -> bool:
        """Vérifie si la limite quotidienne n'est pas atteinte"""
        today = datetime.now().date()
        
        # Réinitialiser le compteur si c'est un nouveau jour
        if today != self.last_reset_date:
            with self.send_lock:
                self.emails_sent_today = 0
                self.last_reset_date = today
        
        return self.emails_sent_today < self.max_emails_per_day

    def _record_email_campaign(self, prospect_id: int, subject: str, content: str, tracking_id: str):
        """
        Enregistre la campagne email dans la base de données
        
        Args:
            prospect_id: ID du prospect
            subject: Sujet de l'email
            content: Contenu de l'email
            tracking_id: ID de tracking
        """
        try:
            from src.core.database import db_manager
            
            campaign_data = EmailCampaignData(
                prospect_id=prospect_id,
                subject=subject,
                content=content,
                tracking_id=tracking_id
            )
            
            db_manager.add_email_campaign(campaign_data.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement de la campagne: {e}")

    def send_batch_emails(self, email_data_list: List[Dict[str, Any]]) -> List[EmailSendingResult]:
        """
        Envoie plusieurs emails en respectant les délais et limites
        
        Args:
            email_data_list: Liste des données d'emails à envoyer
            
        Returns:
            List[EmailSendingResult]: Résultats des envois
        """
        results = []
        
        for email_data in email_data_list:
            try:
                # Vérifier les horaires
                if not is_business_hours():
                    result = EmailSendingResult(
                        success=False,
                        prospect_id=email_data.get('prospect_id', 0),
                        email_address=email_data.get('email', ''),
                        error="Hors horaires de bureau"
                    )
                    results.append(result)
                    continue
                
                # Envoyer l'email
                result = self.send_personalized_email(
                    prospect_data=email_data,
                    email_content=email_data['content']
                )
                results.append(result)
                
                # Délai entre les emails
                if email_data != email_data_list[-1]:  # Pas de délai pour le dernier
                    delay = generate_random_delay(
                        self.delay_between_emails - 10,
                        self.delay_between_emails + 10
                    )
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi batch: {e}")
                result = EmailSendingResult(
                    success=False,
                    prospect_id=email_data.get('prospect_id', 0),
                    email_address=email_data.get('email', ''),
                    error=str(e)
                )
                results.append(result)
        
        return results

    def get_daily_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques quotidiennes d'envoi
        
        Returns:
            Dict[str, Any]: Statistiques quotidiennes
        """
        return {
            'emails_sent_today': self.emails_sent_today,
            'daily_limit': self.max_emails_per_day,
            'remaining_emails': max(0, self.max_emails_per_day - self.emails_sent_today),
            'last_reset': self.last_reset_date.isoformat(),
            'is_business_hours': is_business_hours(),
            'next_business_hour': get_next_business_hour().isoformat()
        }

# Instance globale de l'envoyeur
email_sender = EmailSender()

# Fonction pour l'import facile
def send_email_to_prospect(prospect_data: Dict[str, Any], email_content: str) -> EmailSendingResult:
    """
    Fonction wrapper pour l'envoi d'email à un prospect
    
    Args:
        prospect_data: Données du prospect
        email_content: Contenu de l'email
        
    Returns:
        EmailSendingResult: Résultat de l'envoi
    """
    return email_sender.send_personalized_email(prospect_data, email_content)
