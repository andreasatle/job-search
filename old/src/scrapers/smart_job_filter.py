"""
Smart job filtering system to reduce irrelevant jobs during scraping.
Supports both traditional keyword filtering and LLM-based intelligent filtering.
"""

import re
import os
import asyncio
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from ..models.job_models import JobListing, JobType, RemoteType


@dataclass
class JobFilter:
    """Configuration for filtering jobs during scraping."""
    
    # Keywords to REQUIRE (at least one must be present)
    required_keywords: List[str] = None
    
    # Keywords to EXCLUDE (job rejected if any present)
    exclude_keywords: List[str] = None
    
    # Minimum quality score (0-1)
    min_quality_score: float = 0.5
    
    # Minimum salary (if specified)
    min_salary: Optional[int] = None
    
    # Maximum salary (if specified) 
    max_salary: Optional[int] = None
    
    # Required job types
    allowed_job_types: List[JobType] = None
    
    # Required remote types
    allowed_remote_types: List[RemoteType] = None
    
    # Minimum description length
    min_description_length: int = 100
    
    # Companies to exclude
    exclude_companies: List[str] = None
    
    # Experience levels to exclude
    exclude_experience_levels: List[str] = None
    
    # Enable LLM-based filtering
    use_llm: bool = False
    
    # LLM filtering prompt template
    llm_filter_prompt: Optional[str] = None


class SmartJobFilter:
    """Intelligent job filtering to keep only relevant positions."""
    
    def __init__(self, filter_config: JobFilter):
        """Initialize with filter configuration."""
        self.config = filter_config
        
        # Convert keywords to lowercase for case-insensitive matching
        self.required_keywords = [kw.lower() for kw in (filter_config.required_keywords or [])]
        self.exclude_keywords = [kw.lower() for kw in (filter_config.exclude_keywords or [])]
        self.exclude_companies = [comp.lower() for comp in (filter_config.exclude_companies or [])]
        self.exclude_experience = [exp.lower() for exp in (filter_config.exclude_experience_levels or [])]
        
        # Initialize LLM client if enabled
        self.openai_client = None
        if filter_config.use_llm:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize OpenAI client for LLM filtering."""
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️  Warning: OPENAI_API_KEY not found. LLM filtering disabled.")
                return
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("✅ LLM filtering enabled with OpenAI")
        except ImportError:
            print("⚠️  Warning: openai package not installed. LLM filtering disabled.")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize OpenAI client: {e}")
    
    async def _llm_evaluate_job(self, job: JobListing) -> Tuple[bool, str, float]:
        """
        Use LLM to evaluate job relevance and quality.
        
        Returns:
            (should_keep: bool, reason: str, quality_score: float)
        """
        if not self.openai_client:
            return True, "LLM not available", job.quality_score
        
        # Default prompt if none provided
        default_prompt = """
        You are an expert job market analyst. Evaluate this job posting for relevance and quality.
        
        Consider:
        1. Is this a legitimate, well-written job posting?
        2. Does it match software engineering, AI/ML, or tech roles?
        3. Are the requirements reasonable and specific?
        4. Is the salary/benefits information clear?
        5. Does the company seem reputable?
        
        Job Details:
        Title: {title}
        Company: {company}
        Location: {location}
        Salary: {salary}
        Type: {job_type}
        Remote: {remote_type}
        Description: {description}
        
        Respond in JSON format:
        {{
            "should_keep": true/false,
            "quality_score": 0.0-1.0,
            "reason": "Brief explanation",
            "red_flags": ["list", "of", "concerns"],
            "positive_signals": ["list", "of", "good", "signs"]
        }}
        """
        
        prompt = self.config.llm_filter_prompt or default_prompt
        
        # Format the prompt with job data
        formatted_prompt = prompt.format(
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary_text or "Not specified",
            job_type=job.job_type.value,
            remote_type=job.remote_type.value,
            description=job.description[:500] + "..." if len(job.description) > 500 else job.description
        )
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a job market analyst. Respond only in valid JSON format."},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            result = json.loads(content)
            
            should_keep = result.get("should_keep", True)
            quality_score = max(0.0, min(1.0, result.get("quality_score", job.quality_score)))
            reason = result.get("reason", "LLM evaluation")
            
            # Update job quality score with LLM assessment
            job.quality_score = quality_score
            
            return should_keep, reason, quality_score
            
        except json.JSONDecodeError:
            print(f"⚠️  LLM returned invalid JSON for job: {job.title}")
            return True, "LLM JSON parse error", job.quality_score
        except Exception as e:
            print(f"⚠️  LLM evaluation error for {job.title}: {e}")
            return True, f"LLM error: {str(e)}", job.quality_score
    
    def should_keep_job(self, job: JobListing) -> Tuple[bool, str]:
        """
        Determine if a job should be kept based on filters.
        
        Returns:
            (keep: bool, reason: str)
        """
        # Quality score filter
        if job.quality_score < self.config.min_quality_score:
            return False, f"Quality score {job.quality_score:.2f} below minimum {self.config.min_quality_score}"
        
        # Description length filter (disabled for testing)
        if len(job.description) < 1:  # Only reject completely empty descriptions
            return False, f"Description too short ({len(job.description)} chars)"
        
        # Salary filters
        if self.config.min_salary and job.salary_min and job.salary_min < self.config.min_salary:
            return False, f"Salary ${job.salary_min:,} below minimum ${self.config.min_salary:,}"
        
        if self.config.max_salary and job.salary_max and job.salary_max > self.config.max_salary:
            return False, f"Salary ${job.salary_max:,} above maximum ${self.config.max_salary:,}"
        
        # Job type filter
        if self.config.allowed_job_types and job.job_type not in self.config.allowed_job_types:
            return False, f"Job type {job.job_type} not in allowed types"
        
        # Remote type filter
        if self.config.allowed_remote_types and job.remote_type not in self.config.allowed_remote_types:
            return False, f"Remote type {job.remote_type} not in allowed types"
        
        # Company exclusion filter
        for excluded_company in self.exclude_companies:
            if excluded_company in job.company.lower():
                return False, f"Company '{job.company}' is excluded"
        
        # Experience level exclusion
        if job.experience_level:
            for excluded_exp in self.exclude_experience:
                if excluded_exp in job.experience_level.lower():
                    return False, f"Experience level '{job.experience_level}' is excluded"
        
        # Create searchable text (title + description + requirements + skills)
        searchable_text = " ".join([
            job.title,
            job.description,
            job.requirements or "",
            " ".join(job.skills)
        ]).lower()
        
        # Exclude keywords filter (any match = reject)
        for exclude_kw in self.exclude_keywords:
            if exclude_kw in searchable_text:
                return False, f"Contains excluded keyword: '{exclude_kw}'"
        
        # Required keywords filter (at least one must match)
        if self.required_keywords:
            has_required_keyword = any(req_kw in searchable_text for req_kw in self.required_keywords)
            if not has_required_keyword:
                return False, f"Missing required keywords: {self.required_keywords}"
        
        return True, "Passed all filters"
    
    def filter_jobs(self, jobs: List[JobListing], verbose: bool = True) -> List[JobListing]:
        """
        Filter a list of jobs and return only those that pass.
        
        Args:
            jobs: List of job listings to filter
            verbose: Print filtering statistics
            
        Returns:
            Filtered list of job listings
        """
        if not jobs:
            return []
        
        # Use async filtering if LLM is enabled
        if self.config.use_llm:
            return asyncio.run(self._filter_jobs_async(jobs, verbose))
        else:
            return self._filter_jobs_sync(jobs, verbose)
    
    def _filter_jobs_sync(self, jobs: List[JobListing], verbose: bool = True) -> List[JobListing]:
        """Synchronous job filtering (traditional keyword-based)."""
        kept_jobs = []
        filter_stats = {}
        
        for job in jobs:
            should_keep, reason = self.should_keep_job(job)
            
            if should_keep:
                kept_jobs.append(job)
            else:
                # Track rejection reasons for stats
                filter_stats[reason] = filter_stats.get(reason, 0) + 1
        
        if verbose:
            self._print_filter_stats(jobs, kept_jobs, filter_stats, "Traditional")
        
        return kept_jobs
    
    async def _filter_jobs_async(self, jobs: List[JobListing], verbose: bool = True) -> List[JobListing]:
        """Asynchronous job filtering with LLM evaluation."""
        kept_jobs = []
        filter_stats = {}
        llm_stats = {"evaluated": 0, "llm_rejected": 0, "llm_approved": 0}
        
        for i, job in enumerate(jobs):
            # First apply traditional filters
            should_keep, reason = self.should_keep_job(job)
            
            if not should_keep:
                filter_stats[reason] = filter_stats.get(reason, 0) + 1
                continue
            
            # If traditional filters pass, use LLM for deeper evaluation
            llm_keep, llm_reason, llm_quality = await self._llm_evaluate_job(job)
            llm_stats["evaluated"] += 1
            
            if llm_keep:
                kept_jobs.append(job)
                llm_stats["llm_approved"] += 1
                if verbose and i % 5 == 0:
                    print(f"🤖 LLM evaluated {i+1}/{len(jobs)} jobs...")
            else:
                filter_stats[f"LLM: {llm_reason}"] = filter_stats.get(f"LLM: {llm_reason}", 0) + 1
                llm_stats["llm_rejected"] += 1
        
        if verbose:
            self._print_filter_stats(jobs, kept_jobs, filter_stats, "LLM-Enhanced")
            self._print_llm_stats(llm_stats)
        
        return kept_jobs
    
    def _print_filter_stats(self, input_jobs: List[JobListing], kept_jobs: List[JobListing], 
                           filter_stats: dict, mode: str):
        """Print filtering statistics."""
        print(f"\n🎯 {mode} Filtering Results:")
        print(f"   📥 Input jobs: {len(input_jobs)}")
        print(f"   ✅ Kept jobs: {len(kept_jobs)} ({len(kept_jobs)/len(input_jobs)*100:.1f}%)")
        print(f"   ❌ Filtered out: {len(input_jobs) - len(kept_jobs)}")
        
        if filter_stats:
            print(f"\n📊 Rejection reasons:")
            for reason, count in sorted(filter_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {reason}: {count}")
    
    def _print_llm_stats(self, llm_stats: dict):
        """Print LLM-specific statistics."""
        print(f"\n🤖 LLM Evaluation Stats:")
        print(f"   🔍 Jobs evaluated by LLM: {llm_stats['evaluated']}")
        print(f"   ✅ LLM approved: {llm_stats['llm_approved']}")
        print(f"   ❌ LLM rejected: {llm_stats['llm_rejected']}")
        if llm_stats['evaluated'] > 0:
            approval_rate = llm_stats['llm_approved'] / llm_stats['evaluated'] * 100
            print(f"   📈 LLM approval rate: {approval_rate:.1f}%")


# Pre-configured filters for common use cases
class FilterPresets:
    """Pre-configured job filters for common scenarios."""
    
    @staticmethod
    def software_engineer(use_llm: bool = False) -> JobFilter:
        """Filter for software engineering positions."""
        return JobFilter(
            required_keywords=["python", "javascript", "react", "node", "django", "flask", "api", "backend", "frontend", "full stack", "software", "developer", "engineer"],
            exclude_keywords=["sales", "marketing", "recruiter", "cold calling", "door to door", "commission only", "pyramid", "mlm"],
            min_quality_score=0.6,
            min_salary=70000,
            allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT, JobType.UNKNOWN],
            min_description_length=10,  # Reduced for LLM filtering
            exclude_companies=["door to door", "cold calling", "commission"],
            exclude_experience_levels=["entry level", "intern"],
            use_llm=use_llm
        )
    
    @staticmethod
    def data_scientist(use_llm: bool = False) -> JobFilter:
        """Filter for data science positions."""
        return JobFilter(
            required_keywords=["python", "sql", "machine learning", "data", "analytics", "tensorflow", "pytorch", "pandas", "numpy", "science", "ai", "ml"],
            exclude_keywords=["sales", "marketing", "cold calling", "telemarketing", "door to door"],
            min_quality_score=0.7,
            min_salary=80000,
            allowed_job_types=[JobType.FULL_TIME, JobType.UNKNOWN],
            min_description_length=10 if use_llm else 200,
            use_llm=use_llm
        )
    
    @staticmethod
    def remote_only() -> JobFilter:
        """Filter for remote work only."""
        return JobFilter(
            allowed_remote_types=[RemoteType.REMOTE],
            min_quality_score=0.5,
            min_description_length=100
        )
    
    @staticmethod
    def senior_level(use_llm: bool = False) -> JobFilter:
        """Filter for senior-level positions."""
        return JobFilter(
            required_keywords=["senior", "lead", "principal", "architect", "manager", "director"],
            min_quality_score=0.7,
            min_salary=100000,
            allowed_job_types=[JobType.FULL_TIME, JobType.UNKNOWN],
            exclude_experience_levels=["entry", "junior", "intern"],
            min_description_length=10 if use_llm else 150,
            use_llm=use_llm
        )
    
    @staticmethod
    def startup_roles() -> JobFilter:
        """Filter for startup and tech company roles."""
        return JobFilter(
            required_keywords=["startup", "tech", "saas", "platform", "api", "cloud", "aws", "kubernetes"],
            exclude_keywords=["enterprise", "legacy", "mainframe", "cobol"],
            min_quality_score=0.6,
            allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID]
        )
    
    @staticmethod
    def high_paying(use_llm: bool = False) -> JobFilter:
        """Filter for high-paying positions."""
        return JobFilter(
            min_salary=120000,
            min_quality_score=0.8,
            allowed_job_types=[JobType.FULL_TIME, JobType.UNKNOWN],
            min_description_length=10 if use_llm else 200,
            use_llm=use_llm
        )
    
    @staticmethod
    def llm_engineer(strict_mode: bool = False) -> JobFilter:
        """Filter specifically for LLM Engineer and AI/ML positions with LLM evaluation."""
        required_keywords = [
            # LLM/AI specific
            "llm", "large language model", "gpt", "bert", "transformer",
            "machine learning", "artificial intelligence", "ai engineer",
            "ml engineer", "mlops", "ai/ml",
            
            # Deep learning frameworks
            "pytorch", "tensorflow", "keras", "huggingface", "transformers",
            "langchain", "llamaindex", "openai", "anthropic",
            
            # AI/ML technologies
            "python", "machine learning", "deep learning", "neural network",
            "nlp", "natural language processing", "computer vision",
            "reinforcement learning", "generative ai", "conversational ai",
            
            # Cloud AI platforms
            "aws sagemaker", "azure ml", "google cloud ai", "vertex ai",
            "databricks", "mlflow", "kubeflow",
            
            # Vector databases and embeddings
            "vector database", "embeddings", "chromadb", "pinecone", "weaviate",
            "faiss", "semantic search", "retrieval", "rag"
        ]
        
        exclude_keywords = [
            "sales", "marketing", "recruiter", "cold calling", "door to door",
            "commission only", "mlm", "pyramid", "telemarketing",
            "intern", "unpaid", "volunteer", "entry level",
            "real estate", "insurance", "retail", "restaurant", "driver",
            "warehouse", "construction", "manual labor"
        ]
        
        llm_prompt = """
        You are an expert AI/ML recruiter. Evaluate this job posting for LLM Engineer or AI/ML roles.
        
        Consider:
        1. Does this role involve LLMs, AI/ML, or deep learning?
        2. Are the technical requirements relevant and realistic?
        3. Is this a legitimate tech company or position?
        4. Does the salary match the role complexity?
        5. Are there clear growth opportunities?
        
        Job Details:
        Title: {title}
        Company: {company}
        Location: {location}
        Salary: {salary}
        Type: {job_type}
        Remote: {remote_type}
        Description: {description}
        
        Focus on: LLM, AI, ML, deep learning, NLP, computer vision, PyTorch, TensorFlow, transformers, etc.
        
        Respond in JSON format:
        {{
            "should_keep": true/false,
            "quality_score": 0.0-1.0,
            "reason": "Brief explanation",
            "ai_relevance": "high/medium/low",
            "tech_stack_match": true/false
        }}
        """
        
        if strict_mode:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.8,
                min_salary=120000,
                max_salary=400000,
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT, JobType.UNKNOWN],
                allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
                min_description_length=10,
                exclude_experience_levels=["entry level", "intern", "junior"],
                use_llm=True,
                llm_filter_prompt=llm_prompt
            )
        else:
            return JobFilter(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords,
                min_quality_score=0.65,
                min_salary=80000,
                max_salary=500000,
                allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT, JobType.UNKNOWN],
                allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID, RemoteType.ONSITE],
                min_description_length=10,
                use_llm=True,
                llm_filter_prompt=llm_prompt
            )


# Example usage functions
def create_custom_filter() -> JobFilter:
    """Example of creating a custom filter."""
    return JobFilter(
        required_keywords=["python", "machine learning", "remote"],
        exclude_keywords=["sales", "cold calling", "door to door", "commission only"],
        min_quality_score=0.7,
        min_salary=90000,
        max_salary=200000,
        allowed_job_types=[JobType.FULL_TIME, JobType.CONTRACT],
        allowed_remote_types=[RemoteType.REMOTE, RemoteType.HYBRID],
        min_description_length=150,
        exclude_companies=["spam company", "sketchy inc"],
        exclude_experience_levels=["intern", "entry level"]
    )


if __name__ == "__main__":
    # Example usage
    filter_config = FilterPresets.software_engineer()
    job_filter = SmartJobFilter(filter_config)
    
    print("🎯 Smart Job Filter Example")
    print("==========================")
    print(f"Required keywords: {filter_config.required_keywords[:5]}...")
    print(f"Exclude keywords: {filter_config.exclude_keywords}")
    print(f"Min quality score: {filter_config.min_quality_score}")
    print(f"Min salary: ${filter_config.min_salary:,}" if filter_config.min_salary else "No salary filter")
