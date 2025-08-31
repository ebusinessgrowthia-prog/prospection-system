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
SMTP_GROWTH_PASSWORD = "bssi qnqy rdfz cchf".replace(" ", "")  # bssiqnqyrdfzcchf

# Configuration SMTP pour EBUSINESS AI
SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy".replace(" ", "")  # qqdgwyehqmsinpoy

# Emails de notification
EMAIL_GROWTH = "ebusinessgrowthia@gmail.com"
EMAIL_AI = "ia.ebusinessag@gmail.com"

# Configuration Gemini
genai.configure(api_key=GEMINI_API_KEY)

def extract_form_data_with_gemini(form_data, agency_type):
    """Utilise Gemini 2.0 Flash pour extraire et structurer les données du formulaire"""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Adapter le prompt en fonction du type d'agence
    if agency_type == "EBUSINESS GROWTH":
        prompt = f"""
        Tu es un assistant spécialisé dans l'extraction de données de formulaires pour EBUSINESS GROWTH.
        
        Analyse les données du formulaire ci-dessous et extrais les informations pertinentes :
        
        Données brutes : {form_data}
        
        Extrais et retourne un JSON avec les champs suivants :
        - nom: Nom complet de la personne
        - email: Adresse email
        - telephone: Numéro de téléphone
        - service: Service demandé (généralement "Rétention & Relance B2B")
        - description: Description du projet ou défi client
        - societe: Nom de l'entreprise (si disponible)
        
        Si un champ n'est pas trouvé, mets "Non spécifié".
        Retourne uniquement le JSON, pas d'autre texte.
        """
    else:  # EBUSINESS AI
        prompt = f"""
        Tu es un assistant spécialisé dans l'extraction de données de formulaires pour EBUSINESS AI.
        
        Analyse les données du formulaire ci-dessous et extrais les informations pertinentes :
        
        Données brutes : {form_data}
        
        Extrais et retourne un JSON avec les champs suivants :
        - nom: Nom de l'entreprise (c'est le nom fourni dans le formulaire)
        - email: Email professionnel
        - url: URL du site e-commerce (si disponible)
        - service: Service demandé (généralement "Audit IA")
        - description: Description du principal enjeu
        - telephone: Numéro de téléphone (si disponible)
        
        Si un champ n'est pas trouvé, mets "Non spécifié".
        Retourne uniquement le JSON, pas d'autre texte.
        """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Nettoyer la réponse pour obtenir du JSON pur
        if result.startswith('```json'):
            result = result[7:-3]
        elif result.startswith('```'):
            result = result[3:-3]
            
        return json.loads(result)
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return {
            "nom": "Non spécifié",
            "email": "Non spécifié", 
            "telephone": "Non spécifié",
            "service": "Non spécifié",
            "description": "Non spécifié",
            "societe": "Non spécifié",
            "url": "Non spécifié"
        }

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
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .signature strong {{ color: #FFD700; }}
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
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .signature strong {{ color: #000; }}
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
                <p><strong>URL e-commerce:</strong> {data.get('url', 'Non spécifié')}</p>
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
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .signature strong {{ color: #FFD700; }}
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
                <p>Pour avancer efficacement, envoyez-nous votre CRM et tout document client pertinent dès maintenant. Plus vite nous aurons ces informations, plus vite nous réaliserons l'audit et vous fournirons un plan stratégique clair et actionnable.</p>
                <p>Votre confidentialité est notre priorité. Vos données seront sécurisées et utilisées uniquement pour identifier les opportunités réelles au sein de votre entreprise.</p>
                <p>Nous nous réjouissons de travailler avec vous pour transformer ces informations en résultats concrets.</p>
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
            .list {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #000; }}
            .list ol {{ margin: 0; padding-left: 20px; }}
            .list li {{ margin: 10px 0; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .signature strong {{ color: #000; }}
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
                <p>Pour avancer efficacement, merci de nous transmettre dès maintenant :</p>
                <ul>
                    <li>Vos accès Google Analytics / Shopify Analytics ou rapport exporté (trafic, taux de conversion, sources de ventes).</li>
                    <li>Vos données CRM / emailing (taux d'ouverture, taux de clic, séquences actives).</li>
                    <li>Vos indicateurs logistiques (délai moyen d'expédition, taux de retours produits).</li>
                    <li>Vos principaux KPI financiers (ROAS, CLV/CAC, panier moyen, marges nettes).</li>
                </ul>
                <p>Ces informations nous permettront d'identifier :</p>
                <div class="list">
                    <ol>
                        <li>Les pertes actuelles de chiffre d'affaires (paniers abandonnés, clients non réactivés, marges réduites par coûts cachés).</li>
                        <li>Les gains immédiats possibles via l'automatisation et l'IA (publicité, support client, suivi commandes, relance automatique).</li>
                        <li>Les optimisations structurelles pour rendre votre croissance scalable et prévisible.</li>
                    </ol>
                </div>
                <p>Vos données resteront strictement confidentielles et seront utilisées uniquement pour établir un diagnostic précis et un plan d'action opérationnel.</p>
                <p>Vous recevrez votre audit personnalisé sous 3 jours ouvrés.</p>
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
        # Récupérer les données du formulaire
        form_data = request.form.to_dict() if request.form else request.get_json()
        
        print(f"Données reçues pour GROWTH: {form_data}")  # Debug
        
        # Extraire et structurer les données avec Gemini
        processed_data = extract_form_data_with_gemini(form_data, "EBUSINESS GROWTH")
        
        print(f"Données traitées pour GROWTH: {processed_data}")  # Debug
        
        # Créer l'email de notification pour l'agence
        subject_notification, html_notification = create_growth_notification_email(processed_data)
        
        # Créer l'email de confirmation pour le client
        subject_customer, html_customer = create_growth_customer_email(processed_data)
        
        # Envoyer email de notification à l'agence
        email_sent = send_email(
            EMAIL_GROWTH, 
            subject_notification, 
            html_notification,
            SMTP_GROWTH_SERVER, 
            SMTP_GROWTH_PORT, 
            SMTP_GROWTH_USERNAME, 
            SMTP_GROWTH_PASSWORD
        )
        
        print(f"Email notification GROWTH envoyé: {email_sent}")  # Debug
        
        # Envoyer email de confirmation au client
        customer_email_sent = send_email(
            processed_data.get('email'), 
            subject_customer, 
            html_customer,
            SMTP_GROWTH_SERVER, 
            SMTP_GROWTH_PORT, 
            SMTP_GROWTH_USERNAME, 
            SMTP_GROWTH_PASSWORD
        )
        
        print(f"Email client GROWTH envoyé: {customer_email_sent}")  # Debug
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS GROWTH",
            "data": processed_data,
            "emails_sent": {
                "notification": email_sent,
                "customer": customer_email_sent
            }
        }), 200
        
    except Exception as e:
        print(f"Erreur webhook GROWTH: {str(e)}")  # Debug
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/webhook/ai', methods=['POST'])
def webhook_ai():
    """Webhook pour EBUSINESS AI"""
    try:
        # Récupérer les données du formulaire
        form_data = request.form.to_dict() if request.form else request.get_json()
        
        print(f"Données reçues pour AI: {form_data}")  # Debug
        
        # Extraire et structurer les données avec Gemini
        processed_data = extract_form_data_with_gemini(form_data, "EBUSINESS AI")
        
        print(f"Données traitées pour AI: {processed_data}")  # Debug
        
        # Créer l'email de notification pour l'agence
        subject_notification, html_notification = create_ai_notification_email(processed_data)
        
        # Créer l'email de confirmation pour le client
        subject_customer, html_customer = create_ai_customer_email(processed_data)
        
        # Envoyer email de notification à l'agence
        email_sent = send_email(
            EMAIL_AI, 
            subject_notification, 
            html_notification,
            SMTP_AI_SERVER, 
            SMTP_AI_PORT, 
            SMTP_AI_USERNAME, 
            SMTP_AI_PASSWORD
        )
        
        print(f"Email notification AI envoyé: {email_sent}")  # Debug
        
        # Envoyer email de confirmation au client
        customer_email_sent = send_email(
            processed_data.get('email'), 
            subject_customer, 
            html_customer,
            SMTP_AI_SERVER, 
            SMTP_AI_PORT, 
            SMTP_AI_USERNAME, 
            SMTP_AI_PASSWORD
        )
        
        print(f"Email client AI envoyé: {customer_email_sent}")  # Debug
        
        return jsonify({
            "status": "success",
            "message": "Lead traité avec succès pour EBUSINESS AI",
            "data": processed_data,
            "emails_sent": {
                "notification": email_sent,
                "customer": customer_email_sent
            }
        }), 200
        
    except Exception as e:
        print(f"Erreur webhook AI: {str(e)}")  # Debug
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé pour le monitoring"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/test-growth', methods=['GET', 'POST'])
def test_growth():
    """Endpoint de test pour EBUSINESS GROWTH"""
    if request.method == 'POST':
        return webhook_growth()
    return """
    <h1>Test EBUSINESS GROWTH</h1>
    <form method="post">
        <input type="text" name="nom" placeholder="Nom" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="tel" name="telephone" placeholder="Téléphone" required><br>
        <input type="text" name="societe" placeholder="Société"><br>
        <textarea name="description" placeholder="Description" required></textarea><br>
        <input type="hidden" name="service" value="Rétention & Relance B2B">
        <button type="submit">Tester</button>
    </form>
    """

@app.route('/test-ai', methods=['GET', 'POST'])
def test_ai():
    """Endpoint de test pour EBUSINESS AI"""
    if request.method == 'POST':
        return webhook_ai()
    return """
    <h1>Test EBUSINESS AI</h1>
    <form method="post">
        <input type="text" name="nom" placeholder="Nom de l'entreprise" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="url" name="url" placeholder="URL du site" required><br>
        <textarea name="description" placeholder="Description" required></textarea><br>
        <input type="hidden" name="service" value="Audit IA">
        <input type="hidden" name="telephone" value="Non spécifié">
        <input type="hidden" name="societe" value="Non spécifié">
        <button type="submit">Tester</button>
    </form>
    """

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
