"""Custom test script for your specific job searches."""
import asyncio
from src.scrapers.ziprecruiter_scraper import ZipRecruiterScraper


async def test_my_job_search():
    """Test with your specific job search criteria."""
    print("🔍 Testing ZipRecruiter Scraper with Custom Search")
    print("=" * 55)
    
    # Customize these parameters for your search
    SEARCH_QUERIES = [
        "python developer",
        "data scientist", 
        "software engineer",
        "machine learning"
    ]
    
    MAX_PAGES = 1  # Start with 1 page for testing
    
    async with ZipRecruiterScraper(headless=True) as scraper:
        
        for query in SEARCH_QUERIES:
            print(f"\n🎯 Searching for: '{query}'")
            print("-" * 40)
            
            try:
                result = await scraper.search_houston_jobs(
                    query=query,
                    max_pages=MAX_PAGES
                )
                
                # Display results
                print(f"✅ Success: {result.success}")
                print(f"📊 Jobs found: {len(result.jobs)}")
                print(f"🌐 Total available: {result.total_found}")
                print(f"⭐ Average quality: {result.average_quality:.2f}")
                
                # Show top 3 jobs
                if result.jobs:
                    print(f"\n📋 Top {min(3, len(result.jobs))} jobs:")
                    for i, job in enumerate(result.jobs[:3], 1):
                        print(f"\n  {i}. {job.title}")
                        print(f"     🏢 {job.company}")
                        print(f"     📍 {job.location}")
                        print(f"     💰 {job.salary_text or 'Salary not specified'}")
                        print(f"     🏠 {job.remote_type.value}")
                        print(f"     ⭐ Quality: {job.quality_score:.2f}")
                
                if result.errors:
                    print(f"\n⚠️  Errors: {result.errors}")
                
            except Exception as e:
                print(f"❌ Error searching for '{query}': {e}")
            
            # Small delay between searches
            await asyncio.sleep(2)
    
    print(f"\n🎉 Testing completed!")
    print(f"\n💡 Tips:")
    print(f"  • Increase MAX_PAGES to get more jobs")
    print(f"  • Add your specific job titles to SEARCH_QUERIES")
    print(f"  • Set headless=False to see the browser in action")


if __name__ == "__main__":
    asyncio.run(test_my_job_search())
