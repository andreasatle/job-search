"""
Base job scraper class that all specific scrapers inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..job import Job


class JobScraper(ABC):
    """Base class for all job scrapers."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = ""  # Set in subclasses
        self.site_name = ""  # Set in subclasses
    
    @abstractmethod
    async def search_jobs(self, query: str, location: str = "Houston, TX", max_jobs: int = 10) -> List[Job]:
        """Search for jobs and return a list with full descriptions. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _build_search_url(self, query: str, location: str) -> str:
        """Build the search URL for the specific site."""
        pass
    
    @abstractmethod
    async def _extract_job(self, element) -> Optional[Job]:
        """Extract job data from a page element."""
        pass
