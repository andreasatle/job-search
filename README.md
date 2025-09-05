# Job Search Web Scraper

A modern, Playwright-based web scraper designed for job sites. Built with async/await for performance and includes anti-detection measures to successfully scrape job listings.

## 🎭 Features

- **Playwright-powered** - Modern browser automation with JavaScript support
- **Async/await** - High-performance asynchronous scraping
- **Anti-detection** - Realistic browser fingerprinting and human-like behavior
- **Error handling** - Graceful failure handling and retries
- **Extensible design** - Easy to add new job sites
- **Houston-focused** - Configured for Houston, TX job market

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip for package management

### Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd job-search
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Install Playwright browsers:**
   ```bash
   uv run playwright install
   # or
   playwright install
   ```

### Basic Usage

**Test the scraper:**
```bash
uv run python test_playwright.py
```

**Use the scraper in your code:**
```python
import asyncio
from playwright_scraper import PlaywrightJobScraper

async def scrape_example():
    async with PlaywrightJobScraper(headless=False) as scraper:
        success = await scraper.safe_navigate("https://example.com")
        if success:
            title = await scraper.extract_text("h1")
            print(f"Page title: {title}")

asyncio.run(scrape_example())
```

## 📁 Project Structure

```
job-search/
├── playwright_scraper.py    # Main scraper class
├── test_playwright.py       # Test script
├── pyproject.toml          # Project dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## 🔧 Configuration

The scraper includes several configuration options:

### Browser Settings
- **Headless mode** - Run with or without visible browser
- **Slow motion** - Add delays for debugging
- **Viewport** - Realistic screen resolution (1920x1080)
- **User agent** - Modern Chrome user agent
- **Timezone** - Houston timezone (America/Chicago)

### Anti-Detection Features
- Random delays between actions
- Realistic HTTP headers
- Proper browser fingerprinting
- Human-like navigation patterns

## 🎯 Core Components

### `PlaywrightJobScraper`

Main scraper class with the following key methods:

- `async start()` - Initialize browser and context
- `async safe_navigate(url)` - Navigate with error handling
- `async extract_text(selector)` - Extract text from elements
- `async extract_attribute(selector, attr)` - Extract element attributes
- `async wait_for_element(selector)` - Wait for elements to load
- `async random_delay()` - Add human-like delays

### `JobListing`

Data structure for job information:
```python
@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    job_type: Optional[str] = None
    source: str = "unknown"
```

## 🌐 Supported Features

### Current Capabilities
- ✅ Basic web navigation
- ✅ Element text extraction
- ✅ Attribute extraction
- ✅ Error handling
- ✅ Anti-bot measures
- ✅ Async context management

### Planned Features
- 🔄 Job site-specific scrapers
- 🔄 Pagination handling
- 🔄 Search functionality
- 🔄 Data export capabilities
- 🔄 Rate limiting
- 🔄 Proxy support

## 🛠️ Development

### Running Tests

```bash
# Basic functionality test
uv run python test_playwright.py

# Run with visible browser for debugging
# (Edit test_playwright.py and set headless=False)
```

### Adding New Job Sites

1. Create a new method in `PlaywrightJobScraper`
2. Implement site-specific selectors
3. Add error handling for site-specific issues
4. Test with the target site

Example:
```python
async def scrape_indeed(self, query: str, location: str) -> List[JobListing]:
    """Scrape Indeed job listings."""
    url = f"https://www.indeed.com/jobs?q={query}&l={location}"
    
    if await self.safe_navigate(url):
        # Add site-specific scraping logic here
        pass
```

## 🚨 Important Notes

### Legal and Ethical Considerations
- **Respect robots.txt** - Check site policies before scraping
- **Rate limiting** - Don't overload servers
- **Terms of service** - Comply with site terms
- **Data usage** - Use scraped data responsibly

### Technical Considerations
- **Browser resources** - Playwright uses more memory than requests
- **Speed vs. stealth** - Slower scraping is less likely to be detected
- **Site changes** - Job sites frequently update their HTML structure
- **Error handling** - Always expect and handle failures gracefully

## 🐛 Troubleshooting

### Common Issues

**"playwright install" fails:**
```bash
# Try installing system dependencies first
# On Ubuntu/Debian:
sudo apt-get install libnss3 libatk-bridge2.0-0 libdrm2

# On macOS:
brew install --cask playwright
```

**Browser doesn't start:**
- Check if playwright browsers are installed
- Try running with `headless=False` for debugging
- Check system permissions

**Scraping fails with 403/blocked:**
- Increase delays between requests
- Try different user agents
- Use residential proxies if needed
- Respect site rate limits

**Memory issues:**
- Use headless mode in production
- Close browser contexts when done
- Limit concurrent scrapers

## 📝 License

This project is for educational and personal use only. Please respect the terms of service of the websites you're scraping.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Playwright documentation
3. Open an issue with detailed error information
