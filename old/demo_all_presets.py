#!/usr/bin/env python3
"""
Demo showing how to use ALL available filter presets.
Each preset targets different job types and experience levels.
"""

import asyncio
from src.scrapers.ziprecruiter_scraper import create_ziprecruiter_scraper, list_available_presets


async def demo_preset(preset_name: str, use_llm: bool = False, query: str = "software engineer"):
    """Demo a specific filter preset."""
    print(f"\n🔍 Testing preset: '{preset_name}' (LLM: {use_llm})")
    print("-" * 50)
    
    try:
        # Create scraper with the specified preset
        scraper = create_ziprecruiter_scraper(
            filter_preset=preset_name,
            use_llm=use_llm,
            headless=True
        )
        
        async with scraper:
            result = await scraper.search_houston_jobs(
                query=query,
                max_pages=1  # Limited for demo
            )
            
            print(f"📊 Results for '{preset_name}':")
            print(f"   🎯 Jobs found: {len(result.jobs)}")
            print(f"   🔧 LLM enabled: {result.metadata.get('llm_filtering', False)}")
            
            if result.jobs:
                # Show filter settings
                filter_config = scraper.job_filter.config
                print(f"   💰 Min salary: ${filter_config.min_salary:,}" if filter_config.min_salary else "   💰 Min salary: Not set")
                print(f"   ⭐ Min quality: {filter_config.min_quality_score}")
                
                # Show top job
                top_job = result.jobs[0]
                print(f"   🏆 Top job: {top_job.title} at {top_job.company}")
                print(f"   💵 Salary: {top_job.salary_text or 'Not specified'}")
                print(f"   📈 Quality: {top_job.quality_score:.2f}")
            else:
                print(f"   ⚠️  No jobs found with this preset")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def demo_all_presets():
    """Demo all available filter presets."""
    print("🎯 ALL AVAILABLE FILTER PRESETS DEMO")
    print("=" * 50)
    
    # First, list all available presets
    available_presets = list_available_presets()
    
    print(f"\n🧪 Testing each preset with traditional filtering...")
    
    # Demo each preset with traditional filtering (faster)
    for preset in available_presets:
        # Adjust query based on preset type
        if "llm" in preset or "data" in preset:
            query = "machine learning engineer"
        elif "senior" in preset:
            query = "senior software engineer"
        elif "startup" in preset:
            query = "software engineer startup"
        else:
            query = "software engineer"
            
        await demo_preset(preset, use_llm=False, query=query)
        
        # Small delay to be respectful to the site
        await asyncio.sleep(1)


async def demo_llm_comparison():
    """Compare traditional vs LLM filtering for senior_level preset."""
    print(f"\n🤖 LLM COMPARISON: senior_level preset")
    print("=" * 45)
    
    preset = "senior_level"
    query = "senior software engineer"
    
    # Traditional filtering
    await demo_preset(preset, use_llm=False, query=query)
    
    # LLM filtering  
    await demo_preset(preset, use_llm=True, query=query)


def show_usage_examples():
    """Show practical usage examples."""
    print(f"\n💡 USAGE EXAMPLES")
    print("=" * 20)
    
    examples = [
        ("Basic software engineer search", "software_engineer", False),
        ("Senior roles with LLM filtering", "senior_level", True),
        ("Data science positions", "data_scientist", False),
        ("High-paying roles with AI analysis", "high_paying", True),
        ("Remote-only positions", "remote_only", False),
        ("AI/ML specialist (auto-LLM)", "llm_engineer", False),
        ("Startup/tech companies", "startup_roles", False),
        ("Strict AI/ML senior roles", "llm_engineer_strict", False),
    ]
    
    for description, preset, use_llm in examples:
        llm_note = " (auto-LLM)" if "llm_engineer" in preset else f" (LLM: {use_llm})"
        print(f"📋 {description}{llm_note}")
        print(f"   scraper = create_ziprecruiter_scraper(")
        print(f"       filter_preset='{preset}',")
        print(f"       use_llm={use_llm}")
        print(f"   )")
        print()


if __name__ == "__main__":
    print("🚀 Filter Presets Demo")
    print("This will test all available filter presets!")
    print()
    
    try:
        # Show usage examples first
        show_usage_examples()
        
        # Ask user what they want to demo
        choice = input("Choose demo:\n1. List all presets\n2. Test all presets (takes time)\n3. Compare LLM vs traditional\nChoice (1-3): ").strip()
        
        if choice == "1":
            list_available_presets()
        elif choice == "2":
            asyncio.run(demo_all_presets())
        elif choice == "3":
            asyncio.run(demo_llm_comparison())
        else:
            print("Just showing preset list...")
            list_available_presets()
            
        print("\n✅ Demo completed!")
        print("🎉 You can now use ANY of these presets in your scrapers!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
