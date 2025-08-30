from flask import Flask, request, jsonify
import os
import json
import time
import logging
from datetime import datetime, timedelta

from config import *
from google_sheets_manager import GoogleSheetsManager
from google_dorks_generator import GoogleDorksGenerator
from web_scraper import WebScraper
from email_validator import EmailValidator
from ai_email_writer import AIEmailWriter
from email_sender import EmailSender
from performance_tracker import PerformanceTracker

# Configuration logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ProspectionOrchestrator:
    def __init__(self):
        self.google_sheets = GoogleSheetsManager()
        self.dorks_generator = GoogleDorksGenerator()
        self.scraper = WebScraper()
        self.email_validator = EmailValidator()
        self.ai_writer = AIEmailWriter()
        self.email_sender = EmailSender()
        self.performance_tracker = PerformanceTracker()
        
        # Initialiser Google Sheets
        self.google_sheets.initialize_sheets()
        
        # Pas de threading pour simplifier
        logger.info("Système initialisé - prêt pour les campagnes manuelles")
    
    def run_agency_campaign(self, agency_name, config):
        """Exécute une campagne pour une agence spécifique"""
        logger.info(f"Démarrage de la campagne pour {agency_name}")
        
        # Générer les Google Dorks
        dorks = self.dorks_generator.generate_dorks(config)
        
        # Scraper les prospects
        prospects = self.scraper.scrape_prospects(dorks, config)
        
        # Valider les emails
        valid_prospects = self.email_validator.validate_emails(prospects)
        
        # Stocker les prospects dans Google Sheets
        self.google_sheets.store_prospects(valid_prospects, agency_name)
        
        # Générer et envoyer les emails
        emails_sent = self.send_campaign_emails(valid_prospects, agency_name, config)
        
        # Suivre les performances
        self.performance_tracker.track_campaign(agency_name, emails_sent)
        
        logger.info(f"Campagne terminée pour {agency_name}: {emails_sent} emails envoyés")
    
    def send_campaign_emails(self, prospects, agency_name, config):
        """Génère et envoie les emails pour une campagne"""
        emails_sent = 0
        
        for prospect in prospects[:config["max_emails_jour"]]:
            try:
                # Générer l'email avec l'IA
                email_content = self.ai_writer.generate_email(
                    prospect, 
                    agency_name, 
                    config,
                    PLAN_MESSAGE
                )
                
                # Envoyer l'email
                sent = self.email_sender.send_email(
                    to_email=prospect["email"],
                    subject=self.ai_writer.generate_subject(prospect, agency_name),
                    content=email_content,
                    from_email=config["email_expediteur"],
                    from_name=config["nom"]
                )
                
                if sent:
                    emails_sent += 1
                    # Enregistrer l'email envoyé
                    self.google_sheets.store_email_sent(
                        prospect["email"], 
                        agency_name, 
                        email_content
                    )
                
                # Respecter les limites d'envoi
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email à {prospect['email']}: {e}")
        
        return emails_sent

# Routes API
@app.route('/')
def home():
    return jsonify({
        "status": "Système de prospection actif",
        "agences": list(AGENCES_CONFIG.keys()),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint pour recevoir les webhooks"""
    try:
        data = request.json
        agency_name = data.get("agency")
        
        if agency_name in AGENCES_CONFIG:
            orchestrator.run_agency_campaign(agency_name, AGENCES_CONFIG[agency_name])
            return jsonify({"status": "success", "message": f"Campagne lancée pour {agency_name}"})
        else:
            return jsonify({"status": "error", "message": "Agence non trouvée"}), 404
            
    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run-campaign/<agency_name>', methods=['POST'])
def run_campaign(agency_name):
    """Lance une campagne pour une agence spécifique"""
    try:
        if agency_name in AGENCES_CONFIG:
            orchestrator.run_agency_campaign(agency_name, AGENCES_CONFIG[agency_name])
            return jsonify({"status": "success", "message": f"Campagne lancée pour {agency_name}"})
        else:
            return jsonify({"status": "error", "message": "Agence non trouvée"}), 404
    except Exception as e:
        logger.error(f"Erreur lors du lancement de la campagne: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    """Endpoint de santé"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agences": len(AGENCES_CONFIG)
    })

# Initialisation
if __name__ == "__main__":
    orchestrator = ProspectionOrchestrator()
    app.run(host='0.0.0.0', port=PORT, debug=FLASK_ENV == 'development')
