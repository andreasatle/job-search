"""
Job cleanup and expiration management for the vector database.
Handles removing old, filled, or expired job postings.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from dotenv import load_dotenv

from .job_vector_store import JobVectorStore
from ..models.job_models import JobListing

# Load environment variables
load_dotenv()


class JobCleanupManager:
    """Manages cleanup and expiration of old job postings."""
    
    def __init__(self, vector_store: Optional[JobVectorStore] = None):
        """Initialize the cleanup manager."""
        self.vector_store = vector_store or JobVectorStore()
        
        # Default expiration policies (configurable)
        self.default_expiration_days = 30  # Jobs expire after 30 days
        self.max_database_size = 10000     # Max jobs to keep
        self.cleanup_batch_size = 100      # Process deletions in batches
        
    def set_expiration_policy(self, 
                             days: int = 30,
                             max_jobs: int = 10000,
                             batch_size: int = 100):
        """Configure the expiration policy."""
        self.default_expiration_days = days
        self.max_database_size = max_jobs
        self.cleanup_batch_size = batch_size
        
        print(f"📅 Expiration policy updated:")
        print(f"   • Jobs expire after: {days} days")
        print(f"   • Max database size: {max_jobs:,} jobs")
        print(f"   • Cleanup batch size: {batch_size}")
    
    def get_expired_jobs(self, 
                        expiration_days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find jobs that have expired based on posting or scraping date."""
        expiration_days = expiration_days or self.default_expiration_days
        cutoff_date = datetime.now() - timedelta(days=expiration_days)
        
        print(f"🔍 Finding jobs older than {expiration_days} days (before {cutoff_date.strftime('%Y-%m-%d')})")
        
        # Get all jobs from the database
        try:
            all_jobs = self.vector_store.collection.get(include=["metadatas"])
            expired_jobs = []
            
            for i, metadata in enumerate(all_jobs["metadatas"]):
                job_id = all_jobs["ids"][i]
                
                # Check scraped_date first (always available)
                scraped_date_str = metadata.get("scraped_date")
                posted_date_str = metadata.get("posted_date")
                
                job_date = None
                date_source = None
                
                # Prefer posted_date if available, fall back to scraped_date
                if posted_date_str:
                    try:
                        job_date = datetime.fromisoformat(posted_date_str.replace("Z", "+00:00"))
                        date_source = "posted"
                    except:
                        pass
                
                if not job_date and scraped_date_str:
                    try:
                        job_date = datetime.fromisoformat(scraped_date_str.replace("Z", "+00:00"))
                        date_source = "scraped"
                    except:
                        pass
                
                # If job is older than cutoff, mark for expiration
                if job_date and job_date < cutoff_date:
                    expired_jobs.append({
                        "id": job_id,
                        "title": metadata.get("title", "Unknown"),
                        "company": metadata.get("company", "Unknown"),
                        "job_date": job_date,
                        "date_source": date_source,
                        "days_old": (datetime.now() - job_date).days,
                        "metadata": metadata
                    })
            
            print(f"📊 Found {len(expired_jobs)} expired jobs out of {len(all_jobs['ids'])} total")
            return expired_jobs
            
        except Exception as e:
            print(f"❌ Error finding expired jobs: {e}")
            return []
    
    def get_jobs_by_age_groups(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group jobs by age for analysis."""
        try:
            all_jobs = self.vector_store.collection.get(include=["metadatas"])
            age_groups = {
                "fresh": [],      # 0-7 days
                "recent": [],     # 8-14 days  
                "aging": [],      # 15-30 days
                "old": [],        # 31-60 days
                "expired": []     # 60+ days
            }
            
            now = datetime.now()
            
            for i, metadata in enumerate(all_jobs["metadatas"]):
                job_id = all_jobs["ids"][i]
                
                # Get job date (prefer posted_date)
                date_str = metadata.get("posted_date") or metadata.get("scraped_date")
                if not date_str:
                    continue
                    
                try:
                    job_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    days_old = (now - job_date).days
                    
                    job_info = {
                        "id": job_id,
                        "title": metadata.get("title", "Unknown"),
                        "company": metadata.get("company", "Unknown"),
                        "source": metadata.get("source", "Unknown"),
                        "days_old": days_old,
                        "job_date": job_date
                    }
                    
                    if days_old <= 7:
                        age_groups["fresh"].append(job_info)
                    elif days_old <= 14:
                        age_groups["recent"].append(job_info)
                    elif days_old <= 30:
                        age_groups["aging"].append(job_info)
                    elif days_old <= 60:
                        age_groups["old"].append(job_info)
                    else:
                        age_groups["expired"].append(job_info)
                        
                except Exception as e:
                    print(f"⚠️ Error parsing date for job {job_id}: {e}")
                    continue
            
            return age_groups
            
        except Exception as e:
            print(f"❌ Error grouping jobs by age: {e}")
            return {}
    
    def cleanup_expired_jobs(self, 
                           expiration_days: Optional[int] = None,
                           dry_run: bool = True) -> Dict[str, int]:
        """Remove expired jobs from the database."""
        expired_jobs = self.get_expired_jobs(expiration_days)
        
        if not expired_jobs:
            print("✅ No expired jobs found")
            return {"deleted": 0, "kept": 0}
        
        if dry_run:
            print(f"🔍 DRY RUN: Would delete {len(expired_jobs)} expired jobs:")
            for job in expired_jobs[:10]:  # Show first 10
                print(f"   • {job['title']} at {job['company']} ({job['days_old']} days old)")
            if len(expired_jobs) > 10:
                print(f"   ... and {len(expired_jobs) - 10} more")
            print("\n💡 Run with dry_run=False to actually delete these jobs")
            return {"would_delete": len(expired_jobs), "kept": 0}
        
        # Actually delete the jobs
        deleted_count = 0
        failed_count = 0
        
        print(f"🗑️ Deleting {len(expired_jobs)} expired jobs...")
        
        # Delete in batches
        for i in range(0, len(expired_jobs), self.cleanup_batch_size):
            batch = expired_jobs[i:i + self.cleanup_batch_size]
            batch_ids = [job["id"] for job in batch]
            
            try:
                self.vector_store.collection.delete(ids=batch_ids)
                deleted_count += len(batch_ids)
                print(f"   🗑️ Deleted batch {i//self.cleanup_batch_size + 1}: {len(batch_ids)} jobs")
                
            except Exception as e:
                print(f"   ❌ Failed to delete batch {i//self.cleanup_batch_size + 1}: {e}")
                failed_count += len(batch_ids)
        
        print(f"✅ Cleanup complete: {deleted_count} deleted, {failed_count} failed")
        return {"deleted": deleted_count, "failed": failed_count}
    
    def cleanup_by_database_size(self, dry_run: bool = True) -> Dict[str, int]:
        """Remove oldest jobs if database exceeds max size."""
        try:
            current_count = self.vector_store.collection.count()
            
            if current_count <= self.max_database_size:
                print(f"✅ Database size OK: {current_count:,} jobs (max: {self.max_database_size:,})")
                return {"deleted": 0, "kept": current_count}
            
            excess_jobs = current_count - self.max_database_size
            print(f"📊 Database too large: {current_count:,} jobs (max: {self.max_database_size:,})")
            print(f"🎯 Need to remove oldest {excess_jobs:,} jobs")
            
            # Get all jobs sorted by date (oldest first)
            all_jobs = self.vector_store.collection.get(include=["metadatas"])
            jobs_with_dates = []
            
            for i, metadata in enumerate(all_jobs["metadatas"]):
                job_id = all_jobs["ids"][i]
                date_str = metadata.get("posted_date") or metadata.get("scraped_date")
                
                if date_str:
                    try:
                        job_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        jobs_with_dates.append({
                            "id": job_id,
                            "date": job_date,
                            "title": metadata.get("title", "Unknown"),
                            "company": metadata.get("company", "Unknown")
                        })
                    except:
                        pass
            
            # Sort by date (oldest first)
            jobs_with_dates.sort(key=lambda x: x["date"])
            jobs_to_delete = jobs_with_dates[:excess_jobs]
            
            if dry_run:
                print(f"🔍 DRY RUN: Would delete {len(jobs_to_delete)} oldest jobs:")
                for job in jobs_to_delete[:10]:
                    days_old = (datetime.now() - job["date"]).days
                    print(f"   • {job['title']} at {job['company']} ({days_old} days old)")
                if len(jobs_to_delete) > 10:
                    print(f"   ... and {len(jobs_to_delete) - 10} more")
                return {"would_delete": len(jobs_to_delete), "kept": current_count - len(jobs_to_delete)}
            
            # Actually delete
            ids_to_delete = [job["id"] for job in jobs_to_delete]
            deleted_count = 0
            
            for i in range(0, len(ids_to_delete), self.cleanup_batch_size):
                batch_ids = ids_to_delete[i:i + self.cleanup_batch_size]
                try:
                    self.vector_store.collection.delete(ids=batch_ids)
                    deleted_count += len(batch_ids)
                except Exception as e:
                    print(f"❌ Failed to delete batch: {e}")
            
            print(f"✅ Size cleanup complete: {deleted_count} oldest jobs deleted")
            return {"deleted": deleted_count, "kept": current_count - deleted_count}
            
        except Exception as e:
            print(f"❌ Error in size cleanup: {e}")
            return {"deleted": 0, "failed": 1}
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get comprehensive cleanup statistics."""
        print("📊 Analyzing job database for cleanup opportunities...")
        
        try:
            total_jobs = self.vector_store.collection.count()
            age_groups = self.get_jobs_by_age_groups()
            expired_jobs = self.get_expired_jobs()
            
            stats = {
                "total_jobs": total_jobs,
                "max_database_size": self.max_database_size,
                "expiration_days": self.default_expiration_days,
                "age_breakdown": {
                    "fresh_0_7_days": len(age_groups.get("fresh", [])),
                    "recent_8_14_days": len(age_groups.get("recent", [])),
                    "aging_15_30_days": len(age_groups.get("aging", [])),
                    "old_31_60_days": len(age_groups.get("old", [])),
                    "expired_60plus_days": len(age_groups.get("expired", []))
                },
                "cleanup_recommendations": {
                    "expired_jobs_to_delete": len(expired_jobs),
                    "database_size_ok": total_jobs <= self.max_database_size,
                    "oldest_jobs_to_delete": max(0, total_jobs - self.max_database_size)
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting cleanup stats: {e}")
            return {}
    
    def auto_cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """Perform automatic cleanup based on policies."""
        print("🤖 Starting automatic cleanup...")
        
        results = {
            "expired_cleanup": self.cleanup_expired_jobs(dry_run=dry_run),
            "size_cleanup": self.cleanup_by_database_size(dry_run=dry_run),
            "final_stats": {}
        }
        
        if not dry_run:
            results["final_stats"] = self.get_cleanup_stats()
        
        return results


# Convenience functions
def cleanup_old_jobs(days: int = 30, dry_run: bool = True) -> Dict[str, int]:
    """Quick function to cleanup jobs older than specified days."""
    cleanup_manager = JobCleanupManager()
    return cleanup_manager.cleanup_expired_jobs(expiration_days=days, dry_run=dry_run)


def get_job_age_report() -> Dict[str, Any]:
    """Get a report on job ages in the database."""
    cleanup_manager = JobCleanupManager()
    return cleanup_manager.get_cleanup_stats()


def auto_maintenance(dry_run: bool = True) -> Dict[str, Any]:
    """Perform automatic database maintenance."""
    cleanup_manager = JobCleanupManager()
    return cleanup_manager.auto_cleanup(dry_run=dry_run)


if __name__ == "__main__":
    # Demo the cleanup system
    print("🧹 Job Cleanup System Demo")
    print("=" * 50)
    
    # Get current stats
    stats = get_job_age_report()
    if stats:
        print(f"📊 Database Stats:")
        print(f"   Total jobs: {stats['total_jobs']:,}")
        print(f"   Fresh (0-7 days): {stats['age_breakdown']['fresh_0_7_days']}")
        print(f"   Recent (8-14 days): {stats['age_breakdown']['recent_8_14_days']}")
        print(f"   Aging (15-30 days): {stats['age_breakdown']['aging_15_30_days']}")
        print(f"   Old (31-60 days): {stats['age_breakdown']['old_31_60_days']}")
        print(f"   Expired (60+ days): {stats['age_breakdown']['expired_60plus_days']}")
        
        print(f"\n🎯 Cleanup Recommendations:")
        rec = stats['cleanup_recommendations']
        print(f"   Expired jobs to delete: {rec['expired_jobs_to_delete']}")
        print(f"   Database size OK: {rec['database_size_ok']}")
        if not rec['database_size_ok']:
            print(f"   Oldest jobs to delete: {rec['oldest_jobs_to_delete']}")
    
    # Run auto cleanup (dry run)
    print(f"\n🤖 Auto Cleanup (Dry Run):")
    results = auto_maintenance(dry_run=True)
