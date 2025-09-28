import os
import logging
from flask import Flask, request, jsonify
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration Flask ---
app = Flask(__name__)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- Gmail SMTP config ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")  # ton email Gmail
SMTP_PASS = os.getenv("SMTP_PASS")  # ton mot de passe / App Password
TO_EMAIL = "ia.ebusinessag@gmail.com"


# --- Fonction asynchrone d'envoi email ---
async def send_email(data):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = TO_EMAIL
        msg["Subject"] = f"🚀 Nouveau lead Orbis : {data.get('name','(inconnu)')}"

        body = "\n".join([f"{k}: {v}" for k, v in data.items()])
        msg.attach(MIMEText(body, "plain"))

        logging.info("📧 Connexion au serveur SMTP...")
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASS,
        )
        logging.info("✅ Email envoyé avec succès à %s", TO_EMAIL)

    except Exception as e:
        logging.error(f"❌ Erreur envoi email: {e}")


# --- Webhook ---
@app.route("/webhook/ai", methods=["POST"])
def webhook_ai():
    logging.info("🤖 WEBHOOK AI (ORBIS) REÇU")

    try:
        # Récupération data JSON ou form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Enrichissement
        data["service"] = "Installation Orbis"

        logging.info("📋 Données reçues : %s", data)

        # Lancer l’envoi email en tâche async
        asyncio.run(send_email(data))

        return jsonify({"status": "success", "message": "Webhook reçu et email envoyé"}), 200

    except Exception as e:
        logging.error(f"❌ Erreur traitement webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Root pour test ---
@app.route("/", methods=["GET"])
def home():
    return "🚀 Webhook Automation EBUSINESS AI actif", 200


# --- Lancement ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

