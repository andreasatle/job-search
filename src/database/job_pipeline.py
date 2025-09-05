"""Complete job search pipeline: scrape -> store -> search."""
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from ..scrapers.ziprecruiter_scraper import ZipRecruiterScraper
from .job_vector_store import JobVectorStore
from ..models.job_models import JobListing

# Load environment variables from .env file
load_dotenv()


class JobSearchPipeline:
    """Complete pipeline for scraping, storing, and searching jobs."""
    
    def __init__(self, db_path: str = "./houston_jobs_db"):
        """Initialize the job search pipeline."""
        self.db_path = db_path
        self.vector_store = None
    
    def initialize_storage(self) -> bool:
        """Initialize the vector storage system."""
        try:
            if not os.getenv("OPENAI_API_KEY"):
                print("❌ OpenAI API key required. Set OPENAI_API_KEY environment variable.")
                return False
            
            self.vector_store = JobVectorStore(db_path=self.db_path)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize storage: {e}")
            return False
    
    async def scrape_and_store_jobs(self, 
                                   queries: List[str],
                                   max_pages_per_query: int = 2) -> Dict[str, Any]:
        """
        Scrape jobs for given queries and store them in vector database.
        
        Args:
            queries: List of search queries
            max_pages_per_query: Maximum pages to scrape per query
            
        Returns:
            Dictionary with results summary
        """
        if not self.vector_store:
            if not self.initialize_storage():
                return {"error": "Failed to initialize storage"}
        
        results = {
            "total_scraped": 0,
            "total_stored": 0,
            "queries_processed": 0,
            "errors": [],
            "by_query": {}
        }
        
        async with ZipRecruiterScraper(headless=True) as scraper:
            for query in queries:
                print(f"\n🔍 Processing query: '{query}'")
                
                try:
                    # Scrape jobs
                    scrape_result = await scraper.search_houston_jobs(
                        query=query,
                        max_pages=max_pages_per_query
                    )
                    
                    scraped_count = len(scrape_result.jobs)
                    results["total_scraped"] += scraped_count
                    
                    if scrape_result.jobs:
                        # Store jobs in vector database
                        print(f"📦 Storing {scraped_count} jobs in vector database...")
                        storage_result = self.vector_store.add_jobs_batch(scrape_result.jobs)
                        
                        stored_count = storage_result["success"]
                        results["total_stored"] += stored_count
                        
                        results["by_query"][query] = {
                            "scraped": scraped_count,
                            "stored": stored_count,
                            "failed": storage_result["failed"]
                        }
                        
                        print(f"✅ Query '{query}': {scraped_count} scraped, {stored_count} stored")
                    else:
                        print(f"⚠️  No jobs found for query: '{query}'")
                        results["by_query"][query] = {"scraped": 0, "stored": 0, "failed": 0}
                    
                    results["queries_processed"] += 1
                    
                    # Small delay between queries
                    await asyncio.sleep(2)
                
                except Exception as e:
                    error_msg = f"Error processing query '{query}': {e}"
                    print(f"❌ {error_msg}")
                    results["errors"].append(error_msg)
                    results["by_query"][query] = {"error": str(e)}
        
        return results
    
    def search_jobs(self, 
                   query: str,
                   n_results: int = 10,
                   **filters) -> List[Dict[str, Any]]:
        """
        Search for jobs in the vector database.
        
        Args:
            query: Search query
            n_results: Number of results to return
            **filters: Additional filters (location_filter, job_type_filter, etc.)
            
        Returns:
            List of job results
        """
        if not self.vector_store:
            if not self.initialize_storage():
                return []
        
        return self.vector_store.search_jobs(query, n_results, **filters)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.vector_store:
            if not self.initialize_storage():
                return {"error": "Storage not initialized"}
        
        return self.vector_store.get_statistics()
    
    async def run_houston_job_collection(self) -> Dict[str, Any]:
        """Run a comprehensive job collection for Houston area."""
        print("🏢 Starting Houston Job Collection Pipeline")
        print("=" * 50)
        
        # Define Houston-relevant search queries
        houston_queries = [
            "software engineer",
            "python developer", 
            "data scientist",
            "frontend developer",
            "backend developer",
            "machine learning engineer",
            "devops engineer",
            "full stack developer",
            "energy engineer",  # Houston-specific
            "oil gas engineer",  # Houston-specific
            "medical device engineer",  # Houston Medical Center
            "aerospace engineer"  # NASA JSC area
        ]
        
        print(f"📋 Processing {len(houston_queries)} Houston-focused queries...")
        
        # Scrape and store jobs
        results = await self.scrape_and_store_jobs(
            queries=houston_queries,
            max_pages_per_query=2
        )
        
        # Add statistics
        results["final_stats"] = self.get_statistics()
        results["collection_date"] = datetime.now().isoformat()
        
        print(f"\n📊 Collection Summary:")
        print(f"Total jobs scraped: {results['total_scraped']}")
        print(f"Total jobs stored: {results['total_stored']}")
        print(f"Queries processed: {results['queries_processed']}")
        print(f"Database total: {results['final_stats'].get('total_jobs', 0)}")
        
        if results["errors"]:
            print(f"Errors encountered: {len(results['errors'])}")
        
        return results


# Example usage and testing
async def demo_pipeline():
    """Demonstrate the complete pipeline."""
    print("🚀 Job Search Pipeline Demo")
    print("=" * 35)
    
    pipeline = JobSearchPipeline()
    
    # Check requirements
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    try:
        # Small test with one query
        print("🔍 Running small test...")
        test_results = await pipeline.scrape_and_store_jobs(["python developer"], max_pages_per_query=1)
        
        print(f"\n📊 Test Results:")
        print(f"Scraped: {test_results['total_scraped']}")
        print(f"Stored: {test_results['total_stored']}")
        
        if test_results['total_stored'] > 0:
            # Test search
            print(f"\n🔍 Testing search...")
            search_results = pipeline.search_jobs("python machine learning", n_results=3)
            
            if search_results:
                print(f"📋 Found {len(search_results)} relevant jobs:")
                for result in search_results[:3]:
                    print(f"  • {result['title']} at {result['company']}")
                    print(f"    Similarity: {result['similarity_score']:.3f}")
            else:
                print("⚠️  No search results found")
            
            # Show stats
            stats = pipeline.get_statistics()
            print(f"\n📊 Database Stats:")
            print(f"Total jobs: {stats['total_jobs']}")
            print(f"Sources: {list(stats['sources'].keys())}")
        else:
            print("⚠️  No jobs were stored, skipping search test")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(demo_pipeline())
