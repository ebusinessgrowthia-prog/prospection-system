import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# Configuration API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv("GOOGLE_SHEETS_SPREADSHEET_NAME", "Prospection")

# Email Configuration
FROM_EMAIL_1 = os.getenv("FROM_EMAIL_1", "ebusinessgrowthia@gmail.com")
FROM_NAME_1 = os.getenv("FROM_NAME_1", "EBUSINESS GROWTH")
FROM_EMAIL_2 = os.getenv("FROM_EMAIL_2", "ia.ebusinessag@gmail.com")
FROM_NAME_2 = os.getenv("FROM_NAME_2", "EBUSINESS IA")
DAILY_EMAIL_LIMIT = int(os.getenv("DAILY_EMAIL_LIMIT", "100"))

# Scraping Configuration
MAX_DORKS_PER_CAMPAIGN = int(os.getenv("MAX_DORKS_PER_CAMPAIGN", "50"))
MAX_PROSPECTS_PER_DORK = int(os.getenv("MAX_PROSPECTS_PER_DORK", "20"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))

# Validation Configuration
EMAIL_VALIDATION_THRESHOLD = float(os.getenv("EMAIL_VALIDATION_THRESHOLD", "0.8"))

# RGPD Configuration
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "90"))
UNSUBSCRIBE_LINK = os.getenv("UNSUBSCRIBE_LINK", "%%unsubscribe%%")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "prospection.log")

# Port Configuration
PORT = int(os.getenv("PORT", "5000"))
FLASK_ENV = os.getenv("FLASK_ENV", "production")

# Configuration des agences
AGENCES_CONFIG: Dict[str, Dict[str, Any]] = {
    "EBUSINESS_GROWTH": {
        "nom": "EBUSINESS GROWTH",
        "secteur": "Digital Marketing & E-commerce",
        "cible": "E-commerçants 100k-1M€ CA, Shopify/WooCommerce",
        "objectif": "Calls de 30min pour audit gratuit + vente coaching",
        "style_ton": "Direct, challengeur, ROI-focus",
        "cta_principal": "Réserver un call stratégique gratuit",
        "email_expediteur": "ebusinessgrowthia@gmail.com",
        "max_emails_jour": 5,
        "dorks_base": [
            "site:myshopify.com intitle:'contact' 'founder' OR 'CEO'",
            "site:woocommerce.com intitle:'about' 'email' AND 'store owner'",
            "intitle:'ecommerce success story' 'revenue' 'contact'",
            "site:linkedin.com 'ecommerce founder' '100k revenue' 'email'",
            "intitle:'shopify store' 'revenue' 'contact us'"
        ]
    },
    "EBUSINESS_AI": {
        "nom": "EBUSINESS AI",
        "secteur": "IA & Automatisation E-commerce",
        "cible": "E-commerçants 500k-5M€ CA, process à optimiser",
        "objectif": "Démonstration IA + audit automatisation",
        "style_ton": "Tech-savvy, résultats concrets, élite",
        "cta_principal": "Voir l'IA en action sur Zoom",
        "email_expediteur": "ia.ebusinessag@gmail.com",
        "max_emails_jour": 5,
        "dorks_base": [
            "site:myshopify.com 'automation' 'scaling' 'contact CEO'",
            "intitle:'ecommerce automation case study' 'revenue'",
            "site:linkedin.com 'ecommerce automation' '500k' 'email'",
            "intitle:'AI ecommerce tools' 'store owner' 'contact'",
            "site:woocommerce.com 'automated store' 'revenue' 'founder'"
        ]
    }
}

# Plan de message pour la conception des mails de prospection
PLAN_MESSAGE = {
    "nouveau_positionnement": {
        "EBUSINESS_GROWTH": "La récupération et la conversion des prospects perdus ou inactifs",
        "EBUSINESS_AI": "L'optimisation de la conversion par l'IA (chatbots et contenu IA)"
    },
    "objectif_service": {
        "EBUSINESS_GROWTH": "Analyser le CRM pour identifier les prospects non convertis et déployer une stratégie personnalisée pour les réactiver",
        "EBUSINESS_AI": "Analyser le parcours client pour identifier les points de friction et déployer des solutions IA pour augmenter les conversions"
    },
    "approche": [
        "Collaborative et humaine",
        "Le 'je' avant tout",
        "Questions ouvertes",
        "Faire émerger le besoin chez le prospect",
        "Ultra-personnalisation"
    ],
    "ton_attendu": [
        "Humain: langage naturel, empathique",
        "Concis mais précis",
        "Accroche forte",
        "Émotionnel + rationnel",
        "Collaboratif"
    ],
    "offre_urgence": {
        "service": "Service tout juste lancé",
        "limitation": "Offre limitée à 5 entreprises",
        "tarif": "Tarif symbolique ou gratuit pour créer des cas clients"
    },
    "structure_mail": [
        "Accroche personnelle (phrase choc, humaine, centrée sur le problème de conversion)",
        "Constat partagé (compréhension du secteur)",
        "La faille (coûts d'acquisition élevés vs taux de conversion faibles)",
        "La solution (service précis proposé)",
        "La preuve de rareté (offre limitée, service en lancement)",
        "La question ouverte",
        "Clôture humaine et simple"
    ]
}
