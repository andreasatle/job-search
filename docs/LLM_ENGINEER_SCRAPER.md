# 🤖 LLM Engineer Scraper

A specialized web scraper optimized for finding **LLM Engineer** and **AI/ML Engineering** positions with intelligent filtering.

## ✨ Features

- **🎯 LLM-Optimized Keywords**: 40+ AI/ML specific keywords including LLM, GPT, transformers, PyTorch, HuggingFace
- **💰 Salary-Aware Filtering**: $80k-$500k range with configurable minimums  
- **⭐ Quality-Based Filtering**: High quality score requirements (0.65-0.8)
- **🎚️ Configurable Strictness**: General vs Senior-level filtering modes
- **🔄 Multi-Query Search**: Tests multiple search strategies automatically
- **📊 Technology Analysis**: Breakdown of technologies mentioned in job posts
- **🚫 Spam Protection**: Filters out sales, marketing, and commission-only roles

## 🚀 Quick Start

### Basic Usage

```python
from src.scrapers.llm_engineer_scraper import create_llm_engineer_scraper

# Create LLM engineer scraper
scraper = create_llm_engineer_scraper()

# Search for LLM jobs
results = await scraper.search_llm_jobs(max_pages=3)

print(f"Found {results['total_jobs_found']} LLM engineering jobs")
print(f"Average salary: ${results['salary_range']['avg']:,.0f}")
```

### Advanced Usage

```python
from src.scrapers.llm_engineer_scraper import (
    create_senior_llm_scraper,
    create_junior_llm_scraper,
    LLMEngineerScraper
)

# Senior-level positions only (strict filtering)
senior_scraper = create_senior_llm_scraper()
senior_results = await senior_scraper.search_llm_jobs(
    seniority_level="senior",
    max_pages=2
)

# Junior/mid-level positions (more inclusive)
junior_scraper = create_junior_llm_scraper()  
junior_results = await junior_scraper.search_llm_jobs()

# Custom configuration
custom_scraper = LLMEngineerScraper(strict_mode=True)
custom_results = await custom_scraper.search_llm_jobs()
```

## 🎛️ Configuration Options

### Scraper Types

| Scraper | Min Salary | Quality Score | Experience Level | Use Case |
|---------|------------|---------------|------------------|----------|
| **General** | $80,000 | 0.65 | All levels | Comprehensive search |
| **Senior** | $120,000 | 0.80 | Senior+ only | High-level positions |
| **Junior** | $80,000 | 0.65 | All levels | Inclusive search |

### Search Parameters

```python
results = await scraper.search_llm_jobs(
    location="Houston, TX",           # Job location
    max_pages=3,                      # Pages to scrape
    seniority_level="senior"          # "junior", "mid", "senior", "staff"
)
```

## 🔍 Search Strategies

The scraper automatically tests multiple search queries:

1. **"LLM Engineer"** - Direct LLM roles
2. **"Large Language Model Engineer"** - Explicit LLM titles  
3. **"AI Engineer Machine Learning"** - Broader AI/ML roles
4. **"ML Engineer NLP"** - ML with NLP focus
5. **"Machine Learning Engineer AI"** - General ML+AI
6. **"Generative AI Engineer"** - GenAI specific
7. **"MLOps Engineer"** - ML operations roles

## 🎯 Filtering Criteria

### Required Keywords (at least one must be present)

**LLM/AI Specific:**
- `llm`, `large language model`, `gpt`, `bert`, `transformer`
- `machine learning`, `artificial intelligence`, `ai engineer`
- `deep learning`, `neural network`, `nlp`

**Technologies:**
- `pytorch`, `tensorflow`, `huggingface`, `langchain`
- `openai`, `anthropic`, `vector database`
- `aws sagemaker`, `azure ml`, `databricks`

**Roles:**
- `ml engineer`, `mlops`, `ai/ml engineer`
- `machine learning scientist`, `ai research engineer`

### Excluded Keywords (automatically filtered out)

- `sales`, `marketing`, `recruiter`, `cold calling`
- `commission only`, `mlm`, `pyramid`, `telemarketing`
- `intern`, `unpaid`, `volunteer`, `entry level` (in strict mode)
- `real estate`, `insurance`, `retail`, `construction`

## 📊 Results Analysis

The scraper provides comprehensive analytics:

```python
results = await scraper.search_llm_jobs()

print(f"📊 Results Summary:")
print(f"   Jobs found: {results['total_jobs_found']}")
print(f"   Filtering efficiency: {results['filtering_efficiency']}")
print(f"   Average quality: {results['avg_quality_score']:.2f}")
print(f"   Salary range: ${results['salary_range']['min']:,} - ${results['salary_range']['max']:,}")

# Technology breakdown
tech_analysis = results.get('technology_breakdown', {})
for tech, count in tech_analysis.items():
    print(f"   {tech.upper()}: {count} jobs")
```

## 💾 Integration with Vector Database

```python
from src.database.job_vector_store import JobVectorStore

# Scrape LLM jobs
scraper = create_llm_engineer_scraper()
results = await scraper.search_llm_jobs(max_pages=3)

# Store in vector database
vector_store = JobVectorStore(db_path="./llm_jobs_db")
added, failed = vector_store.add_jobs(results['jobs'])

print(f"Stored {added} LLM jobs in vector database")

# Search with semantic similarity
llm_matches = vector_store.search_jobs("transformer neural network", n_results=5)
```

## 🎨 Practical Examples

### Example 1: Find Remote Senior LLM Roles

```python
# Create senior-level scraper
scraper = create_senior_llm_scraper()

# Search for senior positions
results = await scraper.search_llm_jobs(
    seniority_level="senior",
    max_pages=2
)

# Filter for remote work (done by LLM scraper automatically)
remote_jobs = [job for job in results['jobs'] 
               if job.remote_type in [RemoteType.REMOTE, RemoteType.HYBRID]]

print(f"Found {len(remote_jobs)} senior remote LLM jobs")
```

### Example 2: Comprehensive LLM Job Collection

```python
# Use interactive example script
# This provides a complete workflow:
# 1. Choose scraper type (general/senior/junior)  
# 2. Configure search parameters
# 3. Scrape jobs with filtering
# 4. Store in vector database
# 5. Test semantic search

python examples/llm_job_search.py
```

### Example 3: Technology Analysis

```python
scraper = create_llm_engineer_scraper()
results = await scraper.search_llm_jobs(max_pages=3)

# Analyze technology mentions
jobs = results['jobs']
tech_keywords = ["llm", "gpt", "transformer", "pytorch", "tensorflow"]

for tech in tech_keywords:
    count = sum(1 for job in jobs 
                if tech in f"{job.title} {job.description}".lower())
    percentage = count / len(jobs) * 100
    print(f"{tech.upper()}: {count} jobs ({percentage:.1f}%)")
```

## 🔧 Customization

Create your own LLM-focused filter:

```python
from src.scrapers.smart_job_filter import JobFilter
from src.scrapers.filtered_ziprecruiter_scraper import FilteredZipRecruiterScraper

custom_llm_filter = JobFilter(
    required_keywords=[
        "llm", "transformer", "pytorch", "huggingface",
        "machine learning", "ai engineer"
    ],
    exclude_keywords=[
        "sales", "marketing", "commission", "intern"
    ],
    min_quality_score=0.75,
    min_salary=100000,
    max_salary=300000,
    allowed_job_types=[JobType.FULL_TIME],
    allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID]
)

custom_scraper = FilteredZipRecruiterScraper(custom_llm_filter)
results = await custom_scraper.search_houston_jobs("llm engineer", max_pages=2)
```

## 🚀 Commands

```bash
# Test the LLM scraper
uv run python tests/test_llm_scraper.py

# Interactive LLM job search
uv run python examples/llm_job_search.py

# Use in your own script
from src.scrapers.llm_engineer_scraper import create_llm_engineer_scraper
```

## 💡 Tips for Best Results

1. **Start with General Scraper** - Test with broad settings first
2. **Use Strict Mode for Senior Roles** - Higher quality filtering for experienced positions  
3. **Monitor Filtering Efficiency** - Aim for 20-50% of scraped jobs being kept
4. **Combine with Vector Search** - Store results for semantic job matching
5. **Check Technology Breakdown** - Understand what skills are in demand
6. **Test Multiple Locations** - LLM jobs may be concentrated in tech hubs

## 🎯 Expected Results

For Houston area LLM Engineer searches:

- **General Mode**: 5-15 jobs per search (broader criteria)
- **Senior Mode**: 2-8 jobs per search (stricter filtering)  
- **Quality Score**: 0.7+ average (high-quality job posts)
- **Salary Range**: $80k-$300k+ (competitive AI/ML salaries)
- **Technologies**: PyTorch, TensorFlow, HuggingFace, LangChain commonly mentioned

The LLM Engineer scraper is designed to find those cutting-edge AI roles that are often hard to discover with traditional job search methods! 🤖
