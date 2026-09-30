"""
News URL scraper and metadata extractor.
Fetches articles, extracts headline, body text, author, domain,
and publication metadata for real-time veracity analysis.
"""

import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

class NewsScraper:
    @staticmethod
    def scrape_url(url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Scrapes a news article URL and extracts title, main text, domain,
        author, and publication timestamp.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }

            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}: Unable to reach source page.",
                    "url": url,
                    "domain": domain
                }

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise scripts, styles, nav, footer, ads
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
                tag.decompose()

            # 1. Extract Title
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            elif soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            # 2. Extract Author
            author = "Unknown"
            author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
            if author_meta and author_meta.get("content"):
                author = author_meta["content"].strip()

            # 3. Extract Published Date
            published_date = "Unknown"
            date_meta = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "pubdate"})
            if date_meta and date_meta.get("content"):
                published_date = date_meta["content"].strip()

            # 4. Extract Main Body Paragraphs
            article_tag = soup.find("article") or soup.find("main") or soup.find(class_=re.compile(r"article|content|body|story", re.I))
            search_scope = article_tag if article_tag else soup

            paragraphs = []
            for p in search_scope.find_all("p"):
                txt = p.get_text(strip=True)
                # Keep substantive paragraphs
                if len(txt) > 35 and not any(skip in txt.lower() for skip in ["cookie", "privacy policy", "all rights reserved", "subscribe now", "terms of service"]):
                    paragraphs.append(txt)

            body_text = "\n\n".join(paragraphs)

            if not body_text and not title:
                return {
                    "success": False,
                    "error": "Could not extract article content. The webpage might be protected by paywalls or JavaScript rendering.",
                    "url": url,
                    "domain": domain
                }

            return {
                "success": True,
                "url": url,
                "domain": domain,
                "title": title or "Untitled Article",
                "author": author,
                "published_date": published_date,
                "text": body_text[:6000], # Cap to reasonable length for processing
                "paragraphs_count": len(paragraphs)
            }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out while connecting to the news server.", "url": url}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Failed to establish network connection to the domain.", "url": url}
        except Exception as e:
            return {"success": False, "error": f"Scraping error: {str(e)}", "url": url}
