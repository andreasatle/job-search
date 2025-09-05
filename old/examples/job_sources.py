"""Job sources analysis for Houston area job posts."""
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class SourceDifficulty(Enum):
    """Difficulty level for scraping different sources."""
    EASY = "easy"           # Simple HTML, minimal anti-bot
    MEDIUM = "medium"       # Some JavaScript, moderate protection
    HARD = "hard"          # Heavy JavaScript, strong anti-bot
    VERY_HARD = "very_hard" # Advanced protection, requires special handling


@dataclass
class JobSource:
    """Information about a job source."""
    name: str
    url: str
    description: str
    houston_specific_url: str
    difficulty: SourceDifficulty
    estimated_jobs: str
    pros: List[str]
    cons: List[str]
    scraping_notes: str


# Houston Area Job Sources Analysis
HOUSTON_JOB_SOURCES = [
    JobSource(
        name="Indeed",
        url="https://www.indeed.com",
        description="Largest job aggregator with extensive Houston listings",
        houston_specific_url="https://www.indeed.com/jobs?q=&l=Houston%2C+TX",
        difficulty=SourceDifficulty.HARD,
        estimated_jobs="10,000+ active",
        pros=[
            "Massive job volume",
            "Detailed job descriptions",
            "Salary information often included",
            "Company reviews linked"
        ],
        cons=[
            "Heavy anti-bot protection",
            "Requires sophisticated scraping",
            "Rate limiting",
            "IP blocking common"
        ],
        scraping_notes="Requires Playwright with stealth mode, rotating proxies recommended"
    ),
    
    JobSource(
        name="LinkedIn Jobs",
        url="https://www.linkedin.com/jobs",
        description="Professional network with quality job postings",
        houston_specific_url="https://www.linkedin.com/jobs/search/?location=Houston%2C%20Texas%2C%20United%20States",
        difficulty=SourceDifficulty.VERY_HARD,
        estimated_jobs="5,000+ active",
        pros=[
            "High-quality positions",
            "Professional networking context",
            "Company insights",
            "Remote work clearly marked"
        ],
        cons=[
            "Requires login for full access",
            "Aggressive bot detection",
            "Complex JavaScript rendering",
            "Legal restrictions on scraping"
        ],
        scraping_notes="Consider using LinkedIn API instead of scraping"
    ),
    
    JobSource(
        name="ZipRecruiter",
        url="https://www.ziprecruiter.com",
        description="AI-powered job matching platform",
        houston_specific_url="https://www.ziprecruiter.com/Jobs/Houston-TX",
        difficulty=SourceDifficulty.MEDIUM,
        estimated_jobs="3,000+ active",
        pros=[
            "Moderate anti-bot protection",
            "Clean HTML structure",
            "Good mobile site (easier to scrape)",
            "Local job focus"
        ],
        cons=[
            "Smaller volume than Indeed",
            "Some duplicate postings",
            "Limited advanced search"
        ],
        scraping_notes="Good starting point, mobile site may be easier to scrape"
    ),
    
    JobSource(
        name="Glassdoor",
        url="https://www.glassdoor.com",
        description="Jobs with company reviews and salary data",
        houston_specific_url="https://www.glassdoor.com/Job/houston-jobs-SRCH_IL.0,7_IC1140171.htm",
        difficulty=SourceDifficulty.HARD,
        estimated_jobs="2,000+ active",
        pros=[
            "Salary transparency",
            "Company culture insights",
            "Interview process details",
            "Employee reviews"
        ],
        cons=[
            "Requires account for full access",
            "Popup interruptions",
            "Geographic restrictions",
            "Anti-scraping measures"
        ],
        scraping_notes="Focus on publicly available job listings only"
    ),
    
    JobSource(
        name="Houston.gov Jobs",
        url="https://www.houstontx.gov",
        description="Official Houston city government jobs",
        houston_specific_url="https://www.houstontx.gov/hr/employment.html",
        difficulty=SourceDifficulty.EASY,
        estimated_jobs="200+ active",
        pros=[
            "Stable government positions",
            "Clear job descriptions",
            "Minimal anti-bot protection",
            "Official source"
        ],
        cons=[
            "Limited to government jobs",
            "Slower hiring process",
            "Less frequent updates"
        ],
        scraping_notes="Simple HTML structure, easy to scrape"
    ),
    
    JobSource(
        name="Dice (Tech Jobs)",
        url="https://www.dice.com",
        description="Technology-focused job board",
        houston_specific_url="https://www.dice.com/jobs?location=Houston,%20TX",
        difficulty=SourceDifficulty.MEDIUM,
        estimated_jobs="1,000+ tech jobs",
        pros=[
            "Tech-specific roles",
            "Detailed technical requirements",
            "Contract and permanent roles",
            "Salary ranges provided"
        ],
        cons=[
            "Limited to tech industry",
            "Smaller overall volume",
            "Some outdated listings"
        ],
        scraping_notes="Good for tech roles, moderate JavaScript usage"
    ),
    
    JobSource(
        name="AngelList (Startups)",
        url="https://angel.co",
        description="Startup and tech company jobs",
        houston_specific_url="https://angel.co/jobs?location=Houston",
        difficulty=SourceDifficulty.MEDIUM,
        estimated_jobs="500+ startup jobs",
        pros=[
            "Startup ecosystem focus",
            "Equity information",
            "Company funding details",
            "Direct founder contact"
        ],
        cons=[
            "Limited to startups",
            "Smaller job volume",
            "Requires registration for details"
        ],
        scraping_notes="API available, consider using official endpoints"
    ),
    
    JobSource(
        name="FlexJobs (Remote)",
        url="https://www.flexjobs.com",
        description="Remote and flexible job opportunities",
        houston_specific_url="https://www.flexjobs.com/search?search=&location=Houston%2C+TX",
        difficulty=SourceDifficulty.MEDIUM,
        estimated_jobs="1,500+ remote/flex",
        pros=[
            "Remote work focus",
            "Flexible arrangements",
            "Vetted job postings",
            "Work-life balance emphasis"
        ],
        cons=[
            "Subscription required for full access",
            "Premium content behind paywall",
            "Limited free access"
        ],
        scraping_notes="Limited free content available for scraping"
    ),
    
    JobSource(
        name="ClearanceJobs",
        url="https://www.clearancejobs.com",
        description="Security clearance jobs (relevant for Houston's energy/aerospace)",
        houston_specific_url="https://www.clearancejobs.com/jobs?location=Houston-TX",
        difficulty=SourceDifficulty.EASY,
        estimated_jobs="300+ clearance jobs",
        pros=[
            "Specialized niche",
            "High-paying positions",
            "Houston's energy sector focus",
            "Simple site structure"
        ],
        cons=[
            "Requires security clearance",
            "Limited audience",
            "Smaller volume"
        ],
        scraping_notes="Clean HTML, easy to parse"
    ),
    
    JobSource(
        name="Energy JobLine",
        url="https://www.energyjobline.com",
        description="Oil, gas, and energy industry jobs (Houston's specialty)",
        houston_specific_url="https://www.energyjobline.com/jobs?location=Houston",
        difficulty=SourceDifficulty.EASY,
        estimated_jobs="800+ energy jobs",
        pros=[
            "Industry-specific",
            "Houston's major industry",
            "High-paying roles",
            "Minimal protection"
        ],
        cons=[
            "Limited to energy sector",
            "Cyclical demand",
            "Technical positions focused"
        ],
        scraping_notes="Industry-specific site, likely easier to scrape"
    )
]


def analyze_sources() -> Dict[str, Any]:
    """Analyze the job sources and provide recommendations."""
    
    # Categorize by difficulty
    by_difficulty = {}
    for difficulty in SourceDifficulty:
        by_difficulty[difficulty.value] = [
            source for source in HOUSTON_JOB_SOURCES 
            if source.difficulty == difficulty
        ]
    
    # Calculate total estimated jobs
    total_estimated = sum([
        int(source.estimated_jobs.split('+')[0].replace(',', '').replace('k', '000'))
        for source in HOUSTON_JOB_SOURCES
        if '+' in source.estimated_jobs
    ])
    
    return {
        "total_sources": len(HOUSTON_JOB_SOURCES),
        "by_difficulty": by_difficulty,
        "total_estimated_jobs": total_estimated,
        "recommended_starting_points": [
            source.name for source in HOUSTON_JOB_SOURCES 
            if source.difficulty in [SourceDifficulty.EASY, SourceDifficulty.MEDIUM]
        ]
    }


def get_scraping_priority() -> List[JobSource]:
    """Get sources ordered by scraping priority (easiest first, highest volume)."""
    
    # Priority scoring: easier to scrape + higher volume = higher priority
    def calculate_priority(source: JobSource) -> int:
        difficulty_score = {
            SourceDifficulty.EASY: 4,
            SourceDifficulty.MEDIUM: 3,
            SourceDifficulty.HARD: 2,
            SourceDifficulty.VERY_HARD: 1
        }
        
        volume_score = 1
        if 'k+' in source.estimated_jobs or '000+' in source.estimated_jobs:
            volume_score = 3
        elif '500+' in source.estimated_jobs:
            volume_score = 2
        
        return difficulty_score[source.difficulty] + volume_score
    
    return sorted(HOUSTON_JOB_SOURCES, key=calculate_priority, reverse=True)


if __name__ == "__main__":
    print("🏙️  Houston Job Sources Analysis")
    print("=" * 50)
    
    analysis = analyze_sources()
    
    print(f"Total Sources Identified: {analysis['total_sources']}")
    print(f"Estimated Total Jobs: {analysis['total_estimated_jobs']:,}+")
    print(f"Recommended Starting Points: {', '.join(analysis['recommended_starting_points'])}")
    
    print("\n📊 Sources by Difficulty:")
    for difficulty, sources in analysis['by_difficulty'].items():
        print(f"\n{difficulty.upper()}:")
        for source in sources:
            print(f"  • {source.name} - {source.estimated_jobs}")
    
    print("\n🎯 Recommended Scraping Priority:")
    for i, source in enumerate(get_scraping_priority(), 1):
        print(f"{i:2d}. {source.name} ({source.difficulty.value}) - {source.estimated_jobs}")
    
    print("\n💡 Next Steps:")
    print("1. Start with EASY/MEDIUM difficulty sources")
    print("2. Build scrapers for ZipRecruiter and Houston.gov first")
    print("3. Add energy-specific sources (Houston's specialty)")
    print("4. Tackle Indeed/LinkedIn with advanced techniques later")
