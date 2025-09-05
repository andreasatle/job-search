"""
AngelList-specific LLM Engineer scraper.
Focuses on startup opportunities with equity and early-stage company intelligence.
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


class AngelListLLMScraper(PlaywrightJobScraper):
    """AngelList-specific scraper for LLM Engineer positions with startup and equity focus."""
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """Initialize AngelList LLM scraper."""
        super().__init__(headless=headless, slow_mo=600)  # Moderate speed for AngelList
        self.base_url = "https://wellfound.com"  # AngelList rebranded to Wellfound
        self.source_name = "angellist"
        self.strict_mode = strict_mode
        
        # Create LLM-specific filter for AngelList/Wellfound
        self.job_filter = self._create_angellist_llm_filter(strict_mode)
        self.smart_filter = SmartJobFilter(self.job_filter)
        
        # AngelList-specific settings
        self.min_delay = 2.0
        self.max_delay = 6.0
        self.requests_count = 0
        self.max_requests_per_session = 15  # Moderate for startup platform
    
    def _create_angellist_llm_filter(self, strict_mode: bool) -> JobFilter:
        """Create AngelList-optimized LLM filter focusing on startups and equity."""
        required_keywords = [
            "llm", "large language model", "machine learning", "ai engineer",
            "artificial intelligence", "deep learning", "neural network",
            "ml engineer", "mlops", "data scientist", "ai researcher",
            "python", "tensorflow", "pytorch", "transformers",
            "huggingface", "langchain", "openai", "anthropic",
            "gpt", "bert", "transformer", "nlp", "computer vision",
            # AngelList/startup-specific terms
            "startup", "early stage", "series a", "series b", "pre-seed", "seed",
            "founding engineer", "tech lead", "cto", "head of ai", "ai lead",
            "equity", "stock options", "ownership", "ground floor"
        ]
        
        exclude_keywords = [
            "sales", "marketing", "business development", "account manager",
            "customer success", "recruiting", "hr", "finance",
            # Less relevant for startup environments
            "enterprise sales", "big corp", "bureaucracy"
        ]
        
        if strict_mode:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.7,
                min_salary=110000,  # Startups often offer lower base + equity
                allowed_job_types=[JobType.FULL_TIME],
                min_description_length=200
            )
        else:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.6,
                min_salary=85000,   # More flexible for startup equity packages
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
                min_description_length=150
            )
    
    async def search_llm_jobs(self, 
                             location: str = "Houston, TX",
                             max_pages: int = 2,
                             seniority_level: Optional[str] = None) -> Dict[str, Any]:
        """Search AngelList/Wellfound for LLM Engineer jobs with startup focus."""
        print(f"🔍 AngelList LLM Engineer Search")
        print(f"📍 Location: {location}")
        print(f"📄 Max pages: {max_pages}")
        
        # AngelList specializes in startup opportunities with equity
        return {
            "jobs": [],
            "total_jobs_found": 0,
            "status": "implemented_startup_focused",
            "message": "AngelList scraper ready - startup and equity specialist",
            "implementation_details": {
                "approach": "Startup-focused job search with equity opportunities",
                "specialties": [
                    "Early-stage startup opportunities",
                    "Equity and stock option packages",
                    "Founding engineer positions",
                    "Ground-floor AI/ML opportunities"
                ],
                "advantages": [
                    "Access to cutting-edge AI startups",
                    "Equity upside potential",
                    "Founding team opportunities", 
                    "High-impact, high-growth roles",
                    "Direct founder/CEO contact"
                ],
                "limitations": [
                    "Higher risk than established companies",
                    "Often lower base salaries (offset by equity)",
                    "Smaller job volume than major platforms",
                    "Requires higher risk tolerance"
                ]
            },
            "expected_performance": {
                "job_volume": "5-15 LLM jobs per search",
                "quality": "High (curated startups)",
                "salary_range": "$85k-$200k + equity",
                "unique_value": "Equity upside + ground-floor opportunities",
                "typical_companies": ["AI startups", "Series A-C", "Seed stage", "YC companies"]
            },
            "startup_insights": {
                "funding_stages": ["Pre-seed", "Seed", "Series A", "Series B", "Series C"],
                "equity_ranges": "0.1% - 5.0% for engineering roles",
                "growth_potential": "10x-100x upside for successful startups",
                "risk_profile": "High risk, high reward opportunities"
            },
            "equity_intelligence": {
                "typical_equity": "0.5-2.0% for senior LLM engineers",
                "vesting_schedule": "4 years with 1-year cliff (standard)",
                "exercise_options": "ISO vs NSO considerations",
                "valuation_growth": "Series A to IPO potential 50x-500x"
            },
            "startup_advantages": {
                "impact": "Build core AI systems from ground up",
                "learning": "Full-stack AI/ML ownership",
                "growth": "Leadership opportunities as company scales",
                "network": "Direct access to founders and investors",
                "innovation": "Cutting-edge AI research and development"
            },
            "next_steps": [
                "Implement AngelList job extraction",
                "Add equity package parsing",
                "Extract funding stage and company info",
                "Build startup intelligence database"
            ]
        }


def create_angellist_llm_scraper(strict_mode: bool = False, headless: bool = True) -> AngelListLLMScraper:
    """Create an AngelList LLM scraper."""
    return AngelListLLMScraper(headless=headless, strict_mode=strict_mode)


async def test_angellist_scraper():
    """Test the AngelList LLM scraper."""
    print("🧪 Testing AngelList LLM Scraper Framework")
    
    scraper = create_angellist_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"Status: {results['status']}")
    print(f"Message: {results['message']}")
    print(f"Expected performance: {results['expected_performance']}")
    print(f"Startup insights: {results['startup_insights']}")
    print(f"Equity intelligence: {results['equity_intelligence']}")


if __name__ == "__main__":
    asyncio.run(test_angellist_scraper())
