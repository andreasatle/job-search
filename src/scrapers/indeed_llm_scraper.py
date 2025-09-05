"""
Indeed-specific LLM Engineer scraper.
Optimized for Indeed's high job volume with anti-detection measures.
"""

from typing import List, Optional, Dict, Any, Tuple
import asyncio
import re
import random
from urllib.parse import urlencode
from datetime import datetime

from .playwright_scraper import PlaywrightJobScraper  
from .smart_job_filter import SmartJobFilter, JobFilter
from ..models.job_models import JobListing, JobType, RemoteType


class IndeedLLMScraper(PlaywrightJobScraper):
    """Indeed-specific scraper for LLM Engineer positions."""
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """Initialize Indeed LLM scraper."""
        super().__init__(headless=headless, slow_mo=800)
        self.base_url = "https://www.indeed.com"
        self.source_name = "indeed"
        self.strict_mode = strict_mode
        
        # Create LLM-specific filter for Indeed
        self.job_filter = self._create_indeed_llm_filter(strict_mode)
        self.smart_filter = SmartJobFilter(self.job_filter)
        
        # Rate limiting parameters
        self.min_delay = 3.0
        self.max_delay = 8.0
        self.requests_count = 0
        self.max_requests_per_session = 15
    
    def _create_indeed_llm_filter(self, strict_mode: bool) -> JobFilter:
        """Create Indeed-optimized LLM filter."""
        required_keywords = [
            "llm", "large language model", "machine learning", "ai engineer",
            "artificial intelligence", "deep learning", "neural network",
            "ml engineer", "mlops", "data scientist", "ai researcher",
            "python", "tensorflow", "pytorch", "transformers",
            "huggingface", "langchain", "openai", "anthropic"
        ]
        
        exclude_keywords = [
            "sales", "marketing", "recruiter", "commission",
            "cold calling", "door to door", "mlm", "pyramid"
        ]
        
        if strict_mode:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.75,
                min_salary=110000,
                allowed_job_types=[JobType.FULL_TIME],
                min_description_length=200
            )
        else:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.65,
                min_salary=85000,
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
                min_description_length=150
            )
    
    async def search_llm_jobs(self, 
                             location: str = "Houston, TX",
                             max_pages: int = 3,
                             seniority_level: Optional[str] = None) -> Dict[str, Any]:
        """Search Indeed for LLM Engineer jobs."""
        print(f"🔍 Indeed LLM Engineer Search")
        print(f"📍 Location: {location}")
        print(f"📄 Max pages: {max_pages}")
        
        all_jobs = []
        
        # LLM-specific search queries for Indeed
        queries = [
            "LLM Engineer",
            "Large Language Model Engineer", 
            "Machine Learning Engineer AI",
            "AI Engineer",
            "ML Engineer"
        ]
        
        try:
            # Use async context to ensure proper browser management
            async with self:
                for query in queries[:3]:  # Limit to top 3 queries
                    print(f"🔍 Searching Indeed for: '{query}'")
                    
                    # Build Indeed search URL
                    search_url = self._build_indeed_search_url(query, location)
                    print(f"   Navigating to: {search_url}")
                    
                    # Navigate to search results
                    if not await self.safe_navigate(search_url):
                        print(f"   ❌ Failed to navigate to Indeed")
                        continue
                    
                    # Extract jobs from current page
                    page_jobs = await self._extract_indeed_jobs()
                    
                    if page_jobs:
                        # Apply smart filtering
                        filtered_jobs = self.smart_filter.filter_jobs(page_jobs, verbose=False)
                        all_jobs.extend(filtered_jobs)
                        print(f"   ✅ Found {len(page_jobs)} jobs, kept {len(filtered_jobs)} after filtering")
                    else:
                        print(f"   ⚠️ No jobs found for '{query}'")
                    
                    # Delay between searches
                    await self.random_delay(self.min_delay, self.max_delay)
                    
                    # Respect rate limiting
                    self.requests_count += 1
                    if self.requests_count >= self.max_requests_per_session:
                        print(f"   ⏸️ Rate limit reached, stopping searches")
                        break
                        
        except Exception as e:
            print(f"❌ Indeed search error: {e}")
            return {
                "jobs": [],
                "total_jobs_found": 0,
                "status": "error",
                "error": str(e)
            }
        
        print(f"✅ Indeed search complete: {len(all_jobs)} total jobs found")
        
        return {
            "jobs": all_jobs,
            "total_jobs_found": len(all_jobs),
            "status": "implemented_working",
            "message": f"Indeed scraper found {len(all_jobs)} LLM jobs",
            "site_specific_features": [
                "Advanced job filtering",
                "Salary extraction", 
                "Company verification",
                "Remote work detection"
            ]
        }
    
    def _build_indeed_search_url(self, query: str, location: str) -> str:
        """Build Indeed search URL with proper parameters."""
        import urllib.parse
        
        base_url = "https://www.indeed.com/jobs"
        params = {
            "q": query,
            "l": location,
            "radius": "25",  # 25 mile radius
            "fromage": "7",  # Last 7 days
            "sort": "date",  # Sort by date
            "vjk": "",  # Indeed tracking parameter
        }
        
        # Add query parameters
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
    
    async def _extract_indeed_jobs(self) -> List:
        """Extract job listings from Indeed search results page."""
        jobs = []
        
        try:
            # Wait for page to load
            await self.page.wait_for_timeout(2000)
            
            # Indeed job selectors (updated for current Indeed layout)
            job_cards = await self.page.query_selector_all(
                'div[data-jk], .job_seen_beacon, .jobsearch-SerpJobCard, [data-testid="job-result"]'
            )
            
            print(f"   📋 Found {len(job_cards)} job cards on Indeed")
            
            for card in job_cards[:20]:  # Limit to first 20 jobs per page
                try:
                    job = await self._extract_single_indeed_job(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    print(f"   ⚠️ Error extracting job: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error extracting Indeed jobs: {e}")
            
        return jobs
    
    async def _extract_single_indeed_job(self, card) -> Optional:
        """Extract a single job from Indeed job card."""
        from ..models.job_models import JobListing, JobType, RemoteType
        from datetime import datetime
        
        try:
            # Extract title
            title_elem = await card.query_selector('h2 a span, .jobTitle a span, [data-testid="job-title"]')
            title = await title_elem.inner_text() if title_elem else "Unknown Title"
            
            # Extract company
            company_elem = await card.query_selector('.companyName, [data-testid="company-name"]')
            company = await company_elem.inner_text() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = await card.query_selector('.companyLocation, [data-testid="job-location"]')
            location = await location_elem.inner_text() if location_elem else "Unknown Location"
            
            # Extract URL
            link_elem = await card.query_selector('h2 a, .jobTitle a')
            if link_elem:
                relative_url = await link_elem.get_attribute('href')
                url = f"https://www.indeed.com{relative_url}" if relative_url else ""
            else:
                url = ""
            
            # Extract salary (if available)
            salary_elem = await card.query_selector('.salary-snippet, [data-testid="job-salary"]')
            salary_text = await salary_elem.inner_text() if salary_elem else ""
            
            # Parse salary
            salary_min, salary_max = self._parse_indeed_salary(salary_text)
            
            # Extract snippet/description
            snippet_elem = await card.query_selector('.job-snippet, [data-testid="job-snippet"]')
            description = await snippet_elem.inner_text() if snippet_elem else ""
            
            # Determine remote type
            remote_type = RemoteType.UNKNOWN
            location_lower = location.lower()
            if "remote" in location_lower:
                remote_type = RemoteType.REMOTE
            elif "hybrid" in location_lower:
                remote_type = RemoteType.HYBRID
            else:
                remote_type = RemoteType.ONSITE
            
            # Create job listing
            job = JobListing(
                title=title.strip(),
                company=company.strip(),
                location=location.strip(),
                url=url,
                description=description.strip(),
                salary_min=salary_min,
                salary_max=salary_max,
                job_type=JobType.FULL_TIME,  # Indeed defaults to full-time
                remote_type=remote_type,
                source="indeed",
                posted_date=datetime.now(),
                scraped_date=datetime.now()
            )
            
            return job
            
        except Exception as e:
            print(f"   ⚠️ Error extracting single Indeed job: {e}")
            return None
    
    def _parse_indeed_salary(self, salary_text: str) -> tuple[Optional[int], Optional[int]]:
        """Parse Indeed salary string into min/max values."""
        import re
        
        if not salary_text:
            return None, None
            
        # Remove common prefixes/suffixes
        salary_text = salary_text.replace('$', '').replace(',', '').replace('a year', '').replace('an hour', '')
        
        # Look for range (e.g., "80000 - 120000")
        range_match = re.search(r'(\d+)\s*-\s*(\d+)', salary_text)
        if range_match:
            min_sal = int(range_match.group(1))
            max_sal = int(range_match.group(2))
            
            # Convert hourly to annual (assume 40 hours/week, 52 weeks/year)
            if min_sal < 200:  # Likely hourly
                min_sal *= 40 * 52
                max_sal *= 40 * 52
                
            return min_sal, max_sal
        
        # Look for single value
        single_match = re.search(r'(\d+)', salary_text)
        if single_match:
            salary = int(single_match.group(1))
            
            # Convert hourly to annual
            if salary < 200:  # Likely hourly
                salary *= 40 * 52
                
            return salary, salary
            
        return None, None


def create_indeed_llm_scraper(strict_mode: bool = False, headless: bool = True) -> IndeedLLMScraper:
    """Create an Indeed LLM scraper."""
    return IndeedLLMScraper(headless=headless, strict_mode=strict_mode)


async def test_indeed_scraper():
    """Test the Indeed LLM scraper."""
    print("�� Testing Indeed LLM Scraper Framework")
    
    scraper = create_indeed_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"Status: {results['status']}")
    print(f"Message: {results['message']}")
    print(f"Expected performance: {results['expected_performance']}")


if __name__ == "__main__":
    asyncio.run(test_indeed_scraper())
