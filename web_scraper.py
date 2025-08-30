import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from urllib.parse import urlparse
from config import REQUEST_DELAY

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_prospects(self, dorks, agency_config):
        """Scrape les prospects en utilisant les Google Dorks"""
        prospects = []
        
        for dork in dorks[:10]:  # Limiter à 10 Dorks pour éviter le surcharge
            try:
                # Simuler une recherche Google
                search_url = f"https://www.google.com/search?q={dork}"
                response = self.session.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraire les résultats de recherche
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:5]:  # Limiter à 5 résultats par Dork
                    link_element = result.find('a')
                    if link_element and 'href' in link_element.attrs:
                        url = link_element['href']
                        
                        # Visiter la page pour extraire les informations
                        prospect = self.extract_prospect_info(url)
                        if prospect:
                            prospect["source"] = dork
                            prospects.append(prospect)
                        
                        time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Erreur lors du scraping du Dork {dork}: {e}")
                continue
        
        return prospects
    
    def extract_prospect_info(self, url):
        """Extrait les informations d'un prospect depuis une page web"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire le nom
            name = self.extract_name(soup)
            
            # Extraire l'email
            email = self.extract_email(soup)
            
            # Extraire l'entreprise
            company = self.extract_company(soup, url)
            
            # Extraire le secteur
            sector = self.extract_sector(soup)
            
            if name and email:
                return {
                    "id": f"{name}_{int(time.time())}",
                    "name": name,
                    "email": email,
                    "company": company,
                    "sector": sector,
                    "status": "Nouveau",
                    "date_discovered": time.strftime("%Y-%m-%d"),
                    "validation_score": 0.0
                }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des infos de {url}: {e}")
        
        return None
    
    def extract_name(self, soup):
        """Extrait le nom d'une personne"""
        # Chercher dans les méta-données
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            return meta_author.get('content', '')
        
        # Chercher dans les balises communes
        for tag in ['h1', 'h2', 'h3']:
            element = soup.find(tag)
            if element:
                return element.text.strip()
        
        return ""
    
    def extract_email(self, soup):
        """Extrait les adresses email"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = soup.get_text()
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def extract_company(self, soup, url):
        """Extrait le nom de l'entreprise"""
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extraire le nom de domaine principal
        parts = domain.split('.')
        if len(parts) > 1:
            return parts[0].title()
        
        return domain.title()
    
    def extract_sector(self, soup):
        """Extrait le secteur d'activité"""
        # Chercher des mots-clés dans le contenu
        content = soup.get_text().lower()
        sector_keywords = {
            'ecommerce': ['shop', 'store', 'boutique', 'cart', 'checkout'],
            'technology': ['tech', 'software', 'saas', 'platform'],
            'marketing': ['marketing', 'digital', 'agency', 'brand'],
            'finance': ['finance', 'bank', 'investment', 'fintech']
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in content for keyword in keywords):
                return sector
        
        return "General"
