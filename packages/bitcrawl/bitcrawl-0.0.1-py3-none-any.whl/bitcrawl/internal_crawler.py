"""
Internal Crawler Module
The actual BitCrawler implementation used by the public API
"""

import requests
import json
import csv
import time
import logging
import re
import os
import sys
import threading
from queue import Queue
from collections import deque, defaultdict
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from datetime import datetime
from typing import List, Dict, Set, Optional, Any, Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 is required. Install with: pip install beautifulsoup4")
    sys.exit(1)

from .contextual_searcher import ContextualSearcher


class BitCrawlerInternal:
    """
    Internal crawler class that handles all crawling operations
    This is the actual implementation used by the public BitCrawl API
    """
    
    def __init__(self, start_url: str, mode: str, output_format: str, page_limit: int = 10, context: Optional[str] = None, min_relevance: float = 0.3):
        self.start_url = start_url
        self.mode = mode.lower()
        self.output_format = output_format.lower()
        self.page_limit = page_limit
        self.context = context
        self.min_relevance = min_relevance
        self.visited_urls = set()
        self.crawled_data = []
        self.url_queue = Queue()
        self.session = requests.Session()
        self.domain = self._extract_domain(start_url) if start_url else ""
        self.site_structure = defaultdict(list)
        
        # Configure session with headers
        self.session.headers.update({
            'User-Agent': 'BitCrawl/0.0.1 (Web Crawler; +https://github.com/Akash-nath29/BitCrawl)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Setup logging
        self._setup_logging()
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception as e:
            self.logger.error(f"Error extracting domain from {url}: {e}")
            return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it's the same domain (for crawling mode)
            if self.mode == 'crawl':
                return url.startswith(self.domain)
            
            return True
        except Exception:
            return False
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        try:
            # Remove fragments
            if '#' in url:
                url = url.split('#')[0]
            
            # Remove common tracking parameters
            tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
            parsed = urlparse(url)
            if parsed.query:
                query_params = parse_qs(parsed.query)
                filtered_params = {k: v for k, v in query_params.items() if k not in tracking_params}
                if filtered_params:
                    new_query = urlencode(filtered_params, doseq=True)
                    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                else:
                    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            return url
        except Exception:
            return url
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with error handling and rate limiting"""
        self._rate_limit()
        
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract clean content from HTML"""
        try:
            # Remove unwanted tags
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
                tag.decompose()
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extract main content
            main_content = ""
            
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '#content',
                '.post-content', '.entry-content', '.article-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # If no main content found, extract from body
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text(separator=' ', strip=True)
            
            # Clean up text
            main_content = re.sub(r'\s+', ' ', main_content).strip()
            
            # Extract headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                headings.append({
                    'level': h.name,
                    'text': h.get_text().strip()
                })
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    links.append({
                        'url': absolute_url,
                        'text': link.get_text().strip(),
                        'title': link.get('title', '')
                    })
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'content': main_content,
                'headings': headings,
                'links': links,
                'word_count': len(main_content.split()),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return {
                'url': url,
                'title': "Error",
                'description': "",
                'content': "",
                'headings': [],
                'links': [],
                'word_count': 0,
                'scraped_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                cleaned_url = self._clean_url(absolute_url)
                if self._is_valid_url(cleaned_url) and cleaned_url not in self.visited_urls:
                    links.append(cleaned_url)
        return links
    
    def scrape_single_page(self, url: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Scrape a single webpage with optional contextual filtering"""
        response = self._make_request(url)
        if not response:
            return {'url': url, 'error': 'Failed to fetch page'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Apply contextual filtering if context is provided
        if context:
            self.logger.info(f"Applying contextual filter: '{context}'")
            searcher = ContextualSearcher(context, self.min_relevance)
            contextual_sections = searcher.extract_contextual_content(soup)
            
            # Build contextual result
            result = self._extract_content(soup, url)
            
            if contextual_sections:
                # Replace content with contextual content
                combined_content = '\n\n'.join([section['text'] for section in contextual_sections])
                result['content'] = combined_content
                result['context_query'] = context
                result['total_relevant_sections'] = len(contextual_sections)
                result['content_sections'] = contextual_sections
                result['average_relevance_score'] = sum(s['relevance_score'] for s in contextual_sections) / len(contextual_sections)
                
                self.logger.info(f"Found {len(contextual_sections)} contextually relevant sections")
            else:
                # No relevant content found
                result['content'] = ""
                result['context_query'] = context
                result['total_relevant_sections'] = 0
                result['content_sections'] = []
                result['average_relevance_score'] = 0.0
                
                self.logger.info("No contextually relevant content found")
            
            return result
        else:
            # Regular scraping without context
            return self._extract_content(soup, url)
    
    def crawl_website(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Crawl an entire website following internal links"""
        self.url_queue.put(self.start_url)
        self.visited_urls.add(self.start_url)
        
        while not self.url_queue.empty() and len(self.crawled_data) < self.page_limit:
            current_url = self.url_queue.get()
            
            # Scrape current page
            page_data = self.scrape_single_page(current_url, context)
            
            # Only add page if it has relevant content (when using context)
            if context:
                if page_data.get('total_relevant_sections', 0) > 0:
                    self.crawled_data.append(page_data)
                    self.logger.info(f"Added page with {page_data.get('total_relevant_sections', 0)} relevant sections")
                else:
                    self.logger.info(f"Skipping page with no relevant content: {current_url}")
                    continue  # Don't add to crawled_data, but still extract links
            else:
                self.crawled_data.append(page_data)
            
            # Extract links for further crawling (only if we haven't reached page limit)
            if len(self.crawled_data) < self.page_limit:
                response = self._make_request(current_url)
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = self._extract_links(soup, current_url)
                    
                    # Add new links to queue
                    for link in links:
                        if link not in self.visited_urls and not self.url_queue.full():
                            self.url_queue.put(link)
                            self.visited_urls.add(link)
        
        return self.crawled_data
    
    def search_web(self, query: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo and scrape results"""
        search_url = f"https://duckduckgo.com/html/?q={query}"
        
        self.logger.info(f"Performing contextual web search for: {query} with context: '{context}'")
        response = self._make_request(search_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search result links
        result_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/l/?uddg=' in href:
                # Extract the actual URL from DuckDuckGo's redirect
                try:
                    import urllib.parse
                    actual_url = urllib.parse.unquote(href.split('/l/?uddg=')[1].split('&')[0])
                    if actual_url.startswith('http'):
                        result_links.append(actual_url)
                except:
                    continue
        
        # Limit to page_limit results
        result_links = result_links[:self.page_limit]
        
        # Scrape each result
        results = []
        for link in result_links:
            if len(results) >= self.page_limit:
                break
            
            page_data = self.scrape_single_page(link, context)
            if page_data:
                # Only include pages with relevant content when using context
                if context:
                    if page_data.get('total_relevant_sections', 0) > 0:
                        results.append(page_data)
                else:
                    results.append(page_data)
        
        return results
    
    def map_website(self, url: str) -> Dict[str, Any]:
        """Map website structure and extract link relationships"""
        response = self._make_request(url)
        if not response:
            return {'url': url, 'error': 'Failed to fetch page'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all links
        links = self._extract_links(soup, url)
        
        # Organize links by type
        internal_links = [link for link in links if link.startswith(self.domain)]
        external_links = [link for link in links if not link.startswith(self.domain)]
        
        # Extract page metadata
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Extract headings for structure
        headings = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': h.name,
                'text': h.get_text().strip()
            })
        
        return {
            'url': url,
            'title': title_text,
            'internal_links': internal_links,
            'external_links': external_links,
            'total_internal_links': len(internal_links),
            'total_external_links': len(external_links),
            'page_structure': headings,
            'mapped_at': datetime.now().isoformat()
        }
    
    def extract_structured_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structured data from crawled content"""
        if not data:
            return {'total_pages': 0, 'analysis': 'No data provided'}
        
        # Analyze the crawled data
        total_pages = len(data)
        total_words = sum(page.get('word_count', 0) for page in data)
        
        # Extract all headings
        all_headings = []
        for page in data:
            headings = page.get('headings', [])
            all_headings.extend(headings)
        
        # Extract common keywords
        all_text = ' '.join(page.get('content', '') for page in data)
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only count words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Analyze by context if available
        context_analysis = {}
        if data and 'context_query' in data[0]:
            context = data[0]['context_query']
            relevant_pages = sum(1 for page in data if page.get('total_relevant_sections', 0) > 0)
            avg_relevance = sum(page.get('average_relevance_score', 0) for page in data) / len(data)
            
            context_analysis = {
                'context_query': context,
                'relevant_pages': relevant_pages,
                'average_relevance_score': avg_relevance,
                'total_relevant_sections': sum(page.get('total_relevant_sections', 0) for page in data)
            }
        
        return {
            'total_pages': total_pages,
            'total_words': total_words,
            'average_words_per_page': total_words / total_pages if total_pages > 0 else 0,
            'total_headings': len(all_headings),
            'top_keywords': top_keywords,
            'context_analysis': context_analysis,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def save_output(self, data: Any, filename: str = None):
        """Save output to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bitcrawl_output_{timestamp}.{self.output_format}"
        
        try:
            if self.output_format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif self.output_format == 'csv':
                if isinstance(data, list) and data:
                    # Get all unique keys from all dictionaries
                    all_keys = set()
                    for item in data:
                        if isinstance(item, dict):
                            all_keys.update(item.keys())
                    
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=list(all_keys))
                        writer.writeheader()
                        
                        for item in data:
                            if isinstance(item, dict):
                                # Flatten nested dictionaries
                                flattened = {}
                                for key, value in item.items():
                                    if isinstance(value, (dict, list)):
                                        flattened[key] = json.dumps(value)
                                    else:
                                        flattened[key] = str(value) if value is not None else ""
                                writer.writerow(flattened)
                
                elif isinstance(data, dict):
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data.keys())
                        writer.writeheader()
                        
                        # Flatten nested values
                        flattened = {}
                        for key, value in data.items():
                            if isinstance(value, (dict, list)):
                                flattened[key] = json.dumps(value)
                            else:
                                flattened[key] = str(value) if value is not None else ""
                        writer.writerow(flattened)
                
            elif self.output_format == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    if isinstance(data, (dict, list)):
                        f.write(json.dumps(data, indent=2, ensure_ascii=False))
                    else:
                        f.write(str(data))
            
            self.logger.info(f"Output saved to: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving output: {e}")
            raise