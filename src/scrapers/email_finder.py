"""
Module pour la recherche d'adresses email professionnelles
Permet de trouver des emails sur les sites web et de les valider
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Any, Tuple
import logging
import json

# Import des modules locaux
from src.core.database import db_manager
from src.core.utils import get_logger, validate_email_address, generate_tracking_id
from src.config import get_config

logger = get_logger(__name__)

class EmailFinder:
    """
    Classe pour la recherche et la validation d'adresses email
    """
    
    def __init__(self):
        """Initialisation du chercheur d'emails"""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session.headers.update(self.headers)
        
        config = get_config()
        self.timeout = config.get('timeout', 10)
        self.max_retries = config.get('max_retries', 3)
        self.delay = config.get('delay', 1)
        
        # Signatures pour la détection d'emails
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email standard
            r'\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email obfusqué (at)
            r'\b[A-Za-z0-9._%+-]+ \[at\] [A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email obfusqué [at]
            r'\b[A-Za-z0-9._%+-]+ \(at\) [A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email obfusqué (at)
            r'\b[A-Za-z0-9._%+-]+@\[A-Za-z0-9.-]+\]\.[A-Z|a-z]{2,}\b',  # Email avec domaine obfusqué
        ]
        
        # Pages courantes où trouver des emails
        self.contact_pages = [
            'contact', 'contact-us', 'contactez-nous', 'nous-contacter',
            'about', 'about-us', 'a-propos',
            'team', 'equipe', 'staff',
            'imprint', 'mentions-legales',
            'privacy', 'politique-confidentialite',
            'legal', 'mentions-legales'
        ]
        
        # Sélecteurs courants pour les emails
        self.email_selectors = [
            'a[href^="mailto:"]',
            '.email', '.contact-email', '.mail',
            '[class*="email"]', '[class*="contact"]',
            '.info-box .email', '.contact-info .email',
            '.author-email', '.staff-email',
            '.footer-email', '.header-email'
        ]
        
        # Domaines personnels courants
        self.personal_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'live.com', 'aol.com', 'icloud.com', 'mail.com',
            'yandex.com', 'protonmail.com', 'tutanota.com',
            'gmx.com', 'zoho.com', 'fastmail.com'
        ]
    
    def find_emails(self, url: str, max_pages: int = 5, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Recherche des adresses email sur un site web
        
        Args:
            url: URL du site web à analyser
            max_pages: Nombre maximum de pages à analyser
            save_to_db: Sauvegarder les résultats dans la base de données
            
        Returns:
            Dictionnaire avec les résultats de la recherche
        """
        logger.info(f"Recherche d'emails sur le site: {url}")
        
        # Normaliser l'URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Extraire le domaine
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Initialiser les résultats
        result = {
            'url': url,
            'domain': domain,
            'status': 'error',
            'emails': [],
            'contact_pages': [],
            'pages_analyzed': 0,
            'error': None,
            'saved_to_db': False
        }
        
        try:
            # Récupérer la page principale
            main_page_response = self._fetch_url(url)
            if not main_page_response:
                result['error'] = "Impossible d'accéder au site web"
                return result
            
            # Mettre à jour le statut
            result['status'] = 'success'
            
            # Analyser la page principale
            main_soup = BeautifulSoup(main_page_response.text, 'html.parser')
            
            # Rechercher des emails sur la page principale
            main_emails = self._extract_emails_from_text(main_page_response.text, domain)
            
            # Rechercher des liens vers les pages de contact
            contact_links = self._find_contact_links(main_soup, url)
            
            # Ajouter les liens de contact aux résultats
            result['contact_pages'] = contact_links
            
            # Combiner les URLs à analyser (page principale + pages de contact)
            urls_to_analyze = [url]
            urls_to_analyze.extend([link['url'] for link in contact_links[:max_pages-1]])
            
            # Analyser chaque page
            all_emails = set(main_emails)  # Utiliser un set pour éviter les doublons
            
            for page_url in urls_to_analyze:
                try:
                    page_response = self._fetch_url(page_url)
                    if page_response:
                        page_soup = BeautifulSoup(page_response.text, 'html.parser')
                        
                        # Extraire les emails de la page
                        page_emails = self._extract_emails_from_page(page_soup, page_url, domain)
                        
                        # Ajouter les emails au set
                        all_emails.update(page_emails)
                        
                        # Incrémenter le compteur de pages analysées
                        result['pages_analyzed'] += 1
                        
                        # Petit délai pour ne pas surcharger le serveur
                        time.sleep(self.delay)
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'analyse de la page {page_url}: {str(e)}")
            
            # Valider les emails et calculer les scores de confiance
            validated_emails = []
            for email in all_emails:
                validation_result = self._validate_email(email, domain)
                validated_emails.append(validation_result)
            
            # Filtrer les emails valides
            valid_emails = [email for email in validated_emails if email['valid']]
            
            # Trier par score de confiance
            valid_emails.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Mettre à jour les résultats
            result['emails'] = valid_emails
            
            # Sauvegarder dans la base de données si demandé
            if save_to_db and valid_emails:
                saved_emails = self._save_emails_to_db(url, valid_emails)
                result['saved_to_db'] = saved_emails
            
            logger.info(f"Recherche terminée pour {url}. Trouvé {len(valid_emails)} emails valides")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'emails sur {url}: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _fetch_url(self, url: str) -> Optional[requests.Response]:
        """
        Récupère le contenu d'une URL avec gestion des erreurs
        
        Args:
            url: URL à récupérer
            
        Returns:
            Response object ou None si échec
        """
        for attempt in range(self.max_retries):
            try:
                # Respecter les délais
                time.sleep(self.delay)
                
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Trop de requêtes - attendre plus longtemps
                    wait_time = 30 * (attempt + 1)
                    logger.warning(f"Rate limité. Attente de {wait_time} secondes...")
                    time.sleep(wait_time)
                else:
                    logger.warning(f"Statut HTTP {response.status_code} pour l'URL: {url}")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la requête à {url}: {str(e)}")
                
        return None
    
    def _extract_emails_from_text(self, text: str, domain: str = None) -> List[str]:
        """
        Extrait les adresses email d'un texte
        
        Args:
            text: Texte à analyser
            domain: Domaine de référence pour la validation
            
        Returns:
            Liste d'adresses email
        """
        emails = []
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Nettoyer les emails obfusqués
                email = self._clean_email(match)
                if email and self._is_valid_email_format(email):
                    emails.append(email.lower())
        
        return list(set(emails))  # Supprimer les doublons
    
    def _extract_emails_from_page(self, soup: BeautifulSoup, base_url: str, domain: str) -> List[str]:
        """
        Extrait les adresses email d'une page web
        
        Args:
            soup: BeautifulSoup object
            base_url: URL de base
            domain: Domaine de référence
            
        Returns:
            Liste d'adresses email
        """
        emails = []
        
        # 1. Extraire les emails du texte de la page
        page_text = soup.get_text()
        text_emails = self._extract_emails_from_text(page_text, domain)
        emails.extend(text_emails)
        
        # 2. Extraire les emails des attributs href des liens mailto
        mailto_links = soup.select('a[href^="mailto:"]')
        for link in mailto_links:
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href[7:]  # Supprimer 'mailto:'
                # Nettoyer les paramètres supplémentaires
                email = email.split('?')[0].strip()
                if self._is_valid_email_format(email):
                    emails.append(email.lower())
        
        # 3. Extraire les emails des sélecteurs spécifiques
        for selector in self.email_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Vérifier si c'est un lien mailto
                href = element.get('href', '')
                if href.startswith('mailto:'):
                    email = href[7:]  # Supprimer 'mailto:'
                    email = email.split('?')[0].strip()
                    if self._is_valid_email_format(email):
                        emails.append(email.lower())
                else:
                    # Extraire du texte
                    text = element.get_text(strip=True)
                    element_emails = self._extract_emails_from_text(text, domain)
                    emails.extend(element_emails)
        
        # 4. Extraire les emails des métadonnées
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name') == 'author' or tag.get('property') == 'og:email':
                content = tag.get('content', '')
                if content and '@' in content:
                    email = content.split(',')[0].strip()  # Prendre le premier email si plusieurs
                    if self._is_valid_email_format(email):
                        emails.append(email.lower())
        
        return list(set(emails))  # Supprimer les doublons
    
    def _find_contact_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Trouve les liens vers les pages de contact
        
        Args:
            soup: BeautifulSoup object
            base_url: URL de base
            
        Returns:
            Liste de liens vers les pages de contact
        """
        contact_links = []
        
        # Rechercher les liens qui correspondent aux pages de contact
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # Vérifier si le lien ou le texte correspond à une page de contact
            is_contact_link = False
            
            # Vérifier le texte du lien
            for page in self.contact_pages:
                if page in text:
                    is_contact_link = True
                    break
            
            # Vérifier l'URL du lien
            if not is_contact_link:
                for page in self.contact_pages:
                    if page in href.lower():
                        is_contact_link = True
                        break
            
            if is_contact_link:
                # Construire l'URL absolue
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                contact_links.append({
                    'url': href,
                    'text': link.get_text(strip=True)
                })
        
        return contact_links
    
    def _clean_email(self, email: str) -> Optional[str]:
        """
        Nettoie une adresse email obfusquée
        
        Args:
            email: Email potentiellement obfusqué
            
        Returns:
            Email nettoyé ou None si invalide
        """
        # Remplacer les obfuscations courantes
        email = email.replace(' at ', '@')
        email = email.replace(' [at] ', '@')
        email = email.replace(' (at) ', '@')
        email = email.replace('[at]', '@')
        email = email.replace('(at)', '@')
        email = email.replace(' AT ', '@')
        email = email.replace('[AT]', '@')
        email = email.replace('(AT)', '@')
        
        # Supprimer les espaces supplémentaires
        email = re.sub(r'\s+', '', email)
        
        return email if self._is_valid_email_format(email) else None
    
    def _is_valid_email_format(self, email: str) -> bool:
        """
        Vérifie si une chaîne a un format d'email valide
        
        Args:
            email: Email à valider
            
        Returns:
            True si le format est valide, False sinon
        """
        if not email or len(email) > 254:
            return False
        
        # Expression régulière pour valider le format d'email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_email(self, email: str, domain: str) -> Dict[str, Any]:
        """
        Valide une adresse email et calcule un score de confiance
        
        Args:
            email: Email à valider
            domain: Domaine du site web
            
        Returns:
            Dictionnaire avec les informations de validation
        """
        validation_result = {
            'email': email,
            'valid': False,
            'confidence': 0,
            'reasons': []
        }
        
        # 1. Valider le format
        if not self._is_valid_email_format(email):
            validation_result['reasons'].append('Format invalide')
            return validation_result
        
        validation_result['valid'] = True
        
        # 2. Extraire le domaine de l'email
        email_domain = email.split('@')[1].lower()
        
        # 3. Calculer le score de confiance
        confidence = 50  # Score de base
        
        # Vérifier si le domaine de l'email correspond au domaine du site
        if email_domain == domain.lower():
            confidence += 30
            validation_result['reasons'].append('Domaine correspondant')
        else:
            # Vérifier si c'est un sous-domaine
            if email_domain.endswith('.' + domain.lower()):
                confidence += 20
                validation_result['reasons'].append('Sous-domaine')
            else:
                validation_result['reasons'].append('Domaine différent')
        
        # Vérifier les fournisseurs d'email courants
        if email_domain in self.personal_domains:
            confidence -= 20
            validation_result['reasons'].append('Email personnel')
        else:
            confidence += 10
            validation_result['reasons'].append('Email professionnel')
        
        # Vérifier le format du nom d'utilisateur
        username = email.split('@')[0]
        
        # Bonus pour les formats professionnels
        professional_formats = [
            r'^[a-z]+\.[a-z]+$',  # prenom.nom
            r'^[a-z]+_[a-z]+$',   # prenom_nom
            r'^[a-z]+-[a-z]+$',   # prenom-nom
            r'^[a-z]+$',          # prenom
            r'^[a-z]{1}[0-9]+$',  # p + chiffre
            r'^info$',
            r'^contact$',
            r'^admin$',
            r'^support$',
            r'^hello$'
        ]
        
        for pattern in professional_formats:
            if re.match(pattern, username.lower()):
                confidence += 10
                validation_result['reasons'].append('Format professionnel')
                break
        
        # Pénalité pour les formats peu professionnels
        unprofessional_patterns = [
            r'^[0-9]+',           # Commence par un chiffre
            r'.*[^a-z0-9._-].*',  # Contient des caractères spéciaux
        ]
        
        for pattern in unprofessional_patterns:
            if re.match(pattern, username.lower()):
                confidence -= 10
                validation_result['reasons'].append('Format peu professionnel')
                break
        
        # Bonus pour les noms d'utilisateur contenant des mots professionnels
        professional_keywords = ['contact', 'info', 'admin', 'support', 'hello', 'team']
        if any(keyword in username.lower() for keyword in professional_keywords):
            confidence += 5
            validation_result['reasons'].append('Nom d\'utilisateur professionnel')
        
        # Pénalité pour les noms d'utilisateur contenant des mots personnels
        personal_keywords = ['admin', 'root', 'test', 'demo', 'user']
        if any(keyword in username.lower() for keyword in personal_keywords):
            confidence -= 5
            validation_result['reasons'].append('Nom d\'utilisateur générique')
        
        # S'assurer que le score est entre 0 et 100
        validation_result['confidence'] = max(0, min(100, confidence))
        
        return validation_result
    
    def _save_emails_to_db(self, url: str, emails: List[Dict[str, Any]]) -> bool:
        """
        Sauvegarde les emails trouvés dans la base de données
        
        Args:
            url: URL d'origine
            emails: Liste des emails validés
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Extraire le domaine de l'URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Récupérer ou créer un prospect pour cette URL
            prospect = db_manager.get_prospects()
            existing_prospect = None
            
            # Chercher un prospect existant avec ce domaine
            for p in prospect:
                if p.website and domain in p.website:
                    existing_prospect = p
                    break
            
            if existing_prospect:
                prospect_id = existing_prospect.id
                # Mettre à jour le prospect avec les nouveaux emails
                if not existing_prospect.email and emails:
                    # Prendre le meilleur email
                    best_email = max(emails, key=lambda x: x['confidence'])
                    db_manager.update_prospect(prospect_id, {'email': best_email['email']})
            else:
                # Créer un nouveau prospect
                # Extraire des informations de base de l'URL
                company_name = domain.replace('www.', '').split('.')[0].title()
                
                prospect_data = {
                    'name': company_name,
                    'company': company_name,
                    'email': emails[0]['email'] if emails else None,
                    'website': url,
                    'status': 'nouveau',
                    'source': 'email_finder'
                }
                
                new_prospect = db_manager.add_prospect(prospect_data)
                if new_prospect:
                    prospect_id = new_prospect.id
                else:
                    return False
            
            # Sauvegarder les emails dans les logs système
            for email_data in emails:
                log_entry = {
                    'level': 'INFO',
                    'message': f"Email trouvé: {email_data['email']} (confiance: {email_data['confidence']}%)",
                    'module': 'email_finder',
                    'extra_data': {
                        'url': url,
                        'email': email_data['email'],
                        'confidence': email_data['confidence'],
                        'reasons': email_data['reasons']
                    }
                }
                
                db_manager.log_system_event(
                    log_entry['level'],
                    log_entry['message'],
                    log_entry['module'],
                    log_entry['extra_data']
                )
            
            logger.info(f"Emails sauvegardés dans la base de données pour l'URL: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des emails dans la base de données: {e}")
            return False
    
    def find_emails_from_multiple_websites(self, urls: List[str], max_pages: int = 3, save_to_db: bool = True) -> List[Dict[str, Any]]:
        """
        Recherche des adresses email sur plusieurs sites web
        
        Args:
            urls: Liste d'URLs à analyser
            max_pages: Nombre maximum de pages à analyser par site
            save_to_db: Sauvegarder les résultats dans la base de données
            
        Returns:
            Liste des résultats de recherche
        """
        logger.info(f"Recherche d'emails sur {len(urls)} sites web")
        
        results = []
        for url in urls:
            try:
                result = self.find_emails(url, max_pages, save_to_db)
                results.append(result)
                
                # Petit délai pour ne pas surcharger les serveurs
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Erreur lors de la recherche d'emails sur {url}: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        logger.info(f"Recherche terminée pour {len(urls)} sites web")
        return results
    
    def bulk_email_validation(self, emails: List[str]) -> List[Dict[str, Any]]:
        """
        Valide une liste d'emails en masse
        
        Args:
            emails: Liste d'emails à valider
            
        Returns:
            Liste des résultats de validation
        """
        results = []
        
        for email in emails:
            validation_result = self._validate_email(email, '')
            results.append(validation_result)
        
        # Trier par score de confiance
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return results
    
    def get_email_patterns(self) -> List[str]:
        """
        Retourne les patterns utilisés pour la détection d'emails
        
        Returns:
            Liste des patterns de détection
        """
        return self.email_patterns
    
    def add_custom_pattern(self, pattern: str) -> bool:
        """
        Ajoute un pattern de détection personnalisé
        
        Args:
            pattern: Pattern regex à ajouter
            
        Returns:
            True si le pattern a été ajouté, False sinon
        """
        try:
            # Valider le pattern regex
            re.compile(pattern)
            
            if pattern not in self.email_patterns:
                self.email_patterns.append(pattern)
                logger.info(f"Pattern ajouté: {pattern}")
                return True
            else:
                logger.warning(f"Pattern déjà existant: {pattern}")
                return False
        except Exception as e:
            logger.error(f"Pattern invalide: {pattern}, erreur: {e}")
            return False
    
    def remove_custom_pattern(self, pattern: str) -> bool:
        """
        Supprime un pattern de détection personnalisé
        
        Args:
            pattern: Pattern regex à supprimer
            
        Returns:
            True si le pattern a été supprimé, False sinon
        """
        try:
            if pattern in self.email_patterns:
                self.email_patterns.remove(pattern)
                logger.info(f"Pattern supprimé: {pattern}")
                return True
            else:
                logger.warning(f"Pattern non trouvé: {pattern}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du pattern: {e}")
            return False
