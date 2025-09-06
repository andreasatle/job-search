"""
Job scrapers package for different job sites.
"""

from .base_scraper import JobScraper
from .remoteok_scraper import RemoteOKScraper

__all__ = ['JobScraper', 'RemoteOKScraper']
