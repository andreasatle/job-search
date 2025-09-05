"""
Specialized scraper for LLM Engineer and AI/ML Engineering positions.
Optimized for finding cutting-edge AI roles with smart filtering.
"""

from typing import List, Optional
from .filtered_ziprecruiter_scraper import FilteredZipRecruiterScraper
from .smart_job_filter import JobFilter
from ..models.job_models import JobType, RemoteType


class LLMEngineerScraper(FilteredZipRecruiterScraper):
    """Specialized scraper for LLM Engineer and AI/ML positions."""
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """
        Initialize LLM Engineer scraper.
        
        Args:
            headless: Run browser in headless mode
            strict_mode: Use stricter filtering for senior/specialized roles
        """
        # Create LLM-specific filter
        llm_filter = self._create_llm_filter(strict_mode)
        super().__init__(job_filter=llm_filter, headless=headless)
        self.strict_mode = strict_mode
    
    def _create_llm_filter(self, strict_mode: bool) -> JobFilter:
        """Create optimized filter for LLM Engineer positions."""
        
        # Core LLM/AI keywords - job must have at least one
        required_keywords = [
            # LLM/AI specific
            "llm", "large language model", "gpt", "bert", "transformer",
            "machine learning", "artificial intelligence", "ai engineer",
            "ml engineer", "mlops", "ai/ml",
            
            # Deep learning frameworks
            "pytorch", "tensorflow", "keras", "huggingface", "transformers",
            "langchain", "llamaindex", "openai", "anthropic",
            
            # AI/ML technologies
            "python", "machine learning", "deep learning", "neural network",
            "nlp", "natural language processing", "computer vision",
            "reinforcement learning", "generative ai", "conversational ai",
            
            # Cloud AI platforms
            "aws sagemaker", "azure ml", "google cloud ai", "vertex ai",
            "databricks", "mlflow", "kubeflow",
            
            # Vector databases and embeddings
            "vector database", "embeddings", "chromadb", "pinecone", "weaviate",
            "faiss", "semantic search", "retrieval", "rag"
        ]
        
        # Keywords that indicate spam/irrelevant jobs
        exclude_keywords = [
            # Non-technical roles
            "sales", "marketing", "recruiter", "cold calling", "door to door",
            "commission only", "mlm", "pyramid", "telemarketing",
            
            # Low-level positions
            "intern", "unpaid", "volunteer", "entry level",
            
            # Unrelated fields
            "real estate", "insurance", "retail", "restaurant", "driver",
            "warehouse", "construction", "manual labor",
            
            # Spam indicators
            "make money fast", "work from home easy", "no experience needed"
        ]
        
        # Companies known for AI/ML work (prefer these)
        preferred_companies = [
            "openai", "anthropic", "google", "microsoft", "amazon", "meta",
            "nvidia", "databricks", "huggingface", "cohere", "stability ai",
            "scale ai", "deepmind", "tesla", "uber", "airbnb", "spotify"
        ]
        
        # Set different standards based on strict mode
        if strict_mode:
            # Stricter filtering for senior/specialized roles
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.8,          # Very high quality only
                min_salary=120000,              # Senior-level salaries
                max_salary=400000,              # Cap at reasonable maximum
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT, JobType.UNKNOWN],
                allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
                min_description_length=10,      # Allow short descriptions
                exclude_experience_levels=["entry level", "intern", "junior"]
            )
        else:
            # More inclusive filtering for all LLM roles
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.65,         # Good quality
                min_salary=80000,               # Include mid-level roles
                max_salary=500000,              # Higher cap for staff/principal
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT, JobType.UNKNOWN],
                allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID, RemoteType.ONSITE],
                min_description_length=10       # Allow short descriptions
            )
    
    async def search_llm_jobs(self, 
                             location: str = "Houston, TX",
                             max_pages: int = 3,
                             seniority_level: Optional[str] = None) -> dict:
        """
        Search for LLM Engineer jobs with optimized queries.
        
        Args:
            location: Job location (default: Houston, TX)
            max_pages: Maximum pages to scrape
            seniority_level: "junior", "mid", "senior", or "staff"
            
        Returns:
            Dictionary with results and metadata
        """
        # Build optimized search queries for LLM roles
        base_queries = [
            "LLM Engineer",
            "Large Language Model Engineer", 
            "AI Engineer Machine Learning",
            "ML Engineer NLP",
            "Machine Learning Engineer AI",
            "AI/ML Engineer",
            "MLOps Engineer",
            "Machine Learning Scientist",
            "AI Research Engineer",
            "Generative AI Engineer"
        ]
        
        # Add seniority if specified
        if seniority_level:
            if seniority_level.lower() in ["senior", "sr"]:
                base_queries = [f"Senior {q}" for q in base_queries[:5]]
            elif seniority_level.lower() in ["staff", "principal", "lead"]:
                base_queries = [f"{seniority_level.title()} {q}" for q in base_queries[:3]]
            elif seniority_level.lower() in ["junior", "jr", "mid", "entry"]:
                base_queries = base_queries[:3]  # Use simpler queries
        
        print(f"🤖 Starting LLM Engineer job search in {location}")
        print(f"🎯 Strict mode: {'ON' if self.strict_mode else 'OFF'}")
        print(f"🔍 Search queries: {base_queries[:3]}...")
        
        all_jobs = []
        total_scraped = 0
        total_filtered = 0
        search_results = {}
        
        # Try multiple search queries to get comprehensive results
        for i, query in enumerate(base_queries[:3], 1):  # Limit to top 3 queries
            print(f"\n📡 Search {i}/3: '{query}'")
            
            try:
                # Override location in the search
                result = await super().search_houston_jobs(
                    query=query, 
                    max_pages=max_pages,
                    apply_smart_filter=True
                )
                
                if result.jobs:
                    # Avoid duplicates by checking URLs
                    existing_urls = {job.url for job in all_jobs}
                    new_jobs = [job for job in result.jobs if job.url not in existing_urls]
                    
                    all_jobs.extend(new_jobs)
                    total_scraped += result.metadata.get("jobs_before_filtering", len(result.jobs))
                    total_filtered += len(result.jobs)
                    
                    print(f"   ✅ Found {len(new_jobs)} new LLM jobs ({len(result.jobs)} total)")
                else:
                    print(f"   ⚠️  No jobs found for '{query}'")
                    
            except Exception as e:
                print(f"   ❌ Error searching '{query}': {e}")
                continue
        
        # Sort by quality score and salary
        all_jobs.sort(key=lambda x: (x.quality_score, x.salary_min or 0), reverse=True)
        
        # Create comprehensive results
        search_results = {
            "jobs": all_jobs,
            "total_jobs_found": len(all_jobs),
            "total_jobs_scraped": total_scraped,
            "total_after_filtering": total_filtered,
            "filtering_efficiency": f"{len(all_jobs)/total_scraped*100:.1f}%" if total_scraped > 0 else "0%",
            "strict_mode": self.strict_mode,
            "search_queries_used": base_queries[:3],
            "location": location,
            "avg_quality_score": sum(job.quality_score for job in all_jobs) / len(all_jobs) if all_jobs else 0,
            "salary_range": {
                "min": min(job.salary_min for job in all_jobs if job.salary_min) if any(job.salary_min for job in all_jobs) else None,
                "max": max(job.salary_max for job in all_jobs if job.salary_max) if any(job.salary_max for job in all_jobs) else None,
                "avg": sum(job.salary_min or 0 for job in all_jobs) / len(all_jobs) if all_jobs else 0
            }
        }
        
        # Print summary
        self._print_search_summary(search_results)
        
        return search_results
    
    def _print_search_summary(self, results: dict):
        """Print a summary of the LLM job search results."""
        jobs = results["jobs"]
        
        print(f"\n🤖 LLM Engineer Search Summary")
        print(f"=" * 40)
        print(f"📊 Total LLM jobs found: {len(jobs)}")
        print(f"🎯 Filtering efficiency: {results['filtering_efficiency']}")
        print(f"⭐ Average quality score: {results['avg_quality_score']:.2f}")
        
        if results['salary_range']['min']:
            print(f"💰 Salary range: ${results['salary_range']['min']:,} - ${results['salary_range']['max']:,}")
            print(f"💵 Average salary: ${results['salary_range']['avg']:,.0f}")
        
        if jobs:
            print(f"\n🏆 Top 3 LLM Jobs:")
            for i, job in enumerate(jobs[:3], 1):
                salary_str = f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary not specified"
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      💰 {salary_str} | ⭐ {job.quality_score:.2f} | 🏠 {job.remote_type.value}")
        
        # Show technology breakdown
        tech_keywords = ["llm", "gpt", "transformer", "pytorch", "tensorflow", "huggingface", "langchain", "openai"]
        tech_counts = {}
        
        for job in jobs:
            job_text = f"{job.title} {job.description} {' '.join(job.skills)}".lower()
            for tech in tech_keywords:
                if tech in job_text:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        if tech_counts:
            print(f"\n🔧 Technology mentions:")
            for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {tech.upper()}: {count} jobs")


# Convenience functions for different LLM Engineer levels
def create_llm_engineer_scraper(strict_mode: bool = False, headless: bool = True) -> LLMEngineerScraper:
    """Create a general LLM Engineer scraper."""
    return LLMEngineerScraper(headless=headless, strict_mode=strict_mode)

def create_senior_llm_scraper(headless: bool = True) -> LLMEngineerScraper:
    """Create a scraper for senior-level LLM Engineer positions."""
    return LLMEngineerScraper(headless=headless, strict_mode=True)

def create_junior_llm_scraper(headless: bool = True) -> LLMEngineerScraper:
    """Create a scraper for junior/mid-level LLM Engineer positions."""
    return LLMEngineerScraper(headless=headless, strict_mode=False)


async def demo_llm_scraping():
    """Demonstrate LLM Engineer scraping."""
    print("🤖 LLM Engineer Scraper Demo")
    print("=" * 35)
    
    # Test different configurations
    configs = [
        ("General LLM Engineer", create_llm_engineer_scraper()),
        ("Senior LLM Engineer", create_senior_llm_scraper()),
        ("Junior/Mid LLM Engineer", create_junior_llm_scraper()),
    ]
    
    for config_name, scraper in configs:
        print(f"\n🔍 Testing {config_name} Scraper:")
        try:
            results = await scraper.search_llm_jobs(max_pages=1)
            print(f"   ✅ Found {results['total_jobs_found']} {config_name.lower()} positions")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_llm_scraping())
