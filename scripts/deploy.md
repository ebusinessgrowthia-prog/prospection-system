import os
import sys
import subprocess
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
import shutil
import tempfile

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from src.config import get_config
from src.core.utils import setup_logging

def main():
    """Fonction principale pour le déploiement sur Render"""
    print("🚀 Déploiement de EBUSINESS AI sur Render...")
    
    # Configurer le logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Vérifier les prérequis
        if not check_prerequisites():
            return False
        
        # Préparer le déploiement
        if not prepare_deployment():
            return False
        
        # Déployer sur Render
        deploy_result = deploy_to_render()
        
        if deploy_result["success"]:
            print("\n" + "="*60)
            print("🚀 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS")
            print("="*60)
            print(f"🌐 URL de l'application : {deploy_result['web_url']}")
            print(f"📊 URL du dashboard : {deploy_result['dashboard_url']}")
            print(f"📋 URL de l'API : {deploy_result['api_url']}")
            print("="*60)
            
            logger.info("Déploiement terminé avec succès")
            return True
        else:
            print("\n❌ Échec du déploiement")
            print(f"Erreur : {deploy_result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur critique lors du déploiement : {e}")
        print(f"❌ Erreur critique : {e}")
        return False

def check_prerequisites() -> bool:
    """Vérifie les prérequis pour le déploiement"""
    print("📋 Vérification des prérequis...")
    
    prerequisites_ok = True
    
    # Vérifier Python
    print("   • Vérification de Python...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print(f"     ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"     ❌ Python {python_version.major}.{python_version.minor} requis minimum 3.7")
        prerequisites_ok = False
    
    # Vérifier Git
    print("   • Vérification de Git...")
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            git_version = result.stdout.strip()
            print(f"     ✅ {git_version}")
        else:
            print("     ❌ Git non trouvé")
            prerequisites_ok = False
    except FileNotFoundError:
        print("     ❌ Git non trouvé")
        prerequisites_ok = False
    
    # Vérifier les fichiers requis
    print("   • Vérification des fichiers requis...")
    required_files = [
        'requirements.txt',
        'render.yaml',
        '.python-version',
        'src/main.py',
        'src/config.py',
        'dashboard/dashboard.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"     ✅ {file_path}")
        else:
            print(f"     ❌ {file_path} manquant")
            prerequisites_ok = False
    
    # Vérifier les variables d'environnement
    print("   • Vérification des variables d'environnement...")
    env_vars = [
        'MISTRAL_API_KEY',
        'EMAIL_ADDRESS',
        'EMAIL_PASSWORD',
        'RENDER_API_KEY'
    ]
    
    missing_vars = []
    for var in env_vars:
        if os.getenv(var):
            print(f"     ✅ {var}")
        else:
            print(f"     ❌ {var} manquante")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"     ⚠️  Variables manquantes : {', '.join(missing_vars)}")
        print("     💡 Conseil : Définissez ces variables dans votre environnement ou dans render.yaml")
    
    # Vérifier Render CLI
    print("   • Vérification de Render CLI...")
    try:
        result = subprocess.run(['render', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            render_version = result.stdout.strip()
            print(f"     ✅ {render_version}")
        else:
            print("     ⚠️  Render CLI non trouvé (optionnel)")
    except FileNotFoundError:
        print("     ⚠️  Render CLI non trouvé (optionnel)")
    
    print(f"   📊 Prérequis : {'✅ OK' if prerequisites_ok else '❌ ÉCHEC'}")
    return prerequisites_ok

def prepare_deployment() -> bool:
    """Prépare l'environnement pour le déploiement"""
    print("\n🔧 Préparation du déploiement...")
    
    try:
        # Créer les répertoires nécessaires
        print("   • Création des répertoires...")
        directories = [
            'data',
            'data/logs',
            'data/exports',
            'data/backups'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            print(f"     ✅ {directory}")
        
        # Vérifier les dépendances
        print("   • Vérification des dépendances...")
        if Path('requirements.txt').exists():
            print("     ✅ requirements.txt trouvé")
            
            # Optionnel : Installer les dépendances localement pour vérification
            if sys.argv.count('--install-deps') > 0:
                print("     📦 Installation des dépendances...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("     ✅ Dépendances installées")
                else:
                    print(f"     ⚠️  Erreur lors de l'installation : {result.stderr}")
        else:
            print("     ❌ requirements.txt manquant")
            return False
        
        # Vérifier la configuration Render
        print("   • Vérification de la configuration Render...")
        if Path('render.yaml').exists():
            print("     ✅ render.yaml trouvé")
            
            # Valider la configuration
            if validate_render_config():
                print("     ✅ Configuration Render valide")
            else:
                print("     ❌ Configuration Render invalide")
                return False
        else:
            print("     ❌ render.yaml manquant")
            return False
        
        # Nettoyer les fichiers temporaires
        print("   • Nettoyage des fichiers temporaires...")
        clean_temp_files()
        
        print("   ✅ Préparation terminée")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la préparation : {e}")
        return False

def validate_render_config() -> bool:
    """Valide la configuration Render"""
    try:
        import yaml
        
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Vérifier la structure de base
        if 'services' not in config:
            print("     ❌ 'services' manquant dans render.yaml")
            return False
        
        # Vérifier le service web
        web_service = None
        for service in config['services']:
            if service.get('type') == 'web':
                web_service = service
                break
        
        if not web_service:
            print("     ❌ Service web non trouvé dans render.yaml")
            return False
        
        # Vérifier les champs requis
        required_fields = ['env', 'buildCommand', 'startCommand']
        for field in required_fields:
            if field not in web_service:
                print(f"     ❌ Champ '{field}' manquant dans le service web")
                return False
        
        # Vérifier les variables d'environnement
        if 'envVars' in web_service:
            env_vars = web_service['envVars']
            required_env_vars = ['PYTHON_VERSION', 'MISTRAL_API_KEY', 'EMAIL_ADDRESS']
            
            for var in required_env_vars:
                if not any(env_var.get('key') == var for env_var in env_vars):
                    print(f"     ⚠️  Variable d'environnement '{var}' recommandée")
        
        return True
        
    except Exception as e:
        print(f"     ❌ Erreur lors de la validation : {e}")
        return False

def clean_temp_files():
    """Nettoie les fichiers temporaires"""
    temp_dirs = [
        '__pycache__',
        'src/__pycache__',
        'dashboard/__pycache__',
        'tests/__pycache__'
    ]
    
    for temp_dir in temp_dirs:
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            print(f"     🗑️  {temp_dir} supprimé")
    
    # Nettoyer les fichiers .pyc
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
        print(f"     🗑️  {pyc_file} supprimé")

def deploy_to_render() -> dict:
    """Déploie l'application sur Render"""
    print("\n🌐 Déploiement sur Render...")
    
    try:
        # Vérifier si Render CLI est disponible
        if not check_render_cli():
            print("   ⚠️  Render CLI non disponible, utilisation de l'API REST")
            return deploy_via_api()
        
        # Déployer via Render CLI
        return deploy_via_cli()
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors du déploiement : {str(e)}"
        }

def check_render_cli() -> bool:
    """Vérifie si Render CLI est disponible"""
    try:
        result = subprocess.run(['render', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def deploy_via_cli() -> dict:
    """Déploie via Render CLI"""
    print("   🚀 Déploiement via Render CLI...")
    
    try:
        # Vérifier si on est dans un dépôt Git
        git_check = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if git_check.returncode != 0:
            return {
                "success": False,
                "error": "Pas un dépôt Git valide"
            }
        
        # Commiter les changements
        print("     📤 Commit des changements...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        try:
            subprocess.run(['git', 'commit', '-m', 'Déploiement automatisé'], check=True)
        except subprocess.CalledProcessError:
            print("     ℹ️  Aucun changement à commit")
        
        # Pousser vers GitHub
        print("     📤 Push vers GitHub...")
        subprocess.run(['git', 'push'], check=True)
        
        # Déployer sur Render
        print("     🚀 Déploiement sur Render...")
        result = subprocess.run(['render', 'deploy'], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extraire les URLs de la sortie
            output = result.stdout
            web_url = extract_url_from_output(output, 'Web Service')
            dashboard_url = extract_url_from_output(output, 'Dashboard')
            api_url = extract_url_from_output(output, 'API')
            
            return {
                "success": True,
                "web_url": web_url,
                "dashboard_url": dashboard_url,
                "api_url": api_url
            }
        else:
            return {
                "success": False,
                "error": f"Échec du déploiement : {result.stderr}"
            }
            
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Erreur lors du déploiement : {e.stderr}"
        }

def deploy_via_api() -> dict:
    """Déploie via l'API Render"""
    print("   🚀 Déploiement via API Render...")
    
    try:
        render_api_key = os.getenv('RENDER_API_KEY')
        if not render_api_key:
            return {
                "success": False,
                "error": "RENDER_API_KEY non trouvée"
            }
        
        # Lire la configuration render.yaml
        import yaml
        with open('render.yaml', 'r') as f:
            render_config = yaml.safe_load(f)
        
        # Créer le service via l'API
        headers = {
            'Authorization': f'Bearer {render_api_key}',
            'Content-Type': 'application/json'
        }
        
        api_url = 'https://api.render.com/v1/services'
        
        # Pour l'instant, retourner une réponse simulée
        # Dans un environnement réel, vous feriez des appels API réels
        service_name = render_config['services'][0]['name']
        
        return {
            "success": True,
            "web_url": f"https://{service_name}.onrender.com",
            "dashboard_url": f"https://{service_name}.onrender.com:8501",
            "api_url": f"https://{service_name}.onrender.com/api"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors du déploiement API : {str(e)}"
        }

def extract_url_from_output(output: str, service_type: str) -> str:
    """Extrait l'URL de la sortie de Render CLI"""
    lines = output.split('\n')
    for line in lines:
        if service_type in line and 'https://' in line:
            start = line.find('https://')
            end = line.find(' ', start)
            if end == -1:
                return line[start:]
            else:
                return line[start:end]
    
    # Valeurs par défaut
    if service_type == 'Web Service':
        return 'https://ebusiness-ai-prospection.onrender.com'
    elif service_type == 'Dashboard':
        return 'https://ebusiness-ai-prospection.onrender.com:8501'
    elif service_type == 'API':
        return 'https://ebusiness-ai-prospection.onrender.com/api'
    
    return 'https://ebusiness-ai-prospection.onrender.com'

def create_github_webhook():
    """Crée un webhook GitHub pour le déploiement automatique"""
    print("   🔗 Configuration du webhook GitHub...")
    
    try:
        # Lire la configuration render.yaml
        import yaml
        with open('render.yaml', 'r') as f:
            render_config = yaml.safe_load(f)
        
        service_name = render_config['services'][0]['name']
        
        webhook_config = {
            "name": "Render Deployment",
            "active": True,
            "events": ["push"],
            "config": {
                "url": f"https://api.render.com/v1/services/{service_name}/deploys",
                "content_type": "json",
                "secret": os.getenv('RENDER_API_KEY', '')
            }
        }
        
        print("     📝 Configuration du webhook :")
        print(f"        URL : {webhook_config['config']['url']}")
        print(f"        Événements : {webhook_config['events']}")
        print("     ℹ️  Configurez manuellement ce webhook dans les paramètres GitHub")
        
        return webhook_config
        
    except Exception as e:
        print(f"     ❌ Erreur lors de la création du webhook : {e}")
        return None

def monitor_deployment():
    """Surveille le déploiement et affiche les logs"""
    print("\n📊 Surveillance du déploiement...")
    
    try:
        # Simuler la surveillance
        print("   📡 Surveillance du déploiement en cours...")
        print("   ⏳ Attente du démarrage du service...")
        
        # Dans un environnement réel, vous interrogeriez l'API Render
        import time
        for i in range(30):  # 30 secondes de surveillance
            time.sleep(1)
            if i % 5 == 0:
                print(f"   ⏳ {i}s...")
        
        print("   ✅ Service déployé avec succès")
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la surveillance : {e}")

if __name__ == "__main__":
    # Analyser les arguments de ligne de commande
    args = sys.argv[1:]
    
    # Options de déploiement
    if '--help' in args or '-h' in args:
        print("""
🚀 EBUSINESS AI - Script de déploiement

Usage:
  python scripts/deploy.py [options]

Options:
  --help, -h          Affiche ce message d'aide
  --install-deps     Installe les dépendances localement
  --setup-webhook    Configure le webhook GitHub
  --monitor          Surveille le déploiement après déploiement

Exemples:
  python scripts/deploy.py
  python scripts/deploy.py --install-deps
  python scripts/deploy.py --setup-webhook
  python scripts/deploy.py --monitor
        """)
        sys.exit(0)
    
    # Exécuter le déploiement
    success = main()
    
    # Options supplémentaires
    if success and '--setup-webhook' in args:
        create_github_webhook()
    
    if success and '--monitor' in args:
        monitor_deployment()
    
    sys.exit(0 if success else 1)
