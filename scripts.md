# Job Search Scripts

This document lists all available scripts you can run with your job search system.

## 🚀 Quick Start Commands

### Command-Line Interface
The main scraper now uses argparse for flexible command-line usage:

```bash
# Show help and all available options
uv run python -m src.scraper --help

# List all available query categories
uv run python -m src.scraper --list-categories

# List all 31 available queries
uv run python -m src.scraper --list-queries
```

### Basic Searches
```bash
# Search for specific query
uv run python -m src.scraper --query "LLM engineer" --max-jobs 10

# Random query from any category
uv run python -m src.scraper --random --max-jobs 5

# Search specific category
uv run python -m src.scraper --category "Core LLM / Generative AI" --max-jobs 8

# Multiple specific queries
uv run python -m src.scraper --multiple "LLM engineer" "RAG engineer" --max-jobs-per-query 4

# Comprehensive search (one from each category)
uv run python -m src.scraper --comprehensive --max-jobs-per-category 3
```

### Output Options
```bash
# Brief output (title, company, preview)
uv run python -m src.scraper --query "Python AI engineer" --brief

# Just show counts, no job details
uv run python -m src.scraper --random --no-display

# Normal detailed output (default)
uv run python -m src.scraper --query "LLM scientist" --max-jobs 5
```

### Other Module Tests
```bash
# Show all available queries organized by category
uv run python -m src.queries

# Test specific query (replaces individual scraper test)
uv run python -m src.scraper --query "python developer" --max-jobs 5
```

## 🎯 Specific Search Types

### Search by Category
```python
# In Python shell
from src.scraper import search_by_category
import asyncio

# Core LLM jobs
jobs = asyncio.run(search_by_category("Core LLM / Generative AI", max_jobs=5))

# AI Agents jobs  
jobs = asyncio.run(search_by_category("Agentic AI / AI Agents", max_jobs=5))

# Python ML jobs
jobs = asyncio.run(search_by_category("Python + ML", max_jobs=5))

# RAG/Vector jobs
jobs = asyncio.run(search_by_category("RAG / Vector DB / LangChain", max_jobs=5))

# Startup jobs
jobs = asyncio.run(search_by_category("Catch-All / Startup Variants", max_jobs=5))
```

### Random and Comprehensive Searches
```python
from src.scraper import search_with_random_query, comprehensive_search

# Random query from any category
jobs = asyncio.run(search_with_random_query(max_jobs=10))

# One query from each category (comprehensive)
jobs = asyncio.run(comprehensive_search(max_jobs_per_category=3))
```

### Multiple Specific Queries
```python
from src.scraper import search_multiple_queries

queries = ["LLM engineer", "RAG engineer", "Python AI engineer"]
jobs = asyncio.run(search_multiple_queries(queries, max_jobs_per_query=5))
```

## 🔧 Setup Commands

### Install Browser Dependencies
```bash
uv run playwright install chromium
```

## 📋 Available Query Categories

1. **Core LLM / Generative AI** (6 queries)
   - LLM engineer, Generative AI engineer, etc.

2. **Agentic AI / AI Agents** (6 queries)
   - Agentic AI engineer, AI agent developer, etc.

3. **Python + ML** (6 queries)
   - Python AI engineer, ML engineer Python, etc.

4. **RAG / Vector DB / LangChain** (6 queries)
   - RAG engineer, Vector database AI, etc.

5. **Catch-All / Startup Variants** (6 queries)
   - Founding AI engineer, AI researcher, etc.

## 🧪 Testing Individual Components

```bash
# Test query system
uv run python -c "from src.queries import main; main()"

# Test scraper with specific query
uv run python -c "
import asyncio
from src.scraper import quick_search
jobs = asyncio.run(quick_search('LLM engineer', max_jobs=3))
print(f'Found {len(jobs)} jobs')
"
```

## ⚡ One-liner Examples

```bash
# Quick LLM job search
uv run python -c "import asyncio; from src.scraper import quick_search; jobs = asyncio.run(quick_search('LLM engineer', 5)); print(f'Found {len(jobs)} jobs'); [job.display() for job in jobs[:3]]"

# Show random query
uv run python -c "from src.queries import get_random_query; print(f'Random query: {get_random_query()}')"

# List all queries
uv run python -c "from src.queries import get_all_queries; [print(f'• {q}') for q in get_all_queries()]"
```

All scripts automatically fetch full job descriptions using the enhanced meta tag extraction and loading strategies!
