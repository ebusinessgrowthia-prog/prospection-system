/*
Fichier JavaScript avec des utilitaires pour le dashboard EBUSINESS AI
Fonctions réutilisables et helpers
*/

// Namespace pour éviter les conflits
const DashboardUtils = window.DashboardUtils || {};

// Fonction pour vérifier si un élément est visible dans la fenêtre
DashboardUtils.isElementInViewport = function(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
};

// Fonction pour animer les nombres
DashboardUtils.animateNumber = function(element, start, end, duration, callback) {
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = end;
            clearInterval(timer);
            if (callback) callback();
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
    
    return timer;
};

// Fonction pour formater la taille de fichier
DashboardUtils.formatFileSize = function(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Fonction pour formater la durée
DashboardUtils.formatDuration = function(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${remainingSeconds}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`;
    } else {
        return `${remainingSeconds}s`;
    }
};

// Fonction pour générer une couleur aléatoire
DashboardUtils.getRandomColor = function() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
};

// Fonction pour générer des couleurs à partir d'une chaîne de caractères
DashboardUtils.stringToColor = function(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    let color = '#';
    for (let i = 0; i < 3; i++) {
        const value = (hash >> (i * 8)) & 0xFF;
        color += ('00' + value.toString(16)).substr(-2);
    }
    
    return color;
};

// Fonction pour créer un élément DOM
DashboardUtils.createElement = function(tagName, attributes, children) {
    const element = document.createElement(tagName);
    
    // Ajouter les attributs
    if (attributes) {
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else if (key === 'textContent') {
                element.textContent = value;
            } else {
                element.setAttribute(key, value);
            }
        }
    }
    
    // Ajouter les enfants
    if (children) {
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else {
                element.appendChild(child);
            }
        });
    }
    
    return element;
};

// Fonction pour débouncer une fonction
DashboardUtils.debounce = function(func, wait, immediate) {
    let timeout;
    
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        
        const callNow = immediate && !timeout;
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        
        if (callNow) func(...args);
    };
};

// Fonction pour throttliser une fonction
DashboardUtils.throttle = function(func, limit) {
    let inThrottle;
    
    return function() {
        const args = arguments;
        const context = this;
        
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// Fonction pour cloner un objet
DashboardUtils.deepClone = function(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    
    if (obj instanceof Date) return new Date(obj.getTime());
    
    if (obj instanceof Array) return obj.map(item => DashboardUtils.deepClone(item));
    
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = DashboardUtils.deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
};

// Fonction pour fusionner des objets
DashboardUtils.mergeObjects = function(target, source) {
    const output = Object.assign({}, target);
    
    if (DashboardUtils.isObject(target) && DashboardUtils.isObject(source)) {
        Object.keys(source).forEach(key => {
            if (DashboardUtils.isObject(source[key])) {
                if (!(key in target))
                    Object.assign(output, { [key]: source[key] });
                else
                    output[key] = DashboardUtils.mergeObjects(target[key], source[key]);
            } else {
                Object.assign(output, { [key]: source[key] });
            }
        });
    }
    
    return output;
};

// Fonction pour vérifier si c'est un objet
DashboardUtils.isObject = function(item) {
    return item && typeof item === 'object' && !Array.isArray(item);
};

// Fonction pour convertir un objet en paramètres d'URL
DashboardUtils.objectToQueryString = function(obj) {
    const str = [];
    for (const p in obj)
        if (obj.hasOwnProperty(p)) {
            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        }
    return str.join("&");
};

// Fonction pour convertir des paramètres d'URL en objet
DashboardUtils.queryStringToObject = function(queryString) {
    const query = queryString.substring(1);
    const pairs = query.split('&');
    const result = {};
    
    for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=');
        result[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    
    return result;
};

// Fonction pour obtenir la valeur d'un paramètre d'URL
DashboardUtils.getUrlParameter = function(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
};

// Fonction pour définir la valeur d'un paramètre d'URL
DashboardUtils.setUrlParameter = function(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.pushState({}, '', url);
};

// Fonction pour supprimer un paramètre d'URL
DashboardUtils.removeUrlParameter = function(key) {
    const url = new URL(window.location.href);
    url.searchParams.delete(key);
    window.history.pushState({}, '', url);
};

// Fonction pour vérifier la validité d'un email
DashboardUtils.isValidEmail = function(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};

// Fonction pour vérifier la validité d'un numéro de téléphone
DashboardUtils.isValidPhone = function(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(String(phone).replace(/[\s\-\(\)]/g, ''));
};

// Fonction pour vérifier la validité d'une URL
DashboardUtils.isValidUrl = function(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
};

// Fonction pour extraire le domaine d'une URL
DashboardUtils.extractDomain = function(url) {
    try {
        return new URL(url).hostname;
    } catch (e) {
        return '';
    }
};

// Fonction pour extraire le chemin d'une URL
DashboardUtils.extractPath = function(url) {
    try {
        return new URL(url).pathname;
    } catch (e) {
        return '';
    }
};

// Fonction pour extraire les paramètres d'une URL
DashboardUtils.extractParams = function(url) {
    try {
        const urlObj = new URL(url);
        const params = {};
        urlObj.searchParams.forEach((value, key) => {
            params[key] = value;
        });
        return params;
    } catch (e) {
        return {};
    }
};

// Fonction pour convertir des octets en chaîne hexadécimale
DashboardUtils.bytesToHex = function(bytes) {
    return Array.from(bytes)
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
};

// Fonction pour convertir une chaîne hexadécimale en octets
DashboardUtils.hexToBytes = function(hex) {
    return Array.from(hex.match(/.{1,2}/g) || [])
        .map(byte => parseInt(byte, 16));
};

// Fonction pour convertir une chaîne en base64
DashboardUtils.stringToBase64 = function(str) {
    return btoa(unescape(encodeURIComponent(str)));
};

// Fonction pour convertir une base64 en chaîne
DashboardUtils.base64ToString = function(base64) {
    return decodeURIComponent(escape(atob(base64)));
};

// Fonction pour générer un UUID
DashboardUtils.generateUUID = function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

// Fonction pour générer un identifiant unique court
DashboardUtils.generateShortId = function() {
    return Math.random().toString(36).substring(2, 15);
};

// Fonction pour obtenir la position de la souris
DashboardUtils.getMousePosition = function(event) {
    return {
        x: event.clientX,
        y: event.clientY
    };
};

// Fonction pour obtenir la position d'un élément
DashboardUtils.getElementPosition = function(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + window.scrollX,
        y: rect.top + window.scrollY,
        width: rect.width,
        height: rect.height
    };
};

// Fonction pour faire défiler jusqu'à un élément
DashboardUtils.scrollToElement = function(element, behavior = 'smooth') {
    element.scrollIntoView({ behavior: behavior });
};

// Fonction pour faire défiler jusqu'en haut
DashboardUtils.scrollToTop = function(behavior = 'smooth') {
    window.scrollTo({
        top: 0,
        behavior: behavior
    });
};

// Fonction pour faire défiler jusqu'en bas
DashboardUtils.scrollToBottom = function(behavior = 'smooth') {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: behavior
    });
};

// Fonction pour vérifier si l'utilisateur est sur un appareil mobile
DashboardUtils.isMobile = function() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

// Fonction pour vérifier si l'utilisateur est sur un iPad
DashboardUtils.isiPad = function() {
    return /iPad/i.test(navigator.userAgent);
};

// Fonction pour vérifier si l'utilisateur est sur un iPhone
DashboardUtils.isiPhone = function() {
    return /iPhone/i.test(navigator.userAgent);
};

// Fonction pour vérifier si l'utilisateur est sur un Android
DashboardUtils.isAndroid = function() {
    return /Android/i.test(navigator.userAgent);
};

// Fonction pour vérifier si l'utilisateur est sur un Windows Phone
DashboardUtils.isWindowsPhone = function() {
    return /IEMobile/i.test(navigator.userAgent);
};

// Fonction pour obtenir le système d'exploitation
DashboardUtils.getOS = function() {
    const userAgent = navigator.userAgent;
    let platform = "Unknown";
    
    if (userAgent.indexOf("Win") != -1) platform = "Windows";
    if (userAgent.indexOf("Mac") != -1) platform = "MacOS";
    if (userAgent.indexOf("X11") != -1) platform = "UNIX";
    if (userAgent.indexOf("Linux") != -1) platform = "Linux";
    
    if (/Android/.test(userAgent)) platform = "Android";
    if (/like Mac OS X/.test(userAgent)) {
        if (/CPU iPhone OS/.test(userAgent)) platform = "iOS";
        else platform = "iPadOS";
    }
    
    return platform;
};

// Fonction pour obtenir le navigateur
DashboardUtils.getBrowser = function() {
    const userAgent = navigator.userAgent;
    let browser = "Unknown";
    
    if (userAgent.indexOf("Chrome") > -1) {
        browser = "Chrome";
    } else if (userAgent.indexOf("Safari") > -1) {
        browser = "Safari";
    } else if (userAgent.indexOf("Firefox") > -1) {
        browser = "Firefox";
    } else if (userAgent.indexOf("MSIE") > -1 || userAgent.indexOf("Trident") > -1) {
        browser = "Internet Explorer";
    } else if (userAgent.indexOf("Edge") > -1) {
        browser = "Edge";
    } else if (userAgent.indexOf("Opera") > -1) {
        browser = "Opera";
    }
    
    return browser;
};

// Fonction pour obtenir la version du navigateur
DashboardUtils.getBrowserVersion = function() {
    const userAgent = navigator.userAgent;
    let browserVersion = "Unknown";
    
    if (userAgent.indexOf("Chrome") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("Chrome") + 7).split(" ")[0];
    } else if (userAgent.indexOf("Safari") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("Version") + 8).split(" ")[0];
    } else if (userAgent.indexOf("Firefox") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("Firefox") + 8).split(" ")[0];
    } else if (userAgent.indexOf("MSIE") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("MSIE") + 5).split(";")[0];
    } else if (userAgent.indexOf("Edge") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("Edge") + 5).split(" ")[0];
    } else if (userAgent.indexOf("Opera") > -1) {
        browserVersion = userAgent.substring(userAgent.indexOf("Opera") + 6).split(" ")[0];
    }
    
    return browserVersion;
};

// Fonction pour vérifier la connexion Internet
DashboardUtils.isOnline = function() {
    return navigator.onLine;
};

// Fonction pour ajouter des écouteurs d'événements de connexion
DashboardUtils.addConnectionListeners = function(onlineCallback, offlineCallback) {
    window.addEventListener('online', onlineCallback);
    window.addEventListener('offline', offlineCallback);
};

// Fonction pour supprimer des écouteurs d'événements de connexion
DashboardUtils.removeConnectionListeners = function(onlineCallback, offlineCallback) {
    window.removeEventListener('online', onlineCallback);
    window.removeEventListener('offline', offlineCallback);
};

// Fonction pour stocker des données localement
DashboardUtils.setLocalStorage = function(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage', e);
        return false;
    }
};

// Fonction pour récupérer des données locales
DashboardUtils.getLocalStorage = function(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error reading from localStorage', e);
        return defaultValue;
    }
};

// Fonction pour supprimer des données locales
DashboardUtils.removeLocalStorage = function(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Error removing from localStorage', e);
        return false;
    }
};

// Fonction pour effacer toutes les données locales
DashboardUtils.clearLocalStorage = function() {
    try {
        localStorage.clear();
        return true;
    } catch (e) {
        console.error('Error clearing localStorage', e);
        return false;
    }
};

// Fonction pour stocker des données de session
DashboardUtils.setSessionStorage = function(key, value) {
    try {
        sessionStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to sessionStorage', e);
        return false;
    }
};

// Fonction pour récupérer des données de session
DashboardUtils.getSessionStorage = function(key, defaultValue = null) {
    try {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error reading from sessionStorage', e);
        return defaultValue;
    }
};

// Fonction pour supprimer des données de session
DashboardUtils.removeSessionStorage = function(key) {
    try {
        sessionStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Error removing from sessionStorage', e);
        return false;
    }
};

// Fonction pour effacer toutes les données de session
DashboardUtils.clearSessionStorage = function() {
    try {
        sessionStorage.clear();
        return true;
    } catch (e) {
        console.error('Error clearing sessionStorage', e);
        return false;
    }
};

// Exporter les utilitaires
window.DashboardUtils = DashboardUtils;
