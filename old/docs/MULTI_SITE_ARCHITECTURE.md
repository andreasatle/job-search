# 🌐 Multi-Site LLM Scraper Architecture

**Extensible LLM job scraping across multiple job platforms with unified filtering.**

## 🎯 Current Status

| Site | Status | Priority | Volume | Quality | Specialties |
|------|--------|----------|---------|---------|-------------|
| **ZipRecruiter** | ✅ **Implemented** | #1 | Medium | Good | General, Remote, Contract |
| **Indeed** | ⏳ Coming Soon | #2 | **Very High** | Good | Volume, Local, Enterprise |
| **LinkedIn** | ⏳ Coming Soon | #3 | High | **Excellent** | Senior, Remote, Tech Companies |
| **Glassdoor** | ⏳ Coming Soon | #4 | Medium | Good | Salary Info, Reviews |
| **AngelList** | ⏳ Coming Soon | #5 | Low | Good | Startups, Equity |

## 🚀 Quick Start

```python
from src.scrapers.multi_site_llm_scraper import create_multi_site_llm_scraper

# Search all available sites
scraper = create_multi_site_llm_scraper()
results = await scraper.search_all_sites(
    location="Houston, TX",
    max_pages_per_site=3,
    seniority_level="senior"
)

print(f"Found {results.total_jobs_found} LLM jobs across {results.total_sites_searched} sites")
```

## 🏗️ Architecture Overview

### Core Components

1. **MultiSiteLLMScraper** - Orchestrates searches across multiple sites
2. **Site-Specific Scrapers** - Individual scrapers for each job platform
3. **Unified Filtering** - Consistent LLM-optimized filters across all sites
4. **Result Aggregation** - Deduplication and comprehensive analytics

### Data Flow

```
Search Query → [Site 1, Site 2, Site 3] → Individual Results → Filter → Deduplicate → Aggregate → Analytics
```

## 🔧 Implementation Roadmap

### Phase 1: Foundation ✅
- [x] Multi-site architecture
- [x] ZipRecruiter implementation
- [x] Unified filtering system
- [x] Result aggregation

### Phase 2: Volume Expansion 🚧
- [ ] **Indeed scraper** (highest priority)
  - Challenge: CAPTCHA protection
  - Expected: 3-5x more jobs
  - Approach: Advanced anti-detection

### Phase 3: Quality Enhancement 🚧
- [ ] **LinkedIn scraper** (high quality)
  - Challenge: Authentication required
  - Expected: Senior-level, high-paying roles
  - Approach: API integration preferred

### Phase 4: Specialized Sources 🔄
- [ ] **Glassdoor scraper** (salary insights)
- [ ] **AngelList scraper** (startup focus)

## 🛠️ Adding New Sites

### 1. Create Site-Specific Scraper

```python
# Example: Indeed LLM scraper
class IndeedLLMScraper(PlaywrightJobScraper):
    def __init__(self, strict_mode=False):
        super().__init__()
        self.job_filter = self._create_indeed_llm_filter(strict_mode)
    
    async def search_llm_jobs(self, location, max_pages, seniority_level):
        # Site-specific implementation
        pass
```

### 2. Register with Multi-Site Scraper

```python
# In MultiSiteLLMScraper.__init__
self.scrapers = {
    "ziprecruiter": LLMEngineerScraper(...),
    "indeed": IndeedLLMScraper(...),  # Add new scraper
    "linkedin": LinkedInLLMScraper(...),
}

self.site_configs = {
    "indeed": {
        "enabled": True,
        "max_pages": 5,
        "priority": 2,
        "expected_results": "high",
        "specialties": ["volume", "enterprise"]
    }
}
```

### 3. Handle Site-Specific Challenges

**Indeed:**
- CAPTCHA after 10-20 requests
- Aggressive rate limiting
- Complex JavaScript rendering
- Solution: Advanced anti-detection, residential proxies

**LinkedIn:**
- Requires authentication
- Terms of Service restrictions
- Very sophisticated anti-scraping
- Solution: Official API preferred

**Glassdoor:**
- Moderate anti-bot measures
- Focus on salary/company data
- Limited job volume
- Solution: Standard scraping with delays

## 📊 Expected Results by Site

### ZipRecruiter (Current)
- **Volume**: 5-15 LLM jobs per search
- **Quality**: Good job descriptions
- **Specialties**: Contract work, remote positions
- **Salary Range**: $80k-$200k

### Indeed (Future)
- **Volume**: 20-50 LLM jobs per search
- **Quality**: Variable, enterprise-heavy
- **Specialties**: Enterprise roles, local positions
- **Salary Range**: $100k-$300k

### LinkedIn (Future)
- **Volume**: 10-25 LLM jobs per search
- **Quality**: Very high, detailed descriptions
- **Specialties**: Senior roles, tech companies
- **Salary Range**: $150k-$400k+

## 🎯 Site-Specific Optimizations

### Keyword Strategy
- **ZipRecruiter**: General ML/AI terms
- **Indeed**: Enterprise/corporate terminology
- **LinkedIn**: Tech-forward, senior-level terms
- **Glassdoor**: Company-focused searches
- **AngelList**: Startup/equity terminology

### Filter Adjustments
- **Indeed**: Higher salary minimums (enterprise focus)
- **LinkedIn**: Senior experience levels only
- **Glassdoor**: Emphasis on salary data quality
- **AngelList**: Equity/startup-specific filters

## 🔍 Search Strategy

### Multi-Query Approach
Each site tests multiple search queries:
1. "LLM Engineer"
2. "Large Language Model Engineer"
3. "AI Engineer Machine Learning"
4. "ML Engineer NLP"
5. "Generative AI Engineer"

### Deduplication
- URL-based deduplication
- Title/company similarity detection
- Cross-site job matching

### Quality Scoring
- Site-specific quality adjustments
- Technology mention analysis
- Salary information completeness

## 📈 Analytics & Insights

### Multi-Site Metrics
- Jobs found per site
- Filtering efficiency
- Search duration
- Best performing site

### Technology Analysis
- Cross-site technology trends
- Skill demand analysis
- Salary correlation

### Market Insights
- Site-specific salary ranges
- Remote work distribution
- Experience level demand

## 🚀 Usage Examples

### Basic Multi-Site Search
```python
scraper = create_multi_site_llm_scraper()
results = await scraper.search_all_sites()
```

### Targeted Search
```python
results = await scraper.search_all_sites(
    location="Houston, TX",
    sites_to_search=["ziprecruiter", "indeed"],
    seniority_level="senior",
    max_pages_per_site=3
)
```

### Enterprise Search
```python
enterprise_scraper = create_enterprise_llm_scraper()
results = await enterprise_scraper.search_all_sites()
```

## 🔧 Development Commands

```bash
# Test multi-site architecture
uv run python examples/multi_site_llm_search.py

# Test individual site implementations
uv run python tests/test_llm_scraper.py

# Check site status
from src.scrapers.multi_site_llm_scraper import create_multi_site_llm_scraper
scraper = create_multi_site_llm_scraper()
print(scraper.get_site_status())
```

## 🎯 Next Steps

1. **Implement Indeed Scraper** (highest ROI)
   - Expected 3-5x increase in job volume
   - Focus on enterprise LLM roles
   - Handle CAPTCHA and rate limiting

2. **Implement LinkedIn Scraper** (highest quality)
   - Premium, senior-level positions
   - Tech company focus
   - API-first approach preferred

3. **Add Glassdoor Integration** (salary insights)
   - Complement job data with salary info
   - Company culture insights
   - Interview preparation data

4. **Optimize Cross-Site Analytics**
   - Market trend analysis
   - Salary benchmarking
   - Skill demand forecasting

The multi-site architecture provides a **scalable foundation** for comprehensive LLM job discovery across the entire job market! 🚀
