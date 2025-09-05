"""
Test script for the LLM Engineer scraper.
"""

import asyncio
from src.scrapers.llm_engineer_scraper import (
    create_llm_engineer_scraper,
    create_senior_llm_scraper,
    create_junior_llm_scraper
)


async def test_llm_scraper_basic():
    """Test basic LLM scraper functionality."""
    print("🤖 Testing LLM Engineer Scraper")
    print("=" * 40)
    
    # Test general LLM scraper
    print("\n1️⃣ General LLM Engineer Scraper:")
    try:
        scraper = create_llm_engineer_scraper()
        results = await scraper.search_llm_jobs(max_pages=1)
        
        print(f"   ✅ Search completed successfully")
        print(f"   📊 Found {results['total_jobs_found']} LLM engineering jobs")
        print(f"   🎯 Filtering efficiency: {results['filtering_efficiency']}")
        print(f"   ⭐ Average quality: {results['avg_quality_score']:.2f}")
        
        if results['jobs']:
            print(f"   🏆 Best match: {results['jobs'][0].title} at {results['jobs'][0].company}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_senior_llm_scraper():
    """Test senior-level LLM scraper."""
    print("\n2️⃣ Senior LLM Engineer Scraper (Strict Mode):")
    try:
        scraper = create_senior_llm_scraper()
        results = await scraper.search_llm_jobs(
            max_pages=1, 
            seniority_level="senior"
        )
        
        print(f"   ✅ Senior search completed")
        print(f"   📊 Found {results['total_jobs_found']} senior LLM jobs")
        
        if results['salary_range']['min']:
            print(f"   💰 Salary range: ${results['salary_range']['min']:,} - ${results['salary_range']['max']:,}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def test_llm_search_queries():
    """Test different LLM search queries."""
    print("\n3️⃣ Testing LLM Search Queries:")
    
    test_queries = [
        "LLM Engineer",
        "Machine Learning Engineer AI",
        "GPT Engineer",
        "Transformer Engineer",
        "AI Engineer"
    ]
    
    scraper = create_llm_engineer_scraper()
    
    for query in test_queries[:2]:  # Test first 2 to save time
        print(f"\n   🔍 Testing query: '{query}'")
        try:
            result = await scraper.search_houston_jobs(query, max_pages=1)
            job_count = len(result.jobs) if result.jobs else 0
            print(f"      ✅ Found {job_count} jobs")
            
            if result.jobs:
                # Show top result
                top_job = result.jobs[0]
                print(f"      🏆 Top result: {top_job.title} at {top_job.company}")
                print(f"         Quality: {top_job.quality_score:.2f}")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")


def show_llm_scraper_features():
    """Show what makes the LLM scraper special."""
    print("\n🎯 LLM Engineer Scraper Features:")
    print("=" * 40)
    
    features = [
        "🤖 Optimized for AI/ML roles with 40+ LLM-specific keywords",
        "🎯 Filters out sales/spam jobs automatically", 
        "💰 Salary-aware filtering (80k-500k range)",
        "⭐ High quality score requirements (0.65-0.8)",
        "🔍 Multiple search strategies (LLM, AI Engineer, MLOps, etc.)",
        "🏢 Prefers companies known for AI work",
        "📊 Detailed technology breakdown in results",
        "🎚️ Strict mode for senior-level positions",
        "🔄 Duplicate detection across searches",
        "📈 Comprehensive result analytics"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🚀 Usage Examples:")
    print(f"   # General LLM jobs")
    print(f"   scraper = create_llm_engineer_scraper()")
    print(f"   results = await scraper.search_llm_jobs()")
    print(f"   ")
    print(f"   # Senior-level only (strict filtering)")
    print(f"   scraper = create_senior_llm_scraper()")
    print(f"   results = await scraper.search_llm_jobs(seniority_level='senior')")
    print(f"   ")
    print(f"   # Junior/mid-level (more inclusive)")
    print(f"   scraper = create_junior_llm_scraper()")
    print(f"   results = await scraper.search_llm_jobs()")


async def main():
    """Run all LLM scraper tests."""
    print("🤖 LLM Engineer Scraper Test Suite")
    print("=" * 50)
    print("Testing the specialized LLM Engineer job scraper")
    print("with AI/ML optimized filtering and search queries.")
    
    try:
        await test_llm_scraper_basic()
        await test_senior_llm_scraper()
        await test_llm_search_queries()
        show_llm_scraper_features()
        
        print(f"\n🎉 LLM Scraper tests completed!")
        print(f"🔍 To use in your pipeline:")
        print(f"   from src.scrapers.llm_engineer_scraper import create_llm_engineer_scraper")
        print(f"   scraper = create_llm_engineer_scraper()")
        print(f"   results = await scraper.search_llm_jobs(max_pages=3)")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
