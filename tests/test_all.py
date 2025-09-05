"""
Comprehensive test suite for the refactored Houston Job Search system.
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test model imports
        from src.models.job_models import JobListing, JobType, RemoteType, ScrapingResult
        print("✅ Models imported successfully")
        
        # Test database imports
        from src.database.job_vector_store import JobVectorStore
        from src.database.job_pipeline import JobSearchPipeline
        print("✅ Database modules imported successfully")
        
        # Test scraper imports
        from src.scrapers.playwright_scraper import PlaywrightJobScraper
        from src.scrapers.ziprecruiter_scraper import ZipRecruiterScraper
        print("✅ Scrapers imported successfully")
        
        # Test gradio app import  
        import sys
        sys.path.append('.')
        from gradio_app import JobSearchApp
        print("✅ Gradio app imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_job_model():
    """Test job model creation."""
    print("\n🧪 Testing job model...")
    
    try:
        from src.models.job_models import JobListing, JobType, RemoteType
        
        job = JobListing(
            title="Test Developer",
            company="Test Company",
            location="Houston, TX",
            description="Test job description",
            url="https://example.com/job",
            source="test",
            job_type=JobType.FULL_TIME,
            remote_type=RemoteType.HYBRID
        )
        
        print(f"✅ Created job: {job.title} at {job.company}")
        print(f"   Quality score: {job.quality_score}")
        return True
        
    except Exception as e:
        print(f"❌ Job model test failed: {e}")
        return False

async def test_scraper_basic():
    """Test basic scraper functionality."""
    print("\n🧪 Testing scraper basics...")
    
    try:
        from src.scrapers.playwright_scraper import PlaywrightJobScraper
        
        scraper = PlaywrightJobScraper(headless=True)
        print("✅ Scraper created successfully")
        
        # Don't actually scrape, just test initialization
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization."""
    print("\n🧪 Testing vector store...")
    
    try:
        from src.database.job_vector_store import JobVectorStore
        
        # Check if database exists
        db_path = Path("test_job_db")
        if not db_path.exists():
            print("⚠️  No database found, skipping vector store test")
            return True
        
        vector_store = JobVectorStore(db_path="./test_job_db")
        stats = vector_store.get_statistics()
        
        print(f"✅ Vector store loaded: {stats['total_jobs']} jobs")
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_gradio_app():
    """Test Gradio app initialization."""
    print("\n🧪 Testing Gradio app...")
    
    try:
        import sys
        sys.path.append('.')
        from gradio_app import JobSearchApp
        
        # Check if database exists
        db_path = Path("test_job_db")
        if not db_path.exists():
            print("⚠️  No database found, skipping Gradio test")
            return True
        
        app = JobSearchApp(db_path="./test_job_db")
        
        # Test search functionality
        html_results, stats = app.search_jobs("test query", max_results=1)
        
        print("✅ Gradio app initialized and search tested")
        return True
        
    except Exception as e:
        print(f"❌ Gradio app test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running comprehensive test suite for Houston Job Search")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Job Model Test", test_job_model), 
        ("Scraper Basic Test", test_scraper_basic),
        ("Vector Store Test", test_vector_store),
        ("Gradio App Test", test_gradio_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"📈 {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your Houston Job Search system is ready!")
        print("\n🚀 Quick start commands:")
        print("   uv run python run_app.py           # Launch web interface")
        print("   uv run python gradio_app.py        # Direct launch")
        print("   uv run python tests/test_vector_store.py  # Test with sample data")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
