"""
Gradio Web Interface for Houston Job Search
A beautiful, modern interface for searching through scraped job posts using semantic search.
"""

import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
from dotenv import load_dotenv

from src.database.job_vector_store import JobVectorStore
from src.models.job_models import JobType, RemoteType

# Load environment variables
load_dotenv()

class JobSearchApp:
    """Gradio application for job searching."""
    
    def __init__(self, db_path: str = "./test_job_db"):
        """Initialize the job search app."""
        self.vector_store = JobVectorStore(db_path=db_path)
        self.stats = self.vector_store.get_statistics()
        
    def search_jobs(self, 
                   query: str,
                   max_results: int = 10,
                   min_salary: Optional[int] = None,
                   max_salary: Optional[int] = None,
                   job_type_filter: str = "Any",
                   remote_type_filter: str = "Any",
                   source_filter: str = "Any") -> Tuple[str, str]:
        """
        Search for jobs and return formatted results.
        
        Returns:
            Tuple of (HTML results, summary stats)
        """
        if not query.strip():
            return self._format_no_results(), self._format_stats()
        
        try:
            # Perform the search
            results = self.vector_store.search_jobs(
                query=query,
                n_results=max_results
            )
            
            if not results:
                return self._format_no_results(), self._format_stats()
            
            # Apply filters
            filtered_results = self._apply_filters(
                results, min_salary, max_salary, 
                job_type_filter, remote_type_filter, source_filter
            )
            
            if not filtered_results:
                return self._format_no_results("No jobs match your filters."), self._format_stats()
            
            # Format results as HTML
            html_results = self._format_results_html(filtered_results, query)
            stats_summary = self._format_search_stats(len(filtered_results), len(results), query)
            
            return html_results, stats_summary
            
        except Exception as e:
            error_msg = f"<div style='color: red; padding: 20px;'>❌ Search error: {str(e)}</div>"
            return error_msg, self._format_stats()
    
    def _apply_filters(self, results: List[Dict], min_salary: Optional[int], 
                      max_salary: Optional[int], job_type_filter: str,
                      remote_type_filter: str, source_filter: str) -> List[Dict]:
        """Apply user-specified filters to search results."""
        filtered = results.copy()
        
        # Salary filters
        if min_salary is not None:
            filtered = [r for r in filtered 
                       if r.get('salary_min') and r['salary_min'] >= min_salary]
        
        if max_salary is not None:
            filtered = [r for r in filtered 
                       if r.get('salary_max') and r['salary_max'] <= max_salary]
        
        # Job type filter
        if job_type_filter != "Any":
            filtered = [r for r in filtered 
                       if r.get('job_type') == job_type_filter.lower().replace(' ', '-')]
        
        # Remote type filter  
        if remote_type_filter != "Any":
            filtered = [r for r in filtered 
                       if r.get('remote_type') == remote_type_filter.lower()]
        
        # Source filter
        if source_filter != "Any":
            filtered = [r for r in filtered 
                       if r.get('source') == source_filter.lower()]
        
        return filtered
    
    def _format_results_html(self, results: List[Dict], query: str) -> str:
        """Format search results as beautiful HTML."""
        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            <div style="margin-bottom: 20px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
                <h2 style="margin: 0; font-size: 24px;">🎯 Search Results for "{query}"</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Found {len(results)} matching jobs</p>
            </div>
        """
        
        for i, job in enumerate(results, 1):
            # Determine colors based on similarity score
            score = job.get('similarity_score', 0)
            if score >= 0.8:
                score_color = "#22c55e"  # Green
                score_label = "Excellent Match"
            elif score >= 0.6:
                score_color = "#3b82f6"  # Blue  
                score_label = "Good Match"
            elif score >= 0.4:
                score_color = "#f59e0b"  # Orange
                score_label = "Fair Match"
            else:
                score_color = "#ef4444"  # Red
                score_label = "Weak Match"
            
            # Build salary display
            salary_info = self._format_salary(job)
            
            # Build job details
            job_details = []
            if job.get('job_type') and job['job_type'] != 'unknown':
                job_details.append(f"📋 {job['job_type'].replace('-', ' ').title()}")
            if job.get('remote_type') and job['remote_type'] != 'unknown':
                job_details.append(f"🏠 {job['remote_type'].title()}")
            if job.get('experience_level'):
                job_details.append(f"⭐ {job['experience_level']}")
            
            details_str = " • ".join(job_details) if job_details else ""
            
            # Skills display
            skills_html = ""
            if job.get('skills') and isinstance(job['skills'], list) and job['skills']:
                skills_html = f"""
                <div style="margin-top: 10px;">
                    <strong>🛠️ Skills:</strong> 
                    {', '.join(f'<span style="background: #e5e7eb; padding: 2px 6px; border-radius: 4px; font-size: 12px;">{skill}</span>' for skill in job['skills'][:5])}
                </div>
                """
            
            html += f"""
            <div style="border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin-bottom: 15px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;">
                <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 10px;">
                    <div style="flex: 1;">
                        <h3 style="margin: 0; color: #1f2937; font-size: 20px;">
                            <a href="{job.get('url', '#')}" target="_blank" style="color: #3b82f6; text-decoration: none;">
                                {job.get('title', 'Unknown Title')}
                            </a>
                        </h3>
                        <p style="margin: 5px 0; color: #6b7280; font-size: 16px;">
                            🏢 <strong>{job.get('company', 'Unknown Company')}</strong> • 📍 {job.get('location', 'Unknown Location')}
                        </p>
                        {f'<p style="margin: 5px 0; color: #6b7280; font-size: 14px;">{details_str}</p>' if details_str else ''}
                    </div>
                    <div style="text-align: right; margin-left: 20px;">
                        <div style="background: {score_color}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 5px;">
                            {score:.1%} • {score_label}
                        </div>
                        <div style="font-size: 12px; color: #9ca3af;">
                            Rank #{i}
                        </div>
                    </div>
                </div>
                
                {salary_info}
                {skills_html}
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #f3f4f6; display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 12px; color: #9ca3af;">
                        📅 Scraped: {self._format_date(job.get('scraped_date'))} • 🌐 Source: {job.get('source', 'unknown').title()}
                    </div>
                    <a href="{job.get('url', '#')}" target="_blank" style="background: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500;">
                        View Job →
                    </a>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _format_salary(self, job: Dict) -> str:
        """Format salary information."""
        if job.get('salary_text'):
            return f'<p style="margin: 5px 0; color: #059669; font-weight: 600;">💰 {job["salary_text"]}</p>'
        elif job.get('salary_min') or job.get('salary_max'):
            min_sal = job.get('salary_min', 0)
            max_sal = job.get('salary_max', 0)
            if min_sal and max_sal:
                return f'<p style="margin: 5px 0; color: #059669; font-weight: 600;">💰 ${min_sal:,} - ${max_sal:,}</p>'
            elif min_sal:
                return f'<p style="margin: 5px 0; color: #059669; font-weight: 600;">💰 ${min_sal:,}+</p>'
            elif max_sal:
                return f'<p style="margin: 5px 0; color: #059669; font-weight: 600;">💰 Up to ${max_sal:,}</p>'
        return ""
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string."""
        if not date_str:
            return "Unknown"
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime("%m/%d/%Y")
            return date_str
        except:
            return "Unknown"
    
    def _format_no_results(self, message: str = "No jobs found for your search.") -> str:
        """Format no results message."""
        return f"""
        <div style="text-align: center; padding: 40px; color: #6b7280;">
            <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
            <h3 style="color: #374151; margin-bottom: 10px;">{message}</h3>
            <p>Try different keywords, check your filters, or scrape more jobs from job sites.</p>
        </div>
        """
    
    def _format_stats(self) -> str:
        """Format database statistics."""
        return f"""
        📊 **Database Stats:**
        - **{self.stats['total_jobs']}** total jobs
        - **Sources:** {', '.join(self.stats['sources'].keys())}
        - **Job Types:** {', '.join(self.stats['job_types'].keys())}
        """
    
    def _format_search_stats(self, filtered_count: int, total_matches: int, query: str) -> str:
        """Format search statistics."""
        return f"""
        🎯 **Search Results:**
        - **Query:** "{query}"
        - **Found:** {filtered_count} jobs (from {total_matches} total matches)
        - **Database:** {self.stats['total_jobs']} total jobs available
        """
    
    def get_filter_options(self) -> Tuple[List[str], List[str], List[str]]:
        """Get available filter options from database."""
        job_types = ["Any"] + [jt.replace('-', ' ').title() for jt in self.stats['job_types'].keys() if jt != 'unknown']
        remote_types = ["Any"] + [rt.title() for rt in self.stats['remote_types'].keys() if rt != 'unknown']
        sources = ["Any"] + [s.title() for s in self.stats['sources'].keys()]
        
        return job_types, remote_types, sources


def create_gradio_interface():
    """Create and configure the Gradio interface."""
    
    # Initialize the app
    app = JobSearchApp()
    job_types, remote_types, sources = app.get_filter_options()
    
    # Custom CSS for beautiful styling
    css = """
    .gradio-container {
        font-family: 'Segoe UI', Arial, sans-serif !important;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    .search-section {
        background: #f8fafc;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .filters-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="Houston Job Search", theme=gr.themes.Soft()) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 36px; font-weight: 700;">🏠 Houston Job Search</h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
                Semantic search through local job database • Powered by OpenAI embeddings
            </p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Search Section
                gr.HTML('<div class="search-section">')
                gr.Markdown("### 🔍 **Search Jobs**")
                
                search_query = gr.Textbox(
                    label="Job Search Query",
                    placeholder="e.g., 'Python developer', 'machine learning engineer', 'remote software engineer'",
                    lines=1,
                    scale=4
                )
                
                with gr.Row():
                    search_btn = gr.Button("🔍 Search Jobs", variant="primary", scale=2)
                    max_results = gr.Slider(
                        minimum=5, maximum=50, value=10, step=5,
                        label="Max Results", scale=1
                    )
                gr.HTML('</div>')
                
                # Filters Section  
                gr.HTML('<div class="filters-section">')
                gr.Markdown("### 🎛️ **Filters**")
                
                with gr.Row():
                    job_type_filter = gr.Dropdown(
                        choices=job_types,
                        value="Any",
                        label="Job Type"
                    )
                    remote_type_filter = gr.Dropdown(
                        choices=remote_types,
                        value="Any", 
                        label="Work Type"
                    )
                    source_filter = gr.Dropdown(
                        choices=sources,
                        value="Any",
                        label="Source"
                    )
                
                with gr.Row():
                    min_salary = gr.Number(
                        label="Min Salary ($)",
                        placeholder="e.g., 80000",
                        precision=0
                    )
                    max_salary = gr.Number(
                        label="Max Salary ($)", 
                        placeholder="e.g., 150000",
                        precision=0
                    )
                gr.HTML('</div>')
            
            with gr.Column(scale=1):
                # Stats sidebar
                stats_output = gr.Markdown(
                    value=app._format_stats(),
                    label="Database Statistics"
                )
        
        # Results Section
        gr.Markdown("### 📋 **Search Results**")
        results_output = gr.HTML(
            value=app._format_no_results("Enter a search query above to find jobs!"),
            label="Job Results"
        )
        
        # Search functionality
        search_inputs = [
            search_query, max_results, min_salary, max_salary,
            job_type_filter, remote_type_filter, source_filter
        ]
        
        search_btn.click(
            fn=app.search_jobs,
            inputs=search_inputs,
            outputs=[results_output, stats_output]
        )
        
        # Enter key search
        search_query.submit(
            fn=app.search_jobs,
            inputs=search_inputs,
            outputs=[results_output, stats_output]
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 40px; padding: 20px; color: #6b7280; border-top: 1px solid #e5e7eb;">
            <p>🚀 Built with Gradio • 🤖 Powered by OpenAI Embeddings • 💾 ChromaDB Vector Store</p>
            <p style="font-size: 12px;">Tip: Use natural language queries like "remote python jobs" or "senior data scientist roles"</p>
        </div>
        """)
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_gradio_interface()
    
    print("🚀 Starting Houston Job Search Web App...")
    print("📍 Local database path: ./test_job_db")
    print("🌐 Opening web interface...")
    
    interface.launch(
        server_name="127.0.0.1",  # Local only
        server_port=7860,
        share=False,  # Set to True if you want a public link
        show_error=True,
        quiet=False
    )
