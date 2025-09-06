import os
import sys
import sqlite3
import logging
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from src.config import get_config
from src.core.database import create_database_engine, db_manager
from src.core.utils import setup_logging, export_prospects_to_excel

def main():
    """Fonction principale pour la migration des données"""
    print("🔄 Migration des données EBUSINESS AI...")
    
    # Configurer le logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Obtenir la configuration
        config = get_config()
        
        # Créer le moteur de base de données
        engine = create_database_engine()
        
        # Exécuter les migrations
        migrations = [
            ("20250617_01_add_prospect_source_field", add_prospect_source_field),
            ("20250617_02_add_email_tracking_fields", add_email_tracking_fields),
            ("20250617_03_create_system_logs_table", create_system_logs_table),
            ("20250617_04_add_potential_score_field", add_potential_score_field),
            ("20250617_05_create_task_schedule_table", create_task_schedule_table),
            ("20250617_06_add_enhanced_prospect_fields", add_enhanced_prospect_fields),
            ("20250617_07_create_indexes", create_indexes),
            ("20250617_08_add_data_enrichment_fields", add_data_enrichment_fields),
            ("20250617_09_update_email_campaign_structure", update_email_campaign_structure),
            ("20250617_10_add_system_config_table", add_system_config_table)
        ]
        
        executed_migrations = []
        failed_migrations = []
        
        for migration_name, migration_func in migrations:
            try:
                print(f"📋 Exécution de la migration : {migration_name}")
                migration_func(engine)
                executed_migrations.append(migration_name)
                print(f"✅ Migration {migration_name} terminée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la migration {migration_name} : {e}")
                print(f"❌ Échec de la migration {migration_name} : {e}")
                failed_migrations.append(migration_name)
        
        # Afficher le résumé
        print("\n" + "="*60)
        print("🔄 RÉSUMÉ DE LA MIGRATION DES DONNÉES")
        print("="*60)
        print(f"✅ Migrations réussies : {len(executed_migrations)}")
        print(f"❌ Migrations échouées : {len(failed_migrations)}")
        
        if executed_migrations:
            print("\n📝 Migrations exécutées :")
            for migration in executed_migrations:
                print(f"   • {migration}")
        
        if failed_migrations:
            print("\n⚠️  Migrations échouées :")
            for migration in failed_migrations:
                print(f"   • {migration}")
        
        # Exporter les données si demandé
        if len(sys.argv) > 1 and sys.argv[1] == "--export":
            export_data(engine)
        
        print("="*60)
        
        if failed_migrations:
            logger.error(f"{len(failed_migrations)} migrations ont échoué")
            return False
        else:
            logger.info("Toutes les migrations ont été exécutées avec succès")
            return True
            
    except Exception as e:
        logger.error(f"Erreur critique lors de la migration : {e}")
        print(f"❌ Erreur critique : {e}")
        return False

def add_prospect_source_field(engine):
    """Ajoute le champ source à la table prospects"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'source' not in columns:
            cursor.execute("ALTER TABLE prospects ADD COLUMN source TEXT DEFAULT 'google_dorks'")
            conn.connection.commit()
            print("   • Champ 'source' ajouté à la table prospects")
        else:
            print("   • Champ 'source' déjà existant dans la table prospects")

def add_email_tracking_fields(engine):
    """Ajoute les champs de tracking email à la table prospects"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ('email_sent', 'BOOLEAN DEFAULT FALSE'),
            ('email_opened', 'BOOLEAN DEFAULT FALSE'),
            ('email_clicked', 'BOOLEAN DEFAULT FALSE'),
            ('email_opened_at', 'TIMESTAMP'),
            ('email_clicked_at', 'TIMESTAMP')
        ]
        
        for field_name, field_def in fields_to_add:
            if field_name not in columns:
                cursor.execute(f"ALTER TABLE prospects ADD COLUMN {field_name} {field_def}")
                conn.connection.commit()
                print(f"   • Champ '{field_name}' ajouté à la table prospects")
            else:
                print(f"   • Champ '{field_name}' déjà existant dans la table prospects")

def create_system_logs_table(engine):
    """Crée la table system_logs"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la table existe déjà
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_logs'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    extra_data TEXT
                )
            """)
            conn.connection.commit()
            print("   • Table 'system_logs' créée")
        else:
            print("   • Table 'system_logs' déjà existante")

def add_potential_score_field(engine):
    """Ajoute le champ potential_score à la table prospects"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'potential_score' not in columns:
            cursor.execute("ALTER TABLE prospects ADD COLUMN potential_score REAL DEFAULT 0.0")
            conn.connection.commit()
            print("   • Champ 'potential_score' ajouté à la table prospects")
        else:
            print("   • Champ 'potential_score' déjà existant dans la table prospects")

def create_task_schedule_table(engine):
    """Crée la table task_schedule"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la table existe déjà
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='task_schedule'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE task_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.connection.commit()
            print("   • Table 'task_schedule' créée")
        else:
            print("   • Table 'task_schedule' déjà existante")

def add_enhanced_prospect_fields(engine):
    """Ajoute des champs améliorés à la table prospects"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ('phone', 'TEXT'),
            ('status', 'TEXT DEFAULT \'nouveau\''),
            ('qualification_score', 'REAL DEFAULT 0.0'),
            ('problem_detected', 'TEXT'),
            ('specificity', 'TEXT'),
            ('date_contacted', 'TIMESTAMP'),
            ('date_responded', 'TIMESTAMP'),
            ('date_audit_booked', 'TIMESTAMP'),
            ('raw_data', 'TEXT')
        ]
        
        for field_name, field_def in fields_to_add:
            if field_name not in columns:
                cursor.execute(f"ALTER TABLE prospects ADD COLUMN {field_name} {field_def}")
                conn.connection.commit()
                print(f"   • Champ '{field_name}' ajouté à la table prospects")
            else:
                print(f"   • Champ '{field_name}' déjà existant dans la table prospects")

def create_indexes(engine):
    """Crée les indexes pour optimiser les performances"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        indexes = [
            "idx_prospects_status",
            "idx_prospects_sector",
            "idx_prospects_country",
            "idx_prospects_date_added",
            "idx_prospects_qualification_score"
        ]
        
        for index_name in indexes:
            table_name = index_name.replace('idx_', '').split('_')[0]
            
            # Vérifier si l'index existe déjà
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='{index_name}' AND tbl_name='{table_name}'
            """)
            
            if not cursor.fetchone():
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({index_name.split('_')[1]})")
                conn.connection.commit()
                print(f"   • Index '{index_name}' créé")
            else:
                print(f"   • Index '{index_name}' déjà existant")

def add_data_enrichment_fields(engine):
    """Ajoute des champs pour l'enrichissement des données"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ('website_title', 'TEXT'),
            ('website_description', 'TEXT'),
            ('website_keywords', 'TEXT'),
            ('has_contact_page', 'BOOLEAN DEFAULT FALSE'),
            ('has_blog', 'BOOLEAN DEFAULT FALSE'),
            ('has_ssl', 'BOOLEAN DEFAULT FALSE'),
            ('technologies', 'TEXT'),
            ('social_media', 'TEXT'),
            ('page_count_estimate', 'INTEGER DEFAULT 1'),
            ('estimated_size', 'TEXT'),
            ('size_confidence', 'REAL DEFAULT 0.0'),
            ('maturity_level', 'TEXT'),
            ('maturity_score', 'REAL DEFAULT 0.0')
        ]
        
        for field_name, field_def in fields_to_add:
            if field_name not in columns:
                cursor.execute(f"ALTER TABLE prospects ADD COLUMN {field_name} {field_def}")
                conn.connection.commit()
                print(f"   • Champ '{field_name}' ajouté à la table prospects")
            else:
                print(f"   • Champ '{field_name}' déjà existant dans la table prospects")

def update_email_campaign_structure(engine):
    """Met à jour la structure de la table email_campaigns"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='email_campaigns'
        """)
        
        if cursor.fetchone():
            # Vérifier les colonnes existantes
            cursor.execute("PRAGMA table_info(email_campaigns)")
            columns = [row[1] for row in cursor.fetchall()]
            
            fields_to_add = [
                ('tracking_id', 'TEXT UNIQUE'),
                ('opened_at', 'TIMESTAMP'),
                ('clicked_at', 'TIMESTAMP')
            ]
            
            for field_name, field_def in fields_to_add:
                if field_name not in columns:
                    if field_name == 'tracking_id':
                        cursor.execute(f"ALTER TABLE email_campaigns ADD COLUMN {field_name} {field_def}")
                    else:
                        cursor.execute(f"ALTER TABLE email_campaigns ADD COLUMN {field_name} {field_def}")
                    conn.connection.commit()
                    print(f"   • Champ '{field_name}' ajouté à la table email_campaigns")
                else:
                    print(f"   • Champ '{field_name}' déjà existant dans la table email_campaigns")
        else:
            print("   • Table 'email_campaigns' n'existe pas, création ignorée")

def add_system_config_table(engine):
    """Crée la table system_config"""
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        
        # Vérifier si la table existe déjà
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_config'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.connection.commit()
            print("   • Table 'system_config' créée")
            
            # Insérer la configuration initiale
            config = get_config()
            initial_config = [
                ('system_version', '1.0.0'),
                ('setup_completed', datetime.now().isoformat()),
                ('database_schema_version', '1.0'),
                ('default_timezone', config.timezone),
                ('max_emails_per_day', str(config.max_emails_per_day)),
                ('email_sending_start', str(config.email_sending_start)),
                ('email_sending_end', str(config.email_sending_end))
            ]
            
            cursor.executemany(
                "INSERT INTO system_config (key, value) VALUES (?, ?)",
                initial_config
            )
            
            conn.connection.commit()
            print("   • Configuration système initiale insérée")
        else:
            print("   • Table 'system_config' déjà existante")

def export_data(engine):
    """Exporte les données actuelles"""
    print("\n📤 Export des données...")
    
    try:
        # Exporter les prospects
        with engine.connect() as conn:
            prospects_df = pd.read_sql("SELECT * FROM prospects", conn)
        
        if not prospects_df.empty:
            export_path = export_prospects_to_excel(prospects_df.to_dict('records'))
            print(f"   • Prospects exportés vers : {export_path}")
        
        # Exporter les campagnes email
        with engine.connect() as conn:
            campaigns_df = pd.read_sql("SELECT * FROM email_campaigns", conn)
        
        if not campaigns_df.empty:
            campaigns_path = f"data/exports/email_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            campaigns_df.to_excel(campaigns_path, index=False)
            print(f"   • Campagnes email exportées vers : {campaigns_path}")
        
        # Exporter les logs système
        with engine.connect() as conn:
            logs_df = pd.read_sql("SELECT * FROM system_logs", conn)
        
        if not logs_df.empty:
            logs_path = f"data/exports/system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            logs_df.to_excel(logs_path, index=False)
            print(f"   • Logs système exportés vers : {logs_path}")
        
        print("✅ Export des données terminé")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export des données : {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
