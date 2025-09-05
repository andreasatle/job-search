"""
Enhanced ZipRecruiter scraper with smart job filtering.
"""

from typing import List, Optional
from .ziprecruiter_scraper import ZipRecruiterScraper
from .smart_job_filter import SmartJobFilter, JobFilter, FilterPresets
from ..models.job_models import JobListing, ScrapingResult


class FilteredZipRecruiterScraper(ZipRecruiterScraper):
    """ZipRecruiter scraper with intelligent job filtering."""
    
    def __init__(self, job_filter: Optional[JobFilter] = None, headless: bool = True):
        """
        Initialize scraper with optional job filter.
        
        Args:
            job_filter: JobFilter configuration for filtering results
            headless: Run browser in headless mode
        """
        super().__init__(headless=headless)
        
        # Set up smart filtering
        if job_filter:
            self.smart_filter = SmartJobFilter(job_filter)
            self.filtering_enabled = True
        else:
            self.smart_filter = None
            self.filtering_enabled = False
        
        self.job_filter_config = job_filter
    
    async def search_houston_jobs(self, 
                                 query: str = "", 
                                 max_pages: int = 5,
                                 job_type: Optional[str] = None,
                                 apply_smart_filter: bool = True) -> ScrapingResult:
        """
        Search for jobs with optional smart filtering.
        
        Args:
            query: Search query (job title, skills, etc.)
            max_pages: Maximum number of pages to scrape
            job_type: Filter by job type if specified
            apply_smart_filter: Whether to apply smart filtering to results
            
        Returns:
            ScrapingResult with filtered jobs and metadata
        """
        print(f"🔍 Starting filtered ZipRecruiter search for '{query}' in Houston...")
        
        if self.filtering_enabled and apply_smart_filter:
            print(f"🎯 Smart filtering enabled:")
            if self.job_filter_config.required_keywords:
                print(f"   📝 Required keywords: {self.job_filter_config.required_keywords[:3]}...")
            if self.job_filter_config.exclude_keywords:
                print(f"   ❌ Exclude keywords: {self.job_filter_config.exclude_keywords[:3]}...")
            print(f"   ⭐ Min quality score: {self.job_filter_config.min_quality_score}")
            if self.job_filter_config.min_salary:
                print(f"   💰 Min salary: ${self.job_filter_config.min_salary:,}")
        
        # Get raw results from parent scraper
        raw_result = await super().search_houston_jobs(query, max_pages, job_type)
        
        # Apply smart filtering if enabled
        if self.filtering_enabled and apply_smart_filter and raw_result.jobs:
            print(f"\n🎯 Applying smart filters to {len(raw_result.jobs)} scraped jobs...")
            
            filtered_jobs = self.smart_filter.filter_jobs(raw_result.jobs, verbose=True)
            
            # Create new result with filtered jobs
            filtered_result = ScrapingResult(
                source=raw_result.source,
                jobs=filtered_jobs,
                success=raw_result.success,
                total_found=raw_result.total_found,
                pages_scraped=raw_result.pages_scraped,
                errors=raw_result.errors,
                # Add filtering metadata
                metadata={
                    **raw_result.metadata,
                    "smart_filtering_applied": True,
                    "jobs_before_filtering": len(raw_result.jobs),
                    "jobs_after_filtering": len(filtered_jobs),
                    "filter_efficiency": len(filtered_jobs) / len(raw_result.jobs) if raw_result.jobs else 0
                }
            )
            
            print(f"✅ Smart filtering complete: {len(filtered_jobs)}/{len(raw_result.jobs)} jobs kept")
            return filtered_result
        
        else:
            print("ℹ️  No smart filtering applied")
            return raw_result
    
    def set_filter(self, job_filter: JobFilter):
        """Update the job filter configuration."""
        self.job_filter_config = job_filter
        self.smart_filter = SmartJobFilter(job_filter)
        self.filtering_enabled = True
    
    def disable_filtering(self):
        """Disable smart filtering."""
        self.filtering_enabled = False
        self.smart_filter = None
    
    def get_filter_stats(self) -> dict:
        """Get statistics about the current filter configuration."""
        if not self.job_filter_config:
            return {"filtering_enabled": False}
        
        return {
            "filtering_enabled": self.filtering_enabled,
            "required_keywords_count": len(self.job_filter_config.required_keywords or []),
            "exclude_keywords_count": len(self.job_filter_config.exclude_keywords or []),
            "min_quality_score": self.job_filter_config.min_quality_score,
            "min_salary": self.job_filter_config.min_salary,
            "max_salary": self.job_filter_config.max_salary,
            "job_types_allowed": len(self.job_filter_config.allowed_job_types or []),
            "remote_types_allowed": len(self.job_filter_config.allowed_remote_types or [])
        }


# Convenience functions for common use cases
def create_software_engineer_scraper(headless: bool = True) -> FilteredZipRecruiterScraper:
    """Create a scraper optimized for software engineering roles."""
    return FilteredZipRecruiterScraper(
        job_filter=FilterPresets.software_engineer(),
        headless=headless
    )

def create_data_scientist_scraper(headless: bool = True) -> FilteredZipRecruiterScraper:
    """Create a scraper optimized for data science roles."""
    return FilteredZipRecruiterScraper(
        job_filter=FilterPresets.data_scientist(),
        headless=headless
    )

def create_remote_only_scraper(headless: bool = True) -> FilteredZipRecruiterScraper:
    """Create a scraper that only finds remote jobs."""
    return FilteredZipRecruiterScraper(
        job_filter=FilterPresets.remote_only(),
        headless=headless
    )

def create_senior_level_scraper(headless: bool = True) -> FilteredZipRecruiterScraper:
    """Create a scraper for senior-level positions."""
    return FilteredZipRecruiterScraper(
        job_filter=FilterPresets.senior_level(),
        headless=headless
    )

def create_custom_scraper(
    required_keywords: List[str],
    exclude_keywords: List[str] = None,
    min_salary: Optional[int] = None,
    min_quality_score: float = 0.5,
    headless: bool = True
) -> FilteredZipRecruiterScraper:
    """Create a scraper with custom filtering parameters."""
    
    custom_filter = JobFilter(
        required_keywords=required_keywords,
        exclude_keywords=exclude_keywords or [],
        min_salary=min_salary,
        min_quality_score=min_quality_score
    )
    
    return FilteredZipRecruiterScraper(
        job_filter=custom_filter,
        headless=headless
    )


async def demo_filtered_scraping():
    """Demonstrate filtered scraping with different presets."""
    print("🎯 Filtered Scraping Demo")
    print("=" * 40)
    
    # Software engineer scraper
    print("\n1. Software Engineer Filter:")
    se_scraper = create_software_engineer_scraper()
    se_result = await se_scraper.search_houston_jobs("python developer", max_pages=1)
    print(f"   Found {len(se_result.jobs)} software engineering jobs")
    
    # Data scientist scraper  
    print("\n2. Data Scientist Filter:")
    ds_scraper = create_data_scientist_scraper()
    ds_result = await ds_scraper.search_houston_jobs("machine learning", max_pages=1)
    print(f"   Found {len(ds_result.jobs)} data science jobs")
    
    # Custom scraper
    print("\n3. Custom Filter (Python + Remote):")
    custom_scraper = create_custom_scraper(
        required_keywords=["python", "remote"],
        exclude_keywords=["sales", "marketing"],
        min_salary=80000,
        min_quality_score=0.7
    )
    custom_result = await custom_scraper.search_houston_jobs("developer", max_pages=1)
    print(f"   Found {len(custom_result.jobs)} custom filtered jobs")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_filtered_scraping())
