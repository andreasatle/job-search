"""
Generic job scraper base class with AngelList implementation.
"""

import asyncio
import re
from typing import List, Optional
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright

# Handle both relative and absolute imports
try:
    from .job import Job
except ImportError:
    from job import Job


class JobScraper(ABC):
    """Base class for all job scrapers."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = ""  # Set in subclasses
        self.site_name = ""  # Set in subclasses
    
    @abstractmethod
    async def search_jobs(self, query: str, location: str = "Houston, TX", max_jobs: int = 10) -> List[Job]:
        """Search for jobs and return a list. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _build_search_url(self, query: str, location: str) -> str:
        """Build the search URL for the specific site."""
        pass
    
    @abstractmethod
    async def _extract_job(self, element) -> Optional[Job]:
        """Extract job data from a page element."""
        pass


class RemoteOKScraper(JobScraper):
    """RemoteOK job scraper for remote startup/tech positions."""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.base_url = "https://remoteok.io"
        self.site_name = "RemoteOK"
    
    def _build_search_url(self, query: str, location: str) -> str:
        """Build RemoteOK search URL."""
        # RemoteOK uses tags for search
        query_encoded = query.replace(' ', '+').lower()
        # Location is less relevant for RemoteOK since it's all remote
        return f"{self.base_url}/?search={query_encoded}"
    
    async def search_jobs(self, query: str, location: str = "Remote", max_jobs: int = 10) -> List[Job]:
        """Search RemoteOK for remote tech jobs."""
        print(f"🔍 Searching {self.site_name} for '{query}' (all remote)")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                # Build search URL
                search_url = self._build_search_url(query, location)
                print(f"📡 URL: {search_url}")
                
                # Navigate to search results
                await page.goto(search_url, wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                # RemoteOK job selectors - they use a table structure
                job_cards = []
                selectors_to_try = [
                    'tr.job',
                    '.job',
                    'tr[data-id]',
                    'table tr:has(td)',
                    '.jobs tr'
                ]
                
                for selector in selectors_to_try:
                    try:
                        cards = await page.query_selector_all(selector)
                        if cards and len(cards) > 3:  # Need several results
                            job_cards = cards
                            print(f"📄 Found {len(job_cards)} job cards using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    page_title = await page.title()
                    print(f"⚠️  No job cards found. Page title: {page_title}")
                    return []
                
                jobs = []
                for i, card in enumerate(job_cards[:max_jobs]):
                    try:
                        job = await self._extract_job(card)
                        if job:
                            jobs.append(job)
                            print(f"✅ {len(jobs)}: {job.title} at {job.company}")
                    except Exception as e:
                        print(f"⚠️  Error extracting job {i+1}: {e}")
                        continue
                
                return jobs
                
            finally:
                await browser.close()
    
    async def _extract_job(self, card) -> Optional[Job]:
        """Extract job data from RemoteOK table row."""
        try:
            # Get all text content for parsing
            text_content = await card.text_content()
            if not text_content or len(text_content.strip()) < 10:
                return None
            
            # RemoteOK uses a table structure with specific columns
            title = "Unknown Title"
            
            # Try to get title from specific selectors
            for selector in ['.company h2', '.position', 'h2', '.jobTitle', 'td:nth-child(2)']:
                title_element = await card.query_selector(selector)
                if title_element:
                    title_text = await title_element.text_content()
                    if title_text and len(title_text.strip()) > 3:
                        title = title_text.strip()
                        break
            
            # Get company name
            company = "Unknown Company"
            for selector in ['.company', '.companyLink', 'h3', 'td:nth-child(1)']:
                company_element = await card.query_selector(selector)
                if company_element:
                    company_text = await company_element.text_content()
                    if company_text and len(company_text.strip()) > 1:
                        company = company_text.strip()
                        break
            
            # Location is always Remote for RemoteOK
            location = "Remote"
            
            # Get description (RemoteOK shows limited info in listing)
            description = text_content[:200] + "..." if len(text_content) > 200 else text_content
            description = description.strip()
            
            # Get URL - RemoteOK links to job details
            url = ""
            url_element = await card.query_selector('a[href]')
            if url_element:
                relative_url = await url_element.get_attribute('href')
                if relative_url:
                    if relative_url.startswith('/'):
                        url = f"{self.base_url}{relative_url}"
                    else:
                        url = relative_url
            
            # Get salary - RemoteOK often shows salary in USD
            salary = None
            salary_patterns = [
                r'\$[\d,]+\s*-\s*\$[\d,]+',  # Range like $80k-$120k
                r'\$[\d,]+[kK]?\+?',         # Single value like $100k+
                r'[\d,]+[kK]\s*-\s*[\d,]+[kK]',  # K format like 80k-120k
                r'\$[\d,]+(?:\.\d{2})?'      # Exact dollar amounts
            ]
            
            for pattern in salary_patterns:
                salary_match = re.search(pattern, text_content)
                if salary_match:
                    salary = salary_match.group(0)
                    break
            
            # All RemoteOK jobs are remote by definition
            remote = True
            
            # Skip if we couldn't extract basic info
            if title == "Unknown Title" or company == "Unknown Company":
                return None
            
            return Job(
                title=title,
                company=company,
                location=location,
                description=description,
                url=url,
                salary=salary,
                remote=remote
            )
            
        except Exception as e:
            print(f"⚠️  Error extracting job: {e}")
            return None


# Simple usage function
async def quick_search(query: str = "software engineer", max_jobs: int = 5) -> List[Job]:
    """Quick job search function using RemoteOK."""
    scraper = RemoteOKScraper()
    return await scraper.search_jobs(query, max_jobs=max_jobs)


if __name__ == "__main__":
    # Simple test
    async def test():
        print("🚀 Testing RemoteOK Scraper")
        jobs = await quick_search("python developer", max_jobs=3)
        print(f"\n📊 Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  • {job}")
            if job.salary:
                print(f"    💰 {job.salary}")
            print(f"    🏠 Remote")  # All RemoteOK jobs are remote
    
    asyncio.run(test())
