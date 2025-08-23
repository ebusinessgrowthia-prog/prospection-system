import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', 'your-sendgrid-api-key-here')
ABSTRACT_API_KEY = os.getenv('ABSTRACT_API_KEY', 'your-abstract-api-key-here')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY', 'your-hunter-api-key-here')

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv('GOOGLE_SHEETS_SPREADSHEET_NAME', 'Prospection')
GOOGLE_SHEETS_WORKSHEETS = {
    'prospects': 'Prospects',
    'emails': 'Emails',
    'performance': 'Performance',
    'optimisation': 'Optimisation'
}

# Email Configuration
FROM_EMAIL = os.getenv('FROM_EMAIL', 'prospection@votredomaine.com')
FROM_NAME = os.getenv('FROM_NAME', 'Agence Digitale Pro')
DAILY_EMAIL_LIMIT = int(os.getenv('DAILY_EMAIL_LIMIT', '100'))

# Scraping Configuration
MAX_DORKS_PER_CAMPAIGN = int(os.getenv('MAX_DORKS_PER_CAMPAIGN', '50'))
MAX_PROSPECTS_PER_DORK = int(os.getenv('MAX_PROSPECTS_PER_DORK', '20'))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))

# Validation Configuration
EMAIL_VALIDATION_THRESHOLD = float(os.getenv('EMAIL_VALIDATION_THRESHOLD', '0.8'))
MAX_VALIDATION_RETRIES = int(os.getenv('MAX_VALIDATION_RETRIES', '3'))

# RGPD Configuration
RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', '90'))
UNSUBSCRIBE_LINK = os.getenv('UNSUBSCRIBE_LINK', 'https://votredomaine.com/unsubscribe')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'prospection.log')