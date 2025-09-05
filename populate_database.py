#!/usr/bin/env python3
"""
Database Populator - Scrape LLM jobs from all 5 sites and store in database
This is the main script to fill your vector database with fresh LLM jobs.
"""

import asyncio
from datetime import datetime
from src.scrapers import create_multi_site_llm_scraper
from src.database.job_vector_store import JobVectorStore


async def populate_database(location="Houston, TX", max_pages_per_site=2):
    """
    Scrape LLM jobs from all 5 sites and populate the database.
    
    Args:
        location: Job search location
        max_pages_per_site: How many pages to scrape per site
    """
    
    print("🚀 LLM Job Database Populator")
    print("=" * 50)
    print(f"📍 Location: {location}")
    print(f"📄 Max pages per site: {max_pages_per_site}")
    print(f"🌐 Sites: ZipRecruiter, Indeed, LinkedIn, Glassdoor, AngelList")
    
    # Initialize database
    print(f"\n📊 Checking current database status...")
    vector_store = JobVectorStore()
    initial_count = vector_store.collection.count()
    print(f"   Current jobs in database: {initial_count}")
    
    # Create multi-site scraper
    print(f"\n🔧 Initializing multi-site LLM scraper...")
    scraper = create_multi_site_llm_scraper()
    
    # Search all sites
    print(f"\n🔍 Starting multi-site LLM job search...")
    print(f"   This will search all enabled sites for LLM Engineer positions")
    print(f"   Please wait - this may take several minutes...")
    
    try:
        # This is the key call - it searches all sites
        results = await scraper.search_all_sites(
            location=location,
            max_pages_per_site=max_pages_per_site
        )
        
        print(f"\n📊 Multi-Site Search Results:")
        print(f"   🎯 Total jobs found: {results.total_jobs_found}")
        print(f"   ✅ Successful sites: {len(results.successful_sites)}")
        print(f"   ❌ Failed sites: {len(results.failed_sites)}")
        print(f"   ⏱️ Search duration: {results.search_duration:.1f} seconds")
        
        if results.successful_sites:
            print(f"\n🌐 Site Performance:")
            for site in results.successful_sites:
                site_result = results.site_results.get(site, {})
                job_count = len([job for job in results.all_jobs if job.source == site])
                print(f"   ✅ {site.title()}: {job_count} jobs")
        
        if results.failed_sites:
            print(f"\n❌ Failed Sites:")
            for site in results.failed_sites:
                print(f"   ❌ {site.title()}: {results.site_results.get(site, {}).get('error', 'Unknown error')}")
        
        # Store jobs in database
        if results.all_jobs:
            print(f"\n💾 Storing jobs in vector database...")
            print(f"   📦 Adding {len(results.all_jobs)} jobs to database...")
            
            add_result = vector_store.add_jobs_batch(results.all_jobs)
            
            print(f"   ✅ Successfully added: {add_result['success']} jobs")
            print(f"   ❌ Failed to add: {add_result['failed']} jobs")
            
            final_count = vector_store.collection.count()
            new_jobs = final_count - initial_count
            
            print(f"\n📈 Database Update Summary:")
            print(f"   📊 Jobs before: {initial_count}")
            print(f"   📊 Jobs after: {final_count}")
            print(f"   🆕 New jobs added: {new_jobs}")
            
        else:
            print(f"\n⚠️ No jobs were found to add to database")
            print(f"   This might be due to:")
            print(f"   • Scraping limitations (anti-bot measures)")
            print(f"   • Network issues")
            print(f"   • All jobs filtered out by quality filters")
        
        # Show database stats
        print(f"\n📊 Final Database Statistics:")
        stats = vector_store.get_statistics()
        print(f"   Total jobs: {stats['total_jobs']}")
        print(f"   Sources: {', '.join(stats['sources'])}")
        print(f"   Latest job: {stats['latest_job_date']}")
        
        print(f"\n🎉 Database population complete!")
        print(f"   Ready to search: uv run python gradio_app.py")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during database population: {e}")
        import traceback
        traceback.print_exc()
        return None


async def populate_single_site(site_name="ziprecruiter", location="Houston, TX"):
    """
    Populate database from a single site (for testing).
    
    Args:
        site_name: Which site to scrape ('ziprecruiter', 'indeed', etc.)
        location: Job search location
    """
    
    print(f"🚀 Single Site Database Populator")
    print("=" * 50)
    print(f"🌐 Site: {site_name.title()}")
    print(f"📍 Location: {location}")
    
    vector_store = JobVectorStore()
    initial_count = vector_store.collection.count()
    
    try:
        if site_name.lower() == "ziprecruiter":
            from src.scrapers import create_llm_engineer_scraper
            scraper = create_llm_engineer_scraper()
            result = await scraper.search_houston_jobs()
            jobs = result.jobs
            
        elif site_name.lower() == "indeed":
            from src.scrapers import create_indeed_llm_scraper
            scraper = create_indeed_llm_scraper()
            result = await scraper.search_llm_jobs(location)
            jobs = result.get('jobs', [])
            
        elif site_name.lower() == "linkedin":
            from src.scrapers import create_linkedin_llm_scraper
            scraper = create_linkedin_llm_scraper()
            result = await scraper.search_llm_jobs(location)
            jobs = result.get('jobs', [])
            
        elif site_name.lower() == "glassdoor":
            from src.scrapers import create_glassdoor_llm_scraper
            scraper = create_glassdoor_llm_scraper()
            result = await scraper.search_llm_jobs(location)
            jobs = result.get('jobs', [])
            
        elif site_name.lower() == "angellist":
            from src.scrapers import create_angellist_llm_scraper
            scraper = create_angellist_llm_scraper()
            result = await scraper.search_llm_jobs(location)
            jobs = result.get('jobs', [])
            
        else:
            print(f"❌ Unknown site: {site_name}")
            return
        
        print(f"📊 Found {len(jobs)} jobs from {site_name.title()}")
        
        if jobs:
            add_result = vector_store.add_jobs_batch(jobs)
            final_count = vector_store.collection.count()
            new_jobs = final_count - initial_count
            
            print(f"✅ Added {new_jobs} new jobs to database")
        else:
            print(f"⚠️ No jobs found from {site_name.title()}")
            
    except Exception as e:
        print(f"❌ Error scraping {site_name}: {e}")


def main():
    """Main function - choose your scraping strategy."""
    
    print("🚀 LLM Job Database Populator")
    print("=" * 60)
    print("Choose your scraping strategy:")
    print("1. Full multi-site scraping (recommended)")
    print("2. Single site testing")
    print("3. Quick ZipRecruiter only (most reliable)")
    
    choice = input("\nEnter choice (1-3, or just press Enter for option 1): ").strip()
    
    if choice == "2":
        site = input("Enter site name (ziprecruiter/indeed/linkedin/glassdoor/angellist): ").strip()
        asyncio.run(populate_single_site(site))
    
    elif choice == "3":
        print("\n🚀 Running ZipRecruiter-only population...")
        asyncio.run(populate_single_site("ziprecruiter"))
    
    else:
        print("\n🚀 Running full multi-site population...")
        asyncio.run(populate_database())


if __name__ == "__main__":
    main()
