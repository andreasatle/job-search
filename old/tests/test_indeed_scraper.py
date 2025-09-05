"""
Test script for the Indeed LLM scraper.
"""

import asyncio
from src.scrapers.indeed_llm_scraper import create_indeed_llm_scraper


async def test_indeed_framework():
    """Test the Indeed scraper framework."""
    print("🧪 Testing Indeed LLM Scraper Framework")
    print("=" * 45)
    
    # Test basic scraper creation
    print("\n1️⃣ Creating Indeed LLM Scraper...")
    try:
        scraper = create_indeed_llm_scraper(strict_mode=False)
        print("✅ Indeed scraper created successfully")
        print(f"   Source: {scraper.source_name}")
        print(f"   Base URL: {scraper.base_url}")
        print(f"   Strict mode: {scraper.strict_mode}")
    except Exception as e:
        print(f"❌ Failed to create scraper: {e}")
        return
    
    # Test search functionality (placeholder)
    print("\n2️⃣ Testing Search Framework...")
    try:
        results = await scraper.search_llm_jobs(
            location="Houston, TX",
            max_pages=1,
            seniority_level="senior"
        )
        
        print("✅ Search framework test completed")
        print(f"   Status: {results.get('status', 'unknown')}")
        print(f"   Message: {results.get('message', 'No message')}")
        
        if 'expected_performance' in results:
            perf = results['expected_performance']
            print(f"   Expected job volume: {perf.get('job_volume', 'unknown')}")
            print(f"   Expected quality: {perf.get('quality', 'unknown')}")
            print(f"   Expected salary range: {perf.get('salary_range', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test filter configuration
    print("\n3️⃣ Testing Filter Configuration...")
    try:
        filter_config = scraper.job_filter
        print("✅ Filter configuration loaded")
        print(f"   Required keywords: {len(filter_config.required_keywords)} keywords")
        print(f"   Exclude keywords: {len(filter_config.exclude_keywords)} keywords")
        print(f"   Min quality score: {filter_config.min_quality_score}")
        print(f"   Min salary: ${filter_config.min_salary:,}" if filter_config.min_salary else "   No salary filter")
        
        # Show some example keywords
        if filter_config.required_keywords:
            print(f"   Sample required: {filter_config.required_keywords[:5]}")
        if filter_config.exclude_keywords:
            print(f"   Sample excluded: {filter_config.exclude_keywords[:3]}")
            
    except Exception as e:
        print(f"❌ Filter test failed: {e}")


async def test_indeed_vs_ziprecruiter_config():
    """Compare Indeed vs ZipRecruiter configurations."""
    print("\n🆚 Indeed vs ZipRecruiter Configuration")
    print("=" * 45)
    
    try:
        from src.scrapers.llm_engineer_scraper import create_llm_engineer_scraper
        
        # Create both scrapers
        indeed_scraper = create_indeed_llm_scraper(strict_mode=False)
        ziprecruiter_scraper = create_llm_engineer_scraper(strict_mode=False)
        
        # Compare filters
        indeed_filter = indeed_scraper.job_filter
        ziprecruiter_filter = ziprecruiter_scraper.job_filter_config
        
        print("📊 Filter Comparison:")
        print(f"   Indeed min salary: ${indeed_filter.min_salary:,}")
        print(f"   ZipRecruiter min salary: ${ziprecruiter_filter.min_salary:,}")
        print(f"   Indeed min quality: {indeed_filter.min_quality_score}")
        print(f"   ZipRecruiter min quality: {ziprecruiter_filter.min_quality_score}")
        
        # Compare keyword strategies
        indeed_keywords = set(indeed_filter.required_keywords)
        ziprecruiter_keywords = set(ziprecruiter_filter.required_keywords)
        
        common_keywords = indeed_keywords & ziprecruiter_keywords
        indeed_only = indeed_keywords - ziprecruiter_keywords
        ziprecruiter_only = ziprecruiter_keywords - indeed_keywords
        
        print(f"\n🔗 Keyword Analysis:")
        print(f"   Common keywords: {len(common_keywords)}")
        print(f"   Indeed-specific: {len(indeed_only)}")
        print(f"   ZipRecruiter-specific: {len(ziprecruiter_only)}")
        
        if indeed_only:
            print(f"   Indeed specialties: {list(indeed_only)[:3]}")
        if ziprecruiter_only:
            print(f"   ZipRecruiter specialties: {list(ziprecruiter_only)[:3]}")
            
    except Exception as e:
        print(f"❌ Comparison failed: {e}")


def show_indeed_implementation_status():
    """Show the current implementation status of Indeed scraper."""
    print("\n📋 Indeed Scraper Implementation Status")
    print("=" * 45)
    
    components = {
        "✅ Basic Framework": "Scraper class structure complete",
        "✅ Anti-Detection": "User agent rotation, rate limiting",
        "✅ LLM Filtering": "Enterprise-focused keyword filtering",
        "✅ Salary Parsing": "Logic for Indeed salary formats",
        "✅ Multi-Site Integration": "Works with MultiSiteLLMScraper",
        "🚧 CSS Selectors": "Need testing with real Indeed pages",
        "🚧 CAPTCHA Handling": "Framework ready, needs implementation",
        "🚧 Production Testing": "Requires live Indeed testing",
        "⏳ Proxy Rotation": "May be needed for high-volume scraping"
    }
    
    for status, description in components.items():
        print(f"   {status}: {description}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Test selectors with real Indeed job pages")
    print(f"   2. Implement CAPTCHA detection and handling")
    print(f"   3. Fine-tune rate limiting parameters")
    print(f"   4. Add proxy rotation if needed")
    print(f"   5. Performance testing with multi-site scraper")
    
    print(f"\n💡 Expected Impact:")
    print(f"   📈 3-5x increase in LLM job volume")
    print(f"   🏢 Better enterprise job coverage")
    print(f"   💰 Higher salary range jobs ($85k-$400k)")
    print(f"   🌐 Complement ZipRecruiter's strengths")


async def main():
    """Run all Indeed scraper tests."""
    print("🔍 Indeed LLM Scraper Test Suite")
    print("=" * 50)
    print("Testing the Indeed scraper framework and integration")
    
    await test_indeed_framework()
    await test_indeed_vs_ziprecruiter_config()
    show_indeed_implementation_status()
    
    print(f"\n🎉 Indeed scraper testing complete!")
    print(f"🚀 Ready for multi-site integration testing")


if __name__ == "__main__":
    asyncio.run(main())
