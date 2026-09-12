import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from src.pipeline.scraper import AsyncScraper

class RecursiveCrawler:
    def __init__(self, max_depth: int = 2, max_pages: int = 10):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.scraper = AsyncScraper(concurrency=3)

    async def crawl_site(self, start_url: str, render_js: bool = False) -> List[Dict[str, Any]]:
        target_domain = urllib.parse.urlparse(start_url).netloc
        queue = [(start_url, 0)]
        scraped_documents = []

        while queue and len(self.visited) < self.max_pages:
            current_url, depth = queue.pop(0)

            if current_url in self.visited or depth > self.max_depth:
                continue

            self.visited.add(current_url)
            results = await self.scraper.scrape_urls([current_url], render_js=render_js)
            if not results or results[0]["status"] != 200:
                continue

            page_data = results[0]
            scraped_documents.append(page_data)

            # Discover and queue internal links
            soup = BeautifulSoup(page_data["content"], "html.parser")
            for tag in soup.find_all("a", href=True):
                full_link = urllib.parse.urljoin(current_url, tag["href"])
                link_domain = urllib.parse.urlparse(full_link).netloc
                
                # Stay within the same domain
                if link_domain == target_domain and full_link not in self.visited:
                    queue.append((full_link, depth + 1))

        return scraped_documents
