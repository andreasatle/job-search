"""
Demonstration of smart job filtering to reduce irrelevant jobs.
"""

import asyncio
from src.scrapers.filtered_ziprecruiter_scraper import (
    FilteredZipRecruiterScraper,
    create_software_engineer_scraper,
    create_data_scientist_scraper,
    create_remote_only_scraper,
    create_custom_scraper
)
from src.scrapers.smart_job_filter import JobFilter, FilterPresets
from src.models.job_models import JobType, RemoteType


async def compare_filtered_vs_unfiltered():
    """Compare scraping with and without filters."""
    print("🆚 Filtered vs Unfiltered Scraping Comparison")
    print("=" * 50)
    
    # 1. Regular scraping (no filters)
    print("\n1️⃣ Regular scraping (no filters):")
    regular_scraper = FilteredZipRecruiterScraper()  # No filter
    regular_result = await regular_scraper.search_houston_jobs("engineer", max_pages=1)
    
    print(f"   📥 Total jobs found: {len(regular_result.jobs)}")
    if regular_result.jobs:
        avg_quality = sum(job.quality_score for job in regular_result.jobs) / len(regular_result.jobs)
        print(f"   ⭐ Average quality score: {avg_quality:.2f}")
        
        # Show some examples
        print("   📋 Sample jobs (first 3):")
        for i, job in enumerate(regular_result.jobs[:3], 1):
            print(f"      {i}. {job.title} at {job.company} (Quality: {job.quality_score:.2f})")
    
    # 2. Filtered scraping
    print("\n2️⃣ Filtered scraping (software engineer preset):")
    filtered_scraper = create_software_engineer_scraper()
    filtered_result = await filtered_scraper.search_houston_jobs("engineer", max_pages=1)
    
    print(f"   📥 Jobs after filtering: {len(filtered_result.jobs)}")
    if filtered_result.jobs:
        avg_quality = sum(job.quality_score for job in filtered_result.jobs) / len(filtered_result.jobs)
        print(f"   ⭐ Average quality score: {avg_quality:.2f}")
        
        # Show filtering efficiency
        if "jobs_before_filtering" in filtered_result.metadata:
            before = filtered_result.metadata["jobs_before_filtering"]
            after = filtered_result.metadata["jobs_after_filtering"]
            efficiency = after / before * 100 if before > 0 else 0
            print(f"   🎯 Filtering efficiency: {after}/{before} ({efficiency:.1f}% kept)")
        
        # Show some examples
        print("   📋 Sample filtered jobs (first 3):")
        for i, job in enumerate(filtered_result.jobs[:3], 1):
            print(f"      {i}. {job.title} at {job.company} (Quality: {job.quality_score:.2f})")


async def demo_preset_filters():
    """Demonstrate different preset filters."""
    print("\n🎯 Preset Filter Demonstrations")
    print("=" * 40)
    
    presets = [
        ("Software Engineer", create_software_engineer_scraper()),
        ("Data Scientist", create_data_scientist_scraper()),
        ("Remote Only", create_remote_only_scraper()),
    ]
    
    for preset_name, scraper in presets:
        print(f"\n📋 {preset_name} Filter:")
        
        # Show filter configuration
        filter_stats = scraper.get_filter_stats()
        print(f"   🎛️ Filter settings:")
        print(f"      • Min quality score: {filter_stats.get('min_quality_score', 'N/A')}")
        print(f"      • Min salary: ${filter_stats.get('min_salary'):,}" if filter_stats.get('min_salary') else "      • Min salary: Not set")
        print(f"      • Required keywords: {filter_stats.get('required_keywords_count', 0)} keywords")
        print(f"      • Exclude keywords: {filter_stats.get('exclude_keywords_count', 0)} keywords")
        
        # Test with a broad search
        try:
            result = await scraper.search_houston_jobs("developer", max_pages=1)
            print(f"   ✅ Found {len(result.jobs)} jobs matching {preset_name.lower()} criteria")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def create_your_custom_filter():
    """Example of creating a highly customized filter."""
    print("\n🛠️ Creating Your Custom Filter")
    print("=" * 35)
    
    # Example: Looking for senior Python roles at good companies
    custom_filter = JobFilter(
        # Must have these keywords
        required_keywords=[
            "python", "django", "flask", "fastapi",  # Python frameworks
            "senior", "lead", "principal"            # Seniority levels
        ],
        
        # Reject if any of these are present
        exclude_keywords=[
            "sales", "marketing", "recruiter", "cold calling",
            "door to door", "commission only", "mlm", "pyramid",
            "unpaid", "volunteer", "intern"
        ],
        
        # Quality requirements
        min_quality_score=0.75,        # High quality jobs only
        min_salary=100000,             # $100k minimum
        max_salary=250000,             # $250k maximum
        min_description_length=200,    # Detailed job descriptions
        
        # Job type preferences
        allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
        allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
        
        # Company exclusions (example)
        exclude_companies=[
            "sketchy startup", "commission corp", "pyramid inc"
        ],
        
        # Experience level exclusions
        exclude_experience_levels=["entry level", "intern", "junior"]
    )
    
    # Create scraper with custom filter
    custom_scraper = FilteredZipRecruiterScraper(custom_filter)
    
    print("🎯 Your Custom Filter Configuration:")
    print(f"   📝 Required keywords: {custom_filter.required_keywords[:5]}...")
    print(f"   ❌ Exclude keywords: {custom_filter.exclude_keywords[:5]}...")
    print(f"   ⭐ Min quality score: {custom_filter.min_quality_score}")
    print(f"   💰 Salary range: ${custom_filter.min_salary:,} - ${custom_filter.max_salary:,}")
    print(f"   🏢 Job types: {[jt.value for jt in custom_filter.allowed_job_types]}")
    print(f"   🏠 Remote types: {[rt.value for rt in custom_filter.allowed_remote_types]}")
    
    # Test the custom filter
    print(f"\n🔍 Testing custom filter with 'python senior' search...")
    try:
        result = await custom_scraper.search_houston_jobs("python senior", max_pages=1)
        print(f"✅ Found {len(result.jobs)} highly filtered jobs")
        
        # Show the best matches
        if result.jobs:
            print(f"\n🏆 Top matches:")
            for i, job in enumerate(result.jobs[:3], 1):
                salary_info = f"${job.salary_min:,}-${job.salary_max:,}" if job.salary_min and job.salary_max else "Salary not specified"
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      💰 {salary_info} | ⭐ Quality: {job.quality_score:.2f} | 🏠 {job.remote_type.value}")
    
    except Exception as e:
        print(f"❌ Error testing custom filter: {e}")


def show_filtering_tips():
    """Show practical tips for effective job filtering."""
    print("\n💡 Pro Tips for Effective Job Filtering")
    print("=" * 40)
    
    tips = [
        "🎯 Be specific with required keywords - use technology names, not just 'developer'",
        "❌ Always exclude sales/marketing terms to avoid spam jobs",
        "💰 Set realistic salary minimums based on your market research", 
        "⭐ Start with quality score 0.6+ to filter out low-effort job posts",
        "📝 Require longer descriptions (150+ chars) to get detailed job posts",
        "🏢 Exclude companies known for posting spam or low-quality jobs",
        "🔄 Test different keyword combinations and adjust based on results",
        "📊 Monitor filtering efficiency - aim for 20-50% of jobs kept",
        "🎚️ Start restrictive, then relax filters if you're getting too few results",
        "🔍 Use the web UI filters for post-scraping refinement"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    
    print(f"\n📈 Filtering Strategy:")
    print(f"   1. Start with a preset filter (software_engineer, data_scientist, etc.)")
    print(f"   2. Run a small test (1 page) to see results")
    print(f"   3. Adjust keywords and quality thresholds")
    print(f"   4. Scale up to more pages once you're happy with quality")
    print(f"   5. Use the web UI for final filtering and search")


async def main():
    """Run all filtering demonstrations."""
    print("🎯 Smart Job Filtering System Demo")
    print("=" * 50)
    print("This demo shows how to dramatically reduce irrelevant jobs")
    print("by using smart filtering during the scraping process.")
    
    try:
        # Run demonstrations
        await compare_filtered_vs_unfiltered()
        await demo_preset_filters()
        await create_your_custom_filter()
        show_filtering_tips()
        
        print(f"\n🎉 Demo Complete!")
        print(f"📚 Next steps:")
        print(f"   1. Copy and modify the custom filter example above")
        print(f"   2. Test with: uv run python examples/smart_filtering_demo.py")
        print(f"   3. Use filtered scrapers in your job pipeline")
        print(f"   4. Fine-tune based on the quality of results you get")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
