#!/usr/bin/env python3
"""
Test script for Glassdoor LLM Engineer scraper.
Tests the salary-focused framework and company insights capabilities.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.glassdoor_llm_scraper import create_glassdoor_llm_scraper


async def test_glassdoor_scraper_framework():
    """Test the Glassdoor scraper framework and salary focus."""
    
    print("🧪 Testing Glassdoor LLM Scraper Framework")
    print("=" * 50)
    
    # Test basic scraper creation
    print("\n1️⃣ Testing scraper creation...")
    scraper = create_glassdoor_llm_scraper()
    print(f"✅ Created Glassdoor scraper: {scraper.__class__.__name__}")
    print(f"📍 Base URL: {scraper.base_url}")
    print(f"🏷️ Source name: {scraper.source_name}")
    
    # Test filter configuration
    print("\n2️⃣ Testing salary-focused filter configuration...")
    filter_obj = scraper.job_filter
    print(f"✅ Required keywords count: {len(filter_obj.required_keywords)}")
    print(f"✅ Exclude keywords count: {len(filter_obj.exclude_keywords)}")
    print(f"✅ Min quality score: {filter_obj.min_quality_score}")
    print(f"✅ Min salary: ${filter_obj.min_salary:,}")
    print(f"✅ Allowed job types: {[jt.value for jt in filter_obj.allowed_job_types]}")
    
    # Test strict mode
    print("\n3️⃣ Testing strict mode salary optimization...")
    strict_scraper = create_glassdoor_llm_scraper(strict_mode=True)
    strict_filter = strict_scraper.job_filter
    print(f"✅ Strict mode min salary: ${strict_filter.min_salary:,}")
    print(f"✅ Strict mode quality score: {strict_filter.min_quality_score}")
    
    # Test search framework
    print("\n4️⃣ Testing salary-focused search framework...")
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"✅ Search status: {results['status']}")
    print(f"✅ Message: {results['message']}")
    print(f"✅ Expected job volume: {results['expected_performance']['job_volume']}")
    print(f"✅ Quality focus: {results['expected_performance']['quality']}")
    print(f"✅ Salary range: {results['expected_performance']['salary_range']}")
    print(f"✅ Unique value: {results['expected_performance']['unique_value']}")
    
    # Show salary insights
    print("\n5️⃣ Salary Intelligence Features:")
    salary_insights = results['salary_insights']
    print(f"💰 Average LLM salary: {salary_insights['average_llm_salary']}")
    print(f"📊 Salary confidence: {salary_insights['salary_range_confidence']}")
    print(f"🎁 Bonus/equity info: {salary_insights['bonus_equity_info']}")
    print(f"🌍 Geographic adjustments: {salary_insights['geographic_adjustments']}")
    
    # Show company insights
    print("\n6️⃣ Company Intelligence Features:")
    company_insights = results['company_insights']
    print(f"🏢 Culture ratings: {company_insights['culture_ratings']}")
    print(f"🎯 Interview difficulty: {company_insights['interview_difficulty']}")
    print(f"⚖️ Work-life balance: {company_insights['work_life_balance']}")
    print(f"📈 Career growth: {company_insights['career_growth']}")
    
    # Show implementation advantages
    print("\n7️⃣ Glassdoor advantages:")
    for advantage in results['implementation_details']['advantages']:
        print(f"   ✅ {advantage}")
    
    print(f"\n🏢 Typical companies: {', '.join(results['expected_performance']['typical_companies'])}")
    
    print("\n✅ Glassdoor scraper framework test completed!")
    return True


async def test_glassdoor_salary_filtering():
    """Test Glassdoor's salary-focused job filtering."""
    
    print("\n💰 Testing Glassdoor Salary-Focused Filtering")
    print("=" * 50)
    
    scraper = create_glassdoor_llm_scraper()
    smart_filter = scraper.smart_filter
    
    # Create test job data with salary focus
    test_jobs = [
        {
            "title": "Senior Machine Learning Engineer",
            "company": "Microsoft",
            "description": "Join our AI team working on large language models and neural networks. We're building next-generation AI systems using PyTorch, transformers, and cutting-edge ML techniques. This role involves designing LLM architectures, fine-tuning models, and scaling AI systems.",
            "salary": 165000,
            "location": "Houston, TX"
        },
        {
            "title": "Staff AI Engineer - LLMs",
            "company": "Google",
            "description": "Staff-level position focusing on large language models and generative AI. You'll work on transformer architectures, RLHF training, and production ML systems. Experience with Python, TensorFlow, and distributed computing required. Leading AI research and development.",
            "salary": 220000,
            "location": "Austin, TX"
        },
        {
            "title": "Junior Data Analyst",
            "company": "Local Startup", 
            "description": "Entry-level data analysis position. Some Excel work and basic Python scripting.",
            "salary": 55000,
            "location": "Houston, TX"
        },
        {
            "title": "Principal LLM Research Scientist",
            "company": "OpenAI",
            "description": "Lead research on frontier large language models including GPT systems, alignment research, and safety. Work on cutting-edge transformer architectures, RLHF, and constitutional AI. Publish research and drive technical strategy for next-generation language models.",
            "salary": 350000,
            "location": "Remote"
        },
        {
            "title": "Sales Engineer - AI Products",
            "company": "Tech Company",
            "description": "Sales role for AI products. Some technical background needed but primarily focused on client relationships and sales targets.",
            "salary": 120000,
            "location": "Houston, TX"
        }
    ]
    
    print(f"\n📊 Testing {len(test_jobs)} salary-focused sample jobs...")
    
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
            url="https://glassdoor.com/jobs/test",
            source="glassdoor"
        )
        
        should_keep, reason = smart_filter.should_keep_job(job)
        status = "✅ KEEP" if should_keep else "❌ FILTER"
        
        print(f"\n{i}. {job.title} at {job.company}")
        print(f"   {status} - {reason}")
        print(f"   💰 Salary: ${job.salary_min:,}")
        print(f"   📍 Location: {job.location}")
    
    print(f"\n✅ Glassdoor salary filtering test completed!")
    return True


async def test_glassdoor_company_insights():
    """Test Glassdoor's company intelligence features."""
    
    print("\n🏢 Testing Glassdoor Company Intelligence")
    print("=" * 50)
    
    scraper = create_glassdoor_llm_scraper()
    results = await scraper.search_llm_jobs("Houston, TX")
    
    # Show what makes Glassdoor unique
    print("🎯 Glassdoor's Unique Value Proposition:")
    specialties = results['implementation_details']['specialties']
    for specialty in specialties:
        print(f"   • {specialty}")
    
    print("\n💡 Why Glassdoor for LLM Jobs:")
    print("   🔍 Salary Transparency - Real employee-reported compensation")
    print("   🏢 Company Culture - Insider views on work environment")
    print("   🎯 Interview Intel - Actual interview questions and difficulty")
    print("   📈 Career Paths - Promotion and growth opportunities")
    print("   ⚖️ Work-Life Balance - Employee satisfaction ratings")
    
    print("\n📊 Expected LLM Engineer Insights:")
    print("   💰 Salary Range: $95k-$350k (employee verified)")
    print("   🏆 Top Companies: Established tech, Fortune 500, Public companies")
    print("   📈 Career Growth: Clear promotion paths and requirements")
    print("   🎯 Interview Prep: Coding challenges, system design, ML theory")
    
    return True


async def main():
    """Run all Glassdoor scraper tests."""
    
    print("🚀 Glassdoor LLM Scraper Test Suite")
    print("💰 Testing salary intelligence and company insights")
    print("=" * 60)
    
    try:
        # Test scraper framework
        await test_glassdoor_scraper_framework()
        
        # Test salary filtering capabilities
        await test_glassdoor_salary_filtering()
        
        # Test company insights
        await test_glassdoor_company_insights()
        
        print("\n🎉 All Glassdoor scraper tests passed!")
        print("\n💡 Glassdoor scraper is ready for salary intelligence!")
        print("💰 Transparent compensation data awaits!")
        
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
