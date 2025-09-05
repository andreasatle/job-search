"""
Simple job storage - just save to JSON file.
"""

import json
import os
from typing import List
from datetime import datetime
from .job import Job


class SimpleJobStorage:
    """Dead simple job storage using JSON file."""
    
    def __init__(self, filename: str = "jobs.json"):
        self.filename = filename
    
    def save_jobs(self, jobs: List[Job]):
        """Save jobs to JSON file."""
        # Load existing jobs
        existing_jobs = self.load_jobs()
        existing_urls = {job.url for job in existing_jobs}
        
        # Add new jobs (avoid duplicates by URL)
        new_jobs = [job for job in jobs if job.url not in existing_urls]
        all_jobs = existing_jobs + new_jobs
        
        # Convert to dict format
        jobs_data = {
            'last_updated': datetime.now().isoformat(),
            'total_jobs': len(all_jobs),
            'jobs': [job.to_dict() for job in all_jobs]
        }
        
        # Save to file
        with open(self.filename, 'w') as f:
            json.dump(jobs_data, f, indent=2)
        
        print(f"💾 Saved {len(new_jobs)} new jobs to {self.filename} (total: {len(all_jobs)})")
        return len(new_jobs)
    
    def load_jobs(self) -> List[Job]:
        """Load jobs from JSON file."""
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            jobs = []
            for job_data in data.get('jobs', []):
                # Convert back to Job object
                posted_date = None
                if job_data.get('posted_date'):
                    try:
                        posted_date = datetime.fromisoformat(job_data['posted_date'])
                    except:
                        pass
                
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'],
                    url=job_data['url'],
                    salary=job_data.get('salary'),
                    remote=job_data.get('remote'),
                    posted_date=posted_date
                )
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"❌ Error loading jobs: {e}")
            return []
    
    def search_jobs(self, query: str) -> List[Job]:
        """Simple text search in saved jobs."""
        jobs = self.load_jobs()
        query_lower = query.lower()
        
        matching_jobs = []
        for job in jobs:
            # Search in title, company, and description
            searchable_text = f"{job.title} {job.company} {job.description}".lower()
            if query_lower in searchable_text:
                matching_jobs.append(job)
        
        return matching_jobs
    
    def get_stats(self):
        """Get simple statistics."""
        jobs = self.load_jobs()
        
        if not jobs:
            return {"total": 0}
        
        # Count by company
        companies = {}
        remote_count = 0
        with_salary = 0
        
        for job in jobs:
            companies[job.company] = companies.get(job.company, 0) + 1
            if job.remote:
                remote_count += 1
            if job.salary:
                with_salary += 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total": len(jobs),
            "remote_jobs": remote_count,
            "jobs_with_salary": with_salary,
            "top_companies": top_companies
        }
