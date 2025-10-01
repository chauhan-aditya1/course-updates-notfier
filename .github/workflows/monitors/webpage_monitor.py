import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class WebPageMonitor:
    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_pages(self, pages_config):
        """Check all announcement pages"""
        all_updates = []
        
        for provider, pages in pages_config.items():
            logger.info(f"Checking {provider.upper()} announcement pages...")
            
            for page_info in pages:
                try:
                    updates = self.check_single_page(page_info, provider)
                    all_updates.extend(updates)
                    logger.info(f"  ✓ {page_info['name']}: {len(updates)} updates found")
                except Exception as e:
                    logger.error(f"  ✗ Error checking {page_info['name']}: {str(e)}")
        
        return all_updates
    
    def check_single_page(self, page_info, provider):
        """Check a single announcement page"""
        try:
            response = self.session.get(page_info['url'], timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {page_info['url']}: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        updates = []
        
        if provider == 'aws':
            updates = self.parse_aws_page(soup, page_info)
        elif provider == 'azure':
            updates = self.parse_azure_page(soup, page_info)
        
        # Add common metadata
        for update in updates:
            update['provider'] = provider
            update['source'] = page_info['name']
            update['type'] = 'webpage'
        
        return updates
    
    def parse_aws_page(self, soup, page_info):
        """Parse AWS certification changes page"""
        updates = []
        
        # Look for any text containing the check_for terms
        text_content = soup.get_text()
        
        for term in page_info['check_for']:
            if term.lower() in text_content.lower():
                # Find sections mentioning this term
                sections = soup.find_all(['h2', 'h3', 'h4', 'p', 'div'], 
                                        string=re.compile(term, re.IGNORECASE))
                
                for section in sections[:5]:  # Limit results
                    parent = section.find_parent(['div', 'section', 'article'])
                    if parent:
                        update = {
                            'title': section.get_text().strip()[:200],
                            'url': page_info['url'],
                            'summary': parent.get_text().strip()[:500],
                            'relevance_score': 75,
                            'published_date': datetime.now().isoformat(),
                            'keywords_matched': [term]
                        }
                        updates.append(update)
                        break  # One update per term is enough
        
        return updates
    
    def parse_azure_page(self, soup, page_info):
        """Parse Microsoft Learn announcements"""
        updates = []
        
        # Look for text containing check_for terms
        text_content = soup.get_text()
        
        for term in page_info['check_for']:
            if term.lower() in text_content.lower():
                sections = soup.find_all(['h2', 'h3', 'h4', 'div'], 
                                        string=re.compile(term, re.IGNORECASE))
                
                for section in sections[:5]:
                    update = {
                        'title': section.get_text().strip()[:200] if section else f"Azure: {term}",
                        'url': page_info['url'],
                        'summary': f"Found mention of '{term}' on Microsoft certification page",
                        'relevance_score': 70,
                        'published_date': datetime.now().isoformat(),
                        'keywords_matched': [term]
                    }
                    updates.append(update)
                    break
        
        return updates
