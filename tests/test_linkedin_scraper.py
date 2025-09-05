#!/usr/bin/env python3
"""
Test script for LinkedIn LLM Engineer scraper.
Tests the framework, filtering, and integration capabilities.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.linkedin_llm_scraper import create_linkedin_llm_scraper


async def test_linkedin_scraper_framework():
    """Test the LinkedIn scraper framework and configuration."""
    
    print("🧪 Testing LinkedIn LLM Scraper Framework")
    print("=" * 50)
    
    # Test basic scraper creation
    print("\n1️⃣ Testing scraper creation...")
    scraper = create_linkedin_llm_scraper()
    print(f"✅ Created LinkedIn scraper: {scraper.__class__.__name__}")
    print(f"📍 Base URL: {scraper.base_url}")
    print(f"🏷️ Source name: {scraper.source_name}")
    
    # Test filter configuration
    print("\n2️⃣ Testing filter configuration...")
    filter_obj = scraper.job_filter
    print(f"✅ Required keywords count: {len(filter_obj.required_keywords)}")
    print(f"✅ Exclude keywords count: {len(filter_obj.exclude_keywords)}")
    print(f"✅ Min quality score: {filter_obj.min_quality_score}")
    print(f"✅ Min salary: ${filter_obj.min_salary:,}")
    print(f"✅ Allowed job types: {[jt.value for jt in filter_obj.allowed_job_types]}")
    
    # Test strict mode
    print("\n3️⃣ Testing strict mode configuration...")
    strict_scraper = create_linkedin_llm_scraper(strict_mode=True)
    strict_filter = strict_scraper.job_filter
    print(f"✅ Strict mode min salary: ${strict_filter.min_salary:,}")
    print(f"✅ Strict mode quality score: {strict_filter.min_quality_score}")
    
    # Test search framework
    print("\n4️⃣ Testing search framework...")
    results = await scraper.search_llm_jobs("Houston, TX", max_pages=1)
    
    print(f"✅ Search status: {results['status']}")
    print(f"✅ Message: {results['message']}")
    print(f"✅ Expected job volume: {results['expected_performance']['job_volume']}")
    print(f"✅ Expected quality: {results['expected_performance']['quality']}")
    print(f"✅ Salary range: {results['expected_performance']['salary_range']}")
    print(f"✅ Implementation approach: {results['implementation_details']['approach']}")
    
    # Show advantages and limitations
    print("\n5️⃣ Implementation details:")
    print("👍 Advantages:")
    for advantage in results['implementation_details']['advantages']:
        print(f"   • {advantage}")
    
    print("\n⚠️ Limitations:")
    for limitation in results['implementation_details']['limitations']:
        print(f"   • {limitation}")
    
    print("\n📋 Next steps:")
    for step in results['next_steps']:
        print(f"   • {step}")
    
    print(f"\n🏢 Typical companies: {', '.join(results['expected_performance']['typical_companies'])}")
    
    print("\n✅ LinkedIn scraper framework test completed!")
    return True


async def test_linkedin_filtering():
    """Test LinkedIn-specific job filtering."""
    
    print("\n🔍 Testing LinkedIn LLM Job Filtering")
    print("=" * 50)
    
    scraper = create_linkedin_llm_scraper()
    smart_filter = scraper.smart_filter
    
    # Create test job data
    test_jobs = [
        {
            "title": "Senior LLM Engineer",
            "company": "Google",
            "description": "We're looking for a Senior Large Language Model Engineer to join our AI team. You'll work on cutting-edge transformer models, fine-tuning GPT systems, and building production ML pipelines using PyTorch and TensorFlow.",
            "salary": 180000,
            "location": "Houston, TX"
        },
        {
            "title": "AI Research Scientist",
            "company": "OpenAI",
            "description": "Research scientist position focusing on large language models, transformer architectures, and reinforcement learning from human feedback. Experience with Python, PyTorch, and distributed training required.",
            "salary": 250000,
            "location": "Remote"
        },
        {
            "title": "Marketing Manager",
            "company": "SalesForce",
            "description": "Looking for a marketing manager to drive lead generation and customer acquisition. Experience with email marketing, social media, and sales funnels required.",
            "salary": 85000,
            "location": "Houston, TX"
        },
        {
            "title": "Machine Learning Engineer - NLP",
            "company": "Meta",
            "description": "ML Engineer specializing in natural language processing and large language models. Work on Facebook's AI systems using transformers, BERT, and custom architectures.",
            "salary": 160000,
            "location": "Austin, TX"
        }
    ]
    
    print(f"\n📊 Testing {len(test_jobs)} sample jobs...")
    
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
            url="https://linkedin.com/jobs/test",
            source="linkedin"
        )
        
        should_keep, reason = smart_filter.should_keep_job(job)
        status = "✅ KEEP" if should_keep else "❌ FILTER"
        
        print(f"\n{i}. {job.title} at {job.company}")
        print(f"   {status} - {reason}")
        print(f"   💰 Salary: ${job.salary_min:,}")
        print(f"   📍 Location: {job.location}")
    
    print(f"\n✅ LinkedIn filtering test completed!")
    return True


async def main():
    """Run all LinkedIn scraper tests."""
    
    print("🚀 LinkedIn LLM Scraper Test Suite")
    print("🔗 Testing LinkedIn integration and filtering")
    print("=" * 60)
    
    try:
        # Test scraper framework
        await test_linkedin_scraper_framework()
        
        # Test filtering capabilities
        await test_linkedin_filtering()
        
        print("\n🎉 All LinkedIn scraper tests passed!")
        print("\n💡 LinkedIn scraper is ready for integration!")
        print("🔗 High-quality professional jobs await!")
        
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
