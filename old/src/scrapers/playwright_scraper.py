"""Basic Playwright web scraper for job sites."""
import asyncio
import random
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobListing:
    """Simple job listing data structure."""
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    job_type: Optional[str] = None
    source: str = "unknown"


class PlaywrightJobScraper:
    """Base Playwright scraper for job sites."""
    
    def __init__(self, headless: bool = True, slow_mo: int = 100):
        """Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser and create a new page."""
        print("Starting Playwright browser...")
        
        playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic browser fingerprint
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Chicago'  # Houston timezone
        )
        
        # Create a new page
        self.page = await self.context.new_page()
        
        # Set additional headers
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        
        print("✓ Browser started successfully")
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            print("✓ Browser closed")
    
    async def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add a random delay to mimic human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def safe_navigate(self, url: str, wait_for: str = "networkidle") -> bool:
        """Safely navigate to a URL with error handling.
        
        Args:
            url: URL to navigate to
            wait_for: Wait condition ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            print(f"Navigating to: {url}")
            
            # Navigate with timeout
            await self.page.goto(url, wait_until=wait_for, timeout=30000)
            
            # Random delay to mimic human behavior
            await self.random_delay()
            
            print("✓ Navigation successful")
            return True
            
        except Exception as e:
            print(f"✗ Navigation failed: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for an element to appear on the page.
        
        Args:
            selector: CSS selector or text content
            timeout: Timeout in milliseconds
            
        Returns:
            True if element found, False otherwise
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"✗ Element not found: {selector} - {e}")
            return False
    
    async def extract_text(self, selector: str, default: str = "") -> str:
        """Extract text from an element safely.
        
        Args:
            selector: CSS selector
            default: Default value if element not found
            
        Returns:
            Text content or default value
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else default
            return default
        except Exception:
            return default
    
    async def extract_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        """Extract attribute value from an element safely.
        
        Args:
            selector: CSS selector
            attribute: Attribute name (e.g., 'href', 'src')
            default: Default value if element/attribute not found
            
        Returns:
            Attribute value or default value
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value if value else default
            return default
        except Exception:
            return default


# Example usage function
async def test_basic_scraper():
    """Test the basic scraper functionality."""
    print("Testing Basic Playwright Scraper")
    print("=" * 40)
    
    async with PlaywrightJobScraper(headless=False, slow_mo=1000) as scraper:
        # Test navigation to a simple site
        success = await scraper.safe_navigate("https://example.com")
        
        if success:
            # Extract page title
            title = await scraper.extract_text("h1")
            print(f"Page title: {title}")
            
            # Wait a moment to see the page
            await scraper.random_delay(2, 4)


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_basic_scraper())
