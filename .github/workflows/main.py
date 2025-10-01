import logging
from datetime import datetime
from monitors.rss_monitor import RSSMonitor
from monitors.webpage_monitor import WebPageMonitor
from utils.notifier import Notifier
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CertificationMonitor:
    def __init__(self):
        self.load_config()
        self.notifier = Notifier(self.settings['notification'])
        self.rss_monitor = RSSMonitor(self.settings)
        self.webpage_monitor = WebPageMonitor(self.settings)
    
    def load_config(self):
        with open('config/sources.yaml', 'r') as f:
            self.sources = yaml.safe_load(f)
        with open('config/settings.yaml', 'r') as f:
            self.settings = yaml.safe_load(f)
    
    def scan_all_sources(self):
        """Scan all configured sources for updates"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Certification Update Scan")
        logger.info(f"⏰ Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info("=" * 60)
        
        all_updates = []
        
        # 1. Monitor RSS Feeds
        logger.info("\n📡 Checking RSS feeds...")
        try:
            rss_updates = self.rss_monitor.check_feeds(
                self.sources.get('rss_feeds', {})
            )
            all_updates.extend(rss_updates)
            logger.info(f"   Found {len(rss_updates)} updates from RSS feeds")
        except Exception as e:
            logger.error(f"❌ Error checking RSS feeds: {e}")
        
        # 2. Monitor Announcement Pages
        logger.info("\n🌐 Checking announcement pages...")
        try:
            page_updates = self.webpage_monitor.check_pages(
                self.sources.get('announcement_pages', {})
            )
            all_updates.extend(page_updates)
            logger.info(f"   Found {len(page_updates)} updates from web pages")
        except Exception as e:
            logger.error(f"❌ Error checking announcement pages: {e}")
        
        # 3. Filter and deduplicate
        logger.info("\n🔍 Filtering and deduplicating...")
        filtered_updates = self.filter_updates(all_updates)
        
        # 4. Send notifications
        logger.info("\n" + "=" * 60)
        if filtered_updates:
            logger.info(f"✅ Found {len(filtered_updates)} relevant certification updates!")
            logger.info("📧 Sending notifications...")
            self.notifier.send_notification(filtered_updates)
            
            # Log update titles
            logger.info("\n📋 Updates found:")
            for i, update in enumerate(filtered_updates, 1):
                logger.info(f"   {i}. [{update['provider'].upper()}] {update['title'][:80]}")
        else:
            logger.info("✅ Scan complete - No new certification updates found")
            logger.info("   This is normal if there haven't been recent announcements")
        
        logger.info("=" * 60)
        return filtered_updates
    
    def filter_updates(self, updates):
        """Filter and deduplicate updates"""
        if not updates:
            return []
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_updates = []
        
        for update in updates:
            url = update.get('url', '')
            title = update.get('title', '')
            key = f"{url}:{title}"
            
            if key not in seen_urls:
                seen_urls.add(key)
                unique_updates.append(update)
        
        # Filter by relevance score
        min_score = self.settings.get('filters', {}).get('min_relevance', 0)
        if min_score > 0:
            unique_updates = [
                u for u in unique_updates 
                if u.get('relevance_score', 100) >= min_score
            ]
        
        # Sort by relevance and date
        unique_updates.sort(
            key=lambda x: (x.get('relevance_score', 0), x.get('published_date', '')), 
            reverse=True
        )
        
        return unique_updates

if __name__ == "__main__":
    try:
        monitor = CertificationMonitor()
        monitor.scan_all_sources()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise
