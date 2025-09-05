#!/usr/bin/env python3
"""
Demo of the new consolidated scraper with LLM flag.
Shows the difference between traditional keyword filtering and LLM-enhanced filtering.
"""

import asyncio
from src.scrapers.ziprecruiter_scraper import create_ziprecruiter_scraper


async def demo_llm_vs_traditional():
    """Compare traditional vs LLM filtering side by side."""
    print("🤖 Consolidated Scraper Demo: LLM vs Traditional Filtering")
    print("=" * 60)
    print("Now you can use a single scraper with just a use_llm=True flag!")
    print()
    
    query = "software engineer"
    max_pages = 1
    
    print(f"🔍 Search query: '{query}'")
    print(f"📄 Pages to scrape: {max_pages}")
    print()
    
    # 1. Traditional keyword-based filtering
    print("1️⃣ TRADITIONAL FILTERING (keywords only)")
    print("-" * 40)
    
    traditional_scraper = create_ziprecruiter_scraper(
        use_llm=False,  # 🔑 This is the key difference!
        filter_preset="software_engineer"
    )
    
    async with traditional_scraper:
        traditional_result = await traditional_scraper.search_houston_jobs(
            query=query, 
            max_pages=max_pages
        )
    
    # 2. LLM-enhanced filtering  
    print("\n2️⃣ LLM-ENHANCED FILTERING (AI-powered)")
    print("-" * 40)
    
    llm_scraper = create_ziprecruiter_scraper(
        use_llm=True,   # 🤖 Enable LLM filtering!
        filter_preset="software_engineer"
    )
    
    async with llm_scraper:
        llm_result = await llm_scraper.search_houston_jobs(
            query=query, 
            max_pages=max_pages
        )
    
    # 3. LLM Engineer specialist (always uses LLM)
    print("\n3️⃣ LLM ENGINEER SPECIALIST (AI/ML specific)")
    print("-" * 45)
    
    specialist_scraper = create_ziprecruiter_scraper(
        filter_preset="llm_engineer"  # This preset has use_llm=True built-in
    )
    
    async with specialist_scraper:
        specialist_result = await specialist_scraper.search_houston_jobs(
            query="LLM Engineer AI ML",
            max_pages=max_pages
        )
    
    # Comparison
    print("\n📊 COMPARISON RESULTS")
    print("=" * 30)
    print(f"Traditional filtering: {len(traditional_result.jobs)} jobs")
    print(f"LLM-enhanced filtering: {len(llm_result.jobs)} jobs") 
    print(f"LLM Engineer specialist: {len(specialist_result.jobs)} jobs")
    
    if traditional_result.jobs and llm_result.jobs:
        quality_improvement = llm_result.average_quality - traditional_result.average_quality
        print(f"Quality improvement with LLM: {quality_improvement:+.2f}")
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"• Single codebase - no more duplicated scraper files!")
    print(f"• Just set use_llm=True for AI-powered filtering")
    print(f"• LLM catches spam, evaluates job quality, and improves relevance")
    print(f"• Traditional filtering still available for speed/cost optimization")
    print(f"• Specialized presets (llm_engineer) for targeted searches")
    
    print(f"\n🛠️ USAGE EXAMPLES:")
    print(f"# Basic usage with traditional filtering")
    print(f"scraper = create_ziprecruiter_scraper(use_llm=False)")
    print()
    print(f"# Enhanced with LLM filtering") 
    print(f"scraper = create_ziprecruiter_scraper(use_llm=True)")
    print()
    print(f"# Specialized for AI/ML roles")
    print(f"scraper = create_ziprecruiter_scraper(filter_preset='llm_engineer')")


async def demo_filter_presets():
    """Show different filter presets available."""
    print("\n🎯 AVAILABLE FILTER PRESETS")
    print("=" * 35)
    
    presets = [
        ("software_engineer", "General software engineering roles"),
        ("llm_engineer", "AI/ML and LLM engineering (includes LLM filtering)"),
        ("llm_engineer_strict", "Senior AI/ML roles with strict requirements"),
        ("high_paying", "High-salary positions ($120k+)")
    ]
    
    for preset, description in presets:
        print(f"📋 {preset}")
        print(f"   {description}")
        print(f"   Usage: create_ziprecruiter_scraper(filter_preset='{preset}')")
        print()


if __name__ == "__main__":
    print("🚀 Starting Consolidated Scraper Demo...")
    print("This will make real HTTP requests - please be patient!")
    print()
    
    try:
        asyncio.run(demo_llm_vs_traditional())
        asyncio.run(demo_filter_presets())
        
        print("\n✅ Demo completed successfully!")
        print("🎉 No more separate LLM vs non-LLM files - everything is unified!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This might be due to network issues or API keys")
