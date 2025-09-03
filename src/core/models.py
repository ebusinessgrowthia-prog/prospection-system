"""
Modèles de données pour EBUSINESS AI
Définit les structures de données utilisées dans tout le système
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ProspectStatus(str, Enum):
    """Statuts possibles pour un prospect"""
    NOUVEAU = "nouveau"
    QUALIFIE = "qualifié"
    CONTACTE = "contacté"
    REPONDU = "répondu"
    AUDIT_RESERVE = "audit_réservé"
    INACTIF = "inactif"

class ProspectSource(str, Enum):
    """Sources possibles pour un prospect"""
    GOOGLE_DORKS = "google_dorks"
    LINKEDIN = "linkedin"
    WEBSITE_SCRAPING = "website_scraping"
    MANUAL = "manual"
    IMPORT = "import"

@dataclass
class ProspectData:
    """Structure de données pour un prospect"""
    name: str
    company: str
    email: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    status: ProspectStatus = ProspectStatus.NOUVEAU
    qualification_score: float = 0.0
    problem_detected: Optional[str] = None
    specificity: Optional[str] = None
    source: ProspectSource = ProspectSource.GOOGLE_DORKS
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'sector': self.sector,
            'country': self.country,
            'website': self.website,
            'phone': self.phone,
            'status': self.status.value,
            'qualification_score': self.qualification_score,
            'problem_detected': self.problem_detected,
            'specificity': self.specificity,
            'source': self.source.value,
            'raw_data': self.raw_data
        }

@dataclass
class EmailCampaignData:
    """Structure de données pour une campagne email"""
    prospect_id: int
    subject: str
    content: str
    tracking_id: str
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'prospect_id': self.prospect_id,
            'subject': self.subject,
            'content': self.content,
            'tracking_id': self.tracking_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }

@dataclass
class SystemStats:
    """Structure de données pour les statistiques système"""
    prospects_total: int = 0
    prospects_qualified: int = 0
    prospects_contacted: int = 0
    prospects_responded: int = 0
    prospects_audit_booked: int = 0
    emails_total: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    by_country: Dict[str, int] = field(default_factory=dict)
    by_sector: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'prospects': {
                'total': self.prospects_total,
                'qualified': self.prospects_qualified,
                'contacted': self.prospects_contacted,
                'responded': self.prospects_responded,
                'audit_booked': self.prospects_audit_booked
            },
            'emails': {
                'total': self.emails_total,
                'opened': self.emails_opened,
                'clicked': self.emails_clicked,
                'open_rate': self.open_rate,
                'click_rate': self.click_rate
            },
            'by_country': self.by_country,
            'by_sector': self.by_sector
        }

@dataclass
class ScrapingResult:
    """Structure de données pour les résultats de scraping"""
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    source: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'source': self.source,
            'scraped_at': self.scraped_at.isoformat()
        }

@dataclass
class QualificationResult:
    """Structure de données pour les résultats de qualification"""
    prospect_id: int
    qualified: bool
    score: float
    reasons: List[str] = field(default_factory=list)
    detected_problems: List[str] = field(default_factory=list)
    specificities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'prospect_id': self.prospect_id,
            'qualified': self.qualified,
            'score': self.score,
            'reasons': self.reasons,
            'detected_problems': self.detected_problems,
            'specificities': self.specificities
        }

@dataclass
class EmailGenerationResult:
    """Structure de données pour les résultats de génération d'email"""
    success: bool
    prospect_id: int
    subject: str
    content: str
    error: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'success': self.success,
            'prospect_id': self.prospect_id,
            'subject': self.subject,
            'content': self.content,
            'error': self.error,
            'generated_at': self.generated_at.isoformat()
        }

@dataclass
class EmailSendingResult:
    """Structure de données pour les résultats d'envoi d'email"""
    success: bool
    prospect_id: int
    email_address: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'success': self.success,
            'prospect_id': self.prospect_id,
            'email_address': self.email_address,
            'message_id': self.message_id,
            'error': self.error,
            'sent_at': self.sent_at.isoformat()
        }
