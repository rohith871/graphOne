import re
import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ResearchScraper")

class ResearchPaperScraper:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    async def fetch_github_stars(self, session: aiohttp.ClientSession, repo_url: str) -> int:
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return 0
        owner, repo = match.group(1), match.group(2).rstrip(".git")
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            async with session.get(api_url, headers=self.headers, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("stargazers_count", 0)
        except Exception as e:
            logger.warning(f"Failed to fetch stars for {repo_url}: {e}")
        return 0

    async def scrape_arxiv_papers(self, limit: int = 10) -> List[Dict[str, Any]]:
        papers = []
        url = f"http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = await resp.text()
                soup = BeautifulSoup(content, "xml")
                entries = soup.find_all("entry")
                for entry in entries:
                    title = entry.title.text.strip().replace("\n", " ")
                    authors = [a.find("name").text for a in entry.find_all("author")]
                    paper_url = entry.id.text.strip()
                    published = entry.published.text.strip()
                    summary = entry.summary.text if entry.summary else ""
                    gh_match = re.search(r"https?://github\.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+", summary)
                    github_url = gh_match.group(0) if gh_match else ""
                    stars = await self.fetch_github_stars(session, github_url) if github_url else 0

                    papers.append({
                        "schemaVersion": "1.0",
                        "recordType": "RESEARCH_PAPER",
                        "content": {
                            "title": title,
                            "authors": authors,
                            "paper_url": paper_url,
                            "github_url": github_url,
                            "github_stars": stars,
                            "published_date": published
                        }
                    })
        return papers
