import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging
from config import GOOGLE_SHEETS_CREDENTIALS_FILE, GOOGLE_SHEETS_SPREADSHEET_NAME

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.connect()
    
    def connect(self):
        """Établit la connexion à Google Sheets"""
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_FILE, 
                scopes=scope
            )
            self.client = gspread.authorize(creds)
            
            try:
                self.spreadsheet = self.client.open(GOOGLE_SHEETS_SPREADSHEET_NAME)
                logger.info("Connecté à Google Sheets avec succès")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(GOOGLE_SHEETS_SPREADSHEET_NAME)
                self.create_worksheets()
                logger.info("Feuille de calcul créée avec succès")
                
        except Exception as e:
            logger.error(f"Erreur de connexion à Google Sheets: {e}")
            raise
    
    def create_worksheets(self):
        """Crée les onglets nécessaires"""
        worksheets = [
            ("Prospects", [
                "ID", "Nom", "Email", "Entreprise", "Secteur", "Agence", 
                "Statut", "Date Découverte", "Score Validation", "Date Contact"
            ]),
            ("Emails_Envoyés", [
                "ID", "Prospect ID", "Agence", "Date Envoi", "Sujet", 
                "Statut", "Ouvert", "Clic", "Réponse"
            ]),
            ("Performance", [
                "Date", "Agence", "Emails Envoyés", "Ouverts", "Réponses", 
                "Taux Ouverture", "Taux Réponse", "Taux Conversion"
            ]),
            ("Campagnes", [
                "ID", "Agence", "Date Début", "Date Fin", "Statut", 
                "Emails Envoyés", "Taux Réponse"
            ])
        ]
        
        for name, headers in worksheets:
            try:
                worksheet = self.spreadsheet.add_worksheet(title=name, rows="1000", cols="20")
                worksheet.append_row(headers)
                logger.info(f"Onglet créé: {name}")
            except:
                logger.info(f"L'onglet {name} existe déjà")
    
    def store_prospects(self, prospects, agency_name):
        """Stocke les prospects dans Google Sheets"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            
            for prospect in prospects:
                # Vérifier si le prospect existe déjà
                try:
                    existing = worksheet.find(prospect["email"])
                except:
                    existing = None
                    
                if not existing:
                    row = [
                        prospect["id"],
                        prospect["name"],
                        prospect["email"],
                        prospect["company"],
                        prospect["sector"],
                        agency_name,
                        prospect["status"],
                        prospect["date_discovered"],
                        prospect["validation_score"],
                        datetime.now().strftime("%Y-%m-%d")
                    ]
                    worksheet.append_row(row)
                    
        except Exception as e:
            logger.error(f"Erreur lors du stockage des prospects: {e}")
    
    def store_email_sent(self, email, agency_name, content):
        """Enregistre un email envoyé"""
        try:
            worksheet = self.spreadsheet.worksheet("Emails_Envoyés")
            row = [
                f"{email}_{datetime.now().timestamp()}",
                email,
                agency_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Email personnalisé",
                "Envoyé",
                False,
                False,
                False
            ]
            worksheet.append_row(row)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'email: {e}")
    
    def get_prospects_by_agency(self, agency_name):
        """Récupère les prospects par agence"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            records = worksheet.get_all_records()
            return [r for r in records if r.get("Agence") == agency_name]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des prospects: {e}")
            return []
    
    def update_email_status(self, email_id, status):
        """Met à jour le statut d'un email"""
        try:
            worksheet = self.spreadsheet.worksheet("Emails_Envoyés")
            cell = worksheet.find(email_id)
            if cell:
                worksheet.update_cell(cell.row, 6, status)  # Colonne Statut
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
    
    def track_performance(self, agency_name, metrics):
        """Enregistre les performances"""
        try:
            worksheet = self.spreadsheet.worksheet("Performance")
            row = [
                datetime.now().strftime("%Y-%m-%d"),
                agency_name,
                metrics.get("emails_sent", 0),
                metrics.get("opened", 0),
                metrics.get("replied", 0),
                metrics.get("open_rate", 0),
                metrics.get("reply_rate", 0),
                metrics.get("conversion_rate", 0)
            ]
            worksheet.append_row(row)
        except Exception as e:
            logger.error(f"Erreur lors du suivi des performances: {e}")
