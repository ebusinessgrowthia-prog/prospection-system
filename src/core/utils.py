"""
Utilitaires et fonctions communes pour EBUSINESS AI
Fonctions de logging, validation, et helpers divers
"""
import os
import logging
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from email_validator import validate_email, EmailNotValidError
import pytz

# Import de la configuration
try:
    from src.config import get_config
    config = get_config()
except ImportError:
    # Configuration par défaut en cas d'erreur
    class Config:
        log_level = "INFO"
        target_sectors = ["Mode", "Électronique", "Services", "Digital", "Retail"]
        target_countries = ["France", "Belgique", "Suisse", "Luxembourg"]
        email_sending_days = ["tuesday", "wednesday", "thursday", "friday"]
        email_sending_start = 9
        email_sending_end = 17
        timezone = "Europe/Paris"
    
    config = Config()

def setup_logging():
    """Configure le logging pour l'application"""
    log_level = getattr(logging, config.log_level.upper())
    
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs('data/logs', exist_ok=True)
    
    # Configuration du logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging configuré avec succès")

def validate_email_address(email: str) -> bool:
    """Valide une adresse email"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def generate_tracking_id() -> str:
    """Génère un ID de tracking unique pour les emails"""
    return str(uuid.uuid4())

def extract_domain_from_email(email: str) -> Optional[str]:
    """Extrait le domaine d'une adresse email"""
    if not validate_email_address(email):
        return None
    
    return email.split('@')[1]

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extrait le domaine d'une URL"""
    try:
        # Supprimer le protocole et le chemin
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        # Supprimer le port s'il existe
        domain = domain.split(':')[0]
        return domain
    except:
        return None

def is_business_email(email: str) -> bool:
    """Vérifie si l'email est un email professionnel (pas gmail, yahoo, etc.)"""
    if not validate_email_address(email):
        return False
    
    domain = extract_domain_from_email(email)
    
    # Liste des domaines personnels courants
    personal_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'live.com', 'aol.com', 'icloud.com', 'mail.com',
        'yandex.com', 'protonmail.com', 'tutanota.com'
    ]
    
    return domain not in personal_domains

def clean_text(text: str) -> str:
    """Nettoie un texte pour le rendre utilisable"""
    if not text:
        return ""
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Supprimer les caractères spéciaux inutiles
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|\\]', '', text)
    
    # Supprimer les espaces au début et à la fin
    text = text.strip()
    
    return text

def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extrait les mots-clés d'un texte"""
    found_keywords = []
    text_lower = text.lower()
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def calculate_qualification_score(prospect_data: Dict[str, Any]) -> float:
    """Calcule le score de qualification d'un prospect"""
    score = 0.0
    
    # Email professionnel
    if prospect_data.get('email') and is_business_email(prospect_data['email']):
        score += 3.0
    
    # Site web présent
    if prospect_data.get('website'):
        score += 2.0
    
    # Secteur cible
    if prospect_data.get('sector') in config.target_sectors:
        score += 2.0
    
    # Pays cible
    if prospect_data.get('country') in config.target_countries:
        score += 2.0
    
    # Problématique détectée
    if prospect_data.get('problem_detected'):
        score += 1.0
    
    # Spécificité
    if prospect_data.get('specificity'):
        score += 1.0
    
    return min(score, 10.0)  # Score maximum de 10

def format_date_for_display(date: datetime) -> str:
    """Formate une date pour l'affichage"""
    if not date:
        return ""
    
    # Convertir en timezone locale
    try:
        tz = pytz.timezone(config.timezone)
        date = date.astimezone(tz)
    except:
        pass
    
    return date.strftime("%d/%m/%Y %H:%M")

def format_number(number: int, suffix: str = "") -> str:
    """Formate un nombre pour l'affichage"""
    return f"{number:,}{suffix}".replace(",", " ")

def is_business_hours() -> bool:
    """Vérifie si on est dans les heures de bureau configurées"""
    try:
        tz = pytz.timezone(config.timezone)
        now = datetime.now(tz)
        
        # Vérifier le jour de la semaine
        day_name = now.strftime("%A").lower()
        if day_name not in config.email_sending_days:
            return False
        
        # Vérifier l'heure
        hour = now.hour
        return config.email_sending_start <= hour < config.email_sending_end
        
    except:
        return False

def get_next_business_hour() -> datetime:
    """Retourne la prochaine heure de bureau"""
    try:
        tz = pytz.timezone(config.timezone)
        now = datetime.now(tz)
        
        # Chercher le prochain jour ouvrable
        for i in range(7):  # Maximum 7 jours à l'avance
            check_date = now + timedelta(days=i)
            day_name = check_date.strftime("%A").lower()
            
            if day_name in config.email_sending_days:
                # Si c'est aujourd'hui et on est avant l'heure de début
                if i == 0 and check_date.hour < config.email_sending_start:
                    return check_date.replace(
                        hour=config.email_sending_start,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                # Si c'est aujourd'hui et on est dans les heures de bureau
                elif i == 0 and config.email_sending_start <= check_date.hour < config.email_sending_end:
                    return check_date
                # Si c'est un autre jour
                elif i > 0:
                    return check_date.replace(
                        hour=config.email_sending_start,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
        
        # Si rien trouvé, retourner demain à l'heure de début
        return now.replace(
            hour=config.email_sending_start,
            minute=0,
            second=0,
            microsecond=0
        ) + timedelta(days=1)
        
    except:
        return datetime.now() + timedelta(hours=1)

def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """Charge un JSON en toute sécurité"""
    try:
        return json.loads(json_str)
    except:
        return None

def safe_json_dumps(obj: Any) -> str:
    """Convertit un objet en JSON en toute sécurité"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except:
        return "{}"

def export_prospects_to_excel(prospects: List[Dict[str, Any]], filename: str = None) -> str:
    """Exporte les prospects vers un fichier CSV (au lieu d'Excel)"""
    if not filename:
        filename = f"prospects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # S'assurer que le répertoire existe
    os.makedirs('data/exports', exist_ok=True)
    filepath = os.path.join('data/exports', filename)
    
    # Exporter vers CSV
    import csv
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if prospects:
            fieldnames = prospects[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(prospects)
    
    return filepath

def parse_french_date(date_str: str) -> Optional[datetime]:
    """Parse une date en français"""
    try:
        # Remplacer les mois français en anglais
        month_mapping = {
            'janvier': 'January', 'février': 'February', 'mars': 'March',
            'avril': 'April', 'mai': 'May', 'juin': 'June',
            'juillet': 'July', 'août': 'August', 'septembre': 'September',
            'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
        }
        
        for fr_month, en_month in month_mapping.items():
            date_str = date_str.replace(fr_month, en_month)
        
        # Parser la date
        return datetime.strptime(date_str, "%d %B %Y")
    except:
        return None

def truncate_text(text: str, max_length: int = 100) -> str:
    """Tronque un texte à une longueur maximale"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def generate_random_delay(min_seconds: int = 1, max_seconds: int = 5) -> float:
    """Génère un délai aléatoire entre deux valeurs"""
    import random
    return random.uniform(min_seconds, max_seconds)

def is_valid_website(url: str) -> bool:
    """Vérifie si une URL de site web est valide"""
    if not url:
        return False
    
    # Vérifier le format de base
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port optionnel
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour qu'il soit valide"""
    # Remplacer les caractères invalides
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Supprimer les espaces au début et à la fin
    filename = filename.strip()
    # Limiter la longueur
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def get_file_size(filepath: str) -> int:
    """Retourne la taille d'un fichier en octets"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_file_size(size_bytes: int) -> str:
    """Formate une taille de fichier pour l'affichage"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
