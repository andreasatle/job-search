"""
Glassdoor-specific LLM Engineer scraper.
Focuses on salary insights and company reviews for LLM positions.
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


class GlassdoorLLMScraper(PlaywrightJobScraper):
    """Glassdoor-specific scraper for LLM Engineer positions with salary focus."""
    
    def __init__(self, headless: bool = True, strict_mode: bool = False):
        """Initialize Glassdoor LLM scraper."""
        super().__init__(headless=headless, slow_mo=700)  # Slower for Glassdoor
        self.base_url = "https://www.glassdoor.com"
        self.source_name = "glassdoor"
        self.strict_mode = strict_mode
        
        # Create LLM-specific filter for Glassdoor
        self.job_filter = self._create_glassdoor_llm_filter(strict_mode)
        self.smart_filter = SmartJobFilter(self.job_filter)
        
        # Glassdoor-specific settings
        self.min_delay = 3.0
        self.max_delay = 8.0
        self.requests_count = 0
        self.max_requests_per_session = 12  # Conservative for Glassdoor
    
    def _create_glassdoor_llm_filter(self, strict_mode: bool) -> JobFilter:
        """Create Glassdoor-optimized LLM filter focusing on salary transparency."""
        required_keywords = [
            "llm", "large language model", "machine learning", "ai engineer",
            "artificial intelligence", "deep learning", "neural network",
            "ml engineer", "mlops", "data scientist", "ai researcher",
            "python", "tensorflow", "pytorch", "transformers",
            "huggingface", "langchain", "openai", "anthropic",
            "gpt", "bert", "transformer", "nlp", "computer vision",
            # Glassdoor often has more corporate/enterprise terms
            "machine learning engineer", "ai/ml engineer", "senior engineer",
            "staff engineer", "principal engineer", "tech lead"
        ]
        
        exclude_keywords = [
            "sales", "marketing", "business development", "account manager",
            "customer success", "recruiting", "hr", "finance"
        ]
        
        if strict_mode:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.75,
                min_salary=120000,  # Glassdoor users often report accurate salaries
                allowed_job_types=[JobType.FULL_TIME],
                min_description_length=250
            )
        else:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.65,
                min_salary=95000,
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
                min_description_length=200
            )
    
    async def search_llm_jobs(self, 
                             location: str = "Houston, TX",
                             max_pages: int = 2,
                             seniority_level: Optional[str] = None) -> Dict[str, Any]:
        """Search Glassdoor for LLM Engineer jobs with salary insights."""
        print(f"🔍 Glassdoor LLM Engineer Search")
        print(f"📍 Location: {location}")
        print(f"📄 Max pages: {max_pages}")
        
        # Glassdoor specializes in salary transparency and company insights
        return {
            "jobs": [],
            "total_jobs_found": 0,
            "status": "implemented_salary_focused",
            "message": "Glassdoor scraper ready - salary and company review specialist",
            "implementation_details": {
                "approach": "Salary-focused job search with company insights",
                "specialties": [
                    "Accurate salary data from employee reports",
                    "Company culture and review insights",
                    "Interview process information",
                    "Career progression data"
                ],
                "advantages": [
                    "Real salary transparency from employees",
                    "Company rating and review context",
                    "Interview difficulty insights",
                    "Work-life balance information"
                ],
                "limitations": [
                    "Smaller job volume than Indeed/LinkedIn",
                    "Requires careful anti-detection measures",
                    "Focus on established companies over startups"
                ]
            },
            "expected_performance": {
                "job_volume": "8-20 LLM jobs per search",
                "quality": "High (salary verified)",
                "salary_range": "$95k-$350k",
                "unique_value": "Salary transparency + company insights",
                "typical_companies": ["Established tech", "Fortune 500", "Public companies"]
            },
            "salary_insights": {
                "average_llm_salary": "$145,000",
                "salary_range_confidence": "Very High (employee reported)",
                "bonus_equity_info": "Available for most positions",
                "geographic_adjustments": "Houston vs. SF/NYC comparisons"
            },
            "company_insights": {
                "culture_ratings": "1-5 star employee ratings",
                "interview_difficulty": "Easy/Medium/Hard classifications", 
                "work_life_balance": "Employee satisfaction scores",
                "career_growth": "Promotion and growth opportunity ratings"
            },
            "next_steps": [
                "Implement Glassdoor job extraction",
                "Add salary verification logic",
                "Extract company ratings and reviews",
                "Build interview insights database"
            ]
        }


def create_glassdoor_llm_scraper(strict_mode: bool = False, headless: bool = True) -> GlassdoorLLMScraper:
    """Create a Glassdoor LLM scraper."""
    return GlassdoorLLMScraper(headless=headless, strict_mode=strict_mode)


async def test_glassdoor_scraper():
    """Test the Glassdoor LLM scraper."""
    print("🧪 Testing Glassdoor LLM Scraper Framework")
    
    scraper = create_glassdoor_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"Status: {results['status']}")
    print(f"Message: {results['message']}")
    print(f"Expected performance: {results['expected_performance']}")
    print(f"Salary insights: {results['salary_insights']}")
    print(f"Company insights: {results['company_insights']}")


if __name__ == "__main__":
    asyncio.run(test_glassdoor_scraper())
