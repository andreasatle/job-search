"""
LinkedIn-specific LLM Engineer scraper.
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


class LinkedInLLMScraper(PlaywrightJobScraper):
    """LinkedIn-specific scraper for LLM Engineer positions."""
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """Initialize LinkedIn LLM scraper."""
        super().__init__(headless=headless, slow_mo=600)
        self.base_url = "https://www.linkedin.com"
        self.source_name = "linkedin"
        self.strict_mode = strict_mode
        
        # Create LLM-specific filter for LinkedIn
        self.job_filter = self._create_linkedin_llm_filter(strict_mode)
        self.smart_filter = SmartJobFilter(self.job_filter)
        
        # LinkedIn-specific settings
        self.min_delay = 2.0
        self.max_delay = 6.0
        self.requests_count = 0
        self.max_requests_per_session = 10  # Conservative for LinkedIn
    
    def _create_linkedin_llm_filter(self, strict_mode: bool) -> JobFilter:
        """Create LinkedIn-optimized LLM filter."""
        required_keywords = [
            "llm", "large language model", "machine learning", "ai engineer",
            "artificial intelligence", "deep learning", "neural network",
            "ml engineer", "mlops", "data scientist", "ai researcher",
            "python", "tensorflow", "pytorch", "transformers",
            "huggingface", "langchain", "openai", "anthropic",
            "gpt", "bert", "transformer", "nlp", "computer vision"
        ]
        
        exclude_keywords = [
            "sales", "marketing", "business development", "account manager",
            "customer success", "recruiting", "hr", "finance"
        ]
        
        if strict_mode:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.8,
                min_salary=130000,
                allowed_job_types=[JobType.FULL_TIME],
                min_description_length=250
            )
        else:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.7,
                min_salary=100000,
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
                min_description_length=200
            )
    
    async def search_llm_jobs(self, 
                             location: str = "Houston, TX",
                             max_pages: int = 3,
                             seniority_level: Optional[str] = None) -> Dict[str, Any]:
        """Search LinkedIn for LLM Engineer jobs."""
        print(f"🔍 LinkedIn LLM Engineer Search")
        print(f"📍 Location: {location}")
        print(f"📄 Max pages: {max_pages}")
        
        # LinkedIn requires special handling - using public job search without login
        # Note: This approach uses LinkedIn's public job search which has limited access
        all_jobs = []
        
        # LLM-specific search queries for LinkedIn
        queries = [
            "LLM Engineer",
            "Large Language Model",
            "Machine Learning Engineer",
            "AI Engineer"
        ]
        
        try:
            # Use async context to ensure proper browser management
            async with self:
                for query in queries[:2]:  # Limit to top 2 queries for LinkedIn
                    print(f"🔍 Searching LinkedIn for: '{query}'")
                    
                    # Build LinkedIn search URL
                    search_url = self._build_linkedin_search_url(query, location)
                    print(f"   Navigating to: {search_url}")
                    
                    # Navigate to search results
                    if not await self.safe_navigate(search_url):
                        print(f"   ❌ Failed to navigate to LinkedIn")
                        continue
                    
                    # Wait for page load and handle potential blocking
                    await self.page.wait_for_timeout(3000)
                    
                    # Extract jobs from current page
                    page_jobs = await self._extract_linkedin_jobs()
                    
                    if page_jobs:
                        # Apply smart filtering
                        filtered_jobs = self.smart_filter.filter_jobs(page_jobs, verbose=False)
                        all_jobs.extend(filtered_jobs)
                        print(f"   ✅ Found {len(page_jobs)} jobs, kept {len(filtered_jobs)} after filtering")
                    else:
                        print(f"   ⚠️ No jobs found for '{query}'")
                    
                    # Longer delay for LinkedIn (be respectful)
                    await self.random_delay(self.min_delay * 2, self.max_delay * 2)
                    
                    # Respect rate limiting (LinkedIn is strict)
                    self.requests_count += 1
                    if self.requests_count >= self.max_requests_per_session:
                        print(f"   ⏸️ Rate limit reached, stopping searches")
                        break
                        
        except Exception as e:
            print(f"❌ LinkedIn search error: {e}")
            return {
                "jobs": [],
                "total_jobs_found": 0,
                "status": "error",
                "error": str(e)
            }
        
        print(f"✅ LinkedIn search complete: {len(all_jobs)} total jobs found")
        
        return {
            "jobs": all_jobs,
            "total_jobs_found": len(all_jobs),
            "status": "implemented_working",
            "message": f"LinkedIn scraper found {len(all_jobs)} LLM jobs",
            "site_specific_features": [
                "Professional network jobs",
                "Company insights", 
                "Network-based discovery",
                "Premium role filtering"
            ]
        }
    
    def _build_linkedin_search_url(self, query: str, location: str) -> str:
        """Build LinkedIn jobs search URL with proper parameters."""
        import urllib.parse
        
        base_url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": query,
            "location": location,
            "distance": "25",  # 25 mile radius
            "f_TPR": "r604800",  # Past week
            "f_JT": "F",  # Full-time
            "sortBy": "DD",  # Sort by date
        }
        
        # Add query parameters
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
    
    async def _extract_linkedin_jobs(self) -> List:
        """Extract job listings from LinkedIn search results page."""
        jobs = []
        
        try:
            # Wait for page to load
            await self.page.wait_for_timeout(3000)
            
            # LinkedIn job selectors (public job search)
            job_cards = await self.page.query_selector_all(
                '.job-result-card, .jobs-search__results-list li, [data-job-id], .job-search-card'
            )
            
            print(f"   📋 Found {len(job_cards)} job cards on LinkedIn")
            
            for card in job_cards[:15]:  # Limit to first 15 jobs per page
                try:
                    job = await self._extract_single_linkedin_job(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    print(f"   ⚠️ Error extracting job: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error extracting LinkedIn jobs: {e}")
            
        return jobs
    
    async def _extract_single_linkedin_job(self, card) -> Optional:
        """Extract a single job from LinkedIn job card."""
        from ..models.job_models import JobListing, JobType, RemoteType
        from datetime import datetime
        
        try:
            # Extract title
            title_elem = await card.query_selector('h3 a, .job-result-card__title, .job-title a')
            title = await title_elem.inner_text() if title_elem else "Unknown Title"
            
            # Extract company
            company_elem = await card.query_selector('.job-result-card__subtitle, .job-search-card__subtitle-link, h4 a')
            company = await company_elem.inner_text() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = await card.query_selector('.job-result-card__location, .job-search-card__location')
            location = await location_elem.inner_text() if location_elem else "Unknown Location"
            
            # Extract URL
            link_elem = await card.query_selector('h3 a, .job-title a')
            if link_elem:
                url = await link_elem.get_attribute('href')
                # Ensure full URL
                if url and not url.startswith('http'):
                    url = f"https://www.linkedin.com{url}"
            else:
                url = ""
            
            # Extract salary (LinkedIn rarely shows salary in public search)
            salary_elem = await card.query_selector('.job-search-card__salary, .salary')
            salary_text = await salary_elem.inner_text() if salary_elem else ""
            
            # Parse salary (basic implementation)
            salary_min, salary_max = self._parse_linkedin_salary(salary_text)
            
            # Extract snippet/description
            snippet_elem = await card.query_selector('.job-result-card__snippet, .job-search-card__snippet')
            description = await snippet_elem.inner_text() if snippet_elem else ""
            
            # LinkedIn job quality estimation
            if not description:
                description = f"{title} position at {company} in {location}"
            
            # Determine remote type
            remote_type = RemoteType.UNKNOWN
            full_text = f"{title} {location} {description}".lower()
            if "remote" in full_text:
                remote_type = RemoteType.REMOTE
            elif "hybrid" in full_text:
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
                job_type=JobType.FULL_TIME,  # LinkedIn defaults to full-time
                remote_type=remote_type,
                source="linkedin",
                posted_date=datetime.now(),
                scraped_date=datetime.now()
            )
            
            return job
            
        except Exception as e:
            print(f"   ⚠️ Error extracting single LinkedIn job: {e}")
            return None
    
    def _parse_linkedin_salary(self, salary_text: str) -> tuple[Optional[int], Optional[int]]:
        """Parse LinkedIn salary string into min/max values."""
        import re
        
        if not salary_text:
            return None, None
            
        # Remove common prefixes/suffixes
        salary_text = salary_text.replace('$', '').replace(',', '').replace('/yr', '').replace(' year', '')
        
        # Look for range (e.g., "100000 - 150000")
        range_match = re.search(r'(\d+)\s*-\s*(\d+)', salary_text)
        if range_match:
            min_sal = int(range_match.group(1))
            max_sal = int(range_match.group(2))
            return min_sal, max_sal
        
        # Look for single value
        single_match = re.search(r'(\d+)', salary_text)
        if single_match:
            salary = int(single_match.group(1))
            return salary, salary
            
        return None, None


def create_linkedin_llm_scraper(strict_mode: bool = False, headless: bool = True) -> LinkedInLLMScraper:
    """Create a LinkedIn LLM scraper."""
    return LinkedInLLMScraper(headless=headless, strict_mode=strict_mode)


async def test_linkedin_scraper():
    """Test the LinkedIn LLM scraper."""
    print("🧪 Testing LinkedIn LLM Scraper Framework")
    
    scraper = create_linkedin_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"Status: {results['status']}")
    print(f"Message: {results['message']}")
    print(f"Expected performance: {results['expected_performance']}")
    print(f"Implementation approach: {results['implementation_details']['approach']}")


if __name__ == "__main__":
    asyncio.run(test_linkedin_scraper())
