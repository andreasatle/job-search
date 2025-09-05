#!/usr/bin/env python3
"""
Clean, simple job search system.
Just the essentials - no complexity!
"""

import asyncio
from src.scraper import RemoteOKScraper
from src.storage import SimpleJobStorage


async def search_and_save(query: str = "software engineer", max_jobs: int = 10):
    """Search for jobs and save them."""
    print(f"🚀 Simple Job Search: '{query}'")
    print("=" * 50)
    
    # Create scraper and storage
    scraper = RemoteOKScraper(headless=True)
    storage = SimpleJobStorage()
    
    try:
        # Search for jobs
        jobs = await scraper.search_jobs(query, max_jobs=max_jobs)
        
        if jobs:
            # Save jobs
            new_count = storage.save_jobs(jobs)
            
            # Show results
            print(f"\n📊 Results:")
            print(f"   🎯 Jobs found: {len(jobs)}")
            print(f"   💾 New jobs saved: {new_count}")
            
            # Show some jobs
            print(f"\n📋 Sample Jobs:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"   {i}. {job.title}")
                print(f"      Company: {job.company}")
                print(f"      Location: {job.location}")
                if job.salary:
                    print(f"      Salary: {job.salary}")
                if job.remote:
                    print(f"      🏠 Remote")
                print()
        
        else:
            print("❌ No jobs found")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def search_saved_jobs(query: str):
    """Search in saved jobs."""
    print(f"🔍 Searching saved jobs for: '{query}'")
    storage = SimpleJobStorage()
    
    matching_jobs = storage.search_jobs(query)
    
    if matching_jobs:
        print(f"📊 Found {len(matching_jobs)} matching jobs:")
        for i, job in enumerate(matching_jobs[:5], 1):
            print(f"   {i}. {job}")
    else:
        print("❌ No matching jobs found")


def show_stats():
    """Show job statistics."""
    storage = SimpleJobStorage()
    stats = storage.get_stats()
    
    print("📊 Job Database Stats:")
    print(f"   Total jobs: {stats['total']}")
    
    if stats['total'] > 0:
        print(f"   Remote jobs: {stats['remote_jobs']}")
        print(f"   Jobs with salary: {stats['jobs_with_salary']}")
        
        if stats['top_companies']:
            print(f"   Top companies:")
            for company, count in stats['top_companies']:
                print(f"     • {company}: {count} jobs")


def main():
    """Interactive main function."""
    print("🎯 Simple Job Search System")
    print("Clean, minimal, just works!")
    print()
    
    while True:
        print("Options:")
        print("1. Search for new jobs")
        print("2. Search saved jobs")
        print("3. Show statistics")
        print("4. Quick test (3 jobs)")
        print("5. Exit")
        
        choice = input("\nChoice (1-5): ").strip()
        print()
        
        if choice == "1":
            query = input("Search query (or Enter for 'software engineer'): ").strip()
            if not query:
                query = "software engineer"
            
            try:
                max_jobs = int(input("Max jobs (or Enter for 10): ").strip() or "10")
            except ValueError:
                max_jobs = 10
            
            asyncio.run(search_and_save(query, max_jobs))
            
        elif choice == "2":
            query = input("Search saved jobs for: ").strip()
            if query:
                search_saved_jobs(query)
            else:
                print("❌ Please enter a search term")
                
        elif choice == "3":
            show_stats()
            
        elif choice == "4":
            print("🧪 Quick test - searching for 3 software engineer jobs...")
            asyncio.run(search_and_save("software engineer", 3))
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")
        
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
