# 🚀 Webhook Automation - EBUSINESS GROWTH & AI

Système d'automatisation complet pour traiter les formulaires de deux agences différentes en utilisant Gemini 2.0 Flash pour l'analyse et la génération d'emails personnalisés.

## 🎯 Fonctionnalités

- **Deux webhooks distincts** pour EBUSINESS GROWTH et EBUSINESS AI
- **Traitement par IA** avec Gemini 2.0 Flash pour extraire et structurer les données
- **Génération automatique d'emails** avec mise en page HTML/CSS personnalisée
- **Envoi d'emails** via SMTP dédié pour chaque agence
- **Design personnalisé** pour chaque agence (Gold pour GROWTH, Noir/Rouge pour AI)

## 🚀 Déploiement Rapide

### 1. Forker ce dépôt

Cliquez sur "Fork" en haut de cette page pour créer une copie dans votre compte GitHub.

### 2. Déployer sur Render

1. Allez sur [Render.com](https://render.com) et connectez-vous
2. Cliquez sur **New > Web Service**
3. Connectez votre dépôt GitHub fraîchement forké
4. Configurez le service :
   - **Name**: `webhook-automation`
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. Cliquez sur **Create Web Service**

### 3. Configuration terminée !

Le déploiement est maintenant terminé. Toutes les configurations sont déjà intégrées dans le code.

## 🔗 Vos Liens Webhook

Une fois déployé, Render vous donnera une URL comme : `https://webhook-automation.onrender.com`

### Pour EBUSINESS GROWTH :
https://webhook-automation.onrender.com/webhook/growth


### Pour EBUSINESS AI :
https://webhook-automation.onrender.com/webhook/ai


## 📝 Configuration des formulaires web

### Exemple de formulaire pour EBUSINESS GROWTH :

```html
<form action="https://webhook-automation.onrender.com/webhook/growth" method="POST">
    <input type="text" name="nom" placeholder="Votre nom complet" required>
    <input type="email" name="email" placeholder="Votre email" required>
    <input type="tel" name="telephone" placeholder="Votre téléphone">
    <select name="service" required>
        <option value="">Choisissez un service</option>
        <option value="Rétention & Relance B2B">Rétention & Relance B2B</option>
        <option value="Automatisation Marketing">Automatisation Marketing</option>
        <option value="Growth Hacking">Growth Hacking</option>
    </select>
    <textarea name="description" placeholder="Décrivez votre projet" required></textarea>
    <button type="submit">Envoyer ma demande</button>
</form>
