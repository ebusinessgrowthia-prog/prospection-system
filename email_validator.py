# email_validator.py
import requests
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class EmailValidator:
    def __init__(self, abstract_api_key: str, hunter_api_key: str):
        """Initialize email validator with API keys"""
        self.abstract_api_key = abstract_api_key
        self.hunter_api_key = hunter_api_key
        self.session = requests.Session()
        
    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate single email via Abstract API"""
        if not self.abstract_api_key:
            # Fallback to basic validation if no API key
            return self._basic_validation(email)
            
        try:
            url = f"https://emailvalidation.abstractapi.com/v1/"
            params = {
                'api_key': self.abstract_api_key,
                'email': email
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'email': email,
                'is_valid': data.get('deliverability') == 'DELIVERABLE',
                'score': data.get('quality_score', 0),
                'details': data,
                'source': 'abstract_api'
            }
            
        except Exception as e:
            logger.error(f"Error validating email {email}: {e}")
            return {
                'email': email,
                'is_valid': False,
                'score': 0,
                'error': str(e),
                'fallback': True
            }
    
    def batch_validate(self, emails: List[str]) -> List[Dict[str, Any]]:
        """Validate multiple emails"""
        results = []
        for email in emails:
            result = self.validate_email(email)
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        return results
    
    def _basic_validation(self, email: str) -> Dict[str, Any]:
        """Basic email format validation fallback"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'test@',
            r'@example\.',
            r'fake@',
            r'noemail@',
            r'@mail\.com$',
            r'@tempmail',
            r'10minutemail'
        ]
        
        for invalid in invalid_patterns:
            if re.search(invalid, email, re.IGNORECASE):
                is_valid = False
                break
                
        return {
            'email': email,
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'source': 'basic_validation'
        }
    
    def validate_domain(self, domain: str) -> Dict[str, Any]:
        """Validate domain using Hunter.io (if available)"""
        if not self.hunter_api_key:
            return {'valid': True, 'source': 'no_api'}
            
        try:
            url = f"https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'valid': data.get('data', {}).get('webmail', False) or True,
                'source': 'hunter_io',
                'details': data
            }
            
        except Exception as e:
            logger.error(f"Error validating domain {domain}: {e}")
            return {'valid': True, 'error': str(e)}
