# 🤖 Webhook Automation - EBUSINESS AI (ORBIS)

Système d'automatisation pour traiter les demandes d'installation d'Orbis (Vendeur Digital Pro) en utilisant l'IA pour l'analyse et la génération d'emails personnalisés.

## 🎯 Fonctionnalités

- **Webhook unique** pour EBUSINESS AI (ORBIS)
- **Traitement par IA** avec Gemini 2.0 Flash pour extraire et structurer les données
- **Génération automatique d'emails** avec mise en page HTML/CSS personnalisée
- **Envoi d'emails** via SMTP dédié
- **Design personnalisé** Noir et Rouge pour Orbis

## 🚀 Déploiement Rapide

### 1. Forker ce dépôt

Cliquez sur "Fork" en haut de cette page pour créer une copie dans votre compte GitHub.

### 2. Déployer sur Render

1. Allez sur [Render.com](https://render.com) et connectez-vous
2. Cliquez sur **New > Web Service**
3. Connectez votre dépôt GitHub fraîchement forké
4. Configurez le service :
   - **Name**: `orbis-automation`
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. Cliquez sur **Create Web Service**

### 3. Configuration terminée !

Le déploiement est maintenant terminé. Toutes les configurations sont déjà intégrées dans le code.

## 🔗 Votre Lien Webhook

Une fois déployé, Render vous donnera une URL comme : `https://webhook-automation.onrender.com/webhook/ai`

Votre webhook sera : https://webhook-automation.onrender.com/webhook/ai
## 📝 Configuration du formulaire web

### Exemple de formulaire pour ORBIS :

```html
<form id="orbis-form" action="https://orbis-automation.onrender.com/webhook/ai" method="POST">
    <input type="text" name="name" placeholder="Nom & Prénom" required>
    <input type="email" name="email" placeholder="Email" required>
    <input type="tel" name="phone" placeholder="Téléphone (WhatsApp)" required>
    <input type="text" name="shopName" placeholder="Nom de la boutique" required>
    <input type="text" name="website" placeholder="Site web / Instagram" required>
    <select name="platform" required>
        <option value="">Sélectionnez une plateforme</option>
        <option value="Shopify">Shopify</option>
        <option value="WooCommerce">WooCommerce</option>
        <option value="PrestaShop">PrestaShop</option>
        <option value="Magento">Magento</option>
        <option value="Custom">Site custom</option>
        <option value="Autre">Autre</option>
    </select>
    <button type="submit">Envoyer ma demande</button>
</form>
