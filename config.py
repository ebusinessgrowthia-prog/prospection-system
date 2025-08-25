import os
from dotenv import load_dotenv

load_dotenv()

# Configuration Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configuration SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Configuration Abstract API
ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")

# Configuration Hunter
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

# Configuration Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv("GOOGLE_SHEETS_SPREADSHEET_NAME", "Prospection")

# Configuration Email
FROM_EMAIL_1 = os.getenv("FROM_EMAIL_1", "ebusinessgrowthia@gmail.com")
FROM_NAME_1 = os.getenv("FROM_NAME_1", "EBUSINESS GROWTH")
FROM_EMAIL_2 = os.getenv("FROM_EMAIL_2", "ia.ebusinessag@gmail.com")
FROM_NAME_2 = os.getenv("FROM_NAME_2", "EBUSINESS IA")
DAILY_EMAIL_LIMIT = int(os.getenv("DAILY_EMAIL_LIMIT", "100"))

# Configuration Scraping
MAX_DORKS_PER_CAMPAIGN = int(os.getenv("MAX_DORKS_PER_CAMPAIGN", "50"))
MAX_PROSPECTS_PER_DORK = int(os.getenv("MAX_PROSPECTS_PER_DORK", "20"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))

# Configuration Validation
EMAIL_VALIDATION_THRESHOLD = float(os.getenv("EMAIL_VALIDATION_THRESHOLD", "0.8"))
MAX_VALIDATION_RETRIES = int(os.getenv("MAX_VALIDATION_RETRIES", "3"))

# Configuration RGPD
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "90"))
UNSUBSCRIBE_LINK = os.getenv("UNSUBSCRIBE_LINK", "%%unsubscribe%%")

# Configuration Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "prospection.log")

# Configuration Render
PORT = int(os.getenv("PORT", "5000"))
FLASK_ENV = os.getenv("FLASK_ENV", "production")
