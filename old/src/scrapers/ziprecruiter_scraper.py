"""ZipRecruiter job scraper for Houston area."""
import asyncio
import re
from typing import List, Optional
from urllib.parse import urljoin, quote_plus
from datetime import datetime, timedelta

from .playwright_scraper import PlaywrightJobScraper
from ..models.job_models import JobListing, JobType, RemoteType, ScrapingResult


class ZipRecruiterScraper(PlaywrightJobScraper):
    """Scraper specifically for ZipRecruiter job listings."""
    
    def __init__(self, headless: bool = True, job_filter: Optional['JobFilter'] = None, use_llm: bool = False):
        super().__init__(headless=headless, slow_mo=200)
        self.base_url = "https://www.ziprecruiter.com"
        self.source_name = "ziprecruiter"
        
        # Import here to avoid circular imports
        from .smart_job_filter import SmartJobFilter, FilterPresets
        
        # Set up job filtering
        if job_filter is None:
            # Use default software engineer filter with LLM option
            job_filter = FilterPresets.software_engineer(use_llm=use_llm)
        elif use_llm and not job_filter.use_llm:
            # Enable LLM on provided filter if requested
            job_filter.use_llm = True
        
        self.job_filter = SmartJobFilter(job_filter)
        self.use_smart_filtering = True
    
    async def search_houston_jobs(self, 
                                 query: str = "", 
                                 max_pages: int = 5,
                                 job_type: Optional[str] = None) -> ScrapingResult:
        """
        Search for jobs in Houston area.
        
        Args:
            query: Search query (job title, skills, etc.)
            max_pages: Maximum number of pages to scrape
            job_type: Filter by job type if specified
            
        Returns:
            ScrapingResult with found jobs and metadata
        """
        print(f"🔍 Starting ZipRecruiter search for '{query}' in Houston...")
        
        jobs = []
        errors = []
        pages_scraped = 0
        total_found = 0
        
        try:
            # Build search URL
            search_url = self._build_search_url(query, "Houston, TX", job_type)
            
            # Navigate to search results
            if not await self.safe_navigate(search_url):
                errors.append("Failed to load initial search page")
                return ScrapingResult(
                    source=self.source_name,
                    jobs=jobs,
                    success=False,
                    total_found=0,
                    pages_scraped=0,
                    errors=errors
                )
            
            # Get total job count
            total_found = await self._get_total_job_count()
            print(f"📊 Found approximately {total_found} jobs")
            
            # Scrape multiple pages
            for page in range(1, max_pages + 1):
                print(f"📄 Scraping page {page}/{max_pages}...")
                
                if page > 1:
                    # Navigate to next page
                    if not await self._go_to_page(page):
                        print(f"⚠️  Could not navigate to page {page}")
                        break
                
                # Extract jobs from current page
                page_jobs = await self._extract_jobs_from_page()
                jobs.extend(page_jobs)
                pages_scraped += 1
                
                print(f"✅ Extracted {len(page_jobs)} jobs from page {page}")
                
                # Check if there are more pages
                if not await self._has_next_page():
                    print("📄 No more pages available")
                    break
                
                # Random delay between pages
                await self.random_delay(2, 4)
        
        except Exception as e:
            errors.append(f"Scraping error: {str(e)}")
            print(f"❌ Error during scraping: {e}")
        
        # Apply smart filtering if enabled
        filtered_jobs = jobs
        if self.use_smart_filtering and self.job_filter and jobs:
            print(f"🎯 Applying smart filtering to {len(jobs)} jobs...")
            filtered_jobs = self.job_filter.filter_jobs(jobs, verbose=True)
            print(f"📊 Filtering result: {len(jobs)} → {len(filtered_jobs)} jobs")
        
        result = ScrapingResult(
            source=self.source_name,
            jobs=filtered_jobs,
            success=len(filtered_jobs) > 0,
            total_found=total_found,
            pages_scraped=pages_scraped,
            errors=errors,
            metadata={
                "jobs_before_filtering": len(jobs),
                "jobs_after_filtering": len(filtered_jobs),
                "filtering_enabled": self.use_smart_filtering,
                "llm_filtering": self.job_filter.config.use_llm if self.job_filter else False
            }
        )
        
        print(f"✅ Scraping completed: {len(filtered_jobs)} jobs from {pages_scraped} pages")
        print(f"📊 Success rate: {result.success_rate:.1%}")
        print(f"⭐ Average quality: {result.average_quality:.2f}")
        
        return result
    
    def _build_search_url(self, query: str, location: str, job_type: Optional[str] = None) -> str:
        """Build ZipRecruiter search URL."""
        base = f"{self.base_url}/jobs-search"
        params = []
        
        if query:
            params.append(f"search={quote_plus(query)}")
        
        if location:
            params.append(f"location={quote_plus(location)}")
        
        if job_type:
            params.append(f"employment_type={quote_plus(job_type)}")
        
        # Add Houston-specific parameters
        params.extend([
            "radius=25",  # 25 mile radius
            "days=7",     # Last 7 days
            "refine_by_salary=0USD-999999USD"
        ])
        
        url = base
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    async def _get_total_job_count(self) -> int:
        """Extract total number of jobs from search results."""
        try:
            # Look for job count text (multiple possible selectors)
            selectors = [
                '[data-testid="job-count"]',
                '.jobs_found',
                '.search-results-count',
                'h1:has-text("jobs")',
                '[class*="job-count"]'
            ]
            
            for selector in selectors:
                count_text = await self.extract_text(selector)
                if count_text:
                    # Extract number from text like "1,234 jobs found"
                    numbers = re.findall(r'[\d,]+', count_text)
                    if numbers:
                        return int(numbers[0].replace(',', ''))
            
            return 0
        except Exception:
            return 0
    
    async def _extract_jobs_from_page(self) -> List[JobListing]:
        """Extract all job listings from the current page."""
        jobs = []
        
        try:
            # Wait for job listings to load - ZipRecruiter uses article elements
            await self.wait_for_element('article', timeout=10000)
            
            # Get all job cards - ZipRecruiter uses article elements for job listings
            job_cards = await self.page.query_selector_all('article')
            
            # Filter out non-job articles (like headers, footers, etc.)
            # Look for articles that contain job-related content
            filtered_cards = []
            for card in job_cards:
                # Check if this article contains job-like content
                has_job_content = await self._is_job_article(card)
                if has_job_content:
                    filtered_cards.append(card)
            
            job_cards = filtered_cards
            print(f"🎯 Found {len(job_cards)} job cards on page")
            
            for i, card in enumerate(job_cards):
                try:
                    job = await self._extract_single_job(card)
                    if job:
                        jobs.append(job)
                        if i % 5 == 0:  # Progress indicator
                            print(f"📝 Processed {i+1}/{len(job_cards)} jobs...")
                except Exception as e:
                    print(f"⚠️  Error extracting job {i+1}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error extracting jobs from page: {e}")
        
        return jobs
    
    async def _is_job_article(self, article_element) -> bool:
        """Check if an article element contains a job listing."""
        try:
            # Look for job-related content indicators
            text_content = await article_element.text_content()
            if not text_content:
                return False
            
            # Check for typical job keywords in the content
            job_indicators = [
                'apply',
                'salary',
                'full time',
                'part time',
                'remote',
                'experience',
                'skills',
                'requirements'
            ]
            
            text_lower = text_content.lower()
            
            # Must have some job indicators and reasonable length
            has_indicators = any(indicator in text_lower for indicator in job_indicators)
            has_reasonable_length = len(text_content.strip()) > 50
            
            # Check for company/job title structure
            has_headings = bool(await article_element.query_selector('h1, h2, h3, h4, h5, h6'))
            
            return has_indicators and has_reasonable_length and has_headings
            
        except Exception:
            return False
    
    async def _extract_single_job(self, job_element) -> Optional[JobListing]:
        """Extract data from a single job listing element."""
        try:
            # Extract basic information - updated selectors for ZipRecruiter's structure
            title = await self._extract_text_from_element(
                job_element, 
                'h1, h2, h3, h4, h5, h6, a[title], [class*="title"] a, [class*="job"] a'
            )
            
            # Look for company name in various locations
            company = await self._extract_text_from_element(
                job_element, 
                '[class*="company"], [alt*="company"], img[alt]'
            )
            
            # If company not found in dedicated elements, look in text
            if not company:
                # Sometimes company is in the alt text of images
                img_element = await job_element.query_selector('img[alt]')
                if img_element:
                    alt_text = await img_element.get_attribute('alt')
                    if alt_text and len(alt_text) > 1:
                        company = alt_text
            
            # Extract location - look for location indicators
            location = await self._extract_text_from_element(
                job_element,
                '[class*="location"], [class*="city"], [class*="state"]'
            )
            
            # If no dedicated location element, look for text patterns
            if not location:
                text_content = await job_element.text_content()
                if text_content:
                    # Look for Houston, TX or similar patterns
                    import re
                    location_match = re.search(r'([A-Za-z\s]+,\s*[A-Z]{2})', text_content)
                    if location_match:
                        location = location_match.group(1)
            
            # Extract job URL - look for any clickable link
            url_element = await job_element.query_selector('a[href]')
            relative_url = await url_element.get_attribute('href') if url_element else ""
            job_url = urljoin(self.base_url, relative_url) if relative_url else ""
            
            # Extract description/summary - be more flexible
            description = await self._extract_text_from_element(
                job_element, 
                '.job_summary, [data-testid="job-summary"], .job-summary, p, div[class*="description"]'
            )
            
            # If no dedicated description, use the full text content but limit it
            if not description:
                full_text = await job_element.text_content()
                if full_text:
                    # Clean up and limit the description
                    description = full_text.strip()[:500]  # Limit to 500 chars
            
            # Extract salary information
            salary_text = await self._extract_text_from_element(
                job_element,
                '.salary, [data-testid="job-compensation"], .compensation'
            )
            salary_min, salary_max = self._parse_salary(salary_text)
            
            # Extract job type and remote info
            job_type = await self._determine_job_type(job_element)
            remote_type = await self._determine_remote_type(job_element, location)
            
            # Extract posted date
            posted_date = await self._extract_posted_date(job_element)
            
            # Extract job ID from URL or data attributes
            job_id = await self._extract_job_id(job_element, job_url)
            
            # Validate required fields
            if not all([title, company, location]):
                return None
            
            return JobListing(
                title=title.strip(),
                company=company.strip(),
                location=location.strip(),
                description=description.strip() if description else "",
                url=job_url,
                source=self.source_name,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_text=salary_text,
                job_type=job_type,
                remote_type=remote_type,
                posted_date=posted_date,
                job_id=job_id
            )
        
        except Exception as e:
            print(f"⚠️  Error extracting single job: {e}")
            return None
    
    async def _extract_text_from_element(self, parent_element, selector: str) -> str:
        """Extract text from element using selector."""
        try:
            element = await parent_element.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else ""
            return ""
        except Exception:
            return ""
    
    def _parse_salary(self, salary_text: str) -> tuple[Optional[float], Optional[float]]:
        """Parse salary information from text."""
        if not salary_text:
            return None, None
        
        # Remove common words and normalize
        clean_text = re.sub(r'[^\d\$\-\s\.,k]', '', salary_text.lower())
        
        # Look for salary ranges (e.g., "$50,000 - $80,000", "$50k-$80k")
        range_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?\s*[-–]\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?'
        range_match = re.search(range_pattern, clean_text)
        
        if range_match:
            min_val = float(range_match.group(1).replace(',', ''))
            max_val = float(range_match.group(2).replace(',', ''))
            
            # Handle 'k' suffix
            if 'k' in salary_text.lower():
                min_val *= 1000
                max_val *= 1000
            
            return min_val, max_val
        
        # Look for single salary value
        single_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?'
        single_match = re.search(single_pattern, clean_text)
        
        if single_match:
            salary = float(single_match.group(1).replace(',', ''))
            if 'k' in salary_text.lower():
                salary *= 1000
            return salary, salary
        
        return None, None
    
    async def _determine_job_type(self, job_element) -> JobType:
        """Determine job type from job listing."""
        # Look for job type indicators
        type_text = await self._extract_text_from_element(
            job_element, 
            '.job-type, [data-testid="job-type"], .employment-type'
        )
        
        if not type_text:
            # Check in description or other areas
            description = await self._extract_text_from_element(job_element, '.job_summary')
            type_text = description
        
        if type_text:
            type_text = type_text.lower()
            if 'full time' in type_text or 'full-time' in type_text:
                return JobType.FULL_TIME
            elif 'part time' in type_text or 'part-time' in type_text:
                return JobType.PART_TIME
            elif 'contract' in type_text:
                return JobType.CONTRACT
            elif 'temporary' in type_text or 'temp' in type_text:
                return JobType.TEMPORARY
            elif 'intern' in type_text:
                return JobType.INTERNSHIP
        
        return JobType.UNKNOWN
    
    async def _determine_remote_type(self, job_element, location: str) -> RemoteType:
        """Determine if job is remote, hybrid, or onsite."""
        # Check location text
        if location:
            location_lower = location.lower()
            if 'remote' in location_lower:
                return RemoteType.REMOTE
            elif 'hybrid' in location_lower:
                return RemoteType.HYBRID
        
        # Check for remote indicators in other fields
        remote_text = await self._extract_text_from_element(
            job_element,
            '.remote-indicator, [data-testid="remote-type"]'
        )
        
        if remote_text:
            remote_lower = remote_text.lower()
            if 'remote' in remote_lower:
                return RemoteType.REMOTE
            elif 'hybrid' in remote_lower:
                return RemoteType.HYBRID
        
        return RemoteType.ONSITE
    
    async def _extract_posted_date(self, job_element) -> Optional[datetime]:
        """Extract when the job was posted."""
        date_text = await self._extract_text_from_element(
            job_element,
            '.posted-date, [data-testid="posted-date"], .job-age'
        )
        
        if date_text:
            return self._parse_relative_date(date_text)
        
        return None
    
    def _parse_relative_date(self, date_text: str) -> Optional[datetime]:
        """Parse relative date text like '2 days ago'."""
        try:
            date_text = date_text.lower().strip()
            now = datetime.now()
            
            if 'just posted' in date_text or 'today' in date_text:
                return now
            elif 'yesterday' in date_text:
                return now - timedelta(days=1)
            elif 'days ago' in date_text:
                match = re.search(r'(\d+)\s*days?\s*ago', date_text)
                if match:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
            elif 'weeks ago' in date_text:
                match = re.search(r'(\d+)\s*weeks?\s*ago', date_text)
                if match:
                    weeks = int(match.group(1))
                    return now - timedelta(weeks=weeks)
            elif 'months ago' in date_text:
                match = re.search(r'(\d+)\s*months?\s*ago', date_text)
                if match:
                    months = int(match.group(1))
                    return now - timedelta(days=months * 30)
            
            return None
        except Exception:
            return None
    
    async def _extract_job_id(self, job_element, job_url: str) -> Optional[str]:
        """Extract unique job ID."""
        # Try to get from data attributes
        job_id = await job_element.get_attribute('data-job-id')
        if job_id:
            return job_id
        
        # Extract from URL
        if job_url:
            match = re.search(r'/jobs/([^/?]+)', job_url)
            if match:
                return match.group(1)
        
        return None
    
    async def _has_next_page(self) -> bool:
        """Check if there's a next page available."""
        try:
            next_button = await self.page.query_selector(
                '.next-page, [data-testid="next-page"], .pagination-next:not(.disabled)'
            )
            return next_button is not None
        except Exception:
            return False
    
    async def _go_to_page(self, page_number: int) -> bool:
        """Navigate to a specific page number."""
        try:
            # Add page parameter to current URL
            current_url = self.page.url
            separator = "&" if "?" in current_url else "?"
            next_url = f"{current_url}{separator}page={page_number}"
            
            return await self.safe_navigate(next_url)
        except Exception:
            return False


# Convenience functions for different filtering modes
def create_ziprecruiter_scraper(use_llm: bool = False, headless: bool = True, 
                               filter_preset: str = "software_engineer") -> ZipRecruiterScraper:
    """
    Create a ZipRecruiter scraper with specified filtering.
    
    Args:
        use_llm: Enable LLM-based filtering for better job relevance
        headless: Run browser in headless mode
        filter_preset: Available presets:
            - "software_engineer": General software engineering roles
            - "data_scientist": Data science and analytics positions  
            - "remote_only": Remote work only positions
            - "senior_level": Senior/lead/principal level roles
            - "startup_roles": Startup and tech company positions
            - "high_paying": High-salary positions ($120k+)
            - "llm_engineer": AI/ML and LLM engineering (auto-enables LLM)
            - "llm_engineer_strict": Senior AI/ML roles with strict requirements
    """
    from .smart_job_filter import FilterPresets
    
    # Map preset names to FilterPresets methods
    preset_map = {
        "software_engineer": lambda: FilterPresets.software_engineer(use_llm=use_llm),
        "data_scientist": lambda: FilterPresets.data_scientist(use_llm=use_llm),
        "remote_only": lambda: FilterPresets.remote_only(),
        "senior_level": lambda: FilterPresets.senior_level(use_llm=use_llm),
        "startup_roles": lambda: FilterPresets.startup_roles(),
        "high_paying": lambda: FilterPresets.high_paying(use_llm=use_llm),
        "llm_engineer": lambda: FilterPresets.llm_engineer(strict_mode=False),
        "llm_engineer_strict": lambda: FilterPresets.llm_engineer(strict_mode=True),
    }
    
    if filter_preset not in preset_map:
        available_presets = ", ".join(preset_map.keys())
        raise ValueError(f"Unknown filter preset '{filter_preset}'. Available: {available_presets}")
    
    job_filter = preset_map[filter_preset]()
    
    return ZipRecruiterScraper(headless=headless, job_filter=job_filter, use_llm=use_llm)


def list_available_presets():
    """Print all available filter presets with descriptions."""
    presets = {
        "software_engineer": "General software engineering roles (Python, JS, React, etc.)",
        "data_scientist": "Data science and analytics positions (ML, SQL, Python)",
        "remote_only": "Remote work only positions",
        "senior_level": "Senior/lead/principal level roles ($100k+)",
        "startup_roles": "Startup and tech company positions (SaaS, cloud, APIs)",
        "high_paying": "High-salary positions ($120k+)",
        "llm_engineer": "AI/ML and LLM engineering (auto-enables LLM filtering)",
        "llm_engineer_strict": "Senior AI/ML roles with strict requirements ($120k+)",
    }
    
    print("🎯 Available Filter Presets:")
    print("=" * 40)
    for preset, description in presets.items():
        print(f"📋 {preset}")
        print(f"   {description}")
        print(f"   Usage: create_ziprecruiter_scraper(filter_preset='{preset}')")
        print()
    
    return list(presets.keys())


# Example usage and testing
async def test_ziprecruiter_scraper():
    """Test the ZipRecruiter scraper with different filtering modes."""
    print("🏢 Testing ZipRecruiter Scraper")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        ("Traditional Filtering", False, "software_engineer"),
        ("LLM-Enhanced Filtering", True, "software_engineer"),
        ("LLM Engineer Specialist", False, "llm_engineer"),  # Already has LLM enabled
    ]
    
    for config_name, use_llm, preset in test_configs:
        print(f"\n🔍 Testing: {config_name}")
        print("-" * 40)
        
        try:
            scraper = create_ziprecruiter_scraper(
                use_llm=use_llm, 
                headless=True, 
                filter_preset=preset
            )
            
            async with scraper:
                result = await scraper.search_houston_jobs(
                    query="software engineer" if preset != "llm_engineer" else "LLM engineer",
                    max_pages=1  # Limited for testing
                )
                
                print(f"\n📊 {config_name} Results:")
                print(f"Success: {result.success}")
                print(f"Total found: {result.total_found}")
                print(f"Jobs scraped: {len(result.jobs)}")
                print(f"Pages scraped: {result.pages_scraped}")
                
                if result.metadata:
                    print(f"Before filtering: {result.metadata.get('jobs_before_filtering', 'N/A')}")
                    print(f"After filtering: {result.metadata.get('jobs_after_filtering', 'N/A')}")
                    print(f"LLM enabled: {result.metadata.get('llm_filtering', False)}")
                
                # Show sample jobs
                if result.jobs:
                    print(f"\n📋 Top Jobs:")
                    for i, job in enumerate(result.jobs[:2], 1):
                        print(f"\n{i}. {job.title} at {job.company}")
                        print(f"   💰 {job.salary_text or 'Salary not specified'}")
                        print(f"   🏠 {job.remote_type.value} | ⭐ {job.quality_score:.2f}")
                
        except Exception as e:
            print(f"❌ Error testing {config_name}: {e}")


async def demo_llm_vs_traditional():
    """Compare LLM vs traditional filtering side by side."""
    print("🤖 LLM vs Traditional Filtering Comparison")
    print("=" * 50)
    
    query = "software engineer"
    
    # Traditional scraper
    print("\n1️⃣ Traditional Keyword Filtering:")
    traditional_scraper = create_ziprecruiter_scraper(use_llm=False, filter_preset="software_engineer")
    
    async with traditional_scraper:
        traditional_result = await traditional_scraper.search_houston_jobs(query=query, max_pages=1)
    
    # LLM-enhanced scraper  
    print("\n2️⃣ LLM-Enhanced Filtering:")
    llm_scraper = create_ziprecruiter_scraper(use_llm=True, filter_preset="software_engineer")
    
    async with llm_scraper:
        llm_result = await llm_scraper.search_houston_jobs(query=query, max_pages=1)
    
    # Comparison
    print(f"\n📊 Comparison Results:")
    print(f"Traditional: {len(traditional_result.jobs)} jobs kept")
    print(f"LLM-Enhanced: {len(llm_result.jobs)} jobs kept")
    print(f"Quality improvement: {llm_result.average_quality - traditional_result.average_quality:+.2f}")
    
    print(f"\n💡 Key Insights:")
    print(f"• Traditional filtering relies on keyword matching")
    print(f"• LLM filtering adds semantic understanding and quality assessment")
    print(f"• LLM can catch spam, irrelevant roles, and low-quality postings")
    print(f"• Higher quality scores indicate better job relevance")


if __name__ == "__main__":
    asyncio.run(test_ziprecruiter_scraper())
