import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """Check if the response indicates rate limiting (status code 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """Make a request with retry logic for rate limiting"""
    # Random delay before each request to avoid detection
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    Scrape Google News search results for a given query and date range.
    query: str - search query
    start_date: str - start date in the format yyyy-mm-dd or mm/dd/yyyy
    end_date: str - end date in the format yyyy-mm-dd or mm/dd/yyyy
    """
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    max_pages = 3  # Limit to 3 pages to avoid too many requests
    
    while page < max_pages:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Try multiple selectors for news results
            results_on_page = (
                soup.select("div.SoaBEf") or 
                soup.select("div[data-hveid]") or
                soup.select("div.g") or
                soup.select("div[jscontroller]")
            )

            if not results_on_page:
                print(f"No results found on page {page}")
                break  # No more results found

            for el in results_on_page:
                try:
                    # Try multiple selectors for each field
                    link_elem = el.find("a")
                    if not link_elem:
                        continue
                    
                    link = link_elem.get("href", "")
                    if not link.startswith("http"):
                        continue
                    
                    # Try multiple selectors for title
                    title_elem = (
                        el.select_one("div.MBeuO") or
                        el.select_one("h3") or
                        el.select_one("div[role='heading']") or
                        el.select_one("a")
                    )
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    
                    # Try multiple selectors for snippet
                    snippet_elem = (
                        el.select_one(".GI74Re") or
                        el.select_one(".VwiC3b") or
                        el.select_one("div[data-content-feature='1']") or
                        el.select_one("span[dir='ltr']")
                    )
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No snippet available"
                    
                    # Try multiple selectors for source
                    source_elem = (
                        el.select_one(".NUnG9d span") or
                        el.select_one("cite") or
                        el.select_one("span[aria-label*='source']") or
                        el.select_one("div[data-attrid*='source']")
                    )
                    source = source_elem.get_text(strip=True) if source_elem else "Unknown source"
                    
                    # Only add if we have at least a title and link
                    if title and link and title != "No title":
                        news_results.append({
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "source": source,
                        })
                        
                except Exception as e:
                    # Silently skip problematic results instead of printing errors
                    continue

            # Check for the "Next" link (pagination)
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break

    return news_results
