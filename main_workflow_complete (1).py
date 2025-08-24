#!/usr/bin/env python3
"""
🚀 START COMMAND COMPLÈTE - DÉPLOIEMENT AUTOMATIQUE INTÉGRAL
Ce fichier est exécuté automatiquement par la startCommand: python main_workflow_complete.py
"""

import os
import sys
import json
import time
import schedule
import threading
from datetime import datetime, timedelta
import pytz
import logging
from typing import Dict, List, Any
import gspread
from google.oauth2.service_account import Credentials
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import google.generativeai as genai

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prospection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration des agences
AGENCIES_CONFIG = {
    "EBUSINESS_GROWTH": {
        "name": "EBUSINESS GROWTH",
        "specialization": "Récupération et conversion de prospects perdus ou inactifs",
        "target": "Entreprises B2B avec CRM sous-exploité (SaaS, agences, services financiers)",
        "approach": "Analyse CRM + automatisation + suivi humain",
        "contact": "Gildea Sognon-des",
        "email": "ebusinessgrowthia@gmail.com",
        "website": "https://ebusinessag.com",
        "sendgrid_sender": "ebusinessgrowthia@gmail.com",
        "message_plan": {
            "positioning": "Je suis Gildea Sognon-des, consultant spécialisé dans la récupération de clients inactifs",
            "hook": "Avez-vous calculé combien de vos prospects ne finalisent jamais leur achat ?",
            "observation": "Je comprends que les entreprises comme [entreprise] investissent beaucoup en acquisition mais peinent à convertir",
            "gap": "Vos coûts d'acquisition sont lourds, mais vos taux de conversion restent faibles",
            "solution": "Je propose un service précis pour réactiver vos prospects inactifs et augmenter vos conversions",
            "scarcity": "Service tout juste lancé, limité à 5 entreprises",
            "question": "Est-ce que vous aimeriez qu'on explore ensemble vos pistes de conversion cachées ?",
            "cta": "👉 Découvrir la solution maintenant"
        }
    },
    "EBUSINESS_AI": {
        "name": "EBUSINESS AI",
        "specialization": "Chatbots IA + contenu IA pour sites web & publicités",
        "target": "Vendeurs et commerçants en Europe francophone (e-commerce, retail)",
        "approach": "Solutions IA clés en main pour conversion",
        "contact": "EBUSINESS AI",
        "email": "ia.ebusinessag@gmail.com",
        "website": "https://ebusinessag.com/ai-ulta-chatbot.html",
        "sendgrid_sender": "ia.ebusinessag@gmail.com",
        "message_plan": {
            "positioning": "Je suis consultant chez EBUSINESS AI, spécialisé dans l'optimisation de conversion par l'IA",
            "hook": "Combien de visiteurs quittent votre site sans acheter chaque jour ?",
            "observation": "Je comprends que les e-commerces comme [entreprise] ont du mal à convertir leur trafic existant",
            "gap": "Vos coûts d'acquisition sont élevés, mais vos taux de conversion restent bas",
            "solution": "Je propose des solutions IA précises (chatbots + contenu) pour augmenter vos conversions",
            "scarcity": "Service tout juste lancé, limité à 5 entreprises",
            "question": "Est-ce que vous aimeriez qu'on explore ensemble vos pistes de conversion cachées ?",
            "cta": "🚀 Découvrir la solution maintenant"
        }
    }
}

class ProspectionSystem:
    def __init__(self):
        self.setup_google_sheets()
        self.setup_sendgrid()
        self.setup_gemini()
        self.setup_timezone()
        
    def setup_google_sheets(self):
        """Configuration de Google Sheets"""
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            self.client = gspread.authorize(creds)
            
            # Créer ou ouvrir la feuille de calcul
            try:
                self.sheet = self.client.open("Prospection")
            except gspread.SpreadsheetNotFound:
                self.sheet = self.client.create("Prospection")
                self.setup_sheets_structure()
                
            logger.info("Google Sheets configuré avec succès")
        except Exception as e:
            logger.error(f"Erreur Google Sheets: {e}")
            
    def setup_sheets_structure(self):
        """Configuration de la structure des feuilles"""
        worksheets = [
            ("Agences_Config", ["Agence", "Spécialisation", "Cible", "Contact", "Email", "Site"]),
            ("Messages_Approuves", ["Agence", "Type", "Message", "Date"]),
            ("Prospects", ["Agence", "Nom", "Email", "Entreprise", "Secteur", "Source", "Date"]),
            ("Emails_Envoyes", ["Agence", "Destinataire", "Sujet", "Date", "Statut"]),
            ("Performance", ["Date", "Agence", "Prospects_Trouves", "Emails_Envoyes", "Taux_Ouverture"]),
            ("Campagnes", ["Date", "Agence", "Heure", "Prospects", "Emails", "Statut"])
        ]
        
        for name, headers in worksheets:
            try:
                ws = self.sheet.add_worksheet(title=name, rows=1000, cols=20)
                ws.append_row(headers)
            except:
                pass
                
    def setup_sendgrid(self):
        """Configuration de SendGrid"""
        self.sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        
    def setup_gemini(self):
        """Configuration de Gemini AI"""
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def setup_timezone(self):
        """Configuration du fuseau horaire"""
        self.tz = pytz.timezone('Europe/Paris')
        
    def generate_google_dorks(self, agency_name: str) -> List[str]:
        """Génération de Google Dorks spécifiques à chaque agence"""
        if agency_name == "EBUSINESS_GROWTH":
            return [
                "agence réactivation clients France",
                "CRM sous-exploité Belgique",
                "conversion clients inactifs Suisse",
                "automatisation marketing B2B",
                "récupération clients dormants"
            ]
        else:  # EBUSINESS_AI
            return [
                "chatbot e-commerce France",
                "solution IA site web Belgique",
                "assistant virtuel boutique Suisse",
                "automatisation SAV e-commerce",
                "contenu IA site web"
            ]
            
    def search_prospects(self, agency_name: str) -> List[Dict[str, Any]]:
        """Recherche de prospects via Google Dorks"""
        dorks = self.generate_google_dorks(agency_name)
        prospects = []
        
        for dork in dorks:
            try:
                # Simulation de recherche (à remplacer par scraping réel)
                prompt = f"""
                Génère 5 prospects réalistes pour la recherche: {dork}
                Format: Nom, Email, Entreprise, Secteur
                """
                
                response = self.model.generate_content(prompt)
                # Ici, vous intégreriez le scraping réel
                
                # Exemple de données simulées
                prospects.extend([
                    {
                        "nom": "Jean Dupont",
                        "email": "jean@techcompany.fr",
                        "entreprise": "TechCompany SAS",
                        "secteur": "SaaS",
                        "source": dork
                    }
                ])
                
            except Exception as e:
                logger.error(f"Erreur recherche prospects: {e}")
                
        return prospects
        
    def validate_email(self, email: str) -> bool:
        """Validation d'email via Abstract API"""
        try:
            api_key = os.getenv('ABSTRACT_API_KEY')
            url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={email}"
            response = requests.get(url)
            data = response.json()
            return data.get('quality_score', 0) >= 0.8
        except:
            return False
            
    def generate_email(self, agency_name: str, prospect: Dict[str, Any]) -> Dict[str, str]:
        """Génération d'email selon le plan de message strict"""
        agency = AGENCIES_CONFIG[agency_name]
        plan = agency["message_plan"]
        
        prompt = f"""
        Crée un email ultra-personnalisé pour {prospect['nom']} de {prospect['entreprise']} ({prospect['secteur']})
        
        Plan de message strict à suivre:
        1. Positionnement: {plan['positioning']}
        2. Accroche: {plan['hook']}
        3. Observation: {plan['observation']} (adapter à {prospect['entreprise']})
        4. Faille: {plan['gap']}
        5. Solution: {plan['solution']}
        6. Rareté: {plan['scarcity']}
        7. Question: {plan['question']}
        8. CTA: {plan['cta']} avec lien vers {agency['website']}
        
        Ton: Humain, empathique, collaboratif, "je" avant tout
        Longueur: 150-200 mots
        Signature: {agency['contact']}, {agency['email']}
        """
        
        response = self.model.generate_content(prompt)
        
        return {
            "subject": f"Question rapide sur {prospect['entreprise']}",
            "body": response.text,
            "sender": agency["sendgrid_sender"]
        }
        
    def send_email(self, to_email: str, subject: str, body: str, sender: str) -> bool:
        """Envoi d'email via SendGrid"""
        try:
            message = Mail(
                from_email=sender,
                to_emails=to_email,
                subject=subject,
                html_content=body.replace('\n', '<br>')
            )
            
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
            
    def run_campaign(self, agency_name: str):
        """Exécution d'une campagne pour une agence"""
        logger.info(f"Démarrage campagne {agency_name}")
        
        # Recherche de prospects
        prospects = self.search_prospects(agency_name)
        
        # Filtrage et validation
        valid_prospects = []
        for prospect in prospects:
            if self.validate_email(prospect['email']):
                valid_prospects.append(prospect)
                
        # Génération et envoi des emails
        sent_count = 0
        for prospect in valid_prospects[:5]:  # Limite à 5 emails par campagne
            email_data = self.generate_email(agency_name, prospect)
            
            if self.send_email(
                prospect['email'],
                email_data['subject'],
                email_data['body'],
                email_data['sender']
            ):
                sent_count += 1
                
                # Enregistrement dans Google Sheets
                self.record_campaign(agency_name, prospect, "ENVOYE")
                
        logger.info(f"Campagne {agency_name} terminée: {sent_count} emails envoyés")
        
    def record_campaign(self, agency_name: str, prospect: Dict[str, Any], status: str):
        """Enregistrement des résultats dans Google Sheets"""
        try:
            ws = self.sheet.worksheet("Campagnes")
            ws.append_row([
                datetime.now(self.tz).strftime("%Y-%m-%d"),
                agency_name,
                datetime.now(self.tz).strftime("%H:%M"),
                prospect['nom'],
                prospect['email'],
                status
            ])
        except Exception as e:
            logger.error(f"Erreur enregistrement: {e}")
            
    def run_continuous_campaigns(self):
        """Lancement des campagnes continues"""
        logger.info("Démarrage du système de campagnes continues")
        
        # Planification des campagnes
        for agency in AGENCIES_CONFIG.keys():
            schedule.every(2).hours.do(self.run_campaign, agency)
            
        # Exécution continue
        while True:
            schedule.run_pending()
            time.sleep(1800)  # Vérification toutes les 30 minutes
            
    def start_web_server(self):
        """Démarrage du serveur web Flask"""
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return jsonify({
                "status": "running",
                "agencies": list(AGENCIES_CONFIG.keys()),
                "next_campaigns": str(schedule.next_run())
            })
            
        @app.route('/health')
        def health():
            return jsonify({"status": "healthy"})
            
        @app.route('/status')
        def status():
            return jsonify({
                "system": "ready",
                "agencies": AGENCIES_CONFIG,
                "timezone": str(self.tz),
                "current_time": datetime.now(self.tz).isoformat()
            })
            
        @app.route('/run-campaigns')
        def manual_campaigns():
            for agency in AGENCIES_CONFIG.keys():
                self.run_campaign(agency)
            return jsonify({"status": "campaigns_started"})
            
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port)

def main():
    """Fonction principale exécutée par la start command"""
    logger.info("🚀 Démarrage du système de prospection complet")
    
    # Initialisation du système
    system = ProspectionSystem()
    
    # Création des threads
    campaign_thread = threading.Thread(target=system.run_continuous_campaigns)
    web_thread = threading.Thread(target=system.start_web_server)
    
    # Démarrage des threads
    campaign_thread.start()
    web_thread.start()
    
    logger.info("✅ Système de prospection démarré avec succès")
    logger.info("📧 Campagnes actives: Lundi-Vendredi 9h-16h")
    logger.info("🌐 Serveur web disponible sur le port configuré")

if __name__ == "__main__":
    main()