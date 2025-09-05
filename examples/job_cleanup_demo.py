#!/usr/bin/env python3
"""
Job Cleanup System Demo
Demonstrates how to manage old and expired job postings.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.job_cleanup import JobCleanupManager, get_job_age_report, auto_maintenance
from src.database.scheduled_cleanup import start_cleanup_service, manual_cleanup


def demo_job_age_analysis():
    """Demo job age analysis and reporting."""
    print("📊 Job Age Analysis Demo")
    print("=" * 50)
    
    # Get comprehensive age report
    stats = get_job_age_report()
    
    if not stats:
        print("❌ No job statistics available")
        return
    
    print(f"📈 Database Overview:")
    print(f"   Total jobs: {stats['total_jobs']:,}")
    print(f"   Max database size: {stats['max_database_size']:,}")
    print(f"   Expiration policy: {stats['expiration_days']} days")
    
    print(f"\n📅 Age Breakdown:")
    age_breakdown = stats['age_breakdown']
    print(f"   🟢 Fresh (0-7 days): {age_breakdown['fresh_0_7_days']}")
    print(f"   🟡 Recent (8-14 days): {age_breakdown['recent_8_14_days']}")
    print(f"   🟠 Aging (15-30 days): {age_breakdown['aging_15_30_days']}")
    print(f"   🔴 Old (31-60 days): {age_breakdown['old_31_60_days']}")
    print(f"   ⚫ Expired (60+ days): {age_breakdown['expired_60plus_days']}")
    
    print(f"\n🎯 Cleanup Recommendations:")
    rec = stats['cleanup_recommendations']
    print(f"   Expired jobs to delete: {rec['expired_jobs_to_delete']}")
    print(f"   Database size OK: {'✅ Yes' if rec['database_size_ok'] else '❌ No'}")
    
    if not rec['database_size_ok']:
        print(f"   Oldest jobs to delete: {rec['oldest_jobs_to_delete']}")
    
    return stats


def demo_cleanup_policies():
    """Demo different cleanup policies."""
    print("\n🔧 Cleanup Policies Demo")
    print("=" * 50)
    
    cleanup_manager = JobCleanupManager()
    
    # Show current policy
    print(f"📋 Current Policy:")
    print(f"   Expiration: {cleanup_manager.default_expiration_days} days")
    print(f"   Max database size: {cleanup_manager.max_database_size:,} jobs")
    print(f"   Batch size: {cleanup_manager.cleanup_batch_size}")
    
    # Demo different policies
    policies = [
        {"name": "Conservative", "days": 60, "max_jobs": 15000},
        {"name": "Moderate", "days": 30, "max_jobs": 10000},
        {"name": "Aggressive", "days": 14, "max_jobs": 5000}
    ]
    
    print(f"\n🎯 Available Policies:")
    for policy in policies:
        print(f"   {policy['name']}: {policy['days']} days, max {policy['max_jobs']:,} jobs")
    
    # Test with moderate policy
    print(f"\n🔄 Testing Moderate Policy (30 days, 10k jobs):")
    cleanup_manager.set_expiration_policy(days=30, max_jobs=10000)
    
    # Dry run with new policy
    expired_jobs = cleanup_manager.get_expired_jobs()
    print(f"   Would delete {len(expired_jobs)} expired jobs")


def demo_dry_run_cleanup():
    """Demo dry run cleanup operations."""
    print("\n🔍 Dry Run Cleanup Demo")
    print("=" * 50)
    
    print("🧪 Testing cleanup operations (no actual deletions):")
    
    # Auto maintenance dry run
    results = auto_maintenance(dry_run=True)
    
    print(f"\n📊 Auto Maintenance Results (Dry Run):")
    
    if 'expired_cleanup' in results:
        expired = results['expired_cleanup']
        if 'would_delete' in expired:
            print(f"   Expired jobs: Would delete {expired['would_delete']}")
        else:
            print(f"   Expired jobs: {expired.get('deleted', 0)} deleted, {expired.get('failed', 0)} failed")
    
    if 'size_cleanup' in results:
        size = results['size_cleanup']
        if 'would_delete' in size:
            print(f"   Size cleanup: Would delete {size['would_delete']} oldest jobs")
        else:
            print(f"   Size cleanup: {size.get('deleted', 0)} deleted")
    
    print(f"\n💡 This was a dry run - no jobs were actually deleted")
    print(f"   Set dry_run=False to perform actual cleanup")


def demo_scheduled_cleanup():
    """Demo the scheduled cleanup service."""
    print("\n⏰ Scheduled Cleanup Demo")
    print("=" * 50)
    
    print("🚀 Starting cleanup service...")
    
    # Start the service (but don't auto-start scheduler for demo)
    service = start_cleanup_service(auto_start=False)
    
    # Show default schedule
    print(f"\n📅 Default Schedule:")
    print(f"   Daily cleanup: 2:00 AM (expired jobs)")
    print(f"   Weekly deep cleanup: Sunday 3:00 AM")
    print(f"   Size cleanup: Every 6 hours")
    
    # Show available manual operations
    print(f"\n🔧 Manual Operations Available:")
    print(f"   • manual_cleanup('daily')   - Remove expired jobs")
    print(f"   • manual_cleanup('weekly')  - Deep cleanup")
    print(f"   • manual_cleanup('size')    - Size-based cleanup")
    print(f"   • manual_cleanup('auto')    - Auto maintenance")
    
    # Demo manual cleanup (dry run equivalent)
    print(f"\n🔧 Demo: Manual Auto Cleanup...")
    try:
        # This would normally perform cleanup, but we'll just show the concept
        print(f"   This would run comprehensive cleanup operations")
        print(f"   Including expired job removal and size management")
        
    except Exception as e:
        print(f"   Note: {e}")
    
    print(f"\n💡 In production, the service would run continuously")
    print(f"   Use service.start() to begin scheduled operations")


def demo_real_time_monitoring():
    """Demo real-time job monitoring and alerts."""
    print("\n🔔 Real-Time Monitoring Demo")
    print("=" * 50)
    
    cleanup_manager = JobCleanupManager()
    
    # Get current job ages
    age_groups = cleanup_manager.get_jobs_by_age_groups()
    
    print(f"🎯 Current Job Status:")
    for age_group, jobs in age_groups.items():
        count = len(jobs)
        if count > 0:
            print(f"   {age_group.title()}: {count} jobs")
            
            # Show examples for each group
            if age_group in ['old', 'expired'] and count > 0:
                print(f"     Examples:")
                for job in jobs[:3]:  # Show first 3
                    print(f"       • {job['title']} at {job['company']} ({job['days_old']} days old)")
                if count > 3:
                    print(f"       ... and {count - 3} more")
    
    # Alert conditions
    expired_count = len(age_groups.get('expired', []))
    old_count = len(age_groups.get('old', []))
    
    print(f"\n🚨 Alert Conditions:")
    if expired_count > 0:
        print(f"   ⚠️  {expired_count} jobs have expired (60+ days old)")
    if old_count > 10:
        print(f"   ⚠️  {old_count} jobs are getting old (31-60 days)")
    
    if expired_count == 0 and old_count <= 10:
        print(f"   ✅ No immediate cleanup needed")
    
    print(f"\n💡 Monitoring recommendations:")
    print(f"   • Run cleanup when expired > 50 jobs")
    print(f"   • Monitor database growth trends")
    print(f"   • Set up alerts for cleanup failures")


def main():
    """Run the complete job cleanup demo."""
    print("🧹 Complete Job Cleanup System Demo")
    print("=" * 60)
    print("This demo shows how to manage old and expired job postings")
    print("in your LLM job search database.")
    print("=" * 60)
    
    try:
        # Run all demo sections
        demo_job_age_analysis()
        demo_cleanup_policies()
        demo_dry_run_cleanup()
        demo_scheduled_cleanup()
        demo_real_time_monitoring()
        
        print("\n🎉 Job Cleanup Demo Complete!")
        print("\n📋 Key Features Demonstrated:")
        print("   ✅ Job age analysis and reporting")
        print("   ✅ Flexible cleanup policies") 
        print("   ✅ Safe dry-run operations")
        print("   ✅ Scheduled automatic cleanup")
        print("   ✅ Real-time monitoring and alerts")
        
        print("\n🚀 Next Steps:")
        print("   1. Configure your preferred cleanup policy")
        print("   2. Start the scheduled cleanup service")
        print("   3. Monitor job age distribution")
        print("   4. Run manual cleanup as needed")
        
        print("\n💡 Production Usage:")
        print("   # Auto cleanup with default settings")
        print("   from src.database.job_cleanup import auto_maintenance")
        print("   auto_maintenance(dry_run=False)")
        print("")
        print("   # Start scheduled service")
        print("   from src.database.scheduled_cleanup import start_cleanup_service")
        print("   start_cleanup_service()")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
