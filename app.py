from flask import Flask, request, jsonify
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
from datetime import datetime
import re

app = Flask(__name__)

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

def log_data(data, title=""):
    """Fonction pour afficher les données dans les logs"""
    print(f"\n{'='*50}")
    print(f"LOG: {title}")
    print(f"{'='*50}")
    print(f"Type: {type(data)}")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)
    print(f"{'='*50}\n")

def process_form_data(form_data, agency_type):
    """Traite les données du formulaire avec flexibilité"""
    log_data(form_data, f"Données brutes reçues pour {agency_type}")
    
    # Mapper les champs possibles
    field_mapping = {
        'nom': ['nom', 'name', 'fullname', 'full_name', 'entreprise', 'company'],
        'email': ['email', 'mail', 'e-mail', 'email_address'],
        'telephone': ['telephone', 'tel', 'phone', 'mobile', 'telephone_number'],
        'service': ['service', 'type', 'demande', 'request'],
        'description': ['description', 'message', 'comment', 'enjeu', 'projet', 'de'],
        'societe': ['societe', 'society', 'company', 'organization'],
        'url': ['url', 'website', 'site', 'site_web']
    }
    
    processed_data = {}
    
    # Chercher les champs dans les données reçues
    for target_field, possible_fields in field_mapping.items():
        found = False
        for field in possible_fields:
            if field in form_data:
                processed_data[target_field] = form_data[field]
                found = True
                break
        
        if not found:
            processed_data[target_field] = "Non spécifié"
    
    log_data(processed_data, f"Données traitées pour {agency_type}")
    return processed_data

def send_email(to_email, subject, html_content, smtp_server, smtp_port, smtp_username, smtp_password, from_email=None):
    """Envoie un email HTML avec configuration SMTP spécifique"""
    if from_email is None:
        from_email = smtp_username
        
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

def create_growth_notification_email(data):
    """Crée l'email de notification pour EBUSINESS GROWTH"""
    template = f"""
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
                <p><strong>Service:</strong> {data.get('service', 'Non spécifié')}</p>
                <p><strong>Description:</strong> {data.get('description', 'Non spécifié')}</p>
            </div>
            
            <div class="highlight">
                Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
            </div>
        </div>
    </body>
    </html>
    """
    
    return f"🚀 Nouveau Lead AUTOMATISATION - EBUSINESS GROWTH - {data.get('nom', 'Non spécifié')}", template

def create_ai_notification_email(data):
    """Crée l'email de notification pour EBUSINESS AI"""
    template = f"""
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
                <p><strong>Service:</strong> {data.get('service', 'Non spécifié')}</p>
                <p><strong>Description:</strong> {data.get('description', 'Non spécifié')}</p>
            </div>
            
            <div class="highlight">
                Ce lead a été automatiquement traité par notre système d'IA et nécessite votre attention dans les 24h.
            </div>
        </div>
    </body>
    </html>
    """
    
    return f"🤖 Nouveau Lead AUTOMATISATION - EBUSINESS AI - {data.get('nom', 'Non spécifié')}", template

def create_growth_customer_email(data):
    """Crée l'email de confirmation client pour EBUSINESS GROWTH"""
    subject = "Votre réservation est confirmée ✅"
    
    template = f"""
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
                <h1>{subject}</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{data.get('nom', '')}</strong>,</p>
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
    
    return subject, template

def create_ai_customer_email(data):
    """Crée l'email de confirmation client pour EBUSINESS AI"""
    subject = "Votre demande d'audit e-commerce est confirmée ✅"
    
    template = f"""
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
                <h1>{subject}</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{data.get('nom', '')}</strong>,</p>
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
    
    return subject, template

@app.route('/webhook/growth', methods=['POST'])
def webhook_growth():
    """Webhook pour EBUSINESS GROWTH"""
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
        
        # Traiter les données
        processed_data = process_form_data(form_data, "EBUSINESS GROWTH")
        
        # Créer les emails
        subject_notification, html_notification = create_growth_notification_email(processed_data)
        subject_customer, html_customer = create_growth_customer_email(processed_data)
        
        # Envoyer les emails
        notification_sent = send_email(
            EMAIL_GROWTH, subject_notification, html_notification,
            SMTP_GROWTH_SERVER, SMTP_GROWTH_PORT, SMTP_GROWTH_USERNAME, SMTP_GROWTH_PASSWORD
        )
        
        customer_sent = send_email(
            processed_data.get('email'), subject_customer, html_customer,
            SMTP_GROWTH_SERVER, SMTP_GROWTH_PORT, SMTP_GROWTH_USERNAME, SMTP_GROWTH_PASSWORD
        )
        
        print(f"Emails envoyés - Notification: {notification_sent}, Client: {customer_sent}")
        
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
        print(f"ERREUR WEBHOOK GROWTH: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/webhook/ai', methods=['POST'])
def webhook_ai():
    """Webhook pour EBUSINESS AI"""
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
        
        # Traiter les données
        processed_data = process_form_data(form_data, "EBUSINESS AI")
        
        # Créer les emails
        subject_notification, html_notification = create_ai_notification_email(processed_data)
        subject_customer, html_customer = create_ai_customer_email(processed_data)
        
        # Envoyer les emails
        notification_sent = send_email(
            EMAIL_AI, subject_notification, html_notification,
            SMTP_AI_SERVER, SMTP_AI_PORT, SMTP_AI_USERNAME, SMTP_AI_PASSWORD
        )
        
        customer_sent = send_email(
            processed_data.get('email'), subject_customer, html_customer,
            SMTP_AI_SERVER, SMTP_AI_PORT, SMTP_AI_USERNAME, SMTP_AI_PASSWORD
        )
        
        print(f"Emails envoyés - Notification: {notification_sent}, Client: {customer_sent}")
        
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
