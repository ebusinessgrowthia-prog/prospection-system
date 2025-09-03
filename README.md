# 🚀 EBUSINESS AI - Automatisation de Prospection

## Description
Système d'automatisation complet pour la prospection d'e-commerçants en Europe francophone. Recherche 24h/24, qualification automatique, et envoi d'emails ultra-personnalisés.

## Fonctionnalités
- 🔍 Recherche continue de prospects via Google Dorks
- 🎯 Qualification automatique des prospects
- ✏️ Génération d'emails ultra-personnalisés avec Mistral AI
- 📧 Envoi d'emails selon horaires définis (mar-ven 9h-17h)
- 📊 Dashboard en temps réel avec Streamlit
- 🌍 Ciblage Europe francophone

## Architecture
- **Backend**: FastAPI + Python 3.13.4
- **Frontend**: Streamlit Dashboard
- **Base de données**: SQLite
- **IA**: Mistral AI + OpenAI
- **Déploiement**: Render

## Déploiement

### Prérequis
- Compte Render
- Compte GitHub
- Clés API configurées

### Installation
1. Cloner ce repository
2. Les variables d'environnement sont déjà configurées dans render.yaml
3. Déployer sur Render

### Configuration
Les variables d'environnement sont pré-configurées :
- MISTRAL_API_KEY: Configurée
- EMAIL_ADDRESS: ia.ebusinessag@gmail.com
- EMAIL_PASSWORD: Configurée
- SERPAPI_API_KEY: Configurée
- OPENAI_API_KEY: Configurée
- Et toutes les autres configurations nécessaires

## Utilisation
1. Accéder au dashboard via l'URL Render
2. Suivre les prospects en temps réel
3. Consulter les statistiques de performance
4. Exporter les données si nécessaire

## Structure du projet
ebusiness-ai-prospection/
├── src/ # Code source
├── dashboard/ # Interface Streamlit
├── data/ # Données (gitignored)
├── tests/ # Tests
├── docs/ # Documentation
└── scripts/ # Scripts utilitaires


## Fonctionnement
- **Recherche 24h/24**: Le système recherche continuellement de nouveaux prospects
- **Qualification automatique**: Les prospects sont qualifiés selon des critères prédéfinis
- **Personnalisation IA**: Les emails sont générés avec Mistral AI pour une personnalisation maximale
- **Envoi structuré**: Les emails sont envoyés du mardi au vendredi de 9h à 17h
- **Ciblage précis**: Focus sur l'Europe francophone

## Auteur
Geraldo Domingo - EBUSINESS AI

## Licence
MIT License
