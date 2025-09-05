"""Debug version to see the browser in action."""
import asyncio
from ziprecruiter_scraper import ZipRecruiterScraper


async def debug_scraping():
    """Debug the scraper with visible browser."""
    print("🐛 Debug Mode - Visible Browser")
    print("=" * 35)
    
    # Run with visible browser and slower speed
    async with ZipRecruiterScraper(headless=False) as scraper:
        # Override slow_mo for debugging
        scraper.slow_mo = 1000  # 1 second delays
        
        print("🌐 Browser will open - you can watch the scraping process")
        print("📍 Searching for 'python' jobs in Houston...")
        
        result = await scraper.search_houston_jobs(
            query="python",
            max_pages=1  # Just one page for debugging
        )
        
        print(f"\n📊 Debug Results:")
        print(f"Jobs scraped: {len(result.jobs)}")
        print(f"Success: {result.success}")
        
        if result.jobs:
            job = result.jobs[0]
            print(f"\n📋 First job details:")
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")
            print(f"Location: {job.location}")
            print(f"URL: {job.url}")
        
        print(f"\n⏸️  Browser will stay open for 10 seconds...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(debug_scraping())
