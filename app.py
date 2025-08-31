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

# Configuration SMTP
SMTP_GROWTH_SERVER = "smtp.gmail.com"
SMTP_GROWTH_PORT = 587
SMTP_GROWTH_USERNAME = "ebusinessgrowthai@gmail.com"
SMTP_GROWTH_PASSWORD = "bssi qnqy rdfz cchf".replace(" ", "")

SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy".replace(" ", "")

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
        # Log des informations de la requête
        log_message(f"Content-Type: {request.content_type}")
        log_message(f"Method: {request.method}")
        log_message(f"Headers: {dict(request.headers)}")
        
        # Récupérer les données
        form_data = {}
        if request.form:
            form_data = request.form.to_dict()
            log_message("📝 Données reçues comme form-data")
        elif request.is_json:
            form_data = request.get_json()
            log_message("📝 Données reçues comme JSON")
        elif request.data:
            try:
                form_data = json.loads(request.data.decode('utf-8'))
                log_message("📝 Données reçues comme JSON brut")
            except:
                form_data = {'raw_data': request.data.decode('utf-8')}
                log_message("📝 Données reçues comme texte brut")
        
        log_message(f"📋 Données brutes: {form_data}")
        
        # Vérifier les champs obligatoires
        required_fields = ['nom', 'email']
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            log_message(f"❌ Champs manquants: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            }), 400
        
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
        
        # Configuration SMTP pour GROWTH
        smtp_config = {
            'server': SMTP_GROWTH_SERVER,
            'port': SMTP_GROWTH_PORT,
            'username': SMTP_GROWTH_USERNAME,
            'password': SMTP_GROWTH_PASSWORD
        }
        
        # Créer et envoyer l'email de notification
        subject_notification = f"🚀 Nouveau Lead AUTOMATISATION - EBUSINESS GROWTH - {processed_data['nom']}"
        html_notification = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #FFD700; margin: 0; font-size: 28px; }}
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
                    <p><strong>Nom:</strong> {processed_data['nom']}</p>
                    <p><strong>Email:</strong> {processed_data['email']}</p>
                    <p><strong>Téléphone:</strong> {processed_data['telephone']}</p>
                    <p><strong>Société:</strong> {processed_data['societe']}</p>
                    <p><strong>Service:</strong> {processed_data['service']}</p>
                    <p><strong>Description:</strong> {processed_data['description']}</p>
                </div>
                <div class="highlight">
                    Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
                </div>
            </div>
        </body>
        </html>
        """
        
        notification_sent = send_email_with_logs(
            EMAIL_GROWTH, 
            subject_notification, 
            html_notification, 
            smtp_config, 
            "notification GROWTH"
        )
        
        # Créer et envoyer l'email client
        subject_customer = "Votre réservation est confirmée ✅"
        html_customer = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #FFD700; margin: 0; font-size: 28px; }}
                .content {{ line-height: 1.6; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{subject_customer}</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{processed_data['nom']}</strong>,</p>
                    <p>Votre réservation est confirmée.</p>
                    <p>Pour avancer efficacement, envoyez-nous votre CRM et tout document client pertinent dès maintenant.</p>
                    <p>Merci pour votre confiance,</p>
                    <p><strong>Gildea SOGNON-DES</strong><br>
                    Contact : gildeapalissy@icloud.com | WhatsApp : +229 91 96 77 04</p>
                </div>
            </div>
        </body>
        </html>
        """
        
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
        # Log des informations de la requête
        log_message(f"Content-Type: {request.content_type}")
        log_message(f"Method: {request.method}")
        log_message(f"Headers: {dict(request.headers)}")
        
        # Récupérer les données
        form_data = {}
        if request.form:
            form_data = request.form.to_dict()
            log_message("📝 Données reçues comme form-data")
        elif request.is_json:
            form_data = request.get_json()
            log_message("📝 Données reçues comme JSON")
        elif request.data:
            try:
                form_data = json.loads(request.data.decode('utf-8'))
                log_message("📝 Données reçues comme JSON brut")
            except:
                form_data = {'raw_data': request.data.decode('utf-8')}
                log_message("📝 Données reçues comme texte brut")
        
        log_message(f"📋 Données brutes: {form_data}")
        
        # Vérifier les champs obligatoires
        required_fields = ['nom', 'email']
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            log_message(f"❌ Champs manquants: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            }), 400
        
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
        
        # Configuration SMTP pour AI
        smtp_config = {
            'server': SMTP_AI_SERVER,
            'port': SMTP_AI_PORT,
            'username': SMTP_AI_USERNAME,
            'password': SMTP_AI_PASSWORD
        }
        
        # Créer et envoyer l'email de notification
        subject_notification = f"🤖 Nouveau Lead AUTOMATISATION - EBUSINESS AI - {processed_data['nom']}"
        html_notification = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #000 0%, #333 100%); color: white; padding: 20px; border-radius: 10px; }}
                .header h1 {{ color: #fff; margin: 0; font-size: 28px; }}
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
                    <p><strong>Entreprise:</strong> {processed_data['nom']}</p>
                    <p><strong>Email:</strong> {processed_data['email']}</p>
                    <p><strong>URL:</strong> {processed_data['url']}</p>
                    <p><strong>Téléphone:</strong> {processed_data['telephone']}</p>
                    <p><strong>Service:</strong> {processed_data['service']}</p>
                    <p><strong>Description:</strong> {processed_data['description']}</p>
                </div>
                <div class="highlight">
                    Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
                </div>
            </div>
        </body>
        </html>
        """
        
        notification_sent = send_email_with_logs(
            EMAIL_AI, 
            subject_notification, 
            html_notification, 
            smtp_config, 
            "notification AI"
        )
        
        # Créer et envoyer l'email client
        subject_customer = "Votre demande d'audit e-commerce est confirmée ✅"
        html_customer = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #000 0%, #333 100%); color: white; padding: 20px; border-radius: 10px; }}
                .header h1 {{ color: #fff; margin: 0; font-size: 28px; }}
                .content {{ line-height: 1.6; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{subject_customer}</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{processed_data['nom']}</strong>,</p>
                    <p>Votre demande d'audit e-commerce a bien été enregistrée.</p>
                    <p>Merci pour votre confiance,</p>
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

@app.route('/debug', methods=['POST'])
def debug_endpoint():
    """Endpoint de debug pour voir exactement ce qui est reçu"""
    log_message("🔍 Debug endpoint appelé")
    
    debug_info = {
        "method": request.method,
        "content_type": request.content_type,
        "headers": dict(request.headers),
        "form_data": dict(request.form) if request.form else None,
        "json_data": request.get_json() if request.is_json else None,
        "raw_data": request.data.decode('utf-8') if request.data else None,
        "args": dict(request.args)
    }
    
    log_message(f"🔍 Debug info: {debug_info}")
    
    return jsonify({
        "status": "debug",
        "debug_info": debug_info
    })

if __name__ == '__main__':
    log_message("🚀 Démarrage de l'application")
    app.run(debug=False, host='0.0.0.0', port=10000)
