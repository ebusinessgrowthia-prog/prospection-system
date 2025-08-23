import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_file: str, spreadsheet_name: str):
        """Initialize Google Sheets connection"""
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.spreadsheet = None
        self._connect()
        
    def _connect(self):
        """Establish connection to Google Sheets"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open(self.spreadsheet_name)
            logger.info("Successfully connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def create_worksheets(self, schema: Dict[str, Dict[str, List[str]]]):
        """Create worksheets based on schema"""
        for worksheet_name, config in schema.items():
            try:
                try:
                    worksheet = self.spreadsheet.worksheet(worksheet_name)
                    logger.info(f"Worksheet '{worksheet_name}' already exists")
                except gspread.WorksheetNotFound:
                    worksheet = self.spreadsheet.add_worksheet(
                        title=worksheet_name,
                        rows=1000,
                        cols=len(config['columns'])
                    )
                    worksheet.append_row(config['column_headers'])
                    logger.info(f"Created worksheet '{worksheet_name}'")
                    
            except Exception as e:
                logger.error(f"Error creating worksheet '{worksheet_name}': {e}")
    
    def add_prospect(self, prospect_data: Dict[str, Any]) -> bool:
        """Add a new prospect to the Prospects worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            
            # Check for duplicates
            existing_emails = worksheet.col_values(3)[1:]  # Column C (Email)
            if prospect_data.get('email', '').lower() in [e.lower() for e in existing_emails]:
                logger.info(f"Prospect with email {prospect_data['email']} already exists")
                return False
            
            # Prepare row data
            row_data = [
                str(datetime.now().timestamp()),  # ID
                prospect_data.get('nom_complet', ''),
                prospect_data.get('email', ''),
                prospect_data.get('entreprise', ''),
                prospect_data.get('secteur', ''),
                prospect_data.get('url_site', ''),
                prospect_data.get('source', ''),
                datetime.now().isoformat(),
                prospect_data.get('score_validation', 0),
                prospect_data.get('statut_validation', 'PENDING'),
                'NEW',
                '',
                0,
                '',
                '',
                prospect_data.get('tags', ''),
                prospect_data.get('notes', '')
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"Added prospect: {prospect_data.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding prospect: {e}")
            return False
    
    def update_prospect_status(self, email: str, status: str, notes: str = "") -> bool:
        """Update prospect status"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            
            # Find the row
            cell = worksheet.find(email)
            if cell:
                row = cell.row
                worksheet.update_cell(row, 11, status)  # Status column
                if notes:
                    current_notes = worksheet.cell(row, 17).value or ""
                    new_notes = f"{current_notes}\n{notes}".strip()
                    worksheet.update_cell(row, 17, new_notes)
                return True
                
            logger.warning(f"Prospect with email {email} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating prospect status: {e}")
            return False
    
    def get_prospects_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get prospects by status"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            records = worksheet.get_all_records()
            return [r for r in records if r.get('Statut Prospection') == status]
            
        except Exception as e:
            logger.error(f"Error getting prospects by status: {e}")
            return []
    
    def add_email_record(self, email_data: Dict[str, Any]) -> bool:
        """Add email record to Emails worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet("Emails")
            
            row_data = [
                str(datetime.now().timestamp()),  # ID
                email_data.get('prospect_id', ''),
                email_data.get('objet', ''),
                email_data.get('corps', ''),
                datetime.now().isoformat(),
                email_data.get('statut', 'SENT'),
                email_data.get('ouvert', False),
                email_data.get('clic', False),
                email_data.get('reponse', ''),
                email_data.get('bounce', False),
                email_data.get('variant', 'A'),
                email_data.get('score_personnalisation', 0)
            ]
            
            worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            logger.error(f"Error adding email record: {e}")
            return False
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Update performance metrics"""
        try:
            worksheet = self.spreadsheet.worksheet("Performance")
            
            row_data = [
                datetime.now().date().isoformat(),
                metrics.get('campagnes_envoyees', 0),
                metrics.get('emails_envoyes', 0),
                metrics.get('taux_ouverture', 0),
                metrics.get('taux_clic', 0),
                metrics.get('taux_reponse', 0),
                metrics.get('taux_bounce', 0),
                metrics.get('nouveaux_prospects', 0),
                metrics.get('prospects_valides', 0)
            ]
            
            worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            return False
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily statistics"""
        try:
            worksheet = self.spreadsheet.worksheet("Performance")
            records = worksheet.get_all_records()
            
            if not records:
                return {}
                
            today = datetime.now().date().isoformat()
            today_records = [r for r in records if str(r.get('Date', '')) == today]
            
            if today_records:
                return today_records[-1]
                
            return {}
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}
    
    def export_prospects(self, status: Optional[str] = None) -> pd.DataFrame:
        """Export prospects to DataFrame"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            records = worksheet.get_all_records()
            
            if status:
                records = [r for r in records if r.get('Statut Prospection') == status]
                
            return pd.DataFrame(records)
            
        except Exception as e:
            logger.error(f"Error exporting prospects: {e}")
            return pd.DataFrame()
    
    def cleanup_duplicates(self) -> int:
        """Remove duplicate prospects based on email"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            records = worksheet.get_all_records()
            
            seen_emails = set()
            duplicates = []
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (skip header)
                email = record.get('Email', '').lower()
                if email in seen_emails:
                    duplicates.append(i)
                else:
                    seen_emails.add(email)
            
            # Remove duplicates (in reverse order to maintain row numbers)
            for row_num in reversed(duplicates):
                worksheet.delete_rows(row_num)
                
            logger.info(f"Removed {len(duplicates)} duplicate prospects")
            return len(duplicates)
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            return 0