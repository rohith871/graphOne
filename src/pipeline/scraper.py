import asyncio
import logging
import httpx
from typing import List, Dict, Any
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("AsyncScraper")

class AsyncScraper:
    def __init__(self, concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def fetch_static_url(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """Fast HTTP scraper for standard static HTML web pages."""
        async with self.semaphore:
            try:
                logger.info(f"[HTTPX] Fetching URL: {url}")
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                return {"url": url, "status": response.status_code, "content": response.text, "mode": "static"}
            except Exception as e:
                logger.error(f"[HTTPX] Failed to fetch {url}: {e}")
                return {"url": url, "status": 500, "content": "", "mode": "static"}

    async def fetch_dynamic_url(self, url: str) -> Dict[str, Any]:
        """Headless browser scraper for rendering JavaScript single-page apps (React/Vue/Angular)."""
        async with self.semaphore:
            try:
                logger.info(f"[PLAYWRIGHT] Rendering JS for URL: {url}")
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page(user_agent=self.headers["User-Agent"])
                    
                    # Navigate and wait for DOM content to finish loading
                    response = await page.goto(url, wait_until="networkidle", timeout=15000)
                    content = await page.content()
                    status = response.status if response else 200
                    await browser.close()
                    
                    return {"url": url, "status": status, "content": content, "mode": "dynamic"}
            except Exception as e:
                logger.error(f"[PLAYWRIGHT] Failed rendering {url}: {e}")
                return {"url": url, "status": 500, "content": "", "mode": "dynamic"}

    async def scrape_urls(self, urls: List[str], render_js: bool = False) -> List[Dict[str, Any]]:
        """Scrape a batch of URLs either using fast HTTP requests or full headless browser rendering."""
        if render_js:
            logger.info("Starting headless Playwright browser workerpool...")
            tasks = [self.fetch_dynamic_url(url) for url in urls]
            return await asyncio.gather(*tasks)
        else:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                tasks = [self.fetch_static_url(client, url) for url in urls]
                return await asyncio.gather(*tasks)

if __name__ == "__main__":
    test_urls = ["https://httpbin.org/html"]
    scraper = AsyncScraper()
    results = asyncio.run(scraper.scrape_urls(test_urls, render_js=True))
    print(f"Successfully rendered {len(results)} dynamic page(s). Content length: {len(results[0]['content'])}")
