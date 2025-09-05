"""
Scheduled cleanup system for automatic job database maintenance.
Runs periodic cleanup tasks to remove old, expired, or filled jobs.
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable
import asyncio

from .job_cleanup import JobCleanupManager, auto_maintenance


class ScheduledCleanupService:
    """Service for running scheduled database cleanup tasks."""
    
    def __init__(self, 
                 cleanup_manager: Optional[JobCleanupManager] = None,
                 auto_start: bool = False):
        """Initialize the scheduled cleanup service."""
        self.cleanup_manager = cleanup_manager or JobCleanupManager()
        self.is_running = False
        self.scheduler_thread = None
        
        # Default schedule configuration
        self.configure_default_schedule()
        
        if auto_start:
            self.start()
    
    def configure_default_schedule(self):
        """Configure the default cleanup schedule."""
        # Clear any existing jobs
        schedule.clear()
        
        # Daily cleanup at 2 AM
        schedule.every().day.at("02:00").do(self._daily_cleanup)
        
        # Weekly deep cleanup on Sunday at 3 AM  
        schedule.every().sunday.at("03:00").do(self._weekly_deep_cleanup)
        
        # Size-based cleanup every 6 hours
        schedule.every(6).hours.do(self._size_cleanup)
        
        print("📅 Cleanup schedule configured:")
        print("   • Daily cleanup: 2:00 AM (expired jobs)")
        print("   • Weekly deep cleanup: Sunday 3:00 AM")
        print("   • Size cleanup: Every 6 hours")
    
    def configure_custom_schedule(self,
                                daily_time: str = "02:00",
                                weekly_day: str = "sunday", 
                                weekly_time: str = "03:00",
                                size_cleanup_hours: int = 6):
        """Configure custom cleanup schedule."""
        schedule.clear()
        
        # Daily cleanup
        schedule.every().day.at(daily_time).do(self._daily_cleanup)
        
        # Weekly cleanup
        getattr(schedule.every(), weekly_day.lower()).at(weekly_time).do(self._weekly_deep_cleanup)
        
        # Size-based cleanup
        schedule.every(size_cleanup_hours).hours.do(self._size_cleanup)
        
        print(f"📅 Custom cleanup schedule configured:")
        print(f"   • Daily cleanup: {daily_time}")
        print(f"   • Weekly deep cleanup: {weekly_day.title()} {weekly_time}")
        print(f"   • Size cleanup: Every {size_cleanup_hours} hours")
    
    def _daily_cleanup(self):
        """Daily cleanup task - remove expired jobs."""
        print(f"🌅 Starting daily cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Cleanup jobs older than 30 days
            result = self.cleanup_manager.cleanup_expired_jobs(
                expiration_days=30, 
                dry_run=False
            )
            
            print(f"✅ Daily cleanup complete: {result.get('deleted', 0)} jobs deleted")
            
            # Log cleanup stats
            stats = self.cleanup_manager.get_cleanup_stats()
            self._log_cleanup_stats("daily", stats)
            
        except Exception as e:
            print(f"❌ Daily cleanup failed: {e}")
    
    def _weekly_deep_cleanup(self):
        """Weekly deep cleanup - comprehensive maintenance."""
        print(f"🧹 Starting weekly deep cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # More aggressive cleanup for weekly run
            results = auto_maintenance(dry_run=False)
            
            print("✅ Weekly deep cleanup complete:")
            print(f"   • Expired jobs deleted: {results['expired_cleanup'].get('deleted', 0)}")
            print(f"   • Size cleanup deleted: {results['size_cleanup'].get('deleted', 0)}")
            
            # Log detailed stats
            if 'final_stats' in results:
                self._log_cleanup_stats("weekly", results['final_stats'])
                
        except Exception as e:
            print(f"❌ Weekly cleanup failed: {e}")
    
    def _size_cleanup(self):
        """Size-based cleanup - maintain database size limits."""
        print(f"📏 Starting size cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            result = self.cleanup_manager.cleanup_by_database_size(dry_run=False)
            
            if result.get('deleted', 0) > 0:
                print(f"✅ Size cleanup complete: {result['deleted']} oldest jobs deleted")
            else:
                print("✅ Size cleanup: No action needed, database within limits")
                
        except Exception as e:
            print(f"❌ Size cleanup failed: {e}")
    
    def _log_cleanup_stats(self, cleanup_type: str, stats: dict):
        """Log cleanup statistics."""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "cleanup_type": cleanup_type,
            "total_jobs": stats.get('total_jobs', 0),
            "age_breakdown": stats.get('age_breakdown', {}),
            "recommendations": stats.get('cleanup_recommendations', {})
        }
        
        # You could extend this to write to a log file
        print(f"📊 {cleanup_type.title()} cleanup stats logged for {timestamp}")
    
    def start(self):
        """Start the scheduled cleanup service."""
        if self.is_running:
            print("⚠️ Cleanup service is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("🚀 Scheduled cleanup service started")
        print("   Service runs in background thread")
        print("   Use .stop() to halt scheduled cleanups")
    
    def stop(self):
        """Stop the scheduled cleanup service."""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            print("🛑 Scheduled cleanup service stopped")
        else:
            print("⚠️ Cleanup service was not running")
    
    def _run_scheduler(self):
        """Run the scheduler in a background thread."""
        print("⏰ Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)  # Continue running even if there's an error
        
        print("⏰ Scheduler thread stopped")
    
    def get_next_runs(self) -> dict:
        """Get information about next scheduled runs."""
        jobs = schedule.get_jobs()
        next_runs = {}
        
        for job in jobs:
            job_name = job.job_func.__name__
            next_run = job.next_run
            next_runs[job_name] = {
                "next_run": next_run.isoformat() if next_run else None,
                "interval": str(job.interval),
                "unit": job.unit
            }
        
        return next_runs
    
    def run_manual_cleanup(self, cleanup_type: str = "auto"):
        """Run a manual cleanup outside the schedule."""
        print(f"🔧 Running manual {cleanup_type} cleanup...")
        
        if cleanup_type == "daily":
            self._daily_cleanup()
        elif cleanup_type == "weekly":
            self._weekly_deep_cleanup()
        elif cleanup_type == "size":
            self._size_cleanup()
        elif cleanup_type == "auto":
            results = auto_maintenance(dry_run=False)
            print(f"✅ Manual auto cleanup complete: {results}")
        else:
            print(f"❌ Unknown cleanup type: {cleanup_type}")
    
    def status(self):
        """Get service status and next scheduled runs."""
        print(f"🔍 Cleanup Service Status:")
        print(f"   Running: {'✅ Yes' if self.is_running else '❌ No'}")
        print(f"   Thread alive: {'✅ Yes' if self.scheduler_thread and self.scheduler_thread.is_alive() else '❌ No'}")
        
        if self.is_running:
            next_runs = self.get_next_runs()
            print(f"   Scheduled jobs: {len(next_runs)}")
            
            for job_name, info in next_runs.items():
                if info['next_run']:
                    print(f"     • {job_name}: {info['next_run']}")


# Global service instance
_cleanup_service = None


def start_cleanup_service(auto_start: bool = True) -> ScheduledCleanupService:
    """Start the global cleanup service."""
    global _cleanup_service
    
    if _cleanup_service is None:
        _cleanup_service = ScheduledCleanupService(auto_start=auto_start)
    elif not _cleanup_service.is_running:
        _cleanup_service.start()
    
    return _cleanup_service


def stop_cleanup_service():
    """Stop the global cleanup service."""
    global _cleanup_service
    
    if _cleanup_service:
        _cleanup_service.stop()


def get_cleanup_service() -> Optional[ScheduledCleanupService]:
    """Get the global cleanup service instance."""
    return _cleanup_service


def manual_cleanup(cleanup_type: str = "auto"):
    """Run a manual cleanup."""
    service = get_cleanup_service()
    if service:
        service.run_manual_cleanup(cleanup_type)
    else:
        # Create temporary service for one-off cleanup
        temp_service = ScheduledCleanupService()
        temp_service.run_manual_cleanup(cleanup_type)


if __name__ == "__main__":
    # Demo the scheduled cleanup system
    print("⏰ Scheduled Cleanup System Demo")
    print("=" * 50)
    
    # Start the service
    service = start_cleanup_service(auto_start=True)
    
    # Show status
    service.status()
    
    print("\n🔧 Available manual commands:")
    print("   service.run_manual_cleanup('daily')   # Remove expired jobs")
    print("   service.run_manual_cleanup('weekly')  # Deep cleanup")
    print("   service.run_manual_cleanup('size')    # Size-based cleanup")
    print("   service.run_manual_cleanup('auto')    # Auto maintenance")
    
    # Keep running for demo (remove this in production)
    try:
        print("\n⏰ Service running... Press Ctrl+C to stop")
        while True:
            time.sleep(10)
            # Show next runs every 10 seconds for demo
            next_runs = service.get_next_runs()
            for job_name, info in next_runs.items():
                if info['next_run']:
                    next_time = datetime.fromisoformat(info['next_run'])
                    time_until = next_time - datetime.now()
                    if time_until.total_seconds() > 0:
                        print(f"⏰ Next {job_name}: {time_until}")
                    break  # Just show one for demo
    except KeyboardInterrupt:
        print("\n🛑 Stopping cleanup service...")
        stop_cleanup_service()
        print("✅ Cleanup service stopped")
