from flask import Flask, request, jsonify
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
from datetime import datetime
from flask_cors import CORS  # Ajout du support CORS

app = Flask(__name__)
# Activer CORS pour toutes les routes
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Autorise toutes les origines (à restreindre en production)
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration des variables d'environnement
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDlpgExpY2CqmPki0cb4dNRQICJKZ2i0TM')

# Configuration SMTP pour EBUSINESS GROWTH
SMTP_GROWTH_SERVER = "smtp.gmail.com"
SMTP_GROWTH_PORT = 587
SMTP_GROWTH_USERNAME = "ebusinessgrowthai@gmail.com"
SMTP_GROWTH_PASSWORD = "bssi qnqy rdfz cchf".replace(" ", "")

# Configuration SMTP pour EBUSINESS AI
SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy".replace(" ", "")

# Emails de notification
EMAIL_GROWTH = "ebusinessgrowthia@gmail.com"
EMAIL_AI = "ia.ebusinessag@gmail.com"

# Configuration Gemini
genai.configure(api_key=GEMINI_API_KEY)

@app.after_request
def after_request(response):
    """Ajoute les en-têtes CORS à chaque réponse"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/webhook/growth', methods=['POST', 'OPTIONS'])
def webhook_growth():
    """Webhook pour EBUSINESS GROWTH"""
    # Gérer la requête OPTIONS (pré-vol CORS)
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"\n{'='*50}")
        print("WEBHOOK GROWTH REÇU")
        print(f"{'='*50}")
        
        # Récupérer les données du formulaire
        if request.form:
            form_data = request.form.to_dict()
            print("Données reçues comme formulaire (form-data)")
        elif request.is_json:
            form_data = request.get_json()
            print("Données reçues comme JSON")
        elif request.data:
            try:
                form_data = json.loads(request.data.decode('utf-8'))
                print("Données reçues comme JSON brut")
            except:
                form_data = {'raw_data': request.data.decode('utf-8')}
                print("Données reçues comme texte brut")
        else:
            form_data = {}
            print("Aucune donnée reçue")
        
        print("Données reçues:", form_data)
        
        # Traiter les données
        processed_data = {
            'nom': form_data.get('nom', 'Non spécifié'),
            'email': form_data.get('email', 'Non spécifié'),
            'telephone': form_data.get('telephone', 'Non spécifié'),
            'societe': form_data.get('societe', 'Non spécifié'),
            'service': form_data.get('service', 'Rétention & Relance B2B'),
            'description': form_data.get('description', 'Non spécifié')
        }
        
        print("Données traitées:", processed_data)
        
        # Créer les emails
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
        
        # Envoyer les emails
        try:
            # Email de notification
            msg_notification = MIMEMultipart('alternative')
            msg_notification['Subject'] = subject_notification
            msg_notification['From'] = SMTP_GROWTH_USERNAME
            msg_notification['To'] = EMAIL_GROWTH
            msg_notification.attach(MIMEText(html_notification, 'html'))
            
            with smtplib.SMTP(SMTP_GROWTH_SERVER, SMTP_GROWTH_PORT) as server:
                server.starttls()
                server.login(SMTP_GROWTH_USERNAME, SMTP_GROWTH_PASSWORD)
                server.send_message(msg_notification)
            
            # Email client
            msg_customer = MIMEMultipart('alternative')
            msg_customer['Subject'] = subject_customer
            msg_customer['From'] = SMTP_GROWTH_USERNAME
            msg_customer['To'] = processed_data['email']
            msg_customer.attach(MIMEText(html_customer, 'html'))
            
            with smtplib.SMTP(SMTP_GROWTH_SERVER, SMTP_GROWTH_PORT) as server:
                server.starttls()
                server.login(SMTP_GROWTH_USERNAME, SMTP_GROWTH_PASSWORD)
                server.send_message(msg_customer)
            
            print("Emails envoyés avec succès")
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS GROWTH",
            "data": processed_data
        }), 200
        
    except Exception as e:
        print(f"ERREUR WEBHOOK GROWTH: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/webhook/ai', methods=['POST', 'OPTIONS'])
def webhook_ai():
    """Webhook pour EBUSINESS AI"""
    # Gérer la requête OPTIONS (pré-vol CORS)
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"\n{'='*50}")
        print("WEBHOOK AI REÇU")
        print(f"{'='*50}")
        
        # Récupérer les données du formulaire
        if request.form:
            form_data = request.form.to_dict()
            print("Données reçues comme formulaire (form-data)")
        elif request.is_json:
            form_data = request.get_json()
            print("Données reçues comme JSON")
        elif request.data:
            try:
                form_data = json.loads(request.data.decode('utf-8'))
                print("Données reçues comme JSON brut")
            except:
                form_data = {'raw_data': request.data.decode('utf-8')}
                print("Données reçues comme texte brut")
        else:
            form_data = {}
            print("Aucune donnée reçue")
        
        print("Données reçues:", form_data)
        
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
        
        print("Données traitées:", processed_data)
        
        # Créer les emails
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
        
        # Envoyer les emails
        try:
            # Email de notification
            msg_notification = MIMEMultipart('alternative')
            msg_notification['Subject'] = subject_notification
            msg_notification['From'] = SMTP_AI_USERNAME
            msg_notification['To'] = EMAIL_AI
            msg_notification.attach(MIMEText(html_notification, 'html'))
            
            with smtplib.SMTP(SMTP_AI_SERVER, SMTP_AI_PORT) as server:
                server.starttls()
                server.login(SMTP_AI_USERNAME, SMTP_AI_PASSWORD)
                server.send_message(msg_notification)
            
            # Email client
            msg_customer = MIMEMultipart('alternative')
            msg_customer['Subject'] = subject_customer
            msg_customer['From'] = SMTP_AI_USERNAME
            msg_customer['To'] = processed_data['email']
            msg_customer.attach(MIMEText(html_customer, 'html'))
            
            with smtplib.SMTP(SMTP_AI_SERVER, SMTP_AI_PORT) as server:
                server.starttls()
                server.login(SMTP_AI_USERNAME, SMTP_AI_PASSWORD)
                server.send_message(msg_customer)
            
            print("Emails envoyés avec succès")
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS AI",
            "data": processed_data
        }), 200
        
    except Exception as e:
        print(f"ERREUR WEBHOOK AI: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé pour le monitoring"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
