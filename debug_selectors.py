"""Debug script to inspect ZipRecruiter page structure."""
import asyncio
from ziprecruiter_scraper import ZipRecruiterScraper


async def debug_page_structure():
    """Debug the actual page structure to find correct selectors."""
    print("🔍 Debugging ZipRecruiter Page Structure")
    print("=" * 50)
    
    async with ZipRecruiterScraper(headless=False) as scraper:
        # Navigate to search page
        search_url = "https://www.ziprecruiter.com/jobs-search?search=python&location=Houston%2C+TX"
        
        print(f"🌐 Navigating to: {search_url}")
        success = await scraper.safe_navigate(search_url)
        
        if success:
            print("✅ Navigation successful")
            
            # Wait for page to load completely
            await asyncio.sleep(5)
            
            # Try to find various job-related elements
            print("\n🔍 Looking for job listing selectors...")
            
            potential_selectors = [
                '[data-testid="job-listing"]',
                '.job_content',
                '.job-listing',
                '.job-card',
                '.job_result',
                '.jobs-item',
                '[data-qa="job-tile"]',
                '.job-tile',
                'article',
                '[role="article"]',
                '.search-result',
                '.result-item'
            ]
            
            found_selectors = []
            
            for selector in potential_selectors:
                try:
                    elements = await scraper.page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        found_selectors.append((selector, len(elements)))
                    else:
                        print(f"❌ No elements found for: {selector}")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
            
            # If we found some selectors, inspect the first one
            if found_selectors:
                best_selector, count = found_selectors[0]
                print(f"\n🎯 Inspecting first element with selector: {best_selector}")
                
                first_element = await scraper.page.query_selector(best_selector)
                if first_element:
                    # Get the HTML content
                    html_content = await first_element.inner_html()
                    print(f"📄 Element HTML (first 500 chars):")
                    print(html_content[:500])
                    
                    # Try to find common job fields within this element
                    job_title = await scraper._extract_text_from_element(first_element, 'h1, h2, h3, h4, h5, h6')
                    company = await scraper._extract_text_from_element(first_element, '.company, [class*="company"]')
                    location = await scraper._extract_text_from_element(first_element, '.location, [class*="location"]')
                    
                    print(f"\n📋 Extracted data:")
                    print(f"Title: {job_title}")
                    print(f"Company: {company}")
                    print(f"Location: {location}")
            
            # Check for job count/results info
            print(f"\n📊 Looking for job count indicators...")
            count_selectors = [
                '.jobs-found',
                '.search-results-count',
                '[data-testid="job-count"]',
                'h1:has-text("jobs")',
                '.results-count',
                '.total-results'
            ]
            
            for selector in count_selectors:
                count_text = await scraper.extract_text(selector)
                if count_text:
                    print(f"📊 Count indicator found: {selector} = '{count_text}'")
            
            # Keep browser open for manual inspection
            print(f"\n⏸️  Browser staying open for 30 seconds for manual inspection...")
            print(f"💡 You can inspect the page manually now!")
            await asyncio.sleep(30)
        
        else:
            print("❌ Failed to navigate to search page")


if __name__ == "__main__":
    asyncio.run(debug_page_structure())
