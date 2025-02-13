import os
import re
import asyncio
from urllib.parse import urlparse, urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get model configuration from environment variables
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')  # Default to mistral if not specified
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')  # Default to localhost

class WebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = self._create_output_dir()
        self.processed_urls = set()
        
    def _create_output_dir(self):
        # Create a clean directory name from the domain
        dir_name = re.sub(r'[^\w\-_]', '_', self.domain)
        os.makedirs(dir_name, exist_ok=True)
        return dir_name
    
    def _get_page_name(self, url):
        # Remove query parameters and fragments
        url = url.split('?')[0].split('#')[0]
        
        # Handle root URL
        if url.rstrip('/') == self.base_url.rstrip('/'):
            return 'home'
            
        # Extract the last part of the path
        path = urlparse(url).path.strip('/')
        if not path:
            return 'home'
            
        # Convert path to filename
        parts = path.split('/')
        filename = parts[-1] if parts else 'home'
        if not filename:
            filename = 'home'
            
        # Clean the filename
        filename = re.sub(r'[^\w\-_]', '_', filename)
        return filename
    
    def _save_to_markdown(self, url, content, title):
        filename = self._get_page_name(url)
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        
        # Create markdown content
        markdown_content = f"# {title}\n\nURL: {url}\n\n{content}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath

    def _process_page(self, html_content):
        if not html_content:
            return "Untitled", "No content available"
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "Untitled"
        
        # Extract main content (customize this based on your needs)
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Process text (remove extra whitespace)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return title, text

    def _get_ollama_summary(self, text):
        # Call local Ollama API
        response = requests.post(f'{OLLAMA_HOST}/api/generate', 
                               json={
                                   "model": OLLAMA_MODEL,
                                   "prompt": f"Please structure and summarize the following content in a clear, markdown-friendly format:\n\n{text[:4000]}"  # Limit text length
                               })
        
        try:
            # Combine all response chunks
            summary = ""
            for line in response.text.split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        if 'response' in data:
                            summary += data['response']
                    except json.JSONDecodeError:
                        continue
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}\n\nOriginal Content:\n{text}"

    def _is_same_domain(self, url):
        """Check if the URL belongs to the same domain as base_url"""
        return urlparse(url).netloc == self.domain

    async def process_url(self, crawler, url):
        """Process a single URL and return its links"""
        if url in self.processed_urls:
            return []
            
        self.processed_urls.add(url)
        print(f"Processing URL: {url}")
        
        result = await crawler.arun(url=url)
        links = []
        
        if result.success and result.html:
            # Process the current page
            title, content = self._process_page(result.html)
            summary = self._get_ollama_summary(content)
            filepath = self._save_to_markdown(url, summary, title)
            print(f"Processed and saved: {url} -> {filepath}")
            
            # Extract links from the page
            soup = BeautifulSoup(result.html, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if self._is_same_domain(full_url) and full_url not in self.processed_urls:
                    links.append(full_url)
        else:
            error_msg = result.error_message if hasattr(result, 'error_message') else "Unknown error"
            print(f"Error scraping {url}: {error_msg}")
            
        return links

    async def scrape(self):
        print(f"Starting to scrape {self.base_url}")
        
        browser_config = BrowserConfig(headless=True, verbose=True)
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            process_iframes=False,
            remove_overlay_elements=True,
            exclude_external_links=True,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            urls_to_process = [self.base_url]
            
            while urls_to_process:
                url = urls_to_process.pop(0)
                new_links = await self.process_url(crawler, url)
                urls_to_process.extend([link for link in new_links if link not in self.processed_urls])

        print(f"Scraping completed. Content saved in '{self.output_dir}' directory")
        print(f"Total pages processed: {len(self.processed_urls)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python website_scraper.py <website_url>")
        sys.exit(1)
    
    website_url = sys.argv[1]
    scraper = WebsiteScraper(website_url)
    asyncio.run(scraper.scrape()) 