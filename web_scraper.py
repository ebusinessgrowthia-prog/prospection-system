import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import concurrent.futures
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay: float = 1.0, max_workers: int = 5):
        """Initialize web scraper with rate limiting"""
        self.delay = delay
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_from_dork(self, dork: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Scrape prospects from Google search results"""
        prospects = []
        search_url = f"https://www.google.com/search?q={dork}&num={max_results}"
        
        try:
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results[:max_results]:
                prospect = self._extract_prospect_from_result(result, dork)
                if prospect:
                    prospects.append(prospect)
                    
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Error scraping dork '{dork}': {e}")
            
        return prospects
    
    def _extract_prospect_from_result(self, result, dork: str) -> Dict[str, Any]:
        """Extract prospect information from search result"""
        try:
            # Extract title and URL
            title_elem = result.find('h3')
            title = title_elem.text if title_elem else ""
            
            link_elem = result.find('a')
            url = link_elem.get('href') if link_elem else ""
            
            if not url or 'google.com' in url:
                return None
                
            # Clean URL
            if url.startswith('/url?q='):
                url = url.split('/url?q=')[1].split('&')[0]
                
            # Visit the page to extract contact info
            contact_info = self._extract_contact_info(url)
            
            if contact_info.get('email'):
                return {
                    'nom_complet': contact_info.get('name', ''),
                    'email': contact_info['email'],
                    'entreprise': self._extract_company_name(url),
                    'url_site': url,
                    'secteur': self._infer_sector(url),
                    'source': f"Google Dork: {dork}",
                    'date_decouverte': datetime.now().isoformat(),
                    'titre_page': title
                }
                
        except Exception as e:
            logger.error(f"Error extracting prospect: {e}")
            
        return None
    
    def _extract_contact_info(self, url: str) -> Dict[str, str]:
        """Extract contact information from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            text_content = soup.get_text()
            emails = re.findall(email_pattern, text_content)
            
            # Extract name from page
            name = self._extract_name(soup)
            
            return {
                'email': emails[0] if emails else '',
                'name': name
            }
            
        except Exception as e:
            logger.error(f"Error extracting contact info from {url}: {e}")
            return {'email': '', 'name': ''}
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract name from webpage"""
        # Try different selectors
        name_selectors = [
            'meta[name="author"]',
            '.author-name',
            '.contact-name',
            '[itemprop="name"]',
            'h1'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '')
                else:
                    return element.get_text(strip=True)
                    
        return ""
    
    def _extract_company_name(self, url: str) -> str:
        """Extract company name from URL or page"""
        domain = urlparse(url).netloc
        company = domain.replace('www.', '').split('.')[0]
        return company.title()
    
    def _infer_sector(self, url: str) -> str:
        """Infer sector from URL and content"""
        # Simple sector inference based on keywords
        sector_keywords = {
            'ecommerce': ['shop', 'store', 'boutique', 'ecommerce'],
            'tech': ['tech', 'digital', 'web', 'software', 'app'],
            'restaurant': ['restaurant', 'cafe', 'bistro', 'food'],
            'real_estate': ['immobilier', 'real', 'estate', 'property'],
            'health': ['health', 'medical', 'clinic', 'pharma'],
            'finance': ['finance', 'bank', 'insurance', 'accounting']
        }
        
        url_lower = url.lower()
        for sector, keywords in sector_keywords.items():
            if any(keyword in url_lower for keyword in keywords):
                return sector
                
        return "general"
    
    def scrape_multiple_dorks(self, dorks: List[str], max_per_dork: int = 10) -> List[Dict[str, Any]]:
        """Scrape multiple Dorks concurrently"""
        all_prospects = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_dork = {
                executor.submit(self.scrape_from_dork, dork, max_per_dork): dork 
                for dork in dorks
            }
            
            for future in concurrent.futures.as_completed(future_to_dork):
                dork = future_to_dork[future]
                try:
                    prospects = future.result()
                    all_prospects.extend(prospects)
                except Exception as e:
                    logger.error(f"Error processing dork {dork}: {e}")
                    
        return all_prospects
    
    def deduplicate_prospects(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate prospects based on email"""
        seen_emails = set()
        unique_prospects = []
        
        for prospect in prospects:
            email = prospect.get('email', '').lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_prospects.append(prospect)
                
        return unique_prospects