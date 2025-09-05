"""
Smart job filtering system to reduce irrelevant jobs during scraping.
"""

import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from ..models.job_models import JobListing, JobType, RemoteType


@dataclass
class JobFilter:
    """Configuration for filtering jobs during scraping."""
    
    # Keywords to REQUIRE (at least one must be present)
    required_keywords: List[str] = None
    
    # Keywords to EXCLUDE (job rejected if any present)
    exclude_keywords: List[str] = None
    
    # Minimum quality score (0-1)
    min_quality_score: float = 0.5
    
    # Minimum salary (if specified)
    min_salary: Optional[int] = None
    
    # Maximum salary (if specified) 
    max_salary: Optional[int] = None
    
    # Required job types
    allowed_job_types: List[JobType] = None
    
    # Required remote types
    allowed_remote_types: List[RemoteType] = None
    
    # Minimum description length
    min_description_length: int = 100
    
    # Companies to exclude
    exclude_companies: List[str] = None
    
    # Experience levels to exclude
    exclude_experience_levels: List[str] = None


class SmartJobFilter:
    """Intelligent job filtering to keep only relevant positions."""
    
    def __init__(self, filter_config: JobFilter):
        """Initialize with filter configuration."""
        self.config = filter_config
        
        # Convert keywords to lowercase for case-insensitive matching
        self.required_keywords = [kw.lower() for kw in (filter_config.required_keywords or [])]
        self.exclude_keywords = [kw.lower() for kw in (filter_config.exclude_keywords or [])]
        self.exclude_companies = [comp.lower() for comp in (filter_config.exclude_companies or [])]
        self.exclude_experience = [exp.lower() for exp in (filter_config.exclude_experience_levels or [])]
    
    def should_keep_job(self, job: JobListing) -> Tuple[bool, str]:
        """
        Determine if a job should be kept based on filters.
        
        Returns:
            (keep: bool, reason: str)
        """
        # Quality score filter
        if job.quality_score < self.config.min_quality_score:
            return False, f"Quality score {job.quality_score:.2f} below minimum {self.config.min_quality_score}"
        
        # Description length filter (disabled for testing)
        if len(job.description) < 1:  # Only reject completely empty descriptions
            return False, f"Description too short ({len(job.description)} chars)"
        
        # Salary filters
        if self.config.min_salary and job.salary_min and job.salary_min < self.config.min_salary:
            return False, f"Salary ${job.salary_min:,} below minimum ${self.config.min_salary:,}"
        
        if self.config.max_salary and job.salary_max and job.salary_max > self.config.max_salary:
            return False, f"Salary ${job.salary_max:,} above maximum ${self.config.max_salary:,}"
        
        # Job type filter
        if self.config.allowed_job_types and job.job_type not in self.config.allowed_job_types:
            return False, f"Job type {job.job_type} not in allowed types"
        
        # Remote type filter
        if self.config.allowed_remote_types and job.remote_type not in self.config.allowed_remote_types:
            return False, f"Remote type {job.remote_type} not in allowed types"
        
        # Company exclusion filter
        for excluded_company in self.exclude_companies:
            if excluded_company in job.company.lower():
                return False, f"Company '{job.company}' is excluded"
        
        # Experience level exclusion
        if job.experience_level:
            for excluded_exp in self.exclude_experience:
                if excluded_exp in job.experience_level.lower():
                    return False, f"Experience level '{job.experience_level}' is excluded"
        
        # Create searchable text (title + description + requirements + skills)
        searchable_text = " ".join([
            job.title,
            job.description,
            job.requirements or "",
            " ".join(job.skills)
        ]).lower()
        
        # Exclude keywords filter (any match = reject)
        for exclude_kw in self.exclude_keywords:
            if exclude_kw in searchable_text:
                return False, f"Contains excluded keyword: '{exclude_kw}'"
        
        # Required keywords filter (at least one must match)
        if self.required_keywords:
            has_required_keyword = any(req_kw in searchable_text for req_kw in self.required_keywords)
            if not has_required_keyword:
                return False, f"Missing required keywords: {self.required_keywords}"
        
        return True, "Passed all filters"
    
    def filter_jobs(self, jobs: List[JobListing], verbose: bool = True) -> List[JobListing]:
        """
        Filter a list of jobs and return only those that pass.
        
        Args:
            jobs: List of job listings to filter
            verbose: Print filtering statistics
            
        Returns:
            Filtered list of job listings
        """
        if not jobs:
            return []
        
        kept_jobs = []
        filter_stats = {}
        
        for job in jobs:
            should_keep, reason = self.should_keep_job(job)
            
            if should_keep:
                kept_jobs.append(job)
            else:
                # Track rejection reasons for stats
                filter_stats[reason] = filter_stats.get(reason, 0) + 1
        
        if verbose:
            print(f"\n🎯 Smart Filtering Results:")
            print(f"   📥 Input jobs: {len(jobs)}")
            print(f"   ✅ Kept jobs: {len(kept_jobs)} ({len(kept_jobs)/len(jobs)*100:.1f}%)")
            print(f"   ❌ Filtered out: {len(jobs) - len(kept_jobs)}")
            
            if filter_stats:
                print(f"\n📊 Rejection reasons:")
                for reason, count in sorted(filter_stats.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {reason}: {count}")
        
        return kept_jobs


# Pre-configured filters for common use cases
class FilterPresets:
    """Pre-configured job filters for common scenarios."""
    
    @staticmethod
    def software_engineer() -> JobFilter:
        """Filter for software engineering positions."""
        return JobFilter(
            required_keywords=["python", "javascript", "react", "node", "django", "flask", "api", "backend", "frontend", "full stack", "software", "developer", "engineer"],
            exclude_keywords=["sales", "marketing", "recruiter", "cold calling", "door to door", "commission only", "pyramid", "mlm"],
            min_quality_score=0.6,
            min_salary=70000,
            allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
            min_description_length=150,
            exclude_companies=["door to door", "cold calling", "commission"],
            exclude_experience_levels=["entry level", "intern"]
        )
    
    @staticmethod
    def data_scientist() -> JobFilter:
        """Filter for data science positions."""
        return JobFilter(
            required_keywords=["python", "sql", "machine learning", "data", "analytics", "tensorflow", "pytorch", "pandas", "numpy", "science", "ai", "ml"],
            exclude_keywords=["sales", "marketing", "cold calling", "telemarketing", "door to door"],
            min_quality_score=0.7,
            min_salary=80000,
            allowed_job_types=[JobType.FULL_TIME],
            min_description_length=200
        )
    
    @staticmethod
    def remote_only() -> JobFilter:
        """Filter for remote work only."""
        return JobFilter(
            allowed_remote_types=[RemoteType.REMOTE],
            min_quality_score=0.5,
            min_description_length=100
        )
    
    @staticmethod
    def senior_level() -> JobFilter:
        """Filter for senior-level positions."""
        return JobFilter(
            required_keywords=["senior", "lead", "principal", "architect", "manager", "director"],
            min_quality_score=0.7,
            min_salary=100000,
            allowed_job_types=[JobType.FULL_TIME],
            exclude_experience_levels=["entry", "junior", "intern"]
        )
    
    @staticmethod
    def startup_roles() -> JobFilter:
        """Filter for startup and tech company roles."""
        return JobFilter(
            required_keywords=["startup", "tech", "saas", "platform", "api", "cloud", "aws", "kubernetes"],
            exclude_keywords=["enterprise", "legacy", "mainframe", "cobol"],
            min_quality_score=0.6,
            allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID]
        )
    
    @staticmethod
    def high_paying() -> JobFilter:
        """Filter for high-paying positions."""
        return JobFilter(
            min_salary=120000,
            min_quality_score=0.8,
            allowed_job_types=[JobType.FULL_TIME],
            min_description_length=200
        )


# Example usage functions
def create_custom_filter() -> JobFilter:
    """Example of creating a custom filter."""
    return JobFilter(
        required_keywords=["python", "machine learning", "remote"],
        exclude_keywords=["sales", "cold calling", "door to door", "commission only"],
        min_quality_score=0.7,
        min_salary=90000,
        max_salary=200000,
        allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
        allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
        min_description_length=150,
        exclude_companies=["spam company", "sketchy inc"],
        exclude_experience_levels=["intern", "entry level"]
    )


if __name__ == "__main__":
    # Example usage
    filter_config = FilterPresets.software_engineer()
    job_filter = SmartJobFilter(filter_config)
    
    print("🎯 Smart Job Filter Example")
    print("==========================")
    print(f"Required keywords: {filter_config.required_keywords[:5]}...")
    print(f"Exclude keywords: {filter_config.exclude_keywords}")
    print(f"Min quality score: {filter_config.min_quality_score}")
    print(f"Min salary: ${filter_config.min_salary:,}" if filter_config.min_salary else "No salary filter")
