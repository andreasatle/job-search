"""
Simple Job data model - just the essentials.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Job:
    """Simple job listing with essential fields only."""
    title: str
    company: str
    location: str
    description: str
    url: str
    
    # Optional fields
    salary: Optional[str] = None
    remote: Optional[bool] = None
    posted_date: Optional[datetime] = None
    
    def __str__(self):
        return f"{self.title} at {self.company} ({self.location})"
    
    def to_dict(self):
        """Convert to dictionary for JSON storage."""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'salary': self.salary,
            'remote': self.remote,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None
        }
