"""Vector database storage system for job posts using ChromaDB and OpenAI embeddings."""
import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

import chromadb
from chromadb.config import Settings
import openai
from openai import OpenAI

from job_models import JobListing, ScrapingResult


class JobVectorStore:
    """Vector database for storing and searching job posts."""
    
    def __init__(self, 
                 db_path: str = "./job_vector_db",
                 openai_api_key: Optional[str] = None,
                 embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the job vector store.
        
        Args:
            db_path: Path to store the ChromaDB database
            openai_api_key: OpenAI API key (or from environment)
            embedding_model: OpenAI embedding model to use
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="houston_jobs",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        print(f"✅ JobVectorStore initialized")
        print(f"📁 Database path: {db_path}")
        print(f"🤖 Embedding model: {embedding_model}")
        print(f"📊 Current jobs in database: {self.collection.count()}")
    
    def _create_job_text(self, job: JobListing) -> str:
        """Create a comprehensive text representation of a job for embedding."""
        text_parts = []
        
        # Core information
        text_parts.append(f"Job Title: {job.title}")
        text_parts.append(f"Company: {job.company}")
        text_parts.append(f"Location: {job.location}")
        
        # Job details
        if job.job_type:
            text_parts.append(f"Job Type: {job.job_type.value}")
        
        if job.remote_type:
            text_parts.append(f"Work Type: {job.remote_type.value}")
        
        # Salary information
        if job.salary_text:
            text_parts.append(f"Salary: {job.salary_text}")
        elif job.salary_min or job.salary_max:
            if job.salary_min and job.salary_max:
                text_parts.append(f"Salary: ${job.salary_min:,.0f} - ${job.salary_max:,.0f}")
            elif job.salary_min:
                text_parts.append(f"Salary: ${job.salary_min:,.0f}+")
            elif job.salary_max:
                text_parts.append(f"Salary: Up to ${job.salary_max:,.0f}")
        
        # Skills and requirements
        if job.skills:
            text_parts.append(f"Skills: {', '.join(job.skills)}")
        
        if job.experience_level:
            text_parts.append(f"Experience Level: {job.experience_level}")
        
        if job.education:
            text_parts.append(f"Education: {job.education}")
        
        # Description (truncate if too long)
        if job.description:
            description = job.description.strip()
            if len(description) > 1000:
                description = description[:1000] + "..."
            text_parts.append(f"Description: {description}")
        
        if job.requirements:
            requirements = job.requirements.strip()
            if len(requirements) > 500:
                requirements = requirements[:500] + "..."
            text_parts.append(f"Requirements: {requirements}")
        
        return "\n".join(text_parts)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            raise
    
    def _create_job_id(self, job: JobListing) -> str:
        """Create a unique ID for a job."""
        # Use existing job_id if available, otherwise create from content
        if job.job_id:
            return f"{job.source}_{job.job_id}"
        
        # Create ID from job content
        content = f"{job.source}_{job.title}_{job.company}_{job.location}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_job(self, job: JobListing) -> bool:
        """
        Add a single job to the vector store.
        
        Args:
            job: JobListing to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            job_id = self._create_job_id(job)
            
            # Check if job already exists
            existing = self.collection.get(ids=[job_id])
            if existing['ids']:
                print(f"⚠️  Job already exists: {job.title} at {job.company}")
                return True
            
            # Create text for embedding
            job_text = self._create_job_text(job)
            
            # Get embedding
            print(f"🔄 Creating embedding for: {job.title} at {job.company}")
            embedding = self._get_embedding(job_text)
            
            # Prepare metadata
            metadata = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source,
                "url": job.url,
                "job_type": job.job_type.value if job.job_type else None,
                "remote_type": job.remote_type.value if job.remote_type else None,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_text": job.salary_text,
                "skills": json.dumps(job.skills) if job.skills else None,
                "experience_level": job.experience_level,
                "education": job.education,
                "quality_score": job.quality_score,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                "scraped_date": job.scraped_date.isoformat(),
                "external_apply": job.external_apply
            }
            
            # Add to collection
            self.collection.add(
                ids=[job_id],
                embeddings=[embedding],
                documents=[job_text],
                metadatas=[metadata]
            )
            
            print(f"✅ Added job: {job.title} at {job.company}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding job {job.title}: {e}")
            return False
    
    def add_jobs_batch(self, jobs: List[JobListing], batch_size: int = 10) -> Dict[str, int]:
        """
        Add multiple jobs in batches.
        
        Args:
            jobs: List of JobListing objects
            batch_size: Number of jobs to process at once
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "duplicate": 0}
        
        print(f"📦 Adding {len(jobs)} jobs in batches of {batch_size}")
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            print(f"🔄 Processing batch {i//batch_size + 1}/{(len(jobs)-1)//batch_size + 1}")
            
            for job in batch:
                success = self.add_job(job)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        print(f"📊 Batch results: {results['success']} added, {results['failed']} failed")
        return results
    
    def search_jobs(self, 
                   query: str, 
                   n_results: int = 10,
                   location_filter: Optional[str] = None,
                   job_type_filter: Optional[str] = None,
                   remote_filter: Optional[str] = None,
                   salary_min_filter: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for jobs using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            location_filter: Filter by location (contains match)
            job_type_filter: Filter by job type
            remote_filter: Filter by remote type
            salary_min_filter: Filter by minimum salary
            
        Returns:
            List of job results with metadata and scores
        """
        try:
            print(f"🔍 Searching for: '{query}'")
            
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Build where clause for filtering
            where_clause = {}
            if location_filter:
                where_clause["location"] = {"$contains": location_filter}
            if job_type_filter:
                where_clause["job_type"] = job_type_filter
            if remote_filter:
                where_clause["remote_type"] = remote_filter
            if salary_min_filter:
                where_clause["salary_min"] = {"$gte": salary_min_filter}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0], 
                results["distances"][0]
            )):
                # Convert distance to similarity score (0-1, higher is better)
                similarity_score = max(0, 1 - distance)
                
                # Parse skills back from JSON
                skills = []
                if metadata.get("skills"):
                    try:
                        skills = json.loads(metadata["skills"])
                    except:
                        pass
                
                result = {
                    "rank": i + 1,
                    "similarity_score": similarity_score,
                    "title": metadata["title"],
                    "company": metadata["company"],
                    "location": metadata["location"],
                    "source": metadata["source"],
                    "url": metadata["url"],
                    "job_type": metadata.get("job_type"),
                    "remote_type": metadata.get("remote_type"),
                    "salary_min": metadata.get("salary_min"),
                    "salary_max": metadata.get("salary_max"),
                    "salary_text": metadata.get("salary_text"),
                    "skills": skills,
                    "experience_level": metadata.get("experience_level"),
                    "education": metadata.get("education"),
                    "quality_score": metadata.get("quality_score"),
                    "posted_date": metadata.get("posted_date"),
                    "scraped_date": metadata.get("scraped_date"),
                    "document_text": doc
                }
                formatted_results.append(result)
            
            print(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching jobs: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            total_jobs = self.collection.count()
            
            # Get sample of jobs for analysis
            sample_size = min(1000, total_jobs)
            sample = self.collection.get(limit=sample_size, include=["metadatas"])
            
            # Analyze metadata
            sources = {}
            job_types = {}
            locations = {}
            remote_types = {}
            
            for metadata in sample["metadatas"]:
                # Count sources
                source = metadata.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
                
                # Count job types
                job_type = metadata.get("job_type")
                if job_type:
                    job_types[job_type] = job_types.get(job_type, 0) + 1
                
                # Count locations
                location = metadata.get("location", "unknown")
                locations[location] = locations.get(location, 0) + 1
                
                # Count remote types
                remote_type = metadata.get("remote_type")
                if remote_type:
                    remote_types[remote_type] = remote_types.get(remote_type, 0) + 1
            
            return {
                "total_jobs": total_jobs,
                "sources": sources,
                "job_types": job_types,
                "locations": dict(list(locations.items())[:10]),  # Top 10 locations
                "remote_types": remote_types,
                "sample_size": len(sample["metadatas"]),
                "database_path": self.db_path,
                "embedding_model": self.embedding_model
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {"total_jobs": 0, "error": str(e)}
    
    def clear_database(self) -> bool:
        """Clear all jobs from the database."""
        try:
            self.chroma_client.delete_collection("houston_jobs")
            self.collection = self.chroma_client.create_collection(
                name="houston_jobs",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Database cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            return False
