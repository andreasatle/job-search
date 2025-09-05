"""Web scrapers for job sites."""

from .playwright_scraper import PlaywrightJobScraper
from .ziprecruiter_scraper import ZipRecruiterScraper

__all__ = ['PlaywrightJobScraper', 'ZipRecruiterScraper']
