#!/usr/bin/env python3
"""
Système complet d'automatisation de prospection
Orchestre tous les nœuds du workflow décrit
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import schedule
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import des modules
from config import *
from gemini_integration import GeminiIntegration
from web_scraper import WebScraper
from email_validator import EmailValidator
from google_sheets_manager import GoogleSheetsManager
from email_sender import EmailSender

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

class ProspectionOrchestrator:
    def __init__(self):
        """Initialize the complete prospection system"""
        self.gemini = GeminiIntegration(GEMINI_API_KEY)
        self.scraper = WebScraper(delay=REQUEST_DELAY)
        self.validator = EmailValidator(
            abstract_api_key=ABSTRACT_API_KEY,
            hunter_api_key=HUNTER_API_KEY
        )
        self.sheets = GoogleSheetsManager(
            GOOGLE_SHEETS_CREDENTIALS_FILE,
            GOOGLE_SHEETS_SPREADSHEET_NAME
        )
        self.email_sender = EmailSender(
            SENDGRID_API_KEY,
            FROM_EMAIL,
            FROM_NAME
        )
        
        # Initialize Google Sheets
        self._initialize_sheets()
        
    def _initialize_sheets(self):
        """Initialize Google Sheets with proper schema"""
        from google_sheets_schema import GOOGLE_SHEETS_SCHEMA
        self.sheets.create_worksheets(GOOGLE_SHEETS_SCHEMA)
        logger.info("Google Sheets initialized successfully")
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nœud 1 & 2: Recevoir et organiser les données du webhook
        """
        logger.info("Processing webhook data")
        
        # Organiser les données
        organized_data = self._organize_webhook_data(webhook_data)
        
        # Générer les Dorks
        dorks = self.gemini.generate_dorks(organized_data)
        
        # Lancer le processus de prospection
        results = self._run_prospection_campaign(organized_data, dorks)
        
        return {
            'status': 'success',
            'campaign_id': str(datetime.now().timestamp()),
            'dorks_generated': len(dorks),
            'results': results
        }
    
    def _organize_webhook_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Organiser les données du webhook pour les différents nœuds"""
        return {
            'agence_info': {
                'nom_agence': data.get('nom_agence'),
                'secteur': data.get('secteur'),
                'cible_principale': data.get('cible_principale'),
                'objectifs': data.get('objectifs_prospection', []),
                'style': data.get('style_prospection', {}),
                'localisation': data.get('localisation', 'France'),
                'langue': data.get('langue', 'fr')
            },
            'scraping_params': {
                'max_results': MAX_PROSPECTS_PER_DORK,
                'max_dorks': MAX_DORKS_PER_CAMPAIGN
            },
            'validation_params': {
                'threshold': EMAIL_VALIDATION_THRESHOLD
            }
        }
    
    def _run_prospection_campaign(self, agence_data: Dict[str, Any], dorks: List[str]) -> Dict[str, Any]:
        """Exécuter la campagne de prospection complète"""
        logger.info("Starting prospection campaign")
        
        results = {
            'dorks_used': dorks,
            'prospects_found': 0,
            'emails_validated': 0,
            'emails_sent': 0,
            'errors': []
        }
        
        try:
            # Nœud A & B: Scraping avec les Dorks
            prospects = self._scrape_prospects(dorks, agence_data)
            results['prospects_found'] = len(prospects)
            
            # Nœud C: Validation des emails
            validated_prospects = self._validate_prospects(prospects)
            results['emails_validated'] = len(validated_prospects)
            
            # Nœud D: Stockage dans Google Sheets
            self._store_prospects(validated_prospects)
            
            # Nœud E & F: Analyse et rédaction personnalisée
            personalized_emails = self._create_personalized_emails(
                validated_prospects, 
                agence_data['agence_info']
            )
            
            # Nœud G: Envoi des emails
            sent_count = self._send_emails(personalized_emails, agence_data['agence_info'])
            results['emails_sent'] = sent_count
            
            # Nœud H: Mise à jour des métriques
            self._update_performance_metrics(results)
            
        except Exception as e:
            logger.error(f"Error in prospection campaign: {e}")
            results['errors'].append(str(e))
            
        return results
    
    def _scrape_prospects(self, dorks: List[str], agence_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Nœud A & B: Scraping des prospects"""
        logger.info(f"Scraping prospects with {len(dorks)} dorks")
        
        all_prospects = []
        max_per_dork = agence_data['scraping_params']['max_results']
        
        for dork in dorks[:agence_data['scraping_params']['max_dorks']]:
            prospects = self.scraper.scrape_from_dork(dork, max_per_dork)
            for prospect in prospects:
                prospect['dork_used'] = dork
                prospect['campaign_id'] = str(datetime.now().timestamp())
            all_prospects.extend(prospects)
            
        # Dédoublonnage
        unique_prospects = self.scraper.deduplicate_prospects(all_prospects)
        logger.info(f"Found {len(unique_prospects)} unique prospects")
        
        return unique_prospects
    
    def _validate_prospects(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Nœud C: Validation des emails"""
        logger.info("Validating prospect emails")
        
        validated_prospects = []
        emails_to_validate = [p['email'] for p in prospects]
        
        validation_results = self.validator.batch_validate(emails_to_validate)
        
        for prospect, validation in zip(prospects, validation_results):
            if validation['is_valid'] and validation['score'] >= EMAIL_VALIDATION_THRESHOLD:
                prospect.update({
                    'score_validation': validation['score'],
                    'statut_validation': 'VALID',
                    'validation_details': validation
                })
                validated_prospects.append(prospect)
                
        logger.info(f"Validated {len(validated_prospects)} prospects")
        return validated_prospects
    
    def _store_prospects(self, prospects: List[Dict[str, Any]]):
        """Nœud D: Stockage dans Google Sheets"""
        logger.info("Storing prospects in Google Sheets")
        
        for prospect in prospects:
            self.sheets.add_prospect(prospect)
    
    def _create_personalized_emails(self, prospects: List[Dict[str, Any]], 
                                  agence_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Nœud E & F: Analyse et rédaction personnalisée"""
        logger.info("Creating personalized emails")
        
        personalized_emails = []
        
        for prospect in prospects:
            # Analyse du prospect
            analysis = self.gemini.analyze_prospect(prospect)
            
            # Génération de l'email personnalisé
            email_content = self.gemini.generate_personalized_email(
                analysis, agence_info, prospect
            )
            
            personalized_emails.append({
                'prospect': prospect,
                'analysis': analysis,
                'email_content': email_content
            })
            
        return personalized_emails
    
    def _send_emails(self, personalized_emails: List[Dict[str, Any]], 
                    agence_info: Dict[str, Any]) -> int:
        """Nœud G: Envoi des emails"""
        logger.info("Sending personalized emails")
        
        # Vérifier les limites
        limits = self.email_sender.check_email_limits()
        remaining = limits.get('remaining', 100)
        
        emails_to_send = personalized_emails[:remaining]
        sent_count = 0
        
        for email_data in emails_to_send:
            prospect = email_data['prospect']
            email_content = email_data['email_content']
            
            # Créer le template d'email
            template = self.email_sender.create_email_template(agence_info, prospect)
            
            # Envoyer l'email
            result = self.email_sender.send_single_email(
                to_email=prospect['email'],
                subject=email_content.get('objet', template['subject']),
                html_content=email_content.get('corps', template['html_content']),
                unsubscribe_url=UNSUBSCRIBE_LINK
            )
            
            if result['success']:
                sent_count += 1
                
                # Stocker l'email envoyé
                self.sheets.add_email_record({
                    'prospect_id': prospect.get('id', ''),
                    'objet': email_content.get('objet', ''),
                    'corps': email_content.get('corps', ''),
                    'statut': 'SENT',
                    'variant': 'A'
                })
                
                # Mettre à jour le statut du prospect
                self.sheets.update_prospect_status(
                    prospect['email'], 
                    'CONTACTED',
                    f"Email envoyé le {datetime.now().isoformat()}"
                )
                
        logger.info(f"Sent {sent_count} emails")
        return sent_count
    
    def _update_performance_metrics(self, results: Dict[str, Any]):
        """Nœud H: Mise à jour des métriques de performance"""
        logger.info("Updating performance metrics")
        
        metrics = {
            'campagnes_envoyees': 1,
            'emails_envoyes': results['emails_sent'],
            'nouveaux_prospects': results['prospects_found'],
            'prospects_valides': results['emails_validated'],
            'taux_ouverture': 0,  # Sera mis à jour via webhooks
            'taux_clic': 0,
            'taux_reponse': 0,
            'taux_bounce': 0
        }
        
        self.sheets.update_performance_metrics(metrics)
    
    def run_daily_optimization(self):
        """Optimisation quotidienne basée sur les performances"""
        logger.info("Running daily optimization")
        
        # Récupérer les statistiques
        stats = self.sheets.get_daily_stats()
        
        if stats:
            # Optimiser avec Gemini
            optimization = self.gemini.optimize_campaign(stats)
            
            # Stocker les recommandations
            self.sheets.update_performance_metrics({
                'optimisation': optimization
            })
    
    def schedule_daily_runs(self):
        """Planifier les exécutions quotidiennes"""
        schedule.every().day.at("09:00").do(self.run_daily_optimization)
        logger.info("Daily optimization scheduled for 09:00")

# API Flask pour le webhook
app = Flask(__name__)
CORS(app)

orchestrator = ProspectionOrchestrator()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint webhook pour recevoir les campagnes"""
    try:
        data = request.json
        result = orchestrator.process_webhook(data)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/stats', methods=['GET'])
def stats():
    """Obtenir les statistiques"""
    try:
        stats = orchestrator.sheets.get_daily_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Démarrer le scheduler
    orchestrator.schedule_daily_runs()
    
    # Démarrer l'application Flask
    app.run(host='0.0.0.0', port=5000, debug=True)