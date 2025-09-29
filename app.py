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
    
    log_message("🤖 WEBHOOK REÇU")
    
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
        
        # Créer et envoyer l'email de notification à l'agence (vous)
        subject_notification = f"🤖 Nouvelle demande d'installation AI Sales Pro - {processed_data['shopName']}"
        html_notification = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #000 0%, #333 100%); color: white; padding: 25px; border-radius: 12px; }}
                .header h1 {{ color: #fff; margin: 0; font-size: 28px; font-weight: bold; }}
                .header p {{ color: #ccc; margin: 10px 0 0 0; }}
                .content {{ line-height: 1.6; color: #333; }}
                .info-section {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 4px solid #cc0000; }}
                .info-section h3 {{ color: #cc0000; margin-top: 0; margin-bottom: 15px; font-size: 18px; }}
                .field-row {{ display: flex; margin-bottom: 12px; }}
                .field-label {{ font-weight: bold; color: #333; min-width: 140px; }}
                .field-value {{ color: #555; }}
                .preview-section {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border: 2px solid #cc0000; border-radius: 15px; padding: 30px; margin: 25px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden; }}
                .preview-header {{ text-align: center; margin-bottom: 25px; position: relative; z-index: 2; }}
                .preview-header h2 {{ color: #cc0000; margin: 0; font-size: 22px; font-weight: bold; }}
                .preview-content {{ position: relative; z-index: 2; }}
                .preview-content h3 {{ color: #cc0000; margin-top: 0; margin-bottom: 15px; font-size: 18px; }}
                .preview-content p {{ color: #ffffff; margin: 0 0 15px 0; line-height: 1.6; }}
                .preview-content ul {{ margin: 0 0 15px 0; padding-left: 20px; }}
                .preview-content li {{ color: #ffffff; margin-bottom: 8px; }}
                .highlight-box {{ background: rgba(204, 0, 0, 0.2); border-left: 4px solid #cc0000; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .highlight-box p {{ color: #ffffff; margin: 0; }}
                .shine-effect {{ position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent 30%, rgba(204, 0, 0, 0.1) 50%, transparent 70%); animation: shine 3s infinite; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                .footer p {{ color: #666; margin: 0; }}
                .footer strong {{ color: #333; }}
                @keyframes shine {{
                    0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
                    100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
                }}
            </style>
                        <p>Ce lead a été automatiquement traité et nécessite votre attention dans les 24h.</p>
                        <p><strong>Service:</strong> {processed_data['service']}</p>
                    </div>
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
            "notification AI Sales Pro"
        )
        
        log_message(f"📧 Email de notification envoyé - Statut: {notification_sent}")
        
        return jsonify({
            "status": "success",
            "message": "Demande d'installation de AI Sales Pro traitée avec succès",
            "data": processed_data,
            "notification_sent": notification_sent
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
    log_message("🚀 Démarrage de l'application pour EBUSINESS AI GROWTH")
    app.run(debug=False, host='0.0.0.0', port=10000)
