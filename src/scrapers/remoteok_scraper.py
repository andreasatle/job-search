"""
RemoteOK job scraper for remote startup/tech positions.
"""

import asyncio
import re
from typing import List, Optional
from playwright.async_api import async_playwright

from .base_scraper import JobScraper
from ..job import Job


class RemoteOKScraper(JobScraper):
    """RemoteOK job scraper for remote startup/tech positions."""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.base_url = "https://remoteok.io"
        self.site_name = "RemoteOK"
    
    def _build_search_url(self, query: str, location: str) -> str:
        """Build RemoteOK search URL."""
        # RemoteOK uses tags for search
        query_encoded = query.replace(' ', '+').lower()
        # Location is less relevant for RemoteOK since it's all remote
        return f"{self.base_url}/?search={query_encoded}"
    
    async def search_jobs(self, query: str, location: str = "Remote", max_jobs: int = 10) -> List[Job]:
        """Search RemoteOK for remote tech jobs with full descriptions."""
        print(f"🔍 Searching {self.site_name} for '{query}' (all remote)")
        print(f"📝 Fetching full descriptions from job detail pages")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                # Build search URL
                search_url = self._build_search_url(query, location)
                print(f"📡 URL: {search_url}")
                
                # Navigate to search results
                await page.goto(search_url, wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                # RemoteOK job selectors - they use a table structure
                job_cards = []
                selectors_to_try = [
                    'tr.job',
                    '.job',
                    'tr[data-id]',
                    'table tr:has(td)',
                    '.jobs tr'
                ]
                
                for selector in selectors_to_try:
                    try:
                        cards = await page.query_selector_all(selector)
                        if cards and len(cards) > 3:  # Need several results
                            job_cards = cards
                            print(f"📄 Found {len(job_cards)} job cards using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    page_title = await page.title()
                    print(f"⚠️  No job cards found. Page title: {page_title}")
                    return []
                
                # First pass: extract basic job info and URLs
                jobs = []
                basic_jobs = []
                
                for i, card in enumerate(job_cards[:max_jobs]):
                    try:
                        job = await self._extract_job(card, None)  # No full descriptions on first pass
                        if job:
                            basic_jobs.append(job)
                            print(f"✅ {len(basic_jobs)}: {job.title} at {job.company}")
                    except Exception as e:
                        print(f"⚠️  Error extracting job {i+1}: {e}")
                        continue
                
                # Second pass: get full descriptions for all jobs
                if basic_jobs:
                    print(f"\n📝 Fetching full descriptions for {len(basic_jobs)} jobs...")
                    for i, job in enumerate(basic_jobs):
                        if job.url:
                            try:
                                full_description = await self._get_full_description(page, job.url)
                                if full_description:
                                    # Create new job with full description
                                    enhanced_job = Job(
                                        title=job.title,
                                        company=job.company,
                                        location=job.location,
                                        description=full_description,
                                        url=job.url,
                                        salary=job.salary,
                                        remote=job.remote,
                                        posted_date=job.posted_date
                                    )
                                    jobs.append(enhanced_job)
                                else:
                                    jobs.append(job)  # Keep original if full description fails
                            except Exception as e:
                                print(f"⚠️  Error getting full description for job {i+1}: {e}")
                                jobs.append(job)  # Keep original
                        else:
                            jobs.append(job)
                else:
                    jobs = basic_jobs
                
                return jobs
                
            finally:
                await browser.close()
    
    async def _extract_job(self, card, page=None) -> Optional[Job]:
        """Extract job data from RemoteOK table row."""
        try:
            # Get all text content for parsing
            text_content = await card.text_content()
            if not text_content or len(text_content.strip()) < 10:
                return None
            
            # RemoteOK specific selectors - be very targeted
            title = "Unknown Title"
            
            # Simple title extraction
            title_element = await card.query_selector('h2')
            if title_element:
                title_text = await title_element.text_content()
                if title_text and len(title_text.strip()) > 3:
                    title = re.sub(r'\s+', ' ', title_text.strip())
                else:
                    title = "Unknown Title"
            else:
                title = "Unknown Title"
            
            # Simple company extraction
            company_element = await card.query_selector('h3')
            if company_element:
                company_text = await company_element.text_content()
                if company_text and len(company_text.strip()) > 1:
                    company = re.sub(r'\s+', ' ', company_text.strip())
                else:
                    company = "Unknown Company"
            else:
                company = "Unknown Company"
            
            # Location is always Remote for RemoteOK
            location = "Remote"
            
            # For RemoteOK, just use the skill tags from h3 elements as description
            # This avoids the messy JSON content entirely
            skill_tags = []
            h3_elements = await card.query_selector_all('h3')
            
            # Skip first h3 (company), collect others as skills/tags
            for h3 in h3_elements[1:]:
                tag_text = await h3.text_content()
                if tag_text:
                    clean_tag = re.sub(r'\s+', ' ', tag_text.strip())
                    if (len(clean_tag) > 1 and 
                        clean_tag not in ['Remote', 'Full-Time', 'Part-Time'] and
                        len(clean_tag) < 20):  # Skip very long tags
                        skill_tags.append(clean_tag)
            
            # Create clean description from skills
            if skill_tags:
                description = " • ".join(skill_tags) 
            else:
                description = "Remote position"
            
            # Get URL - RemoteOK links to job details
            url = ""
            url_element = await card.query_selector('a[href]')
            if url_element:
                relative_url = await url_element.get_attribute('href')
                if relative_url:
                    if relative_url.startswith('/'):
                        url = f"{self.base_url}{relative_url}"
                    else:
                        url = relative_url
            
            # Get salary - RemoteOK often shows salary in USD
            salary = None
            salary_patterns = [
                r'\$[\d,]+\s*-\s*\$[\d,]+',  # Range like $80k-$120k
                r'\$[\d,]+[kK]?\+?',         # Single value like $100k+
                r'[\d,]+[kK]\s*-\s*[\d,]+[kK]',  # K format like 80k-120k
                r'\$[\d,]+(?:\.\d{2})?'      # Exact dollar amounts
            ]
            
            for pattern in salary_patterns:
                salary_match = re.search(pattern, text_content)
                if salary_match:
                    salary = salary_match.group(0)
                    break
            
            # All RemoteOK jobs are remote by definition
            remote = True
            
            # Skip if we couldn't extract basic info (but be less strict)
            if title == "Unknown Title" or company == "Unknown Company":
                return None
            
            return Job(
                title=title,
                company=company,
                location=location,
                description=description,
                url=url,
                salary=salary,
                remote=remote
            )
            
        except Exception as e:
            print(f"⚠️  Error extracting job: {e}")
            return None
    
    async def _get_full_description(self, page, job_url: str) -> Optional[str]:
        """Navigate to job detail page and extract full description."""
        try:
            print(f"📝 Fetching full description from {job_url}")
            
            # Navigate and wait for initial load (same as aggressive debug)
            await page.goto(job_url, wait_until='domcontentloaded')
            
            # Wait for all network activity to finish
            await page.wait_for_load_state('networkidle')
            await page.wait_for_load_state('load')
            
            # Scroll to trigger lazy loading
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            
            # Wait for any new content after scrolling
            try:
                await page.wait_for_load_state('networkidle', timeout=5000)
                print("📄 Network idle after scroll")
            except:
                print("📄 No additional network activity")
            
            # Wait for substantial content to appear
            try:
                await page.wait_for_function(
                    '() => document.body.textContent.length > 1000',
                    timeout=10000
                )
                print("📄 Substantial content detected")
            except:
                print("📄 Limited content on page")
            
            # First try: Extract meta tags (cleanest approach)
            meta_description = await self._extract_meta_tags(page)
            if meta_description:
                return meta_description
            
            # Second try: Use the specific selectors we found in aggressive debug
            description_selectors = [
                '.description',  # This worked well in our debug
                '.job',          # This also had good content
                '.markdown',     # RemoteOK uses markdown for job descriptions
                '.job-description',
                'div[class*="description"]',
                '[class*="markdown"]'
            ]
            
            full_description = ""
            for selector in description_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 50:  # Need substantial content
                            full_description = text.strip()
                            print(f"✅ Found description using selector: {selector}")
                            break
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {e}")
                    continue
            
            # If no markdown found, try paragraphs but be more selective
            if not full_description:
                paragraphs = await page.query_selector_all('p')
                desc_parts = []
                for p in paragraphs:
                    text = await p.text_content()
                    if (text and len(text.strip()) > 30 and 
                        'apply now' not in text.lower() and
                        'share this job' not in text.lower() and
                        'qrcode' not in text.lower() and
                        '$(' not in text):  # Skip JavaScript
                        desc_parts.append(text.strip())
                        if len(desc_parts) >= 3:  # Enough content
                            break
                
                if desc_parts:
                    full_description = " ".join(desc_parts)
            
            # Last resort: get all text content and clean it up
            if not full_description:
                try:
                    # Get all text content from the page
                    all_text = await page.evaluate('document.body.textContent')
                    if all_text and len(all_text.strip()) > 100:
                        # Try to extract meaningful content
                        lines = all_text.split('\n')
                        meaningful_lines = []
                        for line in lines:
                            line = line.strip()
                            if (len(line) > 40 and 
                                'apply now' not in line.lower() and
                                'share this job' not in line.lower() and
                                'qrcode' not in line.lower() and
                                'copyright' not in line.lower() and
                                '$(' not in line):
                                meaningful_lines.append(line)
                                if len(meaningful_lines) >= 5:  # Enough content
                                    break
                        
                        if meaningful_lines:
                            full_description = " ".join(meaningful_lines)
                except Exception as e:
                    print(f"⚠️  Error extracting all text: {e}")
            
            if full_description:
                # Clean up the description more thoroughly
                full_description = re.sub(r'\s+', ' ', full_description)
                
                # Remove common page elements
                full_description = re.sub(r'Apply now.*?$', '', full_description, flags=re.IGNORECASE)
                full_description = re.sub(r'Share this job:.*?$', '', full_description, flags=re.IGNORECASE)
                full_description = re.sub(r'\$\(function\(\).*?\}.*?\)', '', full_description)
                full_description = re.sub(r'new QRCode.*?$', '', full_description, flags=re.IGNORECASE)
                full_description = re.sub(r'Get a rok\.co.*?$', '', full_description, flags=re.IGNORECASE)
                
                full_description = full_description.strip()
                
                if len(full_description) > 20:  # Only return if we have substantial content
                    return full_description
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error fetching full description: {e}")
            return None
    
    async def _extract_meta_tags(self, page) -> Optional[str]:
        """Extract job description from meta tags (cleanest approach)."""
        try:
            meta_tags = ['description', 'og:description']
            
            for meta_name in meta_tags:
                try:
                    # Try both name and property attributes
                    meta_content_name = await page.get_attribute(f'meta[name="{meta_name}"]', 'content')
                    if not meta_content_name:
                        meta_content_property = await page.get_attribute(f'meta[property="{meta_name}"]', 'content')
                        content = meta_content_property
                    else:
                        content = meta_content_name
                    
                    if content and len(content.strip()) > 50:  # Need substantial content
                        # Clean up the meta description
                        clean_content = re.sub(r'\s+', ' ', content.strip())
                        print(f"✅ Found clean description in {meta_name} meta tag")
                        return clean_content
                        
                except Exception as e:
                    print(f"⚠️  Error extracting {meta_name}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error extracting meta tags: {e}")
            return None


# RemoteOK scraper implementation complete

