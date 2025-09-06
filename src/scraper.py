"""
Main scraper module that imports all scraper classes from the scrapers directory.
This file provides easy access to all scrapers and common functionality.
"""

import argparse
import asyncio
import sys
from typing import List, Optional

# Import all scrapers from the new organized structure
from .scrapers import JobScraper, RemoteOKScraper
from .job import Job
from .queries import (
    get_random_query, 
    get_random_query_from_set, 
    list_query_sets,
    get_all_queries,
    ALL_QUERY_SETS
)


# Main quick search function
async def quick_search(query: str = "software engineer", max_jobs: int = 5) -> List[Job]:
    """Quick job search function using RemoteOK scraper with full descriptions."""
    scraper = RemoteOKScraper()
    return await scraper.search_jobs(query, max_jobs=max_jobs)


# Enhanced search functions using predefined queries
async def search_with_random_query(max_jobs: int = 5) -> List[Job]:
    """Search using a random query from any category."""
    query = get_random_query()
    print(f"🎲 Using random query: '{query}'")
    return await quick_search(query, max_jobs=max_jobs)


async def search_by_category(category: str, max_jobs: int = 5) -> List[Job]:
    """Search using a random query from a specific category."""
    try:
        query = get_random_query_from_set(category)
        print(f"🎯 Using query from '{category}': '{query}'")
        return await quick_search(query, max_jobs=max_jobs)
    except ValueError as e:
        print(f"❌ {e}")
        print(f"Available categories: {list_query_sets()}")
        return []


async def search_multiple_queries(queries: List[str], max_jobs_per_query: int = 3) -> List[Job]:
    """Search using multiple queries and combine results."""
    all_jobs = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}/{len(queries)}: '{query}'")
        jobs = await quick_search(query, max_jobs=max_jobs_per_query)
        all_jobs.extend(jobs)
        print(f"   Found {len(jobs)} jobs")
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job.url and job.url not in seen_urls:
            seen_urls.add(job.url)
            unique_jobs.append(job)
        elif not job.url:  # Keep jobs without URLs
            unique_jobs.append(job)
    
    print(f"\n📊 Total jobs found: {len(all_jobs)}, Unique jobs: {len(unique_jobs)}")
    return unique_jobs


async def comprehensive_search(max_jobs_per_category: int = 2) -> List[Job]:
    """Search across all categories with one random query from each."""
    all_jobs = []
    
    print(f"🚀 Running comprehensive search across {len(ALL_QUERY_SETS)} categories")
    
    for query_set in ALL_QUERY_SETS:
        query = query_set.get_random_query()
        print(f"\n📂 {query_set.name}: '{query}'")
        jobs = await quick_search(query, max_jobs=max_jobs_per_category)
        all_jobs.extend(jobs)
        print(f"   Found {len(jobs)} jobs")
    
    # Remove duplicates
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        if job.url and job.url not in seen_urls:
            seen_urls.add(job.url)
            unique_jobs.append(job)
        elif not job.url:
            unique_jobs.append(job)
    
    print(f"\n📊 Comprehensive search complete: {len(all_jobs)} total, {len(unique_jobs)} unique jobs")
    return unique_jobs


# Re-export for backward compatibility
__all__ = [
    'JobScraper', 'RemoteOKScraper', 'quick_search',
    'search_with_random_query', 'search_by_category', 
    'search_multiple_queries', 'comprehensive_search'
]


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="AI/ML Job Scraper - Search for jobs across multiple categories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "LLM engineer" --max-jobs 10
  %(prog)s --random --max-jobs 5
  %(prog)s --category "Core LLM / Generative AI" --max-jobs 8
  %(prog)s --comprehensive --max-jobs-per-category 3
  %(prog)s --multiple "LLM engineer" "RAG engineer" --max-jobs-per-query 4
  %(prog)s --list-categories
  %(prog)s --list-queries
        """
    )
    
    # Search type (mutually exclusive)
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument(
        "--query", "-q",
        type=str,
        help="Search for specific query (e.g., 'LLM engineer')"
    )
    search_group.add_argument(
        "--random", "-r",
        action="store_true",
        help="Search using a random query from any category"
    )
    search_group.add_argument(
        "--category", "-c",
        type=str,
        help="Search using random query from specific category"
    )
    search_group.add_argument(
        "--comprehensive", "-a",
        action="store_true", 
        help="Search across all categories (one query from each)"
    )
    search_group.add_argument(
        "--multiple", "-m",
        nargs="+",
        help="Search multiple specific queries"
    )
    search_group.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available query categories"
    )
    search_group.add_argument(
        "--list-queries",
        action="store_true",
        help="List all available queries"
    )
    
    # Job limits
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=5,
        help="Maximum number of jobs to fetch (default: 5)"
    )
    parser.add_argument(
        "--max-jobs-per-query",
        type=int,
        default=3,
        help="Max jobs per query for multiple queries (default: 3)"
    )
    parser.add_argument(
        "--max-jobs-per-category", 
        type=int,
        default=2,
        help="Max jobs per category for comprehensive search (default: 2)"
    )
    
    # Output options
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display job details, just show counts"
    )
    parser.add_argument(
        "--brief",
        action="store_true", 
        help="Show brief job info (title, company, description preview)"
    )
    
    return parser


async def run_search(args):
    """Run the appropriate search based on arguments."""
    jobs = []
    
    if args.query:
        print(f"🔍 Searching for: '{args.query}'")
        jobs = await quick_search(args.query, max_jobs=args.max_jobs)
        
    elif args.random:
        print("🎲 Running random query search")
        jobs = await search_with_random_query(max_jobs=args.max_jobs)
        
    elif args.category:
        print(f"🎯 Searching category: '{args.category}'")
        jobs = await search_by_category(args.category, max_jobs=args.max_jobs)
        
    elif args.comprehensive:
        print("🚀 Running comprehensive search across all categories")
        jobs = await comprehensive_search(max_jobs_per_category=args.max_jobs_per_category)
        
    elif args.multiple:
        print(f"🔍 Searching {len(args.multiple)} queries")
        jobs = await search_multiple_queries(args.multiple, max_jobs_per_query=args.max_jobs_per_query)
    
    # Display results
    if jobs:
        print(f"\n📊 Found {len(jobs)} jobs:")
        
        if not args.no_display:
            for i, job in enumerate(jobs, 1):
                if args.brief:
                    print(f"\n{i}. {job.title} at {job.company}")
                    if job.description:
                        preview = job.description[:150] + "..." if len(job.description) > 150 else job.description
                        print(f"   {preview}")
                    if job.url:
                        print(f"   🔗 {job.url}")
                else:
                    print(f"\n{i}.")
                    job.display()
    else:
        print("❌ No jobs found")


def list_categories():
    """List all available query categories."""
    print("📋 Available Query Categories:")
    for query_set in ALL_QUERY_SETS:
        print(f"\n  • {query_set.name}")
        print(f"    {query_set.description}")
        print(f"    Queries: {len(query_set.queries)}")


def list_all_queries():
    """List all available queries."""
    print("📋 All Available Queries:")
    for query_set in ALL_QUERY_SETS:
        print(f"\n{query_set.name}:")
        for query in query_set.queries:
            print(f"  • {query}")


def main():
    """Main entry point with argument parsing."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list commands
    if args.list_categories:
        list_categories()
        return
        
    if args.list_queries:
        list_all_queries()
        return
    
    # Validate category if provided
    if args.category and args.category not in [qs.name for qs in ALL_QUERY_SETS]:
        print(f"❌ Unknown category: '{args.category}'")
        print("Available categories:")
        for qs in ALL_QUERY_SETS:
            print(f"  • {qs.name}")
        sys.exit(1)
    
    # Run the search
    try:
        asyncio.run(run_search(args))
    except KeyboardInterrupt:
        print("\n⏹️  Search cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
