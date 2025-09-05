"""Enhanced job data models for Houston job search."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    """Types of employment."""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class RemoteType(str, Enum):
    """Remote work options."""
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


@dataclass
class JobListing:
    """Comprehensive job listing data structure."""
    # Basic Information
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    
    # Additional Details
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_text: Optional[str] = None
    job_type: JobType = JobType.UNKNOWN
    remote_type: RemoteType = RemoteType.UNKNOWN
    
    # Dates
    posted_date: Optional[datetime] = None
    scraped_date: datetime = field(default_factory=datetime.now)
    
    # Requirements and Skills
    requirements: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience_level: Optional[str] = None
    education: Optional[str] = None
    
    # Company Information
    company_size: Optional[str] = None
    industry: Optional[str] = None
    
    # Additional Metadata
    job_id: Optional[str] = None  # Original job ID from source
    external_apply: bool = False  # Whether application is external
    
    # Quality Indicators
    has_salary: bool = field(init=False)
    has_description: bool = field(init=False)
    quality_score: float = field(init=False)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.has_salary = bool(self.salary_min or self.salary_max or self.salary_text)
        self.has_description = bool(self.description and len(self.description.strip()) > 50)
        self.quality_score = self._calculate_quality_score()
    
    def _calculate_quality_score(self) -> float:
        """Calculate a quality score for the job listing (0-1)."""
        score = 0.0
        
        # Required fields (base score)
        if self.title: score += 0.2
        if self.company: score += 0.2
        if self.location: score += 0.1
        if self.description: score += 0.2
        
        # Additional valuable information
        if self.has_salary: score += 0.1
        if self.skills: score += 0.1
        if self.posted_date: score += 0.05
        if self.job_type != JobType.UNKNOWN: score += 0.05
        
        return min(1.0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_text': self.salary_text,
            'job_type': self.job_type.value,
            'remote_type': self.remote_type.value,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'scraped_date': self.scraped_date.isoformat(),
            'requirements': self.requirements,
            'skills': self.skills,
            'experience_level': self.experience_level,
            'education': self.education,
            'company_size': self.company_size,
            'industry': self.industry,
            'job_id': self.job_id,
            'external_apply': self.external_apply,
            'quality_score': self.quality_score
        }


@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    source: str
    jobs: List[JobListing]
    success: bool
    total_found: int
    pages_scraped: int
    errors: List[str] = field(default_factory=list)
    scrape_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of scraping."""
        if self.total_found == 0:
            return 0.0
        return len(self.jobs) / self.total_found
    
    @property
    def average_quality(self) -> float:
        """Calculate average quality score of scraped jobs."""
        if not self.jobs:
            return 0.0
        return sum(job.quality_score for job in self.jobs) / len(self.jobs)
