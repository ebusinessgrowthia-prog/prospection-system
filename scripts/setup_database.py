import os
import sys
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from src.config import get_config
from src.core.database import init_database, create_database_engine, Base
from src.core.utils import setup_logging

def main():
    """Fonction principale pour configurer la base de données"""
    print("🚀 Configuration de la base de données EBUSINESS AI...")
    
    # Configurer le logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Obtenir la configuration
        config = get_config()
        
        # Créer le répertoire de données s'il n'existe pas
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Créer le répertoire des logs s'il n'existe pas
        logs_dir = Path("data/logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Créer le répertoire des exports s'il n'existe pas
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        print(f"📁 Répertoires créés : {data_dir}, {logs_dir}, {exports_dir}")
        
        # Initialiser la base de données
        print("🔧 Initialisation de la base de données...")
        init_database()
        
        # Vérifier que la base de données a été créée
        db_path = Path("data/prospects.db")
        if db_path.exists():
            print(f"✅ Base de données créée avec succès : {db_path}")
        else:
            print("❌ Erreur : La base de données n'a pas été créée")
            return False
        
        # Se connecter à la base de données pour vérifier les tables
        engine = create_database_engine()
        with engine.connect() as conn:
            # Vérifier les tables
            inspector = conn.dialect.get_schema_names(conn)
            tables = conn.dialect.get_table_names(conn, "main")
            
            print(f"📋 Tables créées : {', '.join(tables)}")
            
            # Insérer des données de configuration initiales si nécessaire
            cursor = conn.connection.cursor()
            
            # Vérifier si la table system_config existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='system_config'
            """)
            
            if not cursor.fetchone():
                print("📝 Création de la table de configuration système...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_config (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insérer la configuration initiale
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
                print("✅ Configuration système initiale insérée")
            
            # Vérifier si la table task_schedule existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='task_schedule'
            """)
            
            if not cursor.fetchone():
                print("📝 Création de la table de planification des tâches...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS task_schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_name TEXT NOT NULL,
                        last_run TIMESTAMP,
                        next_run TIMESTAMP,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insérer les tâches initiales
                from src.scheduler.tasks import get_scheduled_tasks
                tasks = get_scheduled_tasks()
                
                task_schedule_data = []
                for task in tasks:
                    task_schedule_data.append((
                        task['id'],
                        None,  # last_run
                        None,  # next_run
                        'pending'
                    ))
                
                cursor.executemany(
                    "INSERT INTO task_schedule (task_name, last_run, next_run, status) VALUES (?, ?, ?, ?)",
                    task_schedule_data
                )
                
                conn.connection.commit()
                print(f"✅ Planification des tâches initialisée avec {len(tasks)} tâches")
            
            # Créer des indexes pour optimiser les performances
            print("🔍 Création des indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_sector ON prospects(sector)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_country ON prospects(country)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_date_added ON prospects(date_added)",
                "CREATE INDEX IF NOT EXISTS idx_email_campaigns_prospect_id ON email_campaigns(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_email_campaigns_tracking_id ON email_campaigns(tracking_id)",
                "CREATE INDEX IF NOT EXISTS idx_email_campaigns_sent_at ON email_campaigns(sent_at)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_module ON system_logs(module)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.connection.commit()
            print("✅ Indexes créés avec succès")
        
        # Afficher un résumé
        print("\n" + "="*50)
        print("🎉 CONFIGURATION DE LA BASE DE DONNÉES TERMINÉE")
        print("="*50)
        print(f"📂 Chemin de la base de données : {db_path.absolute()}")
        print(f"📊 Taille de la base de données : {db_path.stat().st_size} octets")
        print(f"🔧 Moteur de base de données : SQLite")
        print(f"📋 Tables créées : {len(tables)}")
        print(f"🔑 Indexes créés : {len(indexes)}")
        print("="*50)
        
        logger.info("Configuration de la base de données terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de la base de données : {e}")
        print(f"❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
