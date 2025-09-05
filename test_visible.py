#!/usr/bin/env python3
"""
Test scraper with visible browser to see what's happening.
"""

import asyncio
from src.scraper import SimpleZipRecruiterScraper


async def test_visible():
    """Test with visible browser to debug."""
    print("🔍 Testing with visible browser...")
    scraper = SimpleZipRecruiterScraper(headless=False)  # Show browser!
    
    try:
        jobs = await scraper.search_jobs("software engineer", max_jobs=3)
        print(f"\n✅ Success! Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  • {job}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_visible())
