#!/usr/bin/env python3
"""
Simple launcher script for the Houston Job Search web app.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Gradio web application."""
    print("🚀 Starting Houston Job Search Web App...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("💡 Create .env with: OPENAI_API_KEY=your-key-here")
        print()
    
    # Check if database exists
    db_path = Path("test_job_db")
    if not db_path.exists():
        print("📊 No job database found. Run this first to add sample data:")
        print("   uv run python tests/test_vector_store.py")
        print()
    
    # Launch the app
    try:
        print("🌐 Launching web interface...")
        print("📍 Will be available at: http://127.0.0.1:7860")
        print("🛑 Press Ctrl+C to stop")
        print()
        
        subprocess.run([sys.executable, "gradio_app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Houston Job Search. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
