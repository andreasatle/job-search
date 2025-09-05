"""
Multi-site LLM Engineer scraper that searches across multiple job platforms.
Finds LLM/AI engineering jobs from ZipRecruiter, Indeed, LinkedIn, and more.
"""

import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .llm_engineer_scraper import LLMEngineerScraper
from .indeed_llm_scraper import IndeedLLMScraper
from .linkedin_llm_scraper import LinkedInLLMScraper
from .smart_job_filter import JobFilter
from ..models.job_models import JobListing, JobType, RemoteType, ScrapingResult


@dataclass
class MultiSiteResult:
    """Results from searching multiple job sites."""
    all_jobs: List[JobListing]
    site_results: Dict[str, Dict[str, Any]]
    total_jobs_found: int
    total_sites_searched: int
    successful_sites: List[str]
    failed_sites: List[str]
    search_duration: float
    best_site: str
    technology_breakdown: Dict[str, int]
    salary_analysis: Dict[str, Any]


class MultiSiteLLMScraper:
    """
    Scrapes LLM Engineer jobs across multiple job sites.
    
    Currently supports:
    - ZipRecruiter (implemented)
    - Indeed (placeholder for future implementation)
    - LinkedIn (placeholder for future implementation)
    - Glassdoor (placeholder for future implementation)
    - AngelList (placeholder for future implementation)
    """
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """
        Initialize multi-site LLM scraper.
        
        Args:
            headless: Run browsers in headless mode
            strict_mode: Use strict filtering across all sites
        """
        self.headless = headless
        self.strict_mode = strict_mode
        
        # Initialize available scrapers
        from .indeed_llm_scraper import IndeedLLMScraper
        
        self.scrapers = {
            "ziprecruiter": LLMEngineerScraper(headless=headless, strict_mode=strict_mode),
            "indeed": IndeedLLMScraper(headless=headless, strict_mode=strict_mode),
            "linkedin": LinkedInLLMScraper(headless=headless, strict_mode=strict_mode),
            # Future implementations:
            # "glassdoor": GlassdoorLLMScraper(headless=headless, strict_mode=strict_mode),
            # "angellist": AngelListLLMScraper(headless=headless, strict_mode=strict_mode),
        }
        
        # Site-specific configurations
        self.site_configs = {
            "ziprecruiter": {
                "enabled": True,
                "max_pages": 3,
                "priority": 1,
                "expected_results": "medium",
                "specialties": ["general", "remote", "contract"]
            },
            "indeed": {
                "enabled": True,  # Now implemented!
                "max_pages": 3,  # Conservative for testing
                "priority": 2,
                "expected_results": "high",
                "specialties": ["volume", "local", "enterprise"]
            },
            "linkedin": {
                "enabled": True,   # Now implemented!
                "max_pages": 2,    # Conservative for LinkedIn
                "priority": 3,
                "expected_results": "high_quality",
                "specialties": ["senior", "remote", "tech_companies"]
            },
            "glassdoor": {
                "enabled": False,  # Not implemented yet
                "max_pages": 2,
                "priority": 4,
                "expected_results": "medium",
                "specialties": ["salary_info", "company_reviews"]
            },
            "angellist": {
                "enabled": False,  # Not implemented yet
                "max_pages": 2,
                "priority": 5,
                "expected_results": "startup_focused",
                "specialties": ["startups", "equity", "early_stage"]
            }
        }
    
    async def search_all_sites(self, 
                              location: str = "Houston, TX",
                              max_pages_per_site: Optional[int] = None,
                              sites_to_search: Optional[List[str]] = None,
                              seniority_level: Optional[str] = None) -> MultiSiteResult:
        """
        Search for LLM Engineer jobs across multiple sites.
        
        Args:
            location: Job location
            max_pages_per_site: Override default pages per site
            sites_to_search: Specific sites to search (default: all enabled)
            seniority_level: "junior", "mid", "senior", "staff"
            
        Returns:
            MultiSiteResult with aggregated results
        """
        start_time = datetime.now()
        
        # Determine which sites to search
        if sites_to_search is None:
            sites_to_search = [site for site, config in self.site_configs.items() 
                             if config["enabled"]]
        
        print(f"🌐 Multi-Site LLM Engineer Search")
        print(f"=" * 40)
        print(f"🎯 Location: {location}")
        print(f"🔍 Searching {len(sites_to_search)} sites: {', '.join(sites_to_search)}")
        print(f"🎚️ Strict mode: {'ON' if self.strict_mode else 'OFF'}")
        if seniority_level:
            print(f"⭐ Seniority: {seniority_level}")
        
        all_jobs = []
        site_results = {}
        successful_sites = []
        failed_sites = []
        
        # Search each site
        for site_name in sites_to_search:
            if site_name not in self.scrapers:
                print(f"\n❌ {site_name.title()}: Not implemented yet")
                failed_sites.append(site_name)
                continue
            
            print(f"\n🔍 Searching {site_name.title()}...")
            
            try:
                # Get site-specific configuration
                config = self.site_configs[site_name]
                pages = max_pages_per_site or config["max_pages"]
                
                # Perform the search
                scraper = self.scrapers[site_name]
                
                if site_name == "ziprecruiter":
                    # Use ZipRecruiter-specific search method
                    result = await scraper.search_llm_jobs(
                        location=location,
                        max_pages=pages,
                        seniority_level=seniority_level
                    )
                    
                    jobs = result["jobs"]
                    site_metadata = {
                        "jobs_found": len(jobs),
                        "search_queries": result.get("search_queries_used", []),
                        "filtering_efficiency": result.get("filtering_efficiency", "N/A"),
                        "avg_quality_score": result.get("avg_quality_score", 0),
                        "salary_range": result.get("salary_range", {}),
                        "pages_scraped": pages,
                        "status": "success"
                    }
                
                elif site_name == "indeed":
                    # Use Indeed-specific search method
                    result = await scraper.search_llm_jobs(
                        location=location,
                        max_pages=pages,
                        seniority_level=seniority_level
                    )
                    
                    jobs = result.get("jobs", [])
                    site_metadata = {
                        "jobs_found": len(jobs),
                        "status": result.get("status", "success"),
                        "message": result.get("message", ""),
                        "expected_performance": result.get("expected_performance", {}),
                        "pages_scraped": pages
                    }
                
                else:
                    # Generic interface for future site implementations
                    # result = await scraper.search_llm_jobs(location, pages, seniority_level)
                    jobs = []
                    site_metadata = {"status": "not_implemented"}
                
                # Deduplicate against existing jobs
                existing_urls = {job.url for job in all_jobs}
                new_jobs = [job for job in jobs if job.url not in existing_urls]
                
                all_jobs.extend(new_jobs)
                site_results[site_name] = site_metadata
                successful_sites.append(site_name)
                
                print(f"   ✅ Found {len(new_jobs)} unique LLM jobs")
                
            except Exception as e:
                print(f"   ❌ Error searching {site_name}: {e}")
                failed_sites.append(site_name)
                site_results[site_name] = {"status": "failed", "error": str(e)}
        
        # Calculate search duration
        end_time = datetime.now()
        search_duration = (end_time - start_time).total_seconds()
        
        # Determine best performing site
        best_site = self._find_best_site(site_results)
        
        # Analyze technologies and salaries
        technology_breakdown = self._analyze_technologies(all_jobs)
        salary_analysis = self._analyze_salaries(all_jobs)
        
        # Sort jobs by quality and salary
        all_jobs.sort(key=lambda x: (x.quality_score, x.salary_min or 0), reverse=True)
        
        # Create comprehensive result
        result = MultiSiteResult(
            all_jobs=all_jobs,
            site_results=site_results,
            total_jobs_found=len(all_jobs),
            total_sites_searched=len(sites_to_search),
            successful_sites=successful_sites,
            failed_sites=failed_sites,
            search_duration=search_duration,
            best_site=best_site,
            technology_breakdown=technology_breakdown,
            salary_analysis=salary_analysis
        )
        
        # Print comprehensive summary
        self._print_multi_site_summary(result)
        
        return result
    
    def _find_best_site(self, site_results: Dict[str, Dict]) -> str:
        """Determine which site performed best."""
        best_site = ""
        best_score = 0
        
        for site, results in site_results.items():
            if results.get("status") == "success":
                # Score based on jobs found and quality
                jobs_found = results.get("jobs_found", 0)
                avg_quality = results.get("avg_quality_score", 0)
                score = jobs_found * avg_quality
                
                if score > best_score:
                    best_score = score
                    best_site = site
        
        return best_site or "none"
    
    def _analyze_technologies(self, jobs: List[JobListing]) -> Dict[str, int]:
        """Analyze technology mentions across all jobs."""
        tech_keywords = [
            "llm", "gpt", "transformer", "bert", "t5",
            "pytorch", "tensorflow", "keras", "jax",
            "huggingface", "langchain", "llamaindex",
            "openai", "anthropic", "cohere",
            "python", "scala", "java", "go",
            "aws", "azure", "gcp", "kubernetes",
            "mlflow", "wandb", "neptune",
            "vector", "embedding", "rag", "fine-tuning"
        ]
        
        tech_counts = {}
        
        for job in jobs:
            job_text = f"{job.title} {job.description} {' '.join(job.skills)}".lower()
            for tech in tech_keywords:
                if tech in job_text:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        # Sort by frequency
        return dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_salaries(self, jobs: List[JobListing]) -> Dict[str, Any]:
        """Analyze salary information across all jobs."""
        salaries = []
        
        for job in jobs:
            if job.salary_min:
                salaries.append(job.salary_min)
            if job.salary_max and job.salary_max != job.salary_min:
                salaries.append(job.salary_max)
        
        if not salaries:
            return {"message": "No salary data available"}
        
        return {
            "min": min(salaries),
            "max": max(salaries),
            "avg": sum(salaries) / len(salaries),
            "median": sorted(salaries)[len(salaries) // 2],
            "jobs_with_salary": len([j for j in jobs if j.salary_min or j.salary_max]),
            "total_jobs": len(jobs),
            "salary_coverage": len([j for j in jobs if j.salary_min or j.salary_max]) / len(jobs) * 100
        }
    
    def _print_multi_site_summary(self, result: MultiSiteResult):
        """Print comprehensive multi-site search summary."""
        print(f"\n🌐 Multi-Site LLM Search Results")
        print(f"=" * 45)
        print(f"⏱️  Search duration: {result.search_duration:.1f} seconds")
        print(f"🎯 Total LLM jobs found: {result.total_jobs_found}")
        print(f"✅ Successful sites: {len(result.successful_sites)}/{result.total_sites_searched}")
        print(f"🏆 Best performing site: {result.best_site.title()}")
        
        # Site breakdown
        print(f"\n📊 Site Performance:")
        for site, results in result.site_results.items():
            status = results.get("status", "unknown")
            if status == "success":
                jobs = results.get("jobs_found", 0)
                quality = results.get("avg_quality_score", 0)
                print(f"   ✅ {site.title()}: {jobs} jobs (avg quality: {quality:.2f})")
            elif status == "not_implemented":
                print(f"   ⏳ {site.title()}: Not implemented yet")
            else:
                print(f"   ❌ {site.title()}: Failed ({results.get('error', 'unknown error')})")
        
        # Salary analysis
        if "message" not in result.salary_analysis:
            salary = result.salary_analysis
            print(f"\n💰 Salary Analysis:")
            print(f"   Range: ${salary['min']:,} - ${salary['max']:,}")
            print(f"   Average: ${salary['avg']:,.0f}")
            print(f"   Coverage: {salary['salary_coverage']:.1f}% of jobs have salary info")
        
        # Top technologies
        if result.technology_breakdown:
            print(f"\n🔧 Top Technologies:")
            for tech, count in list(result.technology_breakdown.items())[:8]:
                percentage = count / result.total_jobs_found * 100
                print(f"   • {tech.upper()}: {count} jobs ({percentage:.1f}%)")
        
        # Top jobs
        if result.all_jobs:
            print(f"\n🏆 Top 3 LLM Jobs Across All Sites:")
            for i, job in enumerate(result.all_jobs[:3], 1):
                salary_str = f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary TBD"
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      💰 {salary_str} | ⭐ {job.quality_score:.2f} | 🌐 {job.source}")
                print(f"      🏠 {job.remote_type.value} | 📍 {job.location}")
    
    def get_site_status(self) -> Dict[str, Any]:
        """Get status of all supported job sites."""
        status = {}
        
        for site, config in self.site_configs.items():
            status[site] = {
                "implemented": site in self.scrapers,
                "enabled": config["enabled"],
                "priority": config["priority"],
                "expected_results": config["expected_results"],
                "specialties": config["specialties"]
            }
        
        return status
    
    def enable_site(self, site_name: str):
        """Enable a specific job site for searching."""
        if site_name in self.site_configs:
            self.site_configs[site_name]["enabled"] = True
            print(f"✅ Enabled {site_name} for searching")
        else:
            print(f"❌ Unknown site: {site_name}")
    
    def disable_site(self, site_name: str):
        """Disable a specific job site from searching."""
        if site_name in self.site_configs:
            self.site_configs[site_name]["enabled"] = False
            print(f"❌ Disabled {site_name} from searching")
        else:
            print(f"❌ Unknown site: {site_name}")


# Convenience functions
def create_multi_site_llm_scraper(strict_mode: bool = False, headless: bool = True) -> MultiSiteLLMScraper:
    """Create a multi-site LLM scraper."""
    return MultiSiteLLMScraper(headless=headless, strict_mode=strict_mode)

def create_enterprise_llm_scraper(headless: bool = True) -> MultiSiteLLMScraper:
    """Create a scraper optimized for enterprise LLM roles."""
    scraper = MultiSiteLLMScraper(headless=headless, strict_mode=True)
    # Future: configure for enterprise-focused sites
    return scraper


async def demo_multi_site_search():
    """Demonstrate multi-site LLM job searching."""
    print("🌐 Multi-Site LLM Scraper Demo")
    print("=" * 35)
    
    # Create multi-site scraper
    scraper = create_multi_site_llm_scraper()
    
    # Show site status
    print("📊 Site Status:")
    site_status = scraper.get_site_status()
    for site, status in site_status.items():
        impl = "✅" if status["implemented"] else "⏳"
        enabled = "ON" if status["enabled"] else "OFF"
        print(f"   {impl} {site.title()}: {enabled} - {status['expected_results']}")
    
    # Perform multi-site search
    print(f"\n🔍 Starting multi-site search...")
    try:
        results = await scraper.search_all_sites(
            location="Houston, TX",
            max_pages_per_site=1,  # Small test
            seniority_level="senior"
        )
        
        print(f"\n🎉 Multi-site search completed!")
        print(f"Found {results.total_jobs_found} total LLM jobs across {results.total_sites_searched} sites")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_multi_site_search())
