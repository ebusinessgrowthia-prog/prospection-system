from flask import Flask, request, jsonify
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*"], "methods": ["GET", "POST", "OPTIONS"]}})

# Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDlpgExpY2CqmPki0cb4dNRQICJKZ2i0TM')

# # Configuration SMTP - CORRIGÉ
SMTP_GROWTH_SERVER = "smtp.gmail.com"
SMTP_GROWTH_PORT = 587
SMTP_GROWTH_USERNAME = "ebusinessgrowthai@gmail.com"
SMTP_GROWTH_PASSWORD = "bssi qnqy rdfz cchf"  # Gardez les espaces !

SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy"  # Gardez les espaces !

EMAIL_GROWTH = "ebusinessgrowthia@gmail.com"
EMAIL_AI = "ia.ebusinessag@gmail.com"

genai.configure(api_key=GEMINI_API_KEY)

def log_message(message):
    """Fonction pour logger les messages avec timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_email_with_logs(to_email, subject, html_content, smtp_config, email_type=""):
    """Envoie un email avec logs détaillés"""
    log_message(f"Tentative d'envoi d'email {email_type} à {to_email}")
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_config['username']
        msg['To'] = to_email
        msg.attach(MIMEText(html_content, 'html'))
        
        log_message(f"Connexion au serveur SMTP {smtp_config['server']}:{smtp_config['port']}")
        
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            log_message("Démarrage TLS...")
            server.starttls()
            
            log_message("Authentification SMTP...")
            server.login(smtp_config['username'], smtp_config['password'])
            
            log_message(f"Envoi de l'email à {to_email}...")
            server.send_message(msg)
        
        log_message(f"✅ Email {email_type} envoyé avec succès à {to_email}")
        return True
        
    except Exception as e:
        log_message(f"❌ Erreur envoi email {email_type}: {str(e)}")
        return False

def create_growth_notification_email(data):
    """Crée l'email de notification pour EBUSINESS GROWTH avec le vrai template"""
    subject = f"🚀 Nouveau Lead AUTOMATISATION - EBUSINESS GROWTH - {data.get('nom', 'Client')}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #FFD700; margin: 0; font-size: 28px; }}
            .header p {{ color: #666; margin: 10px 0 0 0; }}
            .content {{ line-height: 1.6; color: #333; }}
            .highlight {{ background: #FFD700; color: #333; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Nouveau Lead AUTOMATISATION - EBUSINESS GROWTH</h1>
                <p>Lead reçu le {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </div>
            
            <div class="content">
                <h2>Informations du Prospect</h2>
                <p><strong>Nom:</strong> {data.get('nom', 'Non spécifié')}</p>
                <p><strong>Email:</strong> {data.get('email', 'Non spécifié')}</p>
                <p><strong>Téléphone:</strong> {data.get('telephone', 'Non spécifié')}</p>
                <p><strong>Société:</strong> {data.get('societe', 'Non spécifié')}</p>
                <p><strong>Service demandé:</strong> {data.get('service', 'Non spécifié')}</p>
                <p><strong>Description du projet:</strong></p>
                <p>{data.get('description', 'Non spécifié')}</p>
            </div>
            
            <div class="highlight">
                Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def create_growth_customer_email(data):
    """Crée l'email de confirmation client pour EBUSINESS GROWTH avec le vrai template"""
    subject = "Votre réservation est confirmée ✅"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #FFD700; margin: 0; font-size: 28px; }}
            .content {{ line-height: 1.6; color: #333; }}
            .steps {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .steps ol {{ margin: 0; padding-left: 20px; }}
            .steps li {{ margin: 10px 0; }}
            .highlight {{ background: #FFD700; color: #333; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Votre réservation est confirmée ✅</h1>
            </div>
            
            <div class="content">
                <p>Bonjour <strong>{data.get('nom', 'Client')}</strong>,</p>
                <p>Votre réservation est confirmée.</p>
                <p>Pour avancer efficacement, envoyez-nous votre CRM et tout document client pertinent dès maintenant. Plus vite nous aurons ces informations, plus vite nous réaliserons l'audit et vous fournirons un plan stratégique clair et actionnable.</p>
                <p>Votre confidentialité est notre priorité. Vos données seront sécurisées et utilisées uniquement pour identifier les opportunités réelles au sein de votre entreprise.</p>
                <p>Nous nous réjouissons de travailler avec vous pour transformer ces informations en résultats concrets.</p>
                
                <div class="steps">
                    <h3>Le processus se déroule en 5 étapes clés :</h3>
                    <ol>
                        <li>Analyse complète de votre situation - Audit approfondi de vos fuites clients et opportunités dormantes</li>
                        <li>Mapping détaillé de vos clients - Segmentation et identification des leviers de rétention</li>
                        <li>Validation de la stratégie - Présentation de votre plan d'action personnalisé</li>
                        <li>Mise en place des automatisations - Déploiement des agents IA adaptés à votre entreprise</li>
                        <li>Amélioration continue des KPI - Optimisation permanente pour des résultats durables</li>
                    </ol>
                </div>
                
                <div class="highlight">
                    Vous bénéficiez de la tarification de lancement à 800 € au lieu de la valeur réelle de 8 000 – 25 000 €. Cette approche me permet de constituer mes études de cas exclusives tout en vous offrant une transformation visible en quelques semaines.
                </div>
                
                <p>Vous faites partie des 5 seuls clients qui peuvent bénéficier de cette offre avant le retour au tarif normal. Cette limitation garantit un accompagnement premium et des résultats exceptionnels.</p>
                
                <p>Ne laissez plus vos clients partir sans retour. Transformons-les ensemble en revenus récurrents et durables.</p>
            </div>
            
            <div class="signature">
                <p>À très bientôt pour réveiller vos clients dormants et réduire votre churn de façon durable.</p>
                <p>Cordialement,</p>
                <p><strong>Gildea SOGNON-DES</strong><br>
                Growth Hacker & Expert IA<br>
                Cotonou, Bénin<br>
                ebusinessgrowthai@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def create_ai_notification_email(data):
    """Crée l'email de notification pour EBUSINESS AI avec le vrai template"""
    subject = f"🤖 Nouveau Lead AUTOMATISATION - EBUSINESS AI - {data.get('nom', 'Client')}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #000 0%, #333 100%); color: white; padding: 20px; border-radius: 10px; }}
            .header h1 {{ color: #fff; margin: 0; font-size: 28px; }}
            .header p {{ color: #ccc; margin: 10px 0 0 0; }}
            .content {{ line-height: 1.6; color: #333; }}
            .highlight {{ background: #000; color: #fff; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Nouveau Lead AUTOMATISATION - EBUSINESS AI</h1>
                <p>Lead reçu le {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </div>
            
            <div class="content">
                <h2>Informations du Prospect</h2>
                <p><strong>Entreprise:</strong> {data.get('nom', 'Non spécifié')}</p>
                <p><strong>Email:</strong> {data.get('email', 'Non spécifié')}</p>
                <p><strong>URL:</strong> {data.get('url', 'Non spécifié')}</p>
                <p><strong>Téléphone:</strong> {data.get('telephone', 'Non spécifié')}</p>
                <p><strong>Service demandé:</strong> {data.get('service', 'Non spécifié')}</p>
                <p><strong>Description du projet:</strong></p>
                <p>{data.get('description', 'Non spécifié')}</p>
            </div>
            
            <div class="highlight">
                Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def create_ai_customer_email(data):
    """Crée l'email de confirmation client pour EBUSINESS AI avec le vrai template"""
    subject = "Votre demande d'audit e-commerce est confirmée ✅"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #000 0%, #333 100%); color: white; padding: 20px; border-radius: 10px; }}
            .header h1 {{ color: #fff; margin: 0; font-size: 28px; }}
            .content {{ line-height: 1.6; color: #333; }}
            .list {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #000; }}
            .list ol {{ margin: 0; padding-left: 20px; }}
            .list li {{ margin: 10px 0; }}
            .highlight {{ background: #000; color: #fff; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Votre demande d'audit e-commerce est confirmée ✅</h1>
            </div>
            
            <div class="content">
                <p>Bonjour <strong>{data.get('nom', 'Client')}</strong>,</p>
                <p>Votre demande d'audit gratuit a bien été enregistrée.</p>
                <p>Je suis Geraldo DOMINGO, et je tiens à vous confirmer personnellement que votre dossier fait désormais partie de mes priorités.</p>
                
                <p>Dans les 24-48h, vous recevrez une première analyse de votre profil e-commerce, un questionnaire personnalisé pour affiner l'audit, ainsi que les éléments techniques nécessaires pour l'analyse de vos données.</p>
                
                <div class="list">
                    <h3>Le processus se déroule en 3 étapes simples :</h3>
                    <ol>
                        <li>Collecte sécurisée de vos données - Vous transmettez vos analytics, ventes et trafic via notre plateforme sécurisée</li>
                        <li>Analyse approfondie (2-3 jours) - J'identifie les opportunités concrètes d'optimisation par IA</li>
                        <li>Restitution des résultats - Si des opportunités sont détectées, nous discutons du plan d'action personnalisé. Si aucun potentiel n'est identifié, vous repartez avec une vision claire de votre situation.</li>
                    </ol>
                </div>
                
                <div class="highlight">
                    "Je regarde d'abord vos chiffres. Ensuite, on discute."
                </div>
                
                <p>Vous faites partie d'un processus sélectif où seuls les e-commerçants motivés par l'amélioration continue sont accompagnés. Votre engagement dans cette démarche est ce qui compte, pas la taille de votre entreprise.</p>
                
                <p>À très bientôt pour transformer vos données en opportunités concrètes.</p>
            </div>
            
            <div class="signature">
                <p>Cordialement,</p>
                <p><strong>Geraldo DOMINGO</strong><br>
                Expert IA & E-commerce<br>
                Cotonou, Bénin<br>
                +229 01 40 72 05 56<br>
                ia.ebusinessag@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/webhook/growth', methods=['POST', 'OPTIONS'])
def webhook_growth():
    if request.method == 'OPTIONS':
        return '', 200
    
    log_message("🚀 WEBHOOK GROWTH REÇU")
    
    try:
        # Récupérer les données
        form_data = {}
        if request.form:
            form_data = request.form.to_dict()
        elif request.is_json:
            form_data = request.get_json()
        
        log_message(f"📋 Données brutes: {form_data}")
        
        # Traiter les données
        processed_data = {
            'nom': form_data.get('nom', 'Non spécifié'),
            'email': form_data.get('email', 'Non spécifié'),
            'telephone': form_data.get('telephone', 'Non spécifié'),
            'societe': form_data.get('societe', 'Non spécifié'),
            'service': form_data.get('service', 'Rétention & Relance B2B'),
            'description': form_data.get('description', 'Non spécifié')
        }
        
        log_message(f"✅ Données traitées: {processed_data}")
        
        
        # Créer et envoyer l'email de notification
        subject_notification, html_notification = create_growth_notification_email(processed_data)
        notification_sent = send_email_with_logs(
            EMAIL_GROWTH, 
            subject_notification, 
            html_notification, 
            smtp_config, 
            "notification GROWTH"
        )
        
        # Créer et envoyer l'email client
        subject_customer, html_customer = create_growth_customer_email(processed_data)
        customer_sent = send_email_with_logs(
            processed_data['email'], 
            subject_customer, 
            html_customer, 
            smtp_config, 
            "client GROWTH"
        )
        
        log_message(f"📧 Résumé envoi emails - Notification: {notification_sent}, Client: {customer_sent}")
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS GROWTH",
            "data": processed_data,
            "emails_sent": {
                "notification": notification_sent,
                "customer": customer_sent
            }
        }), 200
        
    except Exception as e:
        log_message(f"❌ ERREUR WEBHOOK GROWTH: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/webhook/ai', methods=['POST', 'OPTIONS'])
def webhook_ai():
    if request.method == 'OPTIONS':
        return '', 200
    
    log_message("🤖 WEBHOOK AI REÇU")
    
    try:
        # Récupérer les données
        form_data = {}
        if request.form:
            form_data = request.form.to_dict()
        elif request.is_json:
            form_data = request.get_json()
        
        log_message(f"📋 Données brutes: {form_data}")
        
        # Traiter les données
        processed_data = {
            'nom': form_data.get('nom', 'Non spécifié'),
            'email': form_data.get('email', 'Non spécifié'),
            'url': form_data.get('url', 'Non spécifié'),
            'service': form_data.get('service', 'Audit IA'),
            'description': form_data.get('description', 'Non spécifié'),
            'telephone': form_data.get('telephone', 'Non spécifié'),
            'societe': form_data.get('societe', 'Non spécifié')
        }
        
        log_message(f"✅ Données traitées: {processed_data}")
        
        # Configuration SMTP - CORRIGÉ
SMTP_GROWTH_SERVER = "smtp.gmail.com"
SMTP_GROWTH_PORT = 587
SMTP_GROWTH_USERNAME = "ebusinessgrowthai@gmail.com"
SMTP_GROWTH_PASSWORD = "bssi qnqy rdfz cchf"  # Gardez les espaces !

SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy"  # Gardez les espaces !
        
        # Créer et envoyer l'email de notification
        subject_notification, html_notification = create_ai_notification_email(processed_data)
        notification_sent = send_email_with_logs(
            EMAIL_AI, 
            subject_notification, 
            html_notification, 
            smtp_config, 
            "notification AI"
        )
        
        # Créer et envoyer l'email client
        subject_customer, html_customer = create_ai_customer_email(processed_data)
        customer_sent = send_email_with_logs(
            processed_data['email'], 
            subject_customer, 
            html_customer, 
            smtp_config, 
            "client AI"
        )
        
        log_message(f"📧 Résumé envoi emails - Notification: {notification_sent}, Client: {customer_sent}")
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS AI",
            "data": processed_data,
            "emails_sent": {
                "notification": notification_sent,
                "customer": customer_sent
            }
        }), 200
        
    except Exception as e:
        log_message(f"❌ ERREUR WEBHOOK AI: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    log_message("🏥 Health check demandé")
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    log_message("🚀 Démarrage de l'application")
    app.run(debug=False, host='0.0.0.0', port=10000)
