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

# Configuration SMTP pour EBUSINESS AI
SMTP_AI_SERVER = "smtp.gmail.com"
SMTP_AI_PORT = 587
SMTP_AI_USERNAME = "ia.ebusinessag@gmail.com"
SMTP_AI_PASSWORD = "qqdg wyeh qmsi npoy".replace(" ", "")

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

@app.route('/webhook/ai', methods=['POST', 'OPTIONS'])
def webhook_ai():
    if request.method == 'OPTIONS':
        return '', 200
    
    log_message("🤖 WEBHOOK AI (ORBIS) REÇU")
    
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
        required_fields = ['name', 'email', 'phone', 'shopName', 'website', 'platform']
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            log_message(f"❌ Champs manquants: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            }), 400
        
        # Traiter les données
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
        
        # Configuration SMTP pour AI
        smtp_config = {
            'server': SMTP_AI_SERVER,
            'port': SMTP_AI_PORT,
            'username': SMTP_AI_USERNAME,
            'password': SMTP_AI_PASSWORD
        }
        
        # Créer et envoyer l'email de notification
        subject_notification = f"🤖 Nouvelle demande d'installation Orbis - {processed_data['shopName']}"
        html_notification = f"""
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
                .field {{ margin-bottom: 15px; }}
                .field strong {{ color: #cc0000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Nouvelle demande d'installation Orbis</h1>
                    <p>Lead reçu le {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
                </div>
                <div class="content">
                    <div class="field"><strong>Nom & Prénom:</strong> {processed_data['name']}</div>
                    <div class="field"><strong>Email:</strong> {processed_data['email']}</div>
                    <div class="field"><strong>Téléphone:</strong> {processed_data['phone']}</div>
                    <div class="field"><strong>Nom boutique:</strong> {processed_data['shopName']}</div>
                    <div class="field"><strong>Site web:</strong> {processed_data['website']}</div>
                    <div class="field"><strong>Plateforme:</strong> {processed_data['platform']}</div>
                    <div class="field"><strong>Service:</strong> {processed_data['service']}</div>
                </div>
                <div class="highlight">
                    Ce lead a été automatiquement traité et nécessite votre attention dans les 24h.
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
            "notification ORBIS"
        )
        
        # Créer et envoyer l'email client
        subject_customer = "Mise en place rapide de votre Vendeur Digital – informations requises"
        html_customer = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 30px; border-radius: 15px; color: #ffffff; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 2px solid #cc0000; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #cc0000; margin: 0; font-size: 24px; font-weight: bold; }}
                .content {{ line-height: 1.6; }}
                .section {{ margin-bottom: 25px; }}
                .section h3 {{ color: #cc0000; margin-top: 0; margin-bottom: 15px; font-size: 18px; }}
                .section ul {{ margin: 0; padding-left: 20px; }}
                .section li {{ margin-bottom: 8px; }}
                .highlight {{ background: rgba(204, 0, 0, 0.2); padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #cc0000; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; }}
                .signature {{ color: #ffffff; }}
                .signature strong {{ color: #cc0000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Mise en place rapide de votre Vendeur Digital – informations requises</h1>
                </div>
                
                <div class="content">
                    <p>Bonjour <strong>{processed_data['name']}</strong>,</p>
                    
                    <p>Pour installer et activer Orbis, votre Vendeur Digital Pro, et le rendre pleinement opérationnel sur votre boutique, nous aurons besoin :</p>
                    
                    <div class="section">
                        <h3>1. Accès aux outils d'analyse et suivi</h3>
                        <ul>
                            <li>Google Tag Manager (compte ou conteneur)</li>
                            <li>Hotjar (ou équivalent session replay)</li>
                            <li>Google Analytics (propriété existante ou création par nos soins)</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>2. Accès à votre boutique en ligne</h3>
                        <ul>
                            <li>Shopify / WooCommerce / PrestaShop (accès administrateur ou développeur limité)</li>
                            <li>Si site custom : accès FTP / hébergeur ou code d'intégration</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>3. Accès complémentaires (si disponibles)</h3>
                        <ul>
                            <li>Pixel Meta (Facebook Ads)</li>
                            <li>CRM utilisé (ou export clients si non connecté)</li>
                            <li>WhatsApp Business (numéro ou API si déjà configuré)</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>4. Précisions éventuelles</h3>
                        <p>Plateforme utilisée, contraintes techniques, ou préférences spécifiques pour vos intégrations.</p>
                    </div>
                    
                    <div class="highlight">
                        ⚡ Vous pouvez nous fournir vos accès existants (invitation collaborateur ou clés API) ou nous demander de créer et configurer les comptes à votre place. Nous vous enverrons ensuite les accès pour modification et contrôle.
                    </div>
                    
                    <p>Toutes les informations partagées resteront strictement confidentielles et seront utilisées uniquement pour la mise en place de votre Vendeur Digital Pro.</p>
                    
                    <div class="highlight">
                        👉 Plus vite nous recevons ces éléments, plus vite Orbis pourra commencer à transformer vos visiteurs en clients.
                    </div>
                </div>
                
                <div class="footer">
                    <p>Merci pour votre collaboration,</p>
                    <div class="signature">
                        <p><strong>Geraldo Domingo</strong></p>
                        <p>EBUSINESS AI – Orbis, le Vendeur Digital Pro</p>
                    </div>
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
            "client ORBIS"
        )
        
        log_message(f"📧 Résumé envoi emails - Notification: {notification_sent}, Client: {customer_sent}")
        
        return jsonify({
            "status": "success",
            "message": "Demande d'installation Orbis traitée avec succès",
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
    log_message("🚀 Démarrage de l'application pour EBUSINESS AI (ORBIS)")
    app.run(debug=False, host='0.0.0.0', port=10000)
