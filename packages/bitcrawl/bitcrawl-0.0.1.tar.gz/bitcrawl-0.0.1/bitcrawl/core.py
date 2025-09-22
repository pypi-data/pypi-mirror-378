"""
BitCrawl Core Module
Main BitCrawl class for web crawling and content extraction
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
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
from typing import List, Dict, Set, Optional, Any, Tuple, Union
from difflib import SequenceMatcher
import math

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 is required. Install with: pip install beautifulsoup4")
    sys.exit(1)

from .contextual_searcher import ContextualSearcher


class BitCrawl:
    """
    BitCrawl - Universal Web Crawling SDK for Developers
    
    A comprehensive, developer-friendly web crawling library with intelligent 
    content filtering and flexible output formats. Perfect for any project that 
    needs web data - from simple scraping to complex data processing pipelines.
    
    Key Features:
    - Multiple crawling modes (scrape, crawl, search, map, extract)
    - Contextual content filtering to reduce noise and improve relevance
    - Multiple output formats (JSON, CSV, TXT)
    - Advanced chunking and formatting options
    - Rate limiting and respectful crawling
    - CLI and Python API support
    
    Use Cases:
    - Web scraping and data extraction
    - Content aggregation and analysis
    - Competitive research and monitoring
    - AI/ML data collection
    - Knowledge base building
    - API data collection
    
    Usage:
        from bitcrawl import BitCrawl
        
        bc = BitCrawl()
        
        # Simple page scraping
        data = bc.scrape("https://example.com")
        
        # Crawl with filtering
        data = bc.crawl("https://example.com", 
                       context="pricing information", 
                       page_limit=10)
        
        # Get structured chunks for processing
        chunks = bc.get_chunks(data, chunk_size=1000)
        
        # Search and extract
        results = bc.search("machine learning tutorials", page_limit=5)
        
        # Crawl a website with contextual filtering
        results = bc.crawl("https://example.com", context="pricing information", page_limit=10)
        
        # Search the web
        results = bc.search("machine learning tutorials", page_limit=5)
        
        # Map website structure
        structure = bc.map("https://example.com")
    """
    
    def __init__(self, delay: float = 1.0, verbose: bool = False, api_key: Optional[str] = None):
        """
        Initialize BitCrawl SDK instance.
        
        Args:
            delay (float): Delay between requests in seconds (default: 1.0)
            verbose (bool): Enable verbose logging for debugging (default: False)
            api_key (str): API key for premium features (future use)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.request_delay = delay
        self._setup_session()
        self._setup_logging(verbose)
        
    def _setup_session(self):
        """Configure session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'BitCrawl/0.0.1 (Web Crawler; +https://github.com/Akash-nath29/BitCrawl)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def _setup_logging(self, verbose: bool = False):
        """Setup logging configuration"""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def scrape(self, 
               url: str, 
               context: Optional[str] = None, 
               min_relevance: float = 0.15,
               output_format: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Scrape a single webpage
        
        Args:
            url: URL to scrape
            context: Optional context for filtering content
            min_relevance: Minimum relevance score for contextual filtering (0.0-1.0)
            output_format: Output format - 'dict', 'json', 'csv', or 'txt'
            
        Returns:
            Scraped content in specified format
        """
        crawler = self._create_crawler(url, "scrape", output_format, 1, context, min_relevance)
        result = crawler.scrape_single_page(url, context)
        
        return self._format_output(result, output_format)
        
    def crawl(self, 
              url: str, 
              page_limit: int = 10, 
              context: Optional[str] = None,
              min_relevance: float = 0.15,
              output_format: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Crawl an entire website following internal links
        
        Args:
            url: Starting URL to crawl
            page_limit: Maximum number of pages to crawl
            context: Optional context for filtering content
            min_relevance: Minimum relevance score for contextual filtering (0.0-1.0)
            output_format: Output format - 'dict', 'json', 'csv', or 'txt'
            
        Returns:
            List of crawled pages in specified format
        """
        crawler = self._create_crawler(url, "crawl", output_format, page_limit, context, min_relevance)
        results = crawler.crawl_website(context)
        
        return self._format_output(results, output_format)
        
    def search(self, 
               query: str, 
               page_limit: int = 10,
               context: Optional[str] = None,
               min_relevance: float = 0.15,
               output_format: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Search the web and scrape results
        
        Args:
            query: Search query or direct URL
            page_limit: Maximum number of results to process
            context: Optional context for filtering content
            min_relevance: Minimum relevance score for contextual filtering (0.0-1.0)
            output_format: Output format - 'dict', 'json', 'csv', or 'txt'
            
        Returns:
            Search results in specified format
        """
        # Handle both search queries and direct URLs
        if query.startswith(('http://', 'https://')):
            # Direct URL - use scrape instead
            return self.scrape(query, context, min_relevance, output_format)
        
        # Convert search query to DuckDuckGo URL
        search_url = f"https://duckduckgo.com/html/?q={query}"
        crawler = self._create_crawler(search_url, "search", output_format, page_limit, context, min_relevance)
        
        # For search mode, we need to handle it as web search
        if context:
            crawler.logger.info(f"Performing contextual web search for: {query} with context: '{context}'")
        results = crawler.search_web(query, context)
        
        return self._format_output(results, output_format)
        
    def map(self, 
            url: str,
            output_format: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Map website structure and extract link relationships
        
        Args:
            url: URL to map
            output_format: Output format - 'dict', 'json', 'csv', or 'txt'
            
        Returns:
            Website structure map in specified format
        """
        crawler = self._create_crawler(url, "map", output_format, 1, None, 0.15)
        result = crawler.map_website(url)
        
        return self._format_output(result, output_format)
        
    def extract(self, 
                data: Union[str, List[Dict[str, Any]]], 
                output_format: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Extract structured data from crawled content
        
        Args:
            data: URL or crawled data to extract from
            output_format: Output format - 'dict', 'json', 'csv', or 'txt'
            
        Returns:
            Extracted structured data in specified format
        """
        if isinstance(data, str):
            # If string provided, crawl it first
            crawl_results = self.crawl(data, page_limit=5, output_format="dict")
            if isinstance(crawl_results, list):
                data = crawl_results
            else:
                data = [crawl_results] if crawl_results else []
        
        crawler = self._create_crawler("", "extract", output_format, 1, None, 0.15)
        result = crawler.extract_structured_data(data)
        
        return self._format_output(result, output_format)
    
    def save(self, 
             data: Any, 
             filename: Optional[str] = None, 
             output_format: str = "json") -> str:
        """
        Save data to file
        
        Args:
            data: Data to save
            filename: Optional filename (auto-generated if not provided)
            output_format: File format - 'json', 'csv', or 'txt'
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bitcrawl_output_{timestamp}.{output_format}"
        
        # Create a temporary crawler for file operations
        crawler = self._create_crawler("", "scrape", output_format, 1, None, 0.15)
        crawler.save_output(data, filename)
        
        return filename
        
    def _create_crawler(self, url: str, mode: str, output_format: str, page_limit: int, context: Optional[str], min_relevance: float):
        """Create internal BitCrawler instance"""
        from .internal_crawler import BitCrawlerInternal
        return BitCrawlerInternal(url, mode, output_format, page_limit, context, min_relevance)
        
    def _format_output(self, data: Any, output_format: str) -> Union[Any, str]:
        """Format output according to specified format"""
        if output_format == "dict":
            return data
        elif output_format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif output_format == "csv":
            # For CSV, we need to flatten the data structure
            if isinstance(data, list):
                if not data:
                    return ""
                    
                # Get all unique keys from all dictionaries
                all_keys = set()
                for item in data:
                    if isinstance(item, dict):
                        all_keys.update(item.keys())
                
                # Create CSV content
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list(all_keys))
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
                
                return output.getvalue()
            elif isinstance(data, dict):
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data.keys())
                writer.writeheader()
                
                # Flatten nested values
                flattened = {}
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        flattened[key] = json.dumps(value)
                    else:
                        flattened[key] = str(value) if value is not None else ""
                writer.writerow(flattened)
                
                return output.getvalue()
            else:
                return str(data)
        elif output_format == "txt":
            if isinstance(data, (dict, list)):
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return str(data)
        else:
            return data
    
    # RAG-Specific Methods for AI Agents and Vector Databases
    
    def get_chunks(self, data: Union[Dict, List], chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """
        Split crawled content into chunks suitable for vector databases and RAG systems.
        
        Args:
            data: Crawled data from scrape(), crawl(), etc.
            chunk_size: Maximum characters per chunk (default: 1000)
            overlap: Character overlap between chunks (default: 100)
            
        Returns:
            List of chunk dictionaries with content, metadata, and source info
        """
        chunks = []
        
        def chunk_text(text: str, url: str, title: str = "", chunk_id_base: str = "") -> List[Dict]:
            """Split text into overlapping chunks"""
            if not text or len(text) <= chunk_size:
                return [{
                    "content": text,
                    "metadata": {
                        "source": url,
                        "title": title,
                        "chunk_id": f"{chunk_id_base}_0",
                        "char_count": len(text),
                        "chunk_index": 0
                    }
                }]
            
            chunk_list = []
            start = 0
            chunk_index = 0
            
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to break at sentence or word boundary
                if end < len(text):
                    last_period = text.rfind('.', start, end)
                    last_space = text.rfind(' ', start, end)
                    if last_period > start + chunk_size // 2:
                        end = last_period + 1
                    elif last_space > start + chunk_size // 2:
                        end = last_space
                
                chunk_content = text[start:end].strip()
                if chunk_content:
                    chunk_list.append({
                        "content": chunk_content,
                        "metadata": {
                            "source": url,
                            "title": title,
                            "chunk_id": f"{chunk_id_base}_{chunk_index}",
                            "char_count": len(chunk_content),
                            "chunk_index": chunk_index,
                            "start_char": start,
                            "end_char": end
                        }
                    })
                
                start = max(end - overlap, start + 1)
                chunk_index += 1
            
            return chunk_list
        
        # Process different data formats
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    content = item.get('content', '')
                    url = item.get('url', f'item_{i}')
                    title = item.get('title', '')
                    chunks.extend(chunk_text(content, url, title, f"doc_{i}"))
        elif isinstance(data, dict):
            if 'content' in data:
                url = data.get('url', 'unknown')
                title = data.get('title', '')
                chunks.extend(chunk_text(data['content'], url, title, "doc_0"))
            else:
                # Handle multiple pages in dict format
                for key, value in data.items():
                    if isinstance(value, dict) and 'content' in value:
                        url = value.get('url', key)
                        title = value.get('title', '')
                        chunks.extend(chunk_text(value['content'], url, title, f"doc_{key}"))
        
        return chunks
    
    def to_vector_format(self, data: Union[Dict, List], include_metadata: bool = True) -> List[Dict]:
        """
        Convert crawled data to vector database format (Pinecone, Weaviate, ChromaDB compatible).
        
        Args:
            data: Crawled data from scrape(), crawl(), etc.
            include_metadata: Include source metadata for enhanced retrieval
            
        Returns:
            List of documents in vector database format
        """
        chunks = self.get_chunks(data)
        vector_docs = []
        
        for chunk in chunks:
            doc = {
                "id": chunk["metadata"]["chunk_id"],
                "text": chunk["content"],
            }
            
            if include_metadata:
                doc["metadata"] = {
                    "source": chunk["metadata"]["source"],
                    "title": chunk["metadata"].get("title", ""),
                    "char_count": chunk["metadata"]["char_count"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
                    "crawl_timestamp": datetime.now().isoformat()
                }
            
            vector_docs.append(doc)
        
        return vector_docs
    
    def for_langchain(self, data: Union[Dict, List]) -> List[Dict]:
        """
        Format data for LangChain Document objects.
        
        Args:
            data: Crawled data
            
        Returns:
            List of documents in LangChain format
        """
        chunks = self.get_chunks(data)
        langchain_docs = []
        
        for chunk in chunks:
            doc = {
                "page_content": chunk["content"],
                "metadata": {
                    "source": chunk["metadata"]["source"],
                    "title": chunk["metadata"].get("title", ""),
                    "chunk_id": chunk["metadata"]["chunk_id"]
                }
            }
            langchain_docs.append(doc)
        
        return langchain_docs
    
    def for_llamaindex(self, data: Union[Dict, List]) -> List[Dict]:
        """
        Format data for LlamaIndex Document objects.
        
        Args:
            data: Crawled data
            
        Returns:
            List of documents in LlamaIndex format
        """
        chunks = self.get_chunks(data)
        llamaindex_docs = []
        
        for chunk in chunks:
            doc = {
                "text": chunk["content"],
                "metadata": {
                    "source": chunk["metadata"]["source"],
                    "title": chunk["metadata"].get("title", ""),
                    "chunk_id": chunk["metadata"]["chunk_id"]
                },
                "id_": chunk["metadata"]["chunk_id"]
            }
            llamaindex_docs.append(doc)
        
        return llamaindex_docs
    
    def estimate_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Estimate token count for text (useful for LLM cost estimation).
        
        Args:
            text: Text to estimate tokens for
            model: Model to estimate for (affects tokenization)
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for most models
        if model.startswith("gpt"):
            return len(text) // 4
        elif "claude" in model.lower():
            return len(text) // 4
        else:
            return len(text) // 4  # Default estimation
    
    def crawl_advanced(self, url: str, context: str = None, max_pages: int = 10, 
                      chunk_size: int = 1000, min_relevance: float = 0.2) -> Dict:
        """
        Advanced crawling with automatic processing and multiple output formats.
        
        Args:
            url: Target URL to crawl
            context: Context for relevance filtering
            max_pages: Maximum pages to crawl
            chunk_size: Chunk size for text processing
            min_relevance: Minimum relevance score
            
        Returns:
            Dictionary with chunks, different formats, and processing stats
        """
        # Crawl with contextual filtering
        raw_data = self.crawl(
            url=url, 
            page_limit=max_pages, 
            context=context, 
            min_relevance=min_relevance
        )
        
        # Create chunks
        chunks = self.get_chunks(raw_data, chunk_size=chunk_size)
        
        # Calculate estimates
        total_chars = sum(len(chunk["content"]) for chunk in chunks)
        estimated_tokens = self.estimate_tokens(" ".join(chunk["content"] for chunk in chunks))
        
        return {
            "chunks": chunks,
            "vector_format": self.to_vector_format(raw_data),
            "langchain_format": self.for_langchain(raw_data),
            "llamaindex_format": self.for_llamaindex(raw_data),
            "stats": {
                "total_chunks": len(chunks),
                "total_characters": total_chars,
                "estimated_tokens": estimated_tokens,
                "pages_crawled": len(raw_data) if isinstance(raw_data, list) else 1,
                "context_used": context is not None
            }
        }
    
    def __repr__(self):
        """String representation of BitCrawl instance"""
        return f"BitCrawl(api_key={'***' if self.api_key else None})"