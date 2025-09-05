#!/usr/bin/env python3
"""
Parallel Database Populator - Scrape all 5 sites simultaneously for faster results
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from src.database.job_vector_store import JobVectorStore
from src.scrapers import (
    create_llm_engineer_scraper,
    create_indeed_llm_scraper, 
    create_linkedin_llm_scraper,
    create_glassdoor_llm_scraper,
    create_angellist_llm_scraper
)


async def scrape_ziprecruiter(location: str, pages: int = 2):
    """Scrape ZipRecruiter sequentially (page by page) but in parallel with other sites."""
    try:
        print(f"🌐 ZipRecruiter: Starting sequential page scraping...")
        scraper = create_llm_engineer_scraper()
        
        # Sequential scraping within this site (page 1, then page 2, etc.)
        result = await scraper.search_llm_jobs(location=location, max_pages=pages)
        jobs = result.get("jobs", [])
        
        print(f"🌐 ZipRecruiter: Completed {pages} pages, found {len(jobs)} jobs")
        return {"site": "ziprecruiter", "jobs": jobs, "success": True, "error": None}
    except Exception as e:
        print(f"🌐 ZipRecruiter: Error during sequential scraping - {e}")
        return {"site": "ziprecruiter", "jobs": [], "success": False, "error": str(e)}


async def scrape_indeed(location: str, pages: int = 2):
    """Scrape Indeed sequentially (page by page) but in parallel with other sites."""
    try:
        print(f"🏢 Indeed: Starting sequential page scraping...")
        scraper = create_indeed_llm_scraper()
        
        # Sequential scraping within this site (page 1, then page 2, etc.)
        result = await scraper.search_llm_jobs(location=location, max_pages=pages)
        jobs = result.get("jobs", [])
        
        print(f"🏢 Indeed: Completed {pages} pages, found {len(jobs)} jobs")
        return {"site": "indeed", "jobs": jobs, "success": True, "error": None}
    except Exception as e:
        print(f"🏢 Indeed: Error during sequential scraping - {e}")
        return {"site": "indeed", "jobs": [], "success": False, "error": str(e)}


async def scrape_linkedin(location: str, pages: int = 2):
    """Scrape LinkedIn sequentially (page by page) but in parallel with other sites."""
    try:
        print(f"🔗 LinkedIn: Starting sequential page scraping...")
        scraper = create_linkedin_llm_scraper()
        
        # Sequential scraping within this site (page 1, then page 2, etc.)
        result = await scraper.search_llm_jobs(location=location, max_pages=pages)
        jobs = result.get("jobs", [])
        
        print(f"🔗 LinkedIn: Completed {pages} pages, found {len(jobs)} jobs")
        return {"site": "linkedin", "jobs": jobs, "success": True, "error": None}
    except Exception as e:
        print(f"🔗 LinkedIn: Error during sequential scraping - {e}")
        return {"site": "linkedin", "jobs": [], "success": False, "error": str(e)}


async def scrape_glassdoor(location: str, pages: int = 2):
    """Scrape Glassdoor sequentially (page by page) but in parallel with other sites."""
    try:
        print(f"💰 Glassdoor: Starting sequential page scraping...")
        scraper = create_glassdoor_llm_scraper()
        
        # Sequential scraping within this site (page 1, then page 2, etc.)
        result = await scraper.search_llm_jobs(location=location, max_pages=pages)
        jobs = result.get("jobs", [])
        
        print(f"💰 Glassdoor: Completed {pages} pages, found {len(jobs)} jobs")
        return {"site": "glassdoor", "jobs": jobs, "success": True, "error": None}
    except Exception as e:
        print(f"💰 Glassdoor: Error during sequential scraping - {e}")
        return {"site": "glassdoor", "jobs": [], "success": False, "error": str(e)}


async def scrape_angellist(location: str, pages: int = 2):
    """Scrape AngelList sequentially (page by page) but in parallel with other sites."""
    try:
        print(f"🚀 AngelList: Starting sequential page scraping...")
        scraper = create_angellist_llm_scraper()
        
        # Sequential scraping within this site (page 1, then page 2, etc.)
        result = await scraper.search_llm_jobs(location=location, max_pages=pages)
        jobs = result.get("jobs", [])
        
        print(f"🚀 AngelList: Completed {pages} pages, found {len(jobs)} jobs")
        return {"site": "angellist", "jobs": jobs, "success": True, "error": None}
    except Exception as e:
        print(f"🚀 AngelList: Error during sequential scraping - {e}")
        return {"site": "angellist", "jobs": [], "success": False, "error": str(e)}


async def parallel_populate_database(location="Houston, TX", max_pages_per_site=2):
    """
    Scrape all 5 sites in parallel and populate database.
    
    Args:
        location: Job search location
        max_pages_per_site: How many pages to scrape per site
    """
    
    print("⚡ Hybrid Parallel-Sequential Job Database Populator")
    print("=" * 60)
    print(f"📍 Location: {location}")
    print(f"📄 Max pages per site: {max_pages_per_site}")
    print(f"🌐 Sites: ZipRecruiter, Indeed, LinkedIn, Glassdoor, AngelList")
    print(f"⚡ Mode: HYBRID (sites in parallel, pages sequential per site)")
    print(f"   → Each site scrapes pages 1→2→3 sequentially")
    print(f"   → All 5 sites run simultaneously")
    
    # Check initial database state
    vector_store = JobVectorStore()
    initial_count = vector_store.collection.count()
    print(f"\n📊 Current jobs in database: {initial_count}")
    
    # Launch all scrapers in parallel
    print(f"\n🚀 Launching parallel scraping tasks...")
    print(f"   All 5 sites will search simultaneously...")
    
    start_time = datetime.now()
    
    # Create all scraping tasks
    tasks = [
        scrape_ziprecruiter(location, max_pages_per_site),
        scrape_indeed(location, max_pages_per_site),
        scrape_linkedin(location, max_pages_per_site),
        scrape_glassdoor(location, max_pages_per_site),
        scrape_angellist(location, max_pages_per_site)
    ]
    
    # Wait for all tasks to complete
    print(f"\n⏳ Waiting for all sites to complete...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n📊 Parallel Scraping Results:")
    print(f"   ⏱️ Total time: {duration:.1f} seconds")
    print(f"   🎯 Sites completed: {len(results)}")
    
    # Process results
    all_jobs = []
    successful_sites = []
    failed_sites = []
    
    for result in results:
        if isinstance(result, Exception):
            print(f"   ❌ Exception: {result}")
            continue
            
        site_name = result["site"]
        jobs = result["jobs"]
        success = result["success"]
        
        if success and jobs:
            all_jobs.extend(jobs)
            successful_sites.append(site_name)
            print(f"   ✅ {site_name.title()}: {len(jobs)} jobs")
        elif success:
            successful_sites.append(site_name)
            print(f"   ⚠️ {site_name.title()}: 0 jobs found")
        else:
            failed_sites.append(site_name)
            print(f"   ❌ {site_name.title()}: {result['error']}")
    
    # Deduplicate jobs across sites
    print(f"\n🔄 Deduplicating jobs across sites...")
    unique_jobs = []
    seen_urls = set()
    
    for job in all_jobs:
        if job.url not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(job.url)
    
    removed_duplicates = len(all_jobs) - len(unique_jobs)
    print(f"   📊 Total scraped: {len(all_jobs)} jobs")
    print(f"   🗑️ Duplicates removed: {removed_duplicates}")
    print(f"   ✅ Unique jobs: {len(unique_jobs)}")
    
    # Store in database
    if unique_jobs:
        print(f"\n💾 Storing jobs in vector database...")
        add_result = vector_store.add_jobs_batch(unique_jobs)
        
        final_count = vector_store.collection.count()
        new_jobs = final_count - initial_count
        
        print(f"   ✅ Successfully added: {add_result['success']} jobs")
        print(f"   ❌ Failed to add: {add_result['failed']} jobs")
        print(f"   🆕 Net new jobs: {new_jobs}")
        
    else:
        print(f"\n⚠️ No jobs to add to database")
    
    # Final statistics
    print(f"\n📈 Parallel Scraping Summary:")
    print(f"   ⏱️ Time savings: ~{(len(successful_sites) * 2 * 60) - duration:.0f} seconds vs sequential")
    print(f"   ✅ Successful sites: {len(successful_sites)}")
    print(f"   ❌ Failed sites: {len(failed_sites)}")
    print(f"   🎯 Total unique jobs found: {len(unique_jobs)}")
    
    final_count = vector_store.collection.count()
    print(f"\n📊 Final Database State:")
    print(f"   📊 Total jobs: {final_count}")
    print(f"   🆕 Added this session: {final_count - initial_count}")
    
    print(f"\n🎉 Parallel database population complete!")
    print(f"   Ready to search: uv run python gradio_app.py")
    
    return {
        "total_jobs_found": len(unique_jobs),
        "successful_sites": successful_sites,
        "failed_sites": failed_sites,
        "duration_seconds": duration,
        "jobs_added_to_db": final_count - initial_count
    }


def main():
    """Run hybrid parallel-sequential database population."""
    print("⚡ Hybrid Parallel-Sequential LLM Job Database Populator")
    print("=" * 70)
    print("🎯 HYBRID MODE: Sites run in parallel, pages sequential per site")
    print("   → Respects each site's rate limits (sequential pages)")
    print("   → Maximizes speed (parallel sites)")
    print("   → Best of both worlds!")
    
    location = input("Enter location (or press Enter for 'Houston, TX'): ").strip()
    if not location:
        location = "Houston, TX"
    
    try:
        pages = int(input("Pages per site (or press Enter for 2): ").strip() or "2")
    except ValueError:
        pages = 2
    
    print(f"\n🚀 Starting parallel scraping...")
    print(f"   Location: {location}")
    print(f"   Pages per site: {pages}")
    print(f"   Expected time: 2-4 minutes (vs 8-12 minutes sequential)")
    
    asyncio.run(parallel_populate_database(location, pages))


if __name__ == "__main__":
    main()
