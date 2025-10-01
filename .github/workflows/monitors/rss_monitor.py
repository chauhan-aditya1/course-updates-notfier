import feedparser
import logging
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re

logger = logging.getLogger(__name__)

class RSSMonitor:
    def __init__(self, settings):
        self.settings = settings
        self.lookback_days = settings.get('lookback_days', 7)
    
    def check_feeds(self, feeds_config):
        """Check all RSS feeds for updates"""
        all_updates = []
        
        for provider, feeds in feeds_config.items():
            logger.info(f"Checking {provider.upper()} feeds...")
            
            for feed_info in feeds:
                try:
                    updates = self.check_single_feed(feed_info, provider)
                    all_updates.extend(updates)
                    logger.info(f"  ✓ {feed_info['name']}: {len(updates)} relevant posts")
                except Exception as e:
                    logger.error(f"  ✗ Error checking {feed_info['name']}: {str(e)}")
        
        return all_updates
    
    def check_single_feed(self, feed_info, provider):
        """Check a single RSS feed"""
        feed = feedparser.parse(feed_info['url'])
        updates = []
        
        cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
        
        for entry in feed.entries:
            # Parse publication date
            pub_date = self.parse_date(entry)
            
            # Skip old entries
            if pub_date and pub_date < cutoff_date:
                continue
            
            # Check if entry is relevant
            relevance = self.calculate_relevance(entry, feed_info['keywords'])
            
            if relevance > 0:
                update = {
                    'provider': provider,
                    'source': feed_info['name'],
                    'title': entry.get('title', 'No title'),
                    'url': entry.get('link', ''),
                    'summary': self.clean_html(entry.get('summary', entry.get('description', ''))),
                    'published_date': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                    'relevance_score': relevance,
                    'type': 'rss',
                    'keywords_matched': self.get_matched_keywords(
                        entry, feed_info['keywords']
                    )
                }
                updates.append(update)
        
        return updates
    
    def parse_date(self, entry):
        """Parse date from feed entry"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                return date_parser.parse(entry.published)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6])
            elif hasattr(entry, 'updated'):
                return date_parser.parse(entry.updated)
        except Exception as e:
            logger.debug(f"Could not parse date: {e}")
        
        return None
    
    def calculate_relevance(self, entry, keywords):
        """Calculate relevance score based on keywords"""
        text = f"{entry.get('title', '')} {entry.get('summary', '')} {entry.get('description', '')}".lower()
        
        score = 0
        for keyword in keywords:
            # Exact match
            if keyword.lower() in text:
                score += 30
            # Partial match
            elif any(word in text for word in keyword.lower().split()):
                score += 10
        
        # Boost for certain important terms
        important_terms = ['retiring', 'new version', 'updated', 'launching', 'changes', 'announcement']
        for term in important_terms:
            if term in text:
                score += 20
        
        return min(score, 100)  # Cap at 100
    
    def get_matched_keywords(self, entry, keywords):
        """Get list of matched keywords"""
        text = f"{entry.get('title', '')} {entry.get('summary', '')} {entry.get('description', '')}".lower()
        matched = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                matched.append(keyword)
        
        return matched[:5]  # Limit to 5 keywords
    
    def clean_html(self, html_text):
        """Remove HTML tags and clean text"""
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            text = h.handle(html_text)
            # Limit length
            return text[:500] + '...' if len(text) > 500 else text
        except:
            # Fallback: simple HTML removal
            import re
            text = re.sub('<[^<]+?>', '', html_text)
            return text[:500] + '...' if len(text) > 500 else text
