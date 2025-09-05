"""Test script for ZipRecruiter scraper."""
import asyncio
from ziprecruiter_scraper import ZipRecruiterScraper


async def quick_test():
    """Quick test of ZipRecruiter scraper functionality."""
    print("🧪 Quick ZipRecruiter Test")
    print("=" * 30)
    
    async with ZipRecruiterScraper(headless=True) as scraper:
        print("✅ Scraper initialized successfully")
        
        # Test navigation to ZipRecruiter
        search_url = "https://www.ziprecruiter.com/Jobs/Houston-TX"
        success = await scraper.safe_navigate(search_url)
        
        if success:
            print("✅ Successfully navigated to ZipRecruiter Houston jobs")
            
            # Try to extract page title
            title = await scraper.extract_text("h1")
            print(f"📄 Page title: {title}")
            
            # Look for job count
            count_selectors = [
                '[data-testid="job-count"]',
                '.jobs_found',
                'h1:has-text("jobs")'
            ]
            
            for selector in count_selectors:
                count_text = await scraper.extract_text(selector)
                if count_text:
                    print(f"📊 Found job count indicator: {count_text}")
                    break
            
            print("✅ Basic functionality test passed")
        else:
            print("❌ Failed to navigate to ZipRecruiter")


async def search_test():
    """Test actual job searching."""
    print("\n🔍 Testing Job Search")
    print("=" * 30)
    
    async with ZipRecruiterScraper(headless=True) as scraper:
        # Search for a small number of jobs
        result = await scraper.search_houston_jobs(
            query="python",
            max_pages=1  # Just test one page
        )
        
        print(f"\n📊 Search Results:")
        print(f"Success: {result.success}")
        print(f"Jobs found: {len(result.jobs)}")
        print(f"Total available: {result.total_found}")
        print(f"Pages scraped: {result.pages_scraped}")
        
        if result.jobs:
            print(f"\n📋 First job example:")
            job = result.jobs[0]
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")
            print(f"Location: {job.location}")
            print(f"Quality Score: {job.quality_score:.2f}")
            print(f"Has Salary: {job.has_salary}")
            print(f"URL: {job.url[:50]}...")
        
        if result.errors:
            print(f"\n❌ Errors encountered:")
            for error in result.errors:
                print(f"  • {error}")


async def main():
    """Run all tests."""
    try:
        await quick_test()
        await search_test()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        print("Make sure you have installed Playwright browsers:")
        print("  uv run playwright install")


if __name__ == "__main__":
    asyncio.run(main())
