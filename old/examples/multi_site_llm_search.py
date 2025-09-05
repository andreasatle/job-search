"""
Comprehensive example: Multi-site LLM Engineer job search.
Shows how to search across multiple job platforms for LLM roles.
"""

import asyncio
from src.scrapers.multi_site_llm_scraper import create_multi_site_llm_scraper
from src.database.job_vector_store import JobVectorStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def demonstrate_multi_site_architecture():
    """Show the multi-site scraper architecture and current status."""
    print("🌐 Multi-Site LLM Scraper Architecture")
    print("=" * 45)
    
    # Create multi-site scraper
    scraper = create_multi_site_llm_scraper()
    
    # Show site status
    print("📊 Supported Job Sites:")
    site_status = scraper.get_site_status()
    
    for site, status in site_status.items():
        impl_status = "✅ Ready" if status["implemented"] else "⏳ Coming Soon"
        enabled_status = "🟢 Enabled" if status["enabled"] else "🔴 Disabled"
        
        print(f"\n🌐 {site.title()}")
        print(f"   Status: {impl_status}")
        print(f"   Search: {enabled_status}")
        print(f"   Priority: #{status['priority']}")
        print(f"   Expected Results: {status['expected_results']}")
        print(f"   Specialties: {', '.join(status['specialties'])}")
    
    print(f"\n💡 Implementation Roadmap:")
    print(f"   ✅ ZipRecruiter - Currently working")
    print(f"   🚧 Indeed - High priority (most job volume)")
    print(f"   🚧 LinkedIn - Medium priority (high quality)")
    print(f"   🚧 Glassdoor - Low priority (salary info)")
    print(f"   🚧 AngelList - Low priority (startup focus)")


async def search_current_sites():
    """Search using currently implemented sites."""
    print(f"\n🔍 Multi-Site LLM Job Search")
    print("=" * 35)
    
    # Create scraper
    scraper = create_multi_site_llm_scraper(strict_mode=False)
    
    print("🎯 Searching for LLM Engineer jobs across all available sites...")
    print("📍 Location: Houston, TX")
    print("🎚️ Mode: General (all experience levels)")
    
    try:
        # Perform multi-site search
        results = await scraper.search_all_sites(
            location="Houston, TX",
            max_pages_per_site=2,
            seniority_level=None  # All levels
        )
        
        # Results are automatically printed by the scraper
        # But we can also access the data programmatically
        
        if results.total_jobs_found > 0:
            print(f"\n📈 Detailed Analysis:")
            print(f"   🎯 Search efficiency: {results.total_jobs_found} jobs in {results.search_duration:.1f}s")
            print(f"   🏆 Best site: {results.best_site.title()}")
            
            # Show unique companies
            companies = set(job.company for job in results.all_jobs)
            print(f"   🏢 Unique companies: {len(companies)}")
            if len(companies) <= 5:
                print(f"      Companies: {', '.join(companies)}")
            
            # Show remote work distribution
            remote_jobs = len([j for j in results.all_jobs if j.remote_type.value in ['remote', 'hybrid']])
            remote_percentage = remote_jobs / results.total_jobs_found * 100
            print(f"   🏠 Remote-friendly: {remote_jobs}/{results.total_jobs_found} ({remote_percentage:.1f}%)")
            
            return results
        else:
            print("❌ No LLM jobs found!")
            print("💡 This might be because:")
            print("   • Limited job sites currently implemented")
            print("   • Strict filtering criteria")
            print("   • Limited LLM jobs in Houston area")
            print("   • Scraping issues (rate limiting, etc.)")
            return None
    
    except Exception as e:
        print(f"❌ Multi-site search failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def compare_single_vs_multi_site():
    """Compare single-site vs multi-site LLM job searching."""
    print(f"\n⚖️  Single-Site vs Multi-Site Comparison")
    print("=" * 45)
    
    from src.scrapers.llm_engineer_scraper import create_llm_engineer_scraper
    
    # Single-site search (ZipRecruiter only)
    print("1️⃣ Single-Site Search (ZipRecruiter only):")
    try:
        single_scraper = create_llm_engineer_scraper()
        single_results = await single_scraper.search_llm_jobs(max_pages=2)
        single_jobs = single_results["jobs"]
        
        print(f"   📊 Found: {len(single_jobs)} LLM jobs")
        print(f"   🎯 Source: ZipRecruiter only")
        
    except Exception as e:
        print(f"   ❌ Single-site search failed: {e}")
        single_jobs = []
    
    # Multi-site search
    print(f"\n2️⃣ Multi-Site Search (All available sites):")
    try:
        multi_scraper = create_multi_site_llm_scraper()
        multi_results = await multi_scraper.search_all_sites(max_pages_per_site=2)
        multi_jobs = multi_results.all_jobs
        
        print(f"   📊 Found: {len(multi_jobs)} LLM jobs")
        print(f"   🎯 Sources: {', '.join(multi_results.successful_sites)}")
        
        # Calculate improvement
        if single_jobs:
            improvement = len(multi_jobs) / len(single_jobs)
            print(f"   📈 Improvement: {improvement:.1f}x more jobs")
        
        # Show source breakdown
        if multi_results.site_results:
            print(f"   🔍 Source breakdown:")
            for site, results in multi_results.site_results.items():
                if results.get("status") == "success":
                    jobs_found = results.get("jobs_found", 0)
                    print(f"      • {site.title()}: {jobs_found} jobs")
        
    except Exception as e:
        print(f"   ❌ Multi-site search failed: {e}")
        multi_jobs = []
    
    # Summary
    print(f"\n📋 Comparison Summary:")
    print(f"   Single-site jobs: {len(single_jobs)}")
    print(f"   Multi-site jobs: {len(multi_jobs)}")
    if single_jobs and multi_jobs:
        print(f"   Additional coverage: {len(multi_jobs) - len(single_jobs)} more jobs")


async def store_multi_site_results():
    """Store multi-site LLM job results in vector database."""
    print(f"\n💾 Store Multi-Site Results in Vector Database")
    print("=" * 50)
    
    # Perform multi-site search
    scraper = create_multi_site_llm_scraper()
    results = await scraper.search_all_sites(
        location="Houston, TX",
        max_pages_per_site=3
    )
    
    if not results.all_jobs:
        print("❌ No jobs to store!")
        return
    
    # Store in vector database
    print(f"💾 Storing {len(results.all_jobs)} LLM jobs in vector database...")
    
    try:
        vector_store = JobVectorStore(db_path="./multi_site_llm_db")
        added, failed = vector_store.add_jobs(results.all_jobs)
        
        print(f"✅ Storage complete:")
        print(f"   📥 Added: {added} jobs")
        print(f"   ❌ Failed: {failed} jobs")
        
        # Test semantic search across all sites
        print(f"\n🔍 Testing cross-site semantic search...")
        
        test_queries = [
            "transformer neural networks",
            "pytorch machine learning",
            "remote ai engineer",
            "senior llm developer"
        ]
        
        for query in test_queries:
            search_results = vector_store.search_jobs(query, n_results=3)
            
            print(f"\n📋 Results for '{query}':")
            for i, result in enumerate(search_results, 1):
                source = result.get('source', 'unknown')
                similarity = result.get('similarity_score', 0)
                print(f"   {i}. {result['title']} ({source}) - {similarity:.2%} match")
        
        print(f"\n🎉 Multi-site LLM jobs are now searchable!")
        print(f"📁 Database location: ./multi_site_llm_db")
        
    except Exception as e:
        print(f"❌ Error storing jobs: {e}")


def show_implementation_guide():
    """Show how to implement additional job sites."""
    print(f"\n🛠️  Adding New Job Sites - Implementation Guide")
    print("=" * 55)
    
    guide = [
        "1. 📝 Create site-specific scraper:",
        "   • Inherit from PlaywrightJobScraper",
        "   • Implement site-specific selectors", 
        "   • Handle anti-bot measures",
        "   • Create LLM-optimized filters",
        "",
        "2. 🔧 Add to multi-site scraper:",
        "   • Add scraper to self.scrapers dict",
        "   • Configure in self.site_configs",
        "   • Set priority and expected results",
        "",
        "3. 🧪 Test integration:",
        "   • Test individual scraper", 
        "   • Test multi-site integration",
        "   • Verify deduplication works",
        "",
        "4. 📊 Site-specific considerations:",
        "   • Indeed: CAPTCHA, rate limiting, high volume",
        "   • LinkedIn: Authentication, ToS issues, high quality",
        "   • Glassdoor: Salary focus, moderate volume",
        "   • AngelList: Startup focus, equity info"
    ]
    
    for line in guide:
        print(f"   {line}")
    
    print(f"\n💡 Implementation Priority:")
    print(f"   🥇 Indeed (highest job volume)")
    print(f"   🥈 LinkedIn (highest quality)")
    print(f"   🥉 Glassdoor (salary insights)")
    print(f"   4️⃣ AngelList (startup roles)")


async def main():
    """Main demo function."""
    print("🤖 Multi-Site LLM Engineer Job Search Demo")
    print("=" * 50)
    print("This demo shows the architecture for searching LLM jobs")
    print("across multiple job platforms with unified filtering.")
    
    await demonstrate_multi_site_architecture()
    
    # Show current functionality
    results = await search_current_sites()
    
    if results and results.total_jobs_found > 0:
        # Only run additional demos if we found jobs
        await compare_single_vs_multi_site()
        await store_multi_site_results()
    
    show_implementation_guide()
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Implement Indeed scraper (highest priority)")
    print(f"   2. Implement LinkedIn scraper (high quality)")
    print(f"   3. Add Glassdoor for salary insights")
    print(f"   4. Consider AngelList for startup roles")
    print(f"   5. Add site-specific optimizations")
    
    print(f"\n🚀 Current Usage:")
    print(f"   from src.scrapers.multi_site_llm_scraper import create_multi_site_llm_scraper")
    print(f"   scraper = create_multi_site_llm_scraper()")
    print(f"   results = await scraper.search_all_sites()")


if __name__ == "__main__":
    asyncio.run(main())
