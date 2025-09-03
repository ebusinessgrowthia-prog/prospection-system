"""
Gestion de la base de données SQLite pour EBUSINESS AI
Création, initialisation et opérations sur la base de données
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

# Création de la base SQLAlchemy
Base = declarative_base()

class Prospect(Base):
    """Modèle de données pour les prospects"""
    __tablename__ = 'prospects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Statut et qualification
    status = Column(String(50), default='nouveau')  # nouveau, qualifié, contacté, répondu, audit_réservé
    qualification_score = Column(Float, default=0.0)
    problem_detected = Column(Text, nullable=True)
    specificity = Column(Text, nullable=True)
    
    # Dates
    date_added = Column(DateTime, default=datetime.utcnow)
    date_contacted = Column(DateTime, nullable=True)
    date_responded = Column(DateTime, nullable=True)
    date_audit_booked = Column(DateTime, nullable=True)
    
    # Email tracking
    email_sent = Column(Boolean, default=False)
    email_opened = Column(Boolean, default=False)
    email_clicked = Column(Boolean, default=False)
    email_opened_at = Column(DateTime, nullable=True)
    email_clicked_at = Column(DateTime, nullable=True)
    
    # Données supplémentaires
    source = Column(String(100), default='google_dorks')
    raw_data = Column(Text, nullable=True)  # JSON pour les données brutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le prospect en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'sector': self.sector,
            'country': self.country,
            'website': self.website,
            'phone': self.phone,
            'status': self.status,
            'qualification_score': self.qualification_score,
            'problem_detected': self.problem_detected,
            'specificity': self.specificity,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'date_contacted': self.date_contacted.isoformat() if self.date_contacted else None,
            'date_responded': self.date_responded.isoformat() if self.date_responded else None,
            'date_audit_booked': self.date_audit_booked.isoformat() if self.date_audit_booked else None,
            'email_sent': self.email_sent,
            'email_opened': self.email_opened,
            'email_clicked': self.email_clicked,
            'email_opened_at': self.email_opened_at.isoformat() if self.email_opened_at else None,
            'email_clicked_at': self.email_clicked_at.isoformat() if self.email_clicked_at else None,
            'source': self.source
        }

class EmailCampaign(Base):
    """Modèle pour le suivi des campagnes email"""
    __tablename__ = 'email_campaigns'
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, nullable=False)
    subject = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    tracking_id = Column(String(100), unique=True, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la campagne en dictionnaire"""
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'subject': self.subject,
            'content': self.content,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'tracking_id': self.tracking_id
        }

class SystemLog(Base):
    """Modèle pour le logging du système"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(Text, nullable=True)  # JSON

# Création du moteur de base de données
def create_database_engine():
    """Crée et retourne le moteur de base de données"""
    db_url = config.database_url
    
    # S'assurer que le répertoire data existe
    import os
    os.makedirs('data', exist_ok=True)
    
    engine = create_engine(db_url, echo=config.debug_mode)
    return engine

# Création de la session factory
def create_session_factory():
    """Crée la factory de sessions"""
    engine = create_database_engine()
    return sessionmaker(bind=engine)

# Initialisation de la base de données
def init_database():
    """Initialise la base de données et crée les tables"""
    try:
        engine = create_database_engine()
        Base.metadata.create_all(engine)
        logger.info("✅ Base de données initialisée avec succès")
        
        # Créer les répertoires nécessaires
        import os
        os.makedirs('data/logs', exist_ok=True)
        os.makedirs('data/exports', exist_ok=True)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

# Classe de gestion de la base de données
class DatabaseManager:
    """Gestionnaire principal des opérations de base de données"""
    
    def __init__(self):
        self.SessionLocal = create_session_factory()
    
    def get_session(self) -> Session:
        """Retourne une session de base de données"""
        return self.SessionLocal()
    
    def add_prospect(self, prospect_data: Dict[str, Any]) -> Optional[Prospect]:
        """Ajoute un nouveau prospect à la base de données"""
        try:
            with self.get_session() as session:
                # Vérifier si le prospect existe déjà (par email ou website)
                existing = session.query(Prospect).filter(
                    (Prospect.email == prospect_data.get('email')) |
                    (Prospect.website == prospect_data.get('website'))
                ).first()
                
                if existing:
                    logger.info(f"Prospect déjà existant: {prospect_data.get('email')}")
                    return existing
                
                # Créer le nouveau prospect
                prospect = Prospect(**prospect_data)
                session.add(prospect)
                session.commit()
                session.refresh(prospect)
                
                logger.info(f"✅ Nouveau prospect ajouté: {prospect.name} - {prospect.company}")
                return prospect
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du prospect: {e}")
            return None
    
    def get_prospects(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Prospect]:
        """Récupère la liste des prospects, avec filtrage optionnel"""
        try:
            with self.get_session() as session:
                query = session.query(Prospect)
                
                if status:
                    query = query.filter(Prospect.status == status)
                
                if limit:
                    query = query.limit(limit)
                
                prospects = query.order_by(Prospect.date_added.desc()).all()
                return prospects
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des prospects: {e}")
            return []
    
    def update_prospect(self, prospect_id: int, updates: Dict[str, Any]) -> bool:
        """Met à jour un prospect"""
        try:
            with self.get_session() as session:
                prospect = session.query(Prospect).filter(Prospect.id == prospect_id).first()
                
                if not prospect:
                    logger.warning(f"Prospect non trouvé: {prospect_id}")
                    return False
                
                # Mise à jour des champs
                for key, value in updates.items():
                    if hasattr(prospect, key):
                        setattr(prospect, key, value)
                
                session.commit()
                logger.info(f"✅ Prospect mis à jour: {prospect_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du prospect: {e}")
            return False
    
    def get_prospects_to_contact(self, limit: int = 10) -> List[Prospect]:
        """Récupère les prospects à contacter (qualifiés et non encore contactés)"""
        try:
            with self.get_session() as session:
                prospects = session.query(Prospect).filter(
                    Prospect.status == 'qualifié',
                    Prospect.email_sent == False,
                    Prospect.email.isnot(None)
                ).order_by(Prospect.qualification_score.desc()).limit(limit).all()
                
                return prospects
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des prospects à contacter: {e}")
            return []
    
    def add_email_campaign(self, campaign_data: Dict[str, Any]) -> Optional[EmailCampaign]:
        """Ajoute une campagne email à la base de données"""
        try:
            with self.get_session() as session:
                campaign = EmailCampaign(**campaign_data)
                session.add(campaign)
                session.commit()
                session.refresh(campaign)
                
                logger.info(f"✅ Campagne email ajoutée pour le prospect {campaign.prospect_id}")
                return campaign
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout de la campagne email: {e}")
            return None
    
    def update_email_campaign(self, tracking_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour une campagne email (pour le tracking)"""
        try:
            with self.get_session() as session:
                campaign = session.query(EmailCampaign).filter(
                    EmailCampaign.tracking_id == tracking_id
                ).first()
                
                if not campaign:
                    logger.warning(f"Campagne non trouvée: {tracking_id}")
                    return False
                
                # Mise à jour des champs
                for key, value in updates.items():
                    if hasattr(campaign, key):
                        setattr(campaign, key, value)
                
                session.commit()
                logger.info(f"✅ Campagne email mise à jour: {tracking_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour de la campagne email: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        try:
            with self.get_session() as session:
                # Statistiques des prospects
                total_prospects = session.query(Prospect).count()
                qualified_prospects = session.query(Prospect).filter(Prospect.status == 'qualifié').count()
                contacted_prospects = session.query(Prospect).filter(Prospect.email_sent == True).count()
                responded_prospects = session.query(Prospect).filter(Prospect.email_opened == True).count()
                audit_booked = session.query(Prospect).filter(Prospect.status == 'audit_réservé').count()
                
                # Statistiques des emails
                total_emails = session.query(EmailCampaign).count()
                opened_emails = session.query(EmailCampaign).filter(EmailCampaign.opened_at.isnot(None)).count()
                clicked_emails = session.query(EmailCampaign).filter(EmailCampaign.clicked_at.isnot(None)).count()
                
                # Calcul des taux
                open_rate = (opened_emails / total_emails * 100) if total_emails > 0 else 0
                click_rate = (clicked_emails / opened_emails * 100) if opened_emails > 0 else 0
                
                # Prospects par pays
                prospects_by_country = session.query(
                    Prospect.country,
                    func.count(Prospect.id)
                ).group_by(Prospect.country).all()
                
                # Prospects par secteur
                prospects_by_sector = session.query(
                    Prospect.sector,
                    func.count(Prospect.id)
                ).group_by(Prospect.sector).all()
                
                return {
                    'prospects': {
                        'total': total_prospects,
                        'qualified': qualified_prospects,
                        'contacted': contacted_prospects,
                        'responded': responded_prospects,
                        'audit_booked': audit_booked
                    },
                    'emails': {
                        'total': total_emails,
                        'opened': opened_emails,
                        'clicked': clicked_emails,
                        'open_rate': round(open_rate, 2),
                        'click_rate': round(click_rate, 2)
                    },
                    'by_country': dict(prospects_by_country),
                    'by_sector': dict(prospects_by_sector)
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    def log_system_event(self, level: str, message: str, module: str = None, extra_data: Dict = None):
        """Ajoute un événement système au log"""
        try:
            with self.get_session() as session:
                log_entry = SystemLog(
                    level=level,
                    message=message,
                    module=module,
                    extra_data=json.dumps(extra_data) if extra_data else None
                )
                session.add(log_entry)
                session.commit()
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du logging de l'événement: {e}")

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

# Fonctions utilitaires pour la compatibilité
def get_system_stats() -> Dict[str, Any]:
    """Retourne les statistiques du système (pour FastAPI)"""
    return db_manager.get_system_stats()

# Fonction d'initialisation pour l'import
def init_db():
    """Initialise la base de données (alias pour init_database)"""
    init_database()
