"""Test script for the job vector store."""
import os
import asyncio
from datetime import datetime

from job_vector_store import JobVectorStore
from job_models import JobListing, JobType, RemoteType
from ziprecruiter_scraper import ZipRecruiterScraper


def create_sample_jobs() -> list[JobListing]:
    """Create some sample jobs for testing."""
    return [
        JobListing(
            title="Senior Python Developer",
            company="TechCorp Houston",
            location="Houston, TX",
            description="We are looking for a Senior Python Developer to join our team. You will work on backend systems using Python, Django, and PostgreSQL. Experience with cloud platforms like AWS is a plus.",
            url="https://example.com/job1",
            source="test",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.HYBRID,
            salary_min=90000,
            salary_max=120000,
            skills=["Python", "Django", "PostgreSQL", "AWS"],
            experience_level="Senior",
            education="Bachelor's degree"
        ),
        
        JobListing(
            title="Data Scientist - Machine Learning",
            company="Houston Analytics Inc",
            location="Houston, TX",
            description="Join our data science team to build machine learning models for the energy industry. Experience with Python, scikit-learn, and TensorFlow required.",
            url="https://example.com/job2",
            source="test",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.REMOTE,
            salary_min=100000,
            salary_max=140000,
            skills=["Python", "Machine Learning", "TensorFlow", "scikit-learn", "Data Science"],
            experience_level="Mid-level",
            education="Master's degree"
        ),
        
        JobListing(
            title="Frontend React Developer",
            company="StartupXYZ",
            location="Houston, TX",
            description="Build modern web applications using React, TypeScript, and Next.js. We're looking for someone passionate about user experience and clean code.",
            url="https://example.com/job3",
            source="test",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.ONSITE,
            salary_min=75000,
            salary_max=95000,
            skills=["React", "TypeScript", "Next.js", "JavaScript", "CSS"],
            experience_level="Mid-level",
            education="Bachelor's degree"
        )
    ]


async def test_with_real_jobs():
    """Test with real scraped jobs."""
    print("🔍 Testing with real scraped jobs")
    print("=" * 40)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize vector store
        vector_store = JobVectorStore(db_path="./test_job_db")
        
        # Scrape some real jobs
        async with ZipRecruiterScraper(headless=True) as scraper:
            print("🔄 Scraping a few real jobs...")
            result = await scraper.search_houston_jobs(
                query="python",
                max_pages=1
            )
            
            if result.jobs:
                print(f"📦 Adding {len(result.jobs)} real jobs to vector store...")
                batch_results = vector_store.add_jobs_batch(result.jobs)
                print(f"✅ Added {batch_results['success']} jobs successfully")
                
                # Test search
                print(f"\n🔍 Testing search...")
                search_results = vector_store.search_jobs("python developer", n_results=3)
                
                if search_results:
                    print(f"📋 Search results:")
                    for result in search_results:
                        print(f"  {result['rank']}. {result['title']} at {result['company']}")
                        print(f"     Similarity: {result['similarity_score']:.3f}")
                        print(f"     Location: {result['location']}")
                        print()
                else:
                    print("❌ No search results found")
            else:
                print("⚠️  No jobs scraped, testing with sample data instead...")
                await test_with_sample_data()
    
    except Exception as e:
        print(f"❌ Error in real job test: {e}")
        print("⚠️  Falling back to sample data test...")
        await test_with_sample_data()


async def test_with_sample_data():
    """Test with sample data."""
    print("🧪 Testing with sample data")
    print("=" * 30)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        print("   You can get one at: https://platform.openai.com/api-keys")
        return
    
    try:
        # Initialize vector store
        vector_store = JobVectorStore(db_path="./test_job_db")
        
        # Create sample jobs
        sample_jobs = create_sample_jobs()
        
        # Add jobs to vector store
        print(f"📦 Adding {len(sample_jobs)} sample jobs...")
        batch_results = vector_store.add_jobs_batch(sample_jobs)
        print(f"✅ Added {batch_results['success']} jobs successfully")
        
        # Test different searches
        test_queries = [
            "python developer",
            "machine learning",
            "react frontend",
            "remote work",
            "senior engineer"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            results = vector_store.search_jobs(query, n_results=2)
            
            if results:
                for result in results:
                    print(f"  • {result['title']} at {result['company']}")
                    print(f"    Similarity: {result['similarity_score']:.3f}")
            else:
                print("  No results found")
        
        # Test with filters
        print(f"\n🔍 Testing filtered search (remote jobs)...")
        remote_results = vector_store.search_jobs(
            "python", 
            n_results=5, 
            remote_filter="remote"
        )
        
        if remote_results:
            for result in remote_results:
                print(f"  • {result['title']} - {result['remote_type']}")
        
        # Show statistics
        print(f"\n📊 Database Statistics:")
        stats = vector_store.get_statistics()
        print(f"Total jobs: {stats['total_jobs']}")
        print(f"Sources: {stats['sources']}")
        print(f"Job types: {stats['job_types']}")
        print(f"Remote types: {stats['remote_types']}")
        
    except Exception as e:
        print(f"❌ Error in sample data test: {e}")


async def main():
    """Run the appropriate test."""
    print("🧪 Job Vector Store Test")
    print("=" * 30)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found!")
        print("Please set your API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("You can get an API key at: https://platform.openai.com/api-keys")
        return
    
    # Ask user which test to run
    print("Choose test type:")
    print("1. Sample data test (fast, no scraping)")
    print("2. Real scraped jobs test (slower, requires scraping)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        await test_with_sample_data()
    elif choice == "2":
        await test_with_real_jobs()
    else:
        print("Running sample data test by default...")
        await test_with_sample_data()


if __name__ == "__main__":
    asyncio.run(main())
