# Vector Store Setup Guide

## 🚀 Quick Setup

### 1. Set OpenAI API Key

You'll need an OpenAI API key to generate embeddings:

```bash
# Get your API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Test the Vector Store

```bash
# Test with sample data (no scraping)
uv run python test_vector_store.py

# Test the complete pipeline
uv run python job_pipeline.py
```

## 📊 What the Vector Store Does

### **Job Storage:**
- Converts job descriptions to embeddings using OpenAI `text-embedding-3-small`
- Stores jobs in ChromaDB for fast similarity search
- Handles metadata (salary, location, skills, etc.)

### **Smart Search:**
- Semantic search (understands meaning, not just keywords)
- Example: "machine learning" finds "Data Scientist", "AI Engineer", "ML Engineer"
- Filters by location, job type, remote work, salary

### **Houston Focus:**
- Optimized for Houston job market
- Understands local industries (energy, medical, aerospace)
- Geographic context awareness

## 🔍 Example Usage

```python
from job_pipeline import JobSearchPipeline

# Initialize pipeline
pipeline = JobSearchPipeline()

# Search for jobs
results = pipeline.search_jobs("python developer", n_results=5)

# Search with filters
remote_jobs = pipeline.search_jobs(
    "software engineer", 
    n_results=10,
    remote_filter="remote",
    salary_min_filter=80000
)
```

## 💰 Cost Estimate

**OpenAI Embedding Costs:**
- ~$0.03/month for 10,000 jobs
- ~$0.30/month for 100,000 jobs
- Extremely affordable for personal use

## 🗂️ File Structure

```
job-search/
├── job_vector_store.py    # Core vector database
├── job_pipeline.py        # Complete scrape->store->search pipeline
├── test_vector_store.py   # Test script
└── houston_jobs_db/       # ChromaDB storage (created automatically)
```

## 🚨 Important Notes

1. **API Key Required**: OpenAI API key needed for embeddings
2. **Storage**: ChromaDB files stored locally in `houston_jobs_db/`
3. **Internet**: Required for OpenAI API calls during job storage
4. **Search**: Once stored, search works offline (except for new embeddings)

## 🎯 Next Steps

After testing the vector store, you can:
1. Run the complete pipeline to collect Houston jobs
2. Build the Gradio web interface
3. Schedule regular job collection
4. Add more job sources
