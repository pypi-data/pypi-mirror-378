"""
BitCrawl - A comprehensive web crawler similar to Firecrawl

Features:
- Scrape single pages
- Crawl entire websites
- Map website structure 
- Search web and scrape results
- Extract structured data
- Contextual content filtering

Usage:
    from bitcrawl import BitCrawl
    
    bc = BitCrawl()
    
    # Scrape a single page
    result = bc.scrape("https://example.com")
    
    # Crawl a website with contextual filtering
    results = bc.crawl("https://example.com", context="pricing information", page_limit=10)
    
    # Search the web
    results = bc.search("machine learning tutorials", page_limit=5)
    
    # Map website structure
    structure = bc.map("https://example.com")
"""

__version__ = "0.0.1"
__author__ = "BitCrawl Team"
__email__ = "team@bitcrawl.dev"
__description__ = "A comprehensive web crawler with contextual content filtering"

from .core import BitCrawl

__all__ = ['BitCrawl']