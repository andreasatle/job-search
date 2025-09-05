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
        parts = [f"{self.title} at {self.company}"]
        if self.location and self.location != "Remote":
            parts.append(f"({self.location})")
        elif self.remote:
            parts.append("(Remote)")
        return " ".join(parts)
    
    def display(self):
        """Display job in a clean format."""
        print(f"🔹 {self.title}")
        print(f"   🏢 {self.company}")
        if self.salary:
            print(f"   💰 {self.salary}")
        if self.remote:
            print(f"   🏠 Remote")
        elif self.location:
            print(f"   📍 {self.location}")
        if self.description and len(self.description.strip()) > 10:
            # Clean description for display
            clean_desc = self.description.strip()
            # if len(self.description) > 100:
                # clean_desc += "..."
            print(f"   📝 {clean_desc}")
        print()
    
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
