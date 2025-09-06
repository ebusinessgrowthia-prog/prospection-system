

### scripts/backup.py
```python
import os
import sys
import sqlite3
import shutil
import gzip
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from src.config import get_config
from src.core.database import create_database_engine, db_manager
from src.core.utils import setup_logging

def main():
    """Fonction principale pour la sauvegarde du système"""
    print("💾 Sauvegarde du système EBUSINESS AI...")
    
    # Configurer le logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Obtenir la configuration
        config = get_config()
        
        # Créer le répertoire de sauvegardes
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Générer le nom de fichier de sauvegarde
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"ebusiness_ai_backup_{timestamp}"
        
        # Exécuter les sauvegardes
        backup_results = []
        
        # Sauvegarde de la base de données
        db_backup = backup_database(backup_dir, backup_filename)
        backup_results.append(("Base de données", db_backup))
        
        # Sauvegarde des logs
        logs_backup = backup_logs(backup_dir, backup_filename)
        backup_results.append(("Logs système", logs_backup))
        
        # Sauvegarde des exports
        exports_backup = backup_exports(backup_dir, backup_filename)
        backup_results.append(("Exports", exports_backup))
        
        # Sauvegarde de la configuration
        config_backup = backup_configuration(backup_dir, backup_filename)
        backup_results.append(("Configuration", config_backup))
        
        # Nettoyer les anciennes sauvegardes
        cleanup_old_backups(backup_dir)
        
        # Créer le fichier de métadonnées
        metadata = create_backup_metadata(backup_dir, backup_filename, backup_results)
        
        # Afficher le résumé
        print("\n" + "="*60)
        print("💾 RÉSUMÉ DE LA SAUVEGARDE")
        print("="*60)
        print(f"📂 Répertoire de sauvegarde : {backup_dir.absolute()}")
        print(f"📅 Date de sauvegarde : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for component, result in backup_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {component} : {result['message']}")
        
        print(f"📊 Taille totale de la sauvegarde : {metadata['total_size_mb']:.2f} MB")
        print("="*60)
        
        # Logger le résultat
        success = all(result["success"] for result in backup_results)
        
        if success:
            logger.info("Sauvegarde du système terminée avec succès")
            print("✅ Sauvegarde terminée avec succès")
        else:
            logger.error("Échec de la sauvegarde du système")
            print("❌ Échec de la sauvegarde")
        
        return success
        
    except Exception as e:
        logger.error(f"Erreur critique lors de la sauvegarde : {e}")
        print(f"❌ Erreur critique : {e}")
        return False

def backup_database(backup_dir: Path, backup_filename: str) -> dict:
    """Sauvegarde la base de données SQLite"""
    try:
        source_path = Path("data/prospects.db")
        
        if not source_path.exists():
            return {
                "success": False,
                "message": "Base de données non trouvée",
                "size_bytes": 0
            }
        
        # Créer la sauvegarde
        backup_path = backup_dir / f"{backup_filename}_database.db"
        
        # Copier la base de données
        shutil.copy2(source_path, backup_path)
        
        # Compresser la sauvegarde
        compressed_path = backup_path.with_suffix('.db.gz')
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Supprimer le fichier non compressé
        backup_path.unlink()
        
        # Calculer le hash du fichier
        file_hash = calculate_file_hash(compressed_path)
        
        # Vérifier l'intégrité
        verify_result = verify_database_integrity(compressed_path)
        
        return {
            "success": True,
            "message": f"Sauvegardée vers {compressed_path.name}",
            "size_bytes": compressed_path.stat().st_size,
            "hash": file_hash,
            "integrity_check": verify_result,
            "path": str(compressed_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur : {str(e)}",
            "size_bytes": 0
        }

def backup_logs(backup_dir: Path, backup_filename: str) -> dict:
    """Sauvegarde les fichiers de logs"""
    try:
        logs_dir = Path("data/logs")
        
        if not logs_dir.exists():
            return {
                "success": False,
                "message": "Répertoire de logs non trouvé",
                "size_bytes": 0
            }
        
        # Créer l'archive de logs
        backup_path = backup_dir / f"{backup_filename}_logs.tar.gz"
        
        # Créer l'archive
        shutil.make_archive(
            str(backup_path).replace('.tar.gz', ''),
            'gztar',
            logs_dir
        )
        
        # Calculer le hash
        file_hash = calculate_file_hash(backup_path)
        
        return {
            "success": True,
            "message": f"Logs sauvegardés vers {backup_path.name}",
            "size_bytes": backup_path.stat().st_size,
            "hash": file_hash,
            "path": str(backup_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur : {str(e)}",
            "size_bytes": 0
        }

def backup_exports(backup_dir: Path, backup_filename: str) -> dict:
    """Sauvegarde les fichiers d'export"""
    try:
        exports_dir = Path("data/exports")
        
        if not exports_dir.exists():
            return {
                "success": False,
                "message": "Répertoire d'exports non trouvé",
                "size_bytes": 0
            }
        
        # Créer l'archive d'exports
        backup_path = backup_dir / f"{backup_filename}_exports.tar.gz"
        
        # Créer l'archive
        shutil.make_archive(
            str(backup_path).replace('.tar.gz', ''),
            'gztar',
            exports_dir
        )
        
        # Calculer le hash
        file_hash = calculate_file_hash(backup_path)
        
        return {
            "success": True,
            "message": f"Exports sauvegardés vers {backup_path.name}",
            "size_bytes": backup_path.stat().st_size,
            "hash": file_hash,
            "path": str(backup_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur : {str(e)}",
            "size_bytes": 0
        }

def backup_configuration(backup_dir: Path, backup_filename: str) -> dict:
    """Sauvegarde la configuration du système"""
    try:
        config_data = {
            "backup_timestamp": datetime.now().isoformat(),
            "system_config": {},
            "environment_variables": {},
            "file_hashes": {}
        }
        
        # Sauvegarder la configuration de la base de données
        try:
            engine = create_database_engine()
            with engine.connect() as conn:
                result = conn.execute("SELECT * FROM system_config").fetchall()
                config_data["system_config"] = {row[0]: row[1] for row in result}
        except Exception as e:
            config_data["system_config"] = {"error": str(e)}
        
        # Sauvegarder les variables d'environnement (sans les mots de passe)
        config = get_config()
        safe_config = {
            "target_sectors": config.target_sectors,
            "target_countries": config.target_countries,
            "email_sending_days": config.email_sending_days,
            "email_sending_start": config.email_sending_start,
            "email_sending_end": config.email_sending_end,
            "max_emails_per_day": config.max_emails_per_day,
            "delay_between_emails": config.delay_between_emails,
            "search_frequency_hours": config.search_frequency_hours,
            "timezone": config.timezone,
            "debug_mode": config.debug_mode,
            "log_level": config.log_level
        }
        config_data["environment_variables"] = safe_config
        
        # Calculer les hashes des fichiers importants
        important_files = [
            "requirements.txt",
            "render.yaml",
            ".python-version",
            "src/config.py",
            "src/main.py"
        ]
        
        for file_path in important_files:
            path = Path(file_path)
            if path.exists():
                config_data["file_hashes"][file_path] = calculate_file_hash(path)
        
        # Sauvegarder la configuration
        backup_path = backup_dir / f"{backup_filename}_config.json"
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        # Calculer le hash
        file_hash = calculate_file_hash(backup_path)
        
        return {
            "success": True,
            "message": f"Configuration sauvegardée vers {backup_path.name}",
            "size_bytes": backup_path.stat().st_size,
            "hash": file_hash,
            "path": str(backup_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur : {str(e)}",
            "size_bytes": 0
        }

def calculate_file_hash(file_path: Path) -> str:
    """Calcule le hash SHA-256 d'un fichier"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception:
        return "error"

def verify_database_integrity(db_path: Path) -> bool:
    """Vérifie l'intégrité de la base de données sauvegardée"""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # Exécuter une requête simple pour vérifier l'intégrité
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        conn.close()
        return len(tables) > 0
        
    except Exception:
        return False

def cleanup_old_backups(backup_dir: Path):
    """Nettoie les anciennes sauvegardes (garde les 30 derniers jours)"""
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for backup_file in backup_dir.glob("*"):
            if backup_file.is_file():
                # Extraire la date du nom du fichier
                try:
                    # Format: ebusiness_ai_backup_YYYYMMDD_HHMMSS_*
                    parts = backup_file.stem.split('_')
                    if len(parts) >= 4 and parts[0] == 'ebusinessai' and parts[1] == 'backup':
                        date_str = f"{parts[2][:8]}_{parts[3][:6]}"
                        file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                        
                        if file_date < cutoff_date:
                            backup_file.unlink()
                            print(f"   • Ancienne sauvegarde supprimée : {backup_file.name}")
                except:
                    continue
                    
    except Exception as e:
        print(f"   • Avertissement : Erreur lors du nettoyage des anciennes sauvegardes : {e}")

def create_backup_metadata(backup_dir: Path, backup_filename: str, backup_results: list) -> dict:
    """Crée le fichier de métadonnées de la sauvegarde"""
    try:
        metadata = {
            "backup_filename": backup_filename,
            "backup_timestamp": datetime.now().isoformat(),
            "components": {},
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "success": True
        }
        
        total_size = 0
        
        for component, result in backup_results:
            metadata["components"][component] = {
                "success": result["success"],
                "message": result["message"],
                "size_bytes": result["size_bytes"],
                "hash": result.get("hash", "")
            }
            
            if result["success"]:
                total_size += result["size_bytes"]
        
        metadata["total_size_bytes"] = total_size
        metadata["total_size_mb"] = total_size / (1024 * 1024)
        metadata["success"] = all(result["success"] for result in backup_results)
        
        # Sauvegarder les métadonnées
        metadata_path = backup_dir / f"{backup_filename}_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata
        
    except Exception as e:
        print(f"   • Avertissement : Erreur lors de la création des métadonnées : {e}")
        return {"error": str(e)}

def schedule_backup():
    """Planifie les sauvegardes automatiques"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from src.config import get_config
        
        config = get_config()
        
        scheduler = BackgroundScheduler()
        
        # Sauvegarde quotidienne à 2h du matin
        scheduler.add_job(
            main,
            'cron',
            hour=2,
            minute=0,
            id='daily_backup',
            name='Sauvegarde quotidienne'
        )
        
        # Sauvegarde hebdomadaire le dimanche à 3h du matin
        scheduler.add_job(
            main,
            'cron',
            day_of_week='sun',
            hour=3,
            minute=0,
            id='weekly_backup',
            name='Sauvegarde hebdomadaire'
        )
        
        scheduler.start()
        print("📅 Planification des sauvegardes activée")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Erreur lors de la planification des sauvegardes : {e}")
        return None

if __name__ == "__main__":
    # Exécuter la sauvegarde
    success = main()
    
    # Si l'argument --schedule est passé, démarrer la planification
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        scheduler = schedule_backup()
        if scheduler:
            try:
                # Garder le script en cours d'exécution
                import time
                while True:
                    time.sleep(3600)  # Vérifier toutes les heures
            except KeyboardInterrupt:
                print("\n🛑 Arrêt de la planification des sauvegardes")
                scheduler.shutdown()
    
    sys.exit(0 if success else 1)
```
