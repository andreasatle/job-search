"""
Vector database for job storage using ChromaDB for semantic search and duplicate detection.
Building this step by step to be able to verify each component.
"""

import os
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings

from .job import Job


class JobVectorDB:
    """Vector database for storing and searching jobs with embedding-based similarity."""
    
    def __init__(self, db_path: str = "./job_vector_db", collection_name: str = "jobs"):
        """Initialize the vector database."""
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Create database directory
        os.makedirs(db_path, exist_ok=True)
        
        print(f"🔗 Initializing vector database at: {db_path}")
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"📂 Using existing collection: {collection_name}")
        except Exception:  # Catch any exception (NotFoundError, ValueError, etc.)
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Job search results with embeddings"}
            )
            print(f"📂 Created new collection: {collection_name}")
    
    def _create_job_text(self, job: Job) -> str:
        """Create searchable text from job for embedding."""
        # Combine key fields for embedding
        parts = [
            job.title,
            job.company,
            job.location,
            job.description
        ]
        
        # Add salary if available
        if job.salary:
            parts.append(f"Salary: {job.salary}")
            
        return " | ".join(filter(None, parts))
    
    def _create_job_metadata(self, job: Job) -> Dict:
        """Create metadata dict for storage."""
        return {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.url or "",
            "salary": job.salary or "",
            "remote": str(job.remote) if job.remote is not None else "",
            "posted_date": job.posted_date.isoformat() if job.posted_date else "",
            "added_at": datetime.now().isoformat(),
            "source": "remoteok"  # We can expand this later
        }
    
    def add_job(self, job: Job) -> bool:
        """Add a single job to the vector database."""
        # Create unique ID (we'll use URL if available, otherwise generate)
        job_id = job.url if job.url else str(uuid.uuid4())
        
        # Check if job already exists
        existing = self._get_job_by_id(job_id)
        if existing:
            print(f"⚠️  Job already exists: {job.title} at {job.company}")
            return False
        
        # Create embedding text and metadata
        text = self._create_job_text(job)
        metadata = self._create_job_metadata(job)
        
        try:
            # Add to ChromaDB
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[job_id]
            )
            
            print(f"✅ Added job: {job.title} at {job.company}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding job: {e}")
            return False
    
    def add_jobs(self, jobs: List[Job]) -> int:
        """Add multiple jobs to the vector database."""
        added_count = 0
        
        print(f"📥 Adding {len(jobs)} jobs to vector database...")
        
        for i, job in enumerate(jobs, 1):
            if self.add_job(job):
                added_count += 1
            
            # Progress indicator for large batches
            if i % 10 == 0 or i == len(jobs):
                print(f"   Progress: {i}/{len(jobs)} processed")
        
        print(f"💾 Successfully added {added_count} new jobs to vector database")
        return added_count
    
    def _get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Check if a job exists by ID."""
        try:
            result = self.collection.get(
                ids=[job_id],
                include=["documents", "metadatas"]
            )
            
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
            
        except Exception:
            return None
    
    def get_stats(self) -> Dict:
        """Get basic statistics about the vector database."""
        try:
            # Get total count
            result = self.collection.get()
            total_jobs = len(result['ids'])
            
            if total_jobs == 0:
                return {
                    "total_jobs": 0,
                    "collection_name": self.collection_name,
                    "db_path": self.db_path
                }
            
            # Count by source and other stats
            metadatas = result['metadatas']
            sources = {}
            companies = {}
            remote_count = 0
            
            for metadata in metadatas:
                # Count sources
                source = metadata.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
                
                # Count companies
                company = metadata.get('company', 'unknown')
                companies[company] = companies.get(company, 0) + 1
                
                # Count remote jobs
                if metadata.get('remote') == 'True':
                    remote_count += 1
            
            top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_jobs": total_jobs,
                "sources": sources,
                "remote_jobs": remote_count,
                "top_companies": top_companies,
                "collection_name": self.collection_name,
                "db_path": self.db_path
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {"error": str(e)}
    
    def reset_database(self):
        """Reset the database (careful - this deletes everything!)."""
        print("⚠️  Resetting vector database...")
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Job search results with embeddings"}
            )
            print("✅ Database reset complete")
        except Exception as e:
            print(f"❌ Error resetting database: {e}")


# Simple test function
def test_vector_db():
    """Test the vector database with sample data."""
    print("🧪 Testing Vector Database")
    
    # Create test job
    test_job = Job(
        title="Senior LLM Engineer",
        company="AI Startup",
        location="Remote",
        description="Work on large language models and generative AI systems",
        url="https://example.com/job/123",
        salary="$120k-$180k",
        remote=True
    )
    
    # Initialize database
    db = JobVectorDB(db_path="./test_vector_db")
    
    # Add job
    db.add_job(test_job)
    
    # Get stats
    stats = db.get_stats()
    print("📊 Database Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_vector_db()
