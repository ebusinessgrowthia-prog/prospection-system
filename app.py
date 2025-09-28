from flask import Flask, request, jsonify
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
from datetime import datetime
from flask_cors import CORS

# ------------------------------------------------------------
# Initialisation de l'application Flask
# ------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*"], "methods": ["GET", "POST", "OPTIONS"]}})

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
GEMINI_API_KEY = os.environ.get(
    'GEMINI_API_KEY',
    'AIzaSyDlpgExpY2CqmPki0cb4dNRQICJKZ2i0TM'  # fallback
)

# SMTP EBUSINESS AI
SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "zykr ubtm daaw jgqr".replace(" ", "")  # App Password
EMAIL_AI = "ia.ebusinessag@gmail.com"

# Config Gemini
genai.configure(api_key=GEMINI_API_KEY)


# ------------------------------------------------------------
# Utilitaires
# ------------------------------------------------------------
def log_message(message: str):
    """Logger avec timestamp"""
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


# ------------------------------------------------------------
# Middlewares
# ------------------------------------------------------------
@app.after_request
def after_request(response):
    """Ajout des headers CORS"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# ------------------------------------------------------------
# Webhook Orbis
# ------------------------------------------------------------
@app.route('/webhook/ai', methods=['POST', 'OPTIONS'])
def webhook_ai():
    if request.method == 'OPTIONS':
        return '', 200

    log_message("🤖 WEBHOOK AI (ORBIS) REÇU")

    try:
        # Log infos requête
        log_message(f"Content-Type: {request.content_type}")
        log_message(f"Method: {request.method}")
        log_message(f"Headers: {dict(request.headers)}")

        # Récupération des données
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

        # Vérification des champs
        required_fields = ['name', 'email', 'phone', 'shopName', 'website', 'platform']
        missing_fields = [f for f in required_fields if f not in form_data]

        if missing_fields:
            log_message(f"❌ Champs manquants: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            }), 400

        # Données traitées
        processed_data = {
            'name': form_data.get('name', 'Non spécifié'),
            'email': form_data.get('email', 'Non spécifié'),
            'phone': form_data.get('phone', 'Non spécifié'),
            'shopName': form_data.get('shopName', 'Non spécifié'),
            'website': form_data.get('website', 'Non spécifié'),
            'platform': form_data.get('platform', 'Non spécifié'),
            'service': 'Installation Orbis'
        }
        log_message(f"✅ Données traitées: {processed_data}")

        # Config SMTP
        smtp_config = {
            'server': SMTP_AI_SERVER,
            'port': SMTP_AI_PORT,
            'username': SMTP_AI_USERNAME,
            'password': SMTP_AI_PASSWORD
        }

        # -----------------------------
        # EMAIL 1 - Notification interne
        # -----------------------------
        subject_notification = f"🤖 Nouvelle demande Orbis - {processed_data['shopName']}"
        html_notification = f"""
        <html><body>
        <h2>🤖 Nouvelle demande d'installation Orbis</h2>
        <p><b>Nom:</b> {processed_data['name']}<br>
        <b>Email:</b> {processed_data['email']}<br>
        <b>Téléphone:</b> {processed_data['phone']}<br>
        <b>Boutique:</b> {processed_data['shopName']}<br>
        <b>Site:</b> {processed_data['website']}<br>
        <b>Plateforme:</b> {processed_data['platform']}<br>
        <b>Service:</b> {processed_data['service']}</p>
        </body></html>
        """
        notification_sent = send_email_with_logs(
            EMAIL_AI, subject_notification, html_notification, smtp_config, "notification ORBIS"
        )

        # -----------------------------
        # EMAIL 2 - Réponse client
        # -----------------------------
        subject_customer = "Mise en place rapide de votre Vendeur Digital – Orbis"
        html_customer = f"""
        <html><body>
        <h2>Bienvenue {processed_data['name']} 👋</h2>
        <p>Merci pour votre demande. Pour installer Orbis, nous aurons besoin :</p>
        <ul>
          <li>Accès Google Tag Manager / Analytics / Hotjar</li>
          <li>Accès admin à votre boutique ({processed_data['platform']})</li>
          <li>Accès Pixel Meta / CRM si disponibles</li>
        </ul>
        <p>👉 Plus vite nous recevons ces éléments, plus vite Orbis sera opérationnel.</p>
        <p>EBUSINESS AI – Orbis, le Vendeur Digital Pro</p>
        </body></html>
        """
        customer_sent = send_email_with_logs(
            processed_data['email'], subject_customer, html_customer, smtp_config, "client ORBIS"
        )

        # Résumé
        log_message(f"📧 Emails envoyés - Notification: {notification_sent}, Client: {customer_sent}")

        return jsonify({
            "status": "success",
            "message": "Demande Orbis traitée avec succès",
            "data": processed_data,
            "emails_sent": {
                "notification": notification_sent,
                "customer": customer_sent
            }
        }), 200

    except Exception as e:
        log_message(f"❌ ERREUR WEBHOOK AI: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------------------------------------------
# Healthcheck
# ------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    log_message("🏥 Health check demandé")
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


# ------------------------------------------------------------
# Entrée principale
# ------------------------------------------------------------
if __name__ == '__main__':
    log_message("🚀 Démarrage EBUSINESS AI (ORBIS)")
    app.run(debug=False, host='0.0.0.0', port=10000)

