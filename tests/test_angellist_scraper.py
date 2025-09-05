#!/usr/bin/env python3
"""
Test script for AngelList LLM Engineer scraper.
Tests the startup-focused framework and equity intelligence capabilities.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.angellist_llm_scraper import create_angellist_llm_scraper


async def test_angellist_scraper_framework():
    """Test the AngelList scraper framework and startup focus."""
    
    print("🧪 Testing AngelList LLM Scraper Framework")
    print("=" * 50)
    
    # Test basic scraper creation
    print("\n1️⃣ Testing scraper creation...")
    scraper = create_angellist_llm_scraper()
    print(f"✅ Created AngelList scraper: {scraper.__class__.__name__}")
    print(f"📍 Base URL: {scraper.base_url}")
    print(f"🏷️ Source name: {scraper.source_name}")
    
    # Test filter configuration
    print("\n2️⃣ Testing startup-focused filter configuration...")
    filter_obj = scraper.job_filter
    print(f"✅ Required keywords count: {len(filter_obj.required_keywords)}")
    print(f"✅ Exclude keywords count: {len(filter_obj.exclude_keywords)}")
    print(f"✅ Min quality score: {filter_obj.min_quality_score}")
    print(f"✅ Min salary: ${filter_obj.min_salary:,}")
    print(f"✅ Allowed job types: {[jt.value for jt in filter_obj.allowed_job_types]}")
    
    # Test strict mode
    print("\n3️⃣ Testing strict mode startup optimization...")
    strict_scraper = create_angellist_llm_scraper(strict_mode=True)
    strict_filter = strict_scraper.job_filter
    print(f"✅ Strict mode min salary: ${strict_filter.min_salary:,}")
    print(f"✅ Strict mode quality score: {strict_filter.min_quality_score}")
    
    # Test search framework
    print("\n4️⃣ Testing startup-focused search framework...")
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"✅ Search status: {results['status']}")
    print(f"✅ Message: {results['message']}")
    print(f"✅ Expected job volume: {results['expected_performance']['job_volume']}")
    print(f"✅ Quality focus: {results['expected_performance']['quality']}")
    print(f"✅ Salary range: {results['expected_performance']['salary_range']}")
    print(f"✅ Unique value: {results['expected_performance']['unique_value']}")
    
    # Show startup insights
    print("\n5️⃣ Startup Intelligence Features:")
    startup_insights = results['startup_insights']
    print(f"💼 Funding stages: {', '.join(startup_insights['funding_stages'])}")
    print(f"🎯 Equity ranges: {startup_insights['equity_ranges']}")
    print(f"📈 Growth potential: {startup_insights['growth_potential']}")
    print(f"⚡ Risk profile: {startup_insights['risk_profile']}")
    
    # Show equity intelligence
    print("\n6️⃣ Equity Intelligence Features:")
    equity_intel = results['equity_intelligence']
    print(f"💰 Typical equity: {equity_intel['typical_equity']}")
    print(f"⏰ Vesting schedule: {equity_intel['vesting_schedule']}")
    print(f"🎯 Exercise options: {equity_intel['exercise_options']}")
    print(f"🚀 Valuation growth: {equity_intel['valuation_growth']}")
    
    # Show startup advantages
    print("\n7️⃣ Startup advantages:")
    for advantage in results['implementation_details']['advantages']:
        print(f"   ✅ {advantage}")
    
    print(f"\n🏢 Typical companies: {', '.join(results['expected_performance']['typical_companies'])}")
    
    print("\n✅ AngelList scraper framework test completed!")
    return True


async def test_angellist_startup_filtering():
    """Test AngelList's startup-focused job filtering."""
    
    print("\n🚀 Testing AngelList Startup-Focused Filtering")
    print("=" * 50)
    
    scraper = create_angellist_llm_scraper()
    smart_filter = scraper.smart_filter
    
    # Create test job data with startup focus
    test_jobs = [
        {
            "title": "Founding AI Engineer",
            "company": "SteealthAI (YC S23)",
            "description": "Join our founding team as the first AI engineer at our stealth-mode startup. We're building next-generation LLMs for healthcare and need someone to own the entire ML pipeline from research to production. Equity package includes 2% ownership with ground-floor opportunity. Series A funding secured.",
            "salary": 140000,
            "location": "Austin, TX"
        },
        {
            "title": "Senior LLM Engineer",
            "company": "RoboticsAI",
            "description": "Series B startup building autonomous robots powered by large language models. You'll work on multimodal AI systems, transformers for robotics, and reinforcement learning. Significant equity upside as we scale from 50 to 500 engineers. Join our mission to revolutionize manufacturing.",
            "salary": 160000,
            "location": "Houston, TX"
        },
        {
            "title": "Corporate Software Engineer",
            "company": "Big Enterprise Corp",
            "description": "Traditional enterprise software role with established processes.",
            "salary": 130000,
            "location": "Houston, TX"
        },
        {
            "title": "Head of AI",
            "company": "FinTechStartup",
            "description": "Lead our AI team of 5 engineers building large language models for financial analysis. Pre-series A startup with amazing investors (Andreessen Horowitz, Sequoia). Founding team equity package with 1.5% ownership. Ground floor opportunity to build the future of AI-powered finance.",
            "salary": 180000,
            "location": "Remote"
        },
        {
            "title": "Contract Data Engineer",
            "company": "ConsultingFirm",
            "description": "Short-term contract for data pipeline work. Basic Python and SQL.",
            "salary": 95000,
            "location": "Houston, TX"
        }
    ]
    
    print(f"\n📊 Testing {len(test_jobs)} startup-focused sample jobs...")
    
    for i, job_data in enumerate(test_jobs, 1):
        # Create a mock job listing
        from src.models.job_models import JobListing, JobType, RemoteType
        
        job = JobListing(
            title=job_data["title"],
            company=job_data["company"],
            location=job_data["location"],
            description=job_data["description"],
            salary_min=job_data["salary"],
            salary_max=job_data["salary"],
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.HYBRID,
            url="https://wellfound.com/jobs/test",
            source="angellist"
        )
        
        should_keep, reason = smart_filter.should_keep_job(job)
        status = "✅ KEEP" if should_keep else "❌ FILTER"
        
        print(f"\n{i}. {job.title} at {job.company}")
        print(f"   {status} - {reason}")
        print(f"   💰 Salary: ${job.salary_min:,}")
        print(f"   📍 Location: {job.location}")
    
    print(f"\n✅ AngelList startup filtering test completed!")
    return True


async def test_angellist_equity_insights():
    """Test AngelList's equity and startup intelligence features."""
    
    print("\n💎 Testing AngelList Equity Intelligence")
    print("=" * 50)
    
    scraper = create_angellist_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX")
    
    # Show what makes AngelList unique
    print("🎯 AngelList's Unique Value Proposition:")
    specialties = results['implementation_details']['specialties']
    for specialty in specialties:
        print(f"   • {specialty}")
    
    print("\n💡 Why AngelList for LLM Jobs:")
    print("   🚀 Startup Opportunities - Ground-floor AI company positions")
    print("   💎 Equity Upside - 0.1-5% ownership in high-growth companies")
    print("   🏗️ Founding Roles - Build core AI systems from scratch")
    print("   📈 Growth Potential - 10x-100x returns for successful startups")
    print("   🎯 Innovation Focus - Cutting-edge AI research and development")
    
    print("\n📊 Expected LLM Engineer Opportunities:")
    print("   💰 Salary + Equity: $85k-$200k + 0.5-2% ownership")
    print("   🏆 Companies: AI startups, Series A-C, YC companies")
    print("   📈 Growth: Leadership opportunities as company scales")
    print("   🔬 Impact: Full-stack AI/ML ownership and innovation")
    
    print("\n💎 Equity Intelligence:")
    equity_intel = results['equity_intelligence']
    for key, value in equity_intel.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n🚀 Startup Advantages:")
    advantages = results['startup_advantages']
    for key, value in advantages.items():
        print(f"   {key.title()}: {value}")
    
    return True


async def main():
    """Run all AngelList scraper tests."""
    
    print("🚀 AngelList LLM Scraper Test Suite")
    print("💎 Testing startup opportunities and equity intelligence")
    print("=" * 60)
    
    try:
        # Test scraper framework
        await test_angellist_scraper_framework()
        
        # Test startup filtering capabilities
        await test_angellist_startup_filtering()
        
        # Test equity insights
        await test_angellist_equity_insights()
        
        print("\n🎉 All AngelList scraper tests passed!")
        print("\n💡 AngelList scraper is ready for startup opportunities!")
        print("💎 Ground-floor equity positions await!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    exit(exit_code)
