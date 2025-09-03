"""
Configuration centrale pour l'application EBUSINESS AI
Gère toutes les variables d'environnement et paramètres du système
"""

import os
import json
from typing import List, Dict, Any
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config(BaseSettings):
    """Configuration principale de l'application"""
    
    # --- Clés API ---
    mistral_api_key: str = Field(..., env="MISTRAL_API_KEY")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    serpapi_api_key: str = Field(..., env="SERPAPI_API_KEY")
    render_api_key: str = Field(..., env="RENDER_API_KEY")
    render_service_id: str = Field("", env="RENDER_SERVICE_ID")
    
    # --- Configuration Email ---
    email_address: str = Field(..., env="EMAIL_ADDRESS")
    email_password: str = Field(..., env="EMAIL_PASSWORD")
    smtp_server: str = Field("smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(587, env="SMTP_PORT")
    
    # --- Informations Entreprise ---
    company_name: str = Field("EBUSINESS AI", env="COMPANY_NAME")
    your_name: str = Field("Geraldo Domingo", env="YOUR_NAME")
    your_title: str = Field("Expert IA & E-commerce", env="YOUR_TITLE")
    your_location: str = Field("Cotonou, Bénin", env="YOUR_LOCATION")
    
    # --- Configuration Prospection ---
    target_sectors: List[str] = Field(
        ["Mode", "Électronique", "Services", "Digital", "Retail"],
        env="TARGET_SECTORS"
    )
    target_countries: List[str] = Field(
        ["France", "Belgique", "Suisse", "Luxembourg", "Monaco", "Canada (Québec)"],
        env="TARGET_COUNTRIES"
    )
    min_company_size: int = Field(10000, env="MIN_COMPANY_SIZE")
    max_company_size: int = Field(100000, env="MAX_COMPANY_SIZE")
    
    # --- Configuration Horaires ---
    email_sending_days: List[str] = Field(
        ["tuesday", "wednesday", "thursday", "friday"],
        env="EMAIL_SENDING_DAYS"
    )
    email_sending_start: int = Field(9, env="EMAIL_SENDING_START")
    email_sending_end: int = Field(17, env="EMAIL_SENDING_END")
    timezone: str = Field("Europe/Paris", env="TIMEZONE")
    
    # --- Limites et Paramètres ---
    max_emails_per_day: int = Field(50, env="MAX_EMAILS_PER_DAY")
    delay_between_emails: int = Field(30, env="DELAY_BETWEEN_EMAILS")
    search_frequency_hours: int = Field(2, env="SEARCH_FREQUENCY_HOURS")
    
    # --- Configuration Base de Données ---
    database_url: str = Field("sqlite:///data/prospects.db", env="DATABASE_URL")
    
    # --- Configuration Dashboard ---
    dashboard_title: str = Field("🚀 EBUSINESS AI - Automatisation de Prospection", env="DASHBOARD_TITLE")
    primary_color: str = Field("#667eea", env="PRIMARY_COLOR")
    secondary_color: str = Field("#764ba2", env="SECONDARY_COLOR")
    
    # --- Configuration Avancée ---
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    landing_page_url: str = Field("https://ebusinessag.com/gestion.html", env="LANDING_PAGE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def target_sectors_json(self) -> str:
        """Retourne les secteurs cibles au format JSON"""
        return json.dumps(self.target_sectors)
    
    @property
    def target_countries_json(self) -> str:
        """Retourne les pays cibles au format JSON"""
        return json.dumps(self.target_countries)
    
    @property
    def email_sending_days_json(self) -> str:
        """Retourne les jours d'envoi au format JSON"""
        return json.dumps(self.email_sending_days)
    
    def get_google_dorks(self) -> List[str]:
        """Génère les Google Dorks pour la recherche de prospects"""
        dorks = []
        
        # Dorks de base pour chaque pays
        country_dorks = {
            "France": [
                '"e-commerce" "témoignage" "France" -emploi -stage',
                '"boutique en ligne" "France" "croissance"',
                '"e-commerce" "France" "expert" "solution"',
                '"site e-commerce" "France" "performance"',
                '"vendre en ligne" "France" "conseil"'
            ],
            "Belgique": [
                '"e-commerce" "Belgique" "site"',
                '"boutique en ligne" "Belgique" "shop"',
                '"e-commerce" "Belgique" "expert"'
            ],
            "Suisse": [
                '"e-commerce" "Suisse" "shop"',
                '"boutique en ligne" "Suisse" "vente"',
                '"e-commerce" "Suisse" "solution"'
            ],
            "Luxembourg": [
                '"e-commerce" "Luxembourg" "business"',
                '"boutique en ligne" "Luxembourg"'
            ],
            "Monaco": [
                '"e-commerce" "Monaco" "luxe"',
                '"boutique en ligne" "Monaco"'
            ]
        }
        
        # Dorks pour le Québec
        quebec_dorks = [
            '"e-commerce" "Québec" "boutique en ligne"',
            '"vendre en ligne" "Québec" "conseil"',
            '"site e-commerce" "Québec" "expert"'
        ]
        
        
        # Dorks par secteur
        sector_dorks = {
            "Mode": [
                '"e-commerce mode" "boutique" "francophone"',
                '"vetements en ligne" "shop" "francophone"'
            ],
            "Électronique": [
                '"e-commerce électronique" "shop" "francophone"',
                '"high-tech en ligne" "boutique" "francophone"'
            ],
            "Services": [
                '"e-commerce services" "solution" "francophone"',
                '"services en ligne" "plateforme" "francophone"'
            ],
            "Digital": [
                '"e-commerce digital" "solution" "francophone"',
                '"digital shop" "francophone"'
            ],
            "Retail": [
                '"e-commerce retail" "shop" "francophone"',
                '"retail en ligne" "boutique" "francophone"'
            ]
        }
        
        # Combiner tous les dorks
        for country, country_dork_list in country_dorks.items():
            if country in self.target_countries:
                dorks.extend(country_dork_list)
        
        if "Canada (Québec)" in self.target_countries:
            dorks.extend(quebec_dorks)
        
        # Ajouter les dorks par secteur
        for sector in self.target_sectors:
            if sector in sector_dorks:
                dorks.extend(sector_dorks[sector])
        
        return list(set(dorks))  # Éliminer les doublons
    
    def get_email_prompt_template(self) -> str:
        """Retourne le template de prompt pour la génération d'emails"""
        return """
        Tu es un expert en neurosciences comportementales et psychologie cognitive.
        Tu dois rédiger un email de prospection pour un e-commerçant en respectant strictement ces règles :

        CONTEXTE DU PROSPECT :
        - Nom: {name}
        - Entreprise: {company}
        - Secteur: {sector}
        - Problématique détectée: {problem}
        - Spécificité: {specificity}

        DIRECTIVES OBLIGATOIRES :
        1. Ton humble et collaboratif - utiliser le conditionnel
        2. Personnalisation extrême avec contexte spécifique
        3. Structure exacte :
           - Accroche personnelle (1 phrase sur la douleur)
           - Constat partagé (compréhension du secteur)
           - Identifier la faille (données inexploitées)
           - Proposer solution (audit gratuit)
           - Rareté douce (offre lancement 900€)
           - 1 question ouverte maximum
           - CTA cliquable vers {landing_page}
           - Signature simple

        4. Techniques de persuasion à inclure :
           - Effet de contraste
           - Ancrage cognitif
           - Preuve sociale subtile
           - Réciprocité
           - Rareté douce
           - Autorité par expertise

        INTERDICTIONS ABSOLUES :
        - Pas de téléphone, adresse, URL brute
        - Pas de statistiques inventées
        - Pas d'urgence artificielle
        - Pas d'affirmations absolues

        Génère maintenant l'email en respectant scrupuleusement toutes ces règles.
        """

# Instance globale de la configuration
config = Config()

# Fonction pour obtenir la configuration
def get_config() -> Config:
    """Retourne l'instance de configuration"""
    return config
