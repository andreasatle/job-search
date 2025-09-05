"""
Practical example: Finding LLM Engineer jobs in Houston.
"""

import asyncio
from src.scrapers.llm_engineer_scraper import (
    create_llm_engineer_scraper,
    create_senior_llm_scraper,
    create_junior_llm_scraper
)
from src.database.job_vector_store import JobVectorStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def find_llm_jobs_and_store():
    """Complete workflow: scrape LLM jobs and store in vector database."""
    print("🤖 LLM Engineer Job Search & Storage")
    print("=" * 45)
    
    # Choose your scraper configuration
    print("🎯 Scraper options:")
    print("1. General LLM Engineer (all levels)")
    print("2. Senior LLM Engineer (strict filtering)")
    print("3. Junior/Mid LLM Engineer (inclusive)")
    
    choice = input("\nChoose scraper (1-3): ").strip()
    
    if choice == "2":
        scraper = create_senior_llm_scraper()
        scraper_name = "Senior LLM Engineer"
    elif choice == "3":
        scraper = create_junior_llm_scraper()
        scraper_name = "Junior/Mid LLM Engineer"
    else:
        scraper = create_llm_engineer_scraper()
        scraper_name = "General LLM Engineer"
    
    print(f"✅ Using {scraper_name} scraper")
    
    # Configure search parameters
    max_pages = int(input("Max pages to scrape (1-5): ") or "2")
    
    print(f"\n🔍 Starting LLM job search...")
    print(f"📄 Scraping up to {max_pages} pages")
    
    try:
        # Perform the search
        results = await scraper.search_llm_jobs(
            location="Houston, TX",
            max_pages=max_pages
        )
        
        jobs = results["jobs"]
        
        if not jobs:
            print("❌ No LLM engineering jobs found!")
            print("💡 Try:")
            print("   - Using a different scraper configuration")
            print("   - Increasing max_pages")
            print("   - Checking if ZipRecruiter has LLM jobs in Houston")
            return
        
        print(f"\n📊 Search Results Summary:")
        print(f"   🤖 Total LLM jobs found: {len(jobs)}")
        print(f"   🎯 Filtering efficiency: {results['filtering_efficiency']}")
        print(f"   ⭐ Average quality: {results['avg_quality_score']:.2f}")
        
        if results['salary_range']['min']:
            print(f"   💰 Salary range: ${results['salary_range']['min']:,} - ${results['salary_range']['max']:,}")
        
        # Show top jobs
        print(f"\n🏆 Top 5 LLM Engineering Jobs:")
        for i, job in enumerate(jobs[:5], 1):
            salary_str = f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary TBD"
            print(f"   {i}. {job.title}")
            print(f"      🏢 {job.company} | 💰 {salary_str}")
            print(f"      ⭐ Quality: {job.quality_score:.2f} | 🏠 {job.remote_type.value}")
            print(f"      🔗 {job.url[:60]}...")
            print()
        
        # Ask if user wants to store in vector database
        store_choice = input("Store these jobs in vector database? (y/n): ").strip().lower()
        
        if store_choice in ['y', 'yes']:
            print(f"\n💾 Storing {len(jobs)} LLM jobs in vector database...")
            
            try:
                # Initialize vector store
                vector_store = JobVectorStore(db_path="./llm_jobs_db")
                
                # Add jobs to vector store
                added, failed = vector_store.add_jobs(jobs)
                
                print(f"✅ Storage complete:")
                print(f"   📥 Added: {added} jobs")
                print(f"   ❌ Failed: {failed} jobs")
                
                # Test semantic search
                print(f"\n🔍 Testing semantic search...")
                search_results = vector_store.search_jobs("transformer neural network", n_results=3)
                
                print(f"📋 Sample search results for 'transformer neural network':")
                for i, result in enumerate(search_results, 1):
                    print(f"   {i}. {result['title']} - Similarity: {result['similarity_score']:.2%}")
                
                print(f"\n🎉 LLM jobs are now searchable in your vector database!")
                print(f"📁 Database location: ./llm_jobs_db")
                
            except Exception as e:
                print(f"❌ Error storing jobs: {e}")
        
        # Show technology breakdown
        print(f"\n🔧 Technology Analysis:")
        llm_techs = ["llm", "gpt", "transformer", "pytorch", "tensorflow", "huggingface", "langchain", "openai"]
        tech_counts = {}
        
        for job in jobs:
            job_text = f"{job.title} {job.description} {' '.join(job.skills)}".lower()
            for tech in llm_techs:
                if tech in job_text:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        if tech_counts:
            for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(jobs) * 100
                print(f"   🔹 {tech.upper()}: {count} jobs ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error during LLM job search: {e}")
        import traceback
        traceback.print_exc()


async def search_existing_llm_jobs():
    """Search existing LLM jobs in vector database."""
    print("\n🔍 Search Existing LLM Jobs")
    print("=" * 30)
    
    try:
        vector_store = JobVectorStore(db_path="./llm_jobs_db")
        stats = vector_store.get_statistics()
        
        print(f"📊 Database stats: {stats['total_jobs']} total LLM jobs")
        
        if stats['total_jobs'] == 0:
            print("❌ No LLM jobs in database yet!")
            print("💡 Run the scraper first to collect LLM jobs.")
            return
        
        # Interactive search
        while True:
            query = input("\nEnter search query (or 'quit'): ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query:
                results = vector_store.search_jobs(query, n_results=5)
                
                print(f"\n📋 Results for '{query}':")
                for i, result in enumerate(results, 1):
                    print(f"   {i}. {result['title']} at {result['company']}")
                    print(f"      Similarity: {result['similarity_score']:.2%} | Quality: {result['quality_score']}")
                    print(f"      {result['url'][:60]}...")
                    print()
    
    except Exception as e:
        print(f"❌ Error searching database: {e}")


def main_menu():
    """Show main menu for LLM job search."""
    print("🤖 LLM Engineer Job Search Tool")
    print("=" * 35)
    print("1. Scrape new LLM jobs")
    print("2. Search existing LLM jobs")
    print("3. Quit")
    
    choice = input("\nChoose option (1-3): ").strip()
    return choice


async def main():
    """Main application loop."""
    while True:
        choice = main_menu()
        
        if choice == "1":
            await find_llm_jobs_and_store()
        elif choice == "2":
            await search_existing_llm_jobs()
        elif choice == "3":
            print("👋 Happy job hunting!")
            break
        else:
            print("❌ Invalid choice, please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
