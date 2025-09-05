"""Test script for the Playwright scraper."""
import asyncio
from playwright_scraper import PlaywrightJobScraper


async def test_scraper():
    """Test the basic Playwright scraper."""
    print("🎭 Testing Playwright Job Scraper")
    print("=" * 40)
    
    # Test with headless mode (default)
    async with PlaywrightJobScraper() as scraper:
        print("\n1. Testing navigation to example.com...")
        success = await scraper.safe_navigate("https://example.com")
        
        if success:
            # Extract some basic information
            title = await scraper.extract_text("h1")
            print(f"   ✓ Page title: {title}")
            
            # Test waiting for an element
            found = await scraper.wait_for_element("p", timeout=5000)
            if found:
                description = await scraper.extract_text("p")
                print(f"   ✓ Found paragraph: {description[:50]}...")
            
            # Add a short pause
            print("\n   Adding brief delay...")
            await scraper.random_delay(1, 2)
        
        print("\n2. Testing navigation to a job site (httpbin for demo)...")
        # Test with a different site that shows headers (useful for debugging)
        success2 = await scraper.safe_navigate("https://httpbin.org/headers")
        
        if success2:
            print("   ✓ Successfully loaded httpbin headers page")
            await scraper.random_delay(1, 2)
    
    print("\n✅ Test completed!")
    print("\nNext steps:")
    print("• Install playwright browsers: playwright install")
    print("• Test with real job sites")
    print("• Add job-specific extraction methods")


if __name__ == "__main__":
    asyncio.run(test_scraper())
