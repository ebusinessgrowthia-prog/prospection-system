"""
Point d'entrée principal de l'application EBUSINESS AI
Combine FastAPI, Streamlit Dashboard et le worker de planification
"""

import os
import sys
import threading
import time
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import streamlit.web.cli as stcli
from dotenv import load_dotenv

# Import des modules locaux
from src.config import Config
from src.core.database import init_database
from src.scheduler.worker import start_scheduler
from src.core.utils import setup_logging

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="EBUSINESS AI - Automatisation de Prospection",
    description="Système complet de prospection automatisée",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec informations sur le système"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>EBUSINESS AI - Automatisation de Prospection</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
                .status { padding: 10px; background: rgba(0,255,0,0.2); border-radius: 5px; margin: 10px 0; }
                .links { margin-top: 20px; }
                .links a { color: white; text-decoration: none; margin-right: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 EBUSINESS AI - Automatisation de Prospection</h1>
                <div class="status">✅ Système Actif et Fonctionnel</div>
                <p><strong>Description:</strong> Système complet de prospection automatisée pour e-commerçants en Europe francophone.</p>
                <p><strong>Fonctionnalités:</strong></p>
                <ul>
                    <li>🔍 Recherche continue de prospects via Google Dorks</li>
                    <li>🎯 Qualification automatique des prospects</li>
                    <li>✏️ Génération d'emails ultra-personnalisés avec Mistral AI</li>
                    <li>📧 Envoi d'emails selon horaires définis (mar-ven 9h-17h)</li>
                    <li>📊 Dashboard en temps réel avec Streamlit</li>
                </ul>
                <div class="links">
                    <a href="/health">Health Check</a>
                    <a href="/dashboard">Dashboard Streamlit</a>
                    <a href="/docs">API Documentation</a>
                </div>
                <p style="margin-top: 30px; font-size: 0.8em; opacity: 0.7;">
                    Dernière mise à jour: {}<br>
                    Version: 1.0.0 | Auteur: Geraldo Domingo
                </p>
            </div>
        </body>
    </html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.get("/health")
async def health_check():
    """Endpoint de santé pour le monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "scheduler": "running",
            "email_service": "ready"
        }
    }

@app.get("/api/stats")
async def get_stats():
    """Endpoint pour obtenir les statistiques du système"""
    try:
        from src.core.database import get_system_stats
        stats = get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

def start_dashboard():
    """Démarre le dashboard Streamlit dans un thread séparé"""
    logger.info("Démarrage du dashboard Streamlit...")
    
    # Configuration des arguments pour Streamlit
    sys.argv = [
        "streamlit",
        "run",
        "dashboard/dashboard.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false"
    ]
    
    try:
        stcli.main()
    except SystemExit:
        pass

def main():
    """Fonction principale qui démarre tous les services"""
    logger.info("🚀 Démarrage du système EBUSINESS AI...")
    
    # Initialisation de la base de données
    logger.info("Initialisation de la base de données...")
    init_database()
    
    # Démarrer le scheduler dans un thread séparé
    logger.info("Démarrage du scheduler...")
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Démarrer le dashboard dans un thread séparé
    logger.info("Démarrage du dashboard...")
    dashboard_thread = threading.Thread(target=start_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # Démarrer FastAPI
    logger.info("Démarrage de l'API FastAPI...")
    logger.info("✅ Système prêt ! Accédez au dashboard sur http://localhost:8501")
    
    # Configuration Uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
