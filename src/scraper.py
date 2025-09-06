"""
Main scraper module that imports all scraper classes from the scrapers directory.
This file provides easy access to all scrapers and common functionality.
"""

import asyncio
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


async def test():
    """Enhanced test script with query options."""
    print("🚀 Testing Job Scrapers with Query System")
    print("=" * 60)
    
    # Show available categories
    print("📋 Available Query Categories:")
    for query_set in ALL_QUERY_SETS:
        print(f"  • {query_set.name}: {len(query_set.queries)} queries")
    
    print("\n" + "=" * 60)
    
    # Demo different search methods
    print("🎯 Demo 1: Search by category (Core LLM)")
    jobs1 = await search_by_category("Core LLM / Generative AI", max_jobs=3)
    print(f"Found {len(jobs1)} jobs\n")
    
    print("🎲 Demo 2: Random query search")
    jobs2 = await search_with_random_query(max_jobs=3)
    print(f"Found {len(jobs2)} jobs\n")
    
    print("🔍 Demo 3: Multiple specific queries")
    test_queries = ["LLM engineer", "RAG engineer", "Python AI engineer"]
    jobs3 = await search_multiple_queries(test_queries, max_jobs_per_query=2)
    print(f"Found {len(jobs3)} unique jobs across {len(test_queries)} queries\n")
    
    # Show some results
    all_jobs = jobs1 + jobs2 + jobs3
    if all_jobs:
        print("📊 Sample Results:")
        for i, job in enumerate(all_jobs[:5], 1):  # Show first 5
            print(f"\n{i}. {job.title} at {job.company}")
            if job.description and len(job.description) > 100:
                print(f"   {job.description[:100]}...")
            else:
                print(f"   {job.description}")


def main():
    """Main entry point for the scraper module."""
    asyncio.run(test())


if __name__ == "__main__":
    main()
