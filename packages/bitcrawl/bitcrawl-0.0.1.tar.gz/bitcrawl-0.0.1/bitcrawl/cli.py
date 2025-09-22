# Command Line Interface for BitCrawl
"""
BitCrawl CLI - Command line interface for BitCrawl web crawler
Provides the same functionality as the standalone app.py but through the package
"""

import argparse
import sys
from typing import Optional

from .core import BitCrawl


def main():
    """Main CLI entry point with full argument handling like app.py"""
    parser = argparse.ArgumentParser(
        description="BitCrawl - A comprehensive web crawler with contextual filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bitcrawl --link https://example.com --mode scrape --output json
  bitcrawl --link https://example.com --mode crawl --output csv --pagenumber 50
  bitcrawl --link https://example.com --mode map --output txt
  bitcrawl --link "search query" --mode search --output json --pagenumber 10
  bitcrawl --link https://example.com --mode extract --output json --pagenumber 20
  
Contextual Search Examples:
  bitcrawl --link https://example.com --mode scrape --context "machine learning" --output json
  bitcrawl --link https://example.com --mode crawl --context "python programming" --pagenumber 20 --output csv
  bitcrawl --link "data science" --mode search --context "pandas numpy" --pagenumber 15 --output json

Modes:
  scrape  - Scrape a single page
  crawl   - Crawl entire website (following internal links)
  map     - Extract website structure and link map
  search  - Perform web search and scrape results
  extract - AI-powered data extraction and analysis
        """
    )
    
    parser.add_argument(
        '--link',
        required=True,
        help='URL to crawl or search query for search mode'
    )
    
    parser.add_argument(
        '--mode',
        required=True,
        choices=['scrape', 'crawl', 'map', 'search', 'extract'],
        help='Crawling mode: scrape (single page), crawl (entire site), map (site structure), search (web search), extract (AI extraction)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        choices=['json', 'csv', 'txt'],
        help='Output format: json, csv, or txt'
    )
    
    parser.add_argument(
        '--pagenumber',
        type=int,
        default=10,
        help='Maximum number of pages to crawl (default: 10)'
    )
    
    parser.add_argument(
        '--context',
        type=str,
        help='Context/keywords for filtering relevant content only. Reduces data volume and improves LLM processing efficiency.'
    )
    
    parser.add_argument(
        '--min-relevance',
        type=float,
        default=0.15,
        help='Minimum relevance score for contextual filtering (0.0-1.0, default: 0.15)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for premium features (future use)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.pagenumber < 1:
        print("❌ Error: pagenumber must be greater than 0")
        sys.exit(1)
    
    if args.delay < 0:
        print("❌ Error: delay must be non-negative")
        sys.exit(1)
    
    # Handle search mode URL processing
    original_link = args.link
    if args.mode == 'search' and not args.link.startswith(('http://', 'https://')):
        print(f"🔍 Search mode detected. Query: '{args.link}'")
        # Keep original link for search, BitCrawl will handle it
    
    # Validate URL for non-search modes
    if args.mode != 'search':
        if not args.link.startswith(('http://', 'https://')):
            print("❌ Error: URL must start with http:// or https:// (or provide search keywords with --mode search)")
            sys.exit(1)
    
    # Validate contextual search parameters
    if args.context:
        if args.min_relevance < 0.0 or args.min_relevance > 1.0:
            print("❌ Error: min-relevance must be between 0.0 and 1.0")
            sys.exit(1)
        print(f"🎯 Contextual search enabled: '{args.context}'")
        print(f"📈 Minimum relevance threshold: {args.min_relevance}")
    
    # Display startup info (like app.py)
    print(f"\n🚀 BitCrawl starting...")
    print(f"📍 Target: {original_link}")
    print(f"⚙️  Mode: {args.mode}")
    print(f"📄 Output: {args.output}")
    print(f"📊 Page limit: {args.pagenumber}")
    if args.context:
        print(f"🎯 Context: {args.context}")
        print(f"📈 Min relevance: {args.min_relevance}")
    print("-" * 50)
    
    try:
        # Initialize BitCrawl
        bc = BitCrawl(api_key=args.api_key)
        
        # Set request delay (this would need to be added to BitCrawl core)
        # For now, we'll pass it as a parameter where possible
        
        # Execute based on mode
        if args.mode == 'scrape':
            print("Starting single page scraping...")
            result = bc.scrape(
                url=args.link,
                context=args.context,
                min_relevance=args.min_relevance,
                output_format=args.output
            )
            filename = bc.save(result, output_format=args.output)
            
        elif args.mode == 'crawl':
            print("Starting website crawling...")
            results = bc.crawl(
                url=args.link,
                page_limit=args.pagenumber,
                context=args.context,
                min_relevance=args.min_relevance,
                output_format=args.output
            )
            filename = bc.save(results, output_format=args.output)
            
        elif args.mode == 'map':
            print("Starting website mapping...")
            result = bc.map(
                url=args.link,
                output_format=args.output
            )
            filename = bc.save(result, output_format=args.output)
            
        elif args.mode == 'search':
            print(f"Starting web search for: {original_link}")
            results = bc.search(
                query=original_link,
                page_limit=args.pagenumber,
                context=args.context,
                min_relevance=args.min_relevance,
                output_format=args.output
            )
            filename = bc.save(results, output_format=args.output)
            
        elif args.mode == 'extract':
            print("Starting data extraction...")
            # First crawl, then extract
            crawl_results = bc.crawl(
                url=args.link,
                page_limit=args.pagenumber,
                context=args.context,
                min_relevance=args.min_relevance,
                output_format="dict"
            )
            result = bc.extract(crawl_results, output_format=args.output)
            filename = bc.save(result, output_format=args.output)
        
        print(f"\n✅ BitCrawl completed successfully!")
        print(f"📄 Results saved to: {filename}")
        
        # Show contextual results summary if context was used
        if args.context and args.mode in ['crawl', 'search', 'extract']:
            if isinstance(results, list):
                relevant_pages = len([p for p in results if isinstance(p, dict) and p.get('total_relevant_sections', 0) > 0])
                print(f"🎯 Pages with relevant content: {relevant_pages}")
                if relevant_pages > 0:
                    avg_relevance = sum(p.get('average_relevance_score', 0) for p in results if isinstance(p, dict) and p.get('total_relevant_sections', 0) > 0) / relevant_pages
                    print(f"⭐ Average relevance score: {avg_relevance:.3f}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Crawling interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error during crawling: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()