#!/usr/bin/env python3
"""
Sequential Database Populator - Simple, reliable LLM job scraping
Starting with ZipRecruiter (proven working) and expanding from there.
"""

import asyncio
from src.scrapers import create_llm_engineer_scraper
from src.database.job_vector_store import JobVectorStore


async def populate_database_ziprecruiter(location="Houston, TX", max_pages=2):
    """
    Scrape LLM jobs from ZipRecruiter and populate the database.
    
    Args:
        location: Job search location
        max_pages: How many pages to scrape
    """
    
    print("🚀 Sequential LLM Job Database Populator")
    print("=" * 50)
    print(f"📍 Location: {location}")
    print(f"📄 Max pages: {max_pages}")
    print(f"🌐 Site: ZipRecruiter (proven working)")
    
    # Initialize database
    print(f"\n📊 Checking current database status...")
    vector_store = JobVectorStore()
    initial_count = vector_store.collection.count()
    print(f"   Current jobs in database: {initial_count}")
    
    # Start ZipRecruiter search
    print(f"\n🔍 Starting ZipRecruiter LLM job search...")
    print(f"   Searching for LLM Engineer positions")
    print(f"   Please wait - this may take 1-2 minutes...")
    
    try:
        # Create and run ZipRecruiter scraper with proper async context
        async with create_llm_engineer_scraper() as scraper:
            result = await scraper.search_llm_jobs(location=location, max_pages=max_pages)
            
            jobs = result.get("jobs", [])
            print(f"\n📊 ZipRecruiter Search Results:")
            print(f"   🎯 Jobs found: {len(jobs)}")
            
            if jobs:
                print(f"   📝 Sample jobs:")
                for i, job in enumerate(jobs[:3], 1):
                    salary_str = f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary not specified"
                    print(f"      {i}. {job.title} at {job.company}")
                    print(f"         💰 {salary_str} | 🏠 {job.remote_type.value}")
                
                # Add jobs to database
                print(f"\n💾 Adding jobs to vector database...")
                add_result = vector_store.add_jobs_batch(jobs)
                
                print(f"   ✅ Successfully added: {add_result['success']} jobs")
                print(f"   ❌ Failed to add: {add_result['failed']} jobs")
                
                if add_result['failed'] > 0:
                    print(f"   ⚠️  Some jobs failed (likely duplicates)")
                
            else:
                print(f"   ⚠️  No jobs found. This could mean:")
                print(f"      • Very strict LLM filtering (try broader search)")
                print(f"      • Site changes (selectors may need updating)")
                print(f"      • Temporary site issues")
                
    except Exception as e:
        print(f"\n❌ Error during scraping:")
        print(f"   {str(e)}")
        print(f"   This could be due to:")
        print(f"   • Network issues")
        print(f"   • Site blocking bot traffic")
        print(f"   • Browser initialization problems")
        return False
    
    # Final database statistics
    final_count = vector_store.collection.count()
    new_jobs = final_count - initial_count
    
    print(f"\n📈 Database Update Summary:")
    print(f"   📊 Jobs before: {initial_count}")
    print(f"   📊 Jobs after: {final_count}")
    print(f"   🆕 New jobs added: {new_jobs}")
    
    print(f"\n🎉 Database population complete!")
    if final_count > 0:
        print(f"   Ready to search: uv run python gradio_app.py")
    else:
        print(f"   No jobs in database yet. Try running again or check network connection.")
    
    return True


def main():
    """Interactive main function."""
    print("🚀 Welcome to the Sequential LLM Job Database Populator!")
    print("This version focuses on reliability over speed.")
    print()
    
    # Get user input
    location = input("Enter location (or press Enter for 'Houston, TX'): ").strip()
    if not location:
        location = "Houston, TX"
    
    try:
        pages = int(input("Number of pages to scrape (or press Enter for 2): ").strip() or "2")
    except ValueError:
        pages = 2
    
    print(f"\n🎯 Configuration:")
    print(f"   📍 Location: {location}")
    print(f"   📄 Pages: {pages}")
    print(f"   🌐 Site: ZipRecruiter")
    print(f"   ⏱️ Expected time: {pages * 30} seconds")
    
    # Run the scraper
    try:
        success = asyncio.run(populate_database_ziprecruiter(location, pages))
        
        if success:
            print(f"\n✅ Success! Your database has been updated.")
            print(f"Next steps:")
            print(f"   1. uv run python gradio_app.py  # Search your jobs")
            print(f"   2. Add more sites once this works reliably")
        else:
            print(f"\n❌ Something went wrong. Check the error messages above.")
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()