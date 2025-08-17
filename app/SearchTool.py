from langchain.tools import tool
import os
import time
from typing import List
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from langchain_community.tools.tavily_search import TavilySearchResults

# Ensure .env is loaded before we try to read TAVILY_API_KEY
load_dotenv()

def _format_results(results: List[dict], limit: int = 3) -> str:
    lines = []
    for item in results[:limit]:
        title = item.get("title") or ""
        href = item.get("href") or item.get("link") or ""
        snippet = item.get("body") or item.get("snippet") or ""
        lines.append(f"{title} - {href}\n{snippet}")
    return "\n\n".join(lines) if lines else "No results found."


@tool("DuckDuckGo Search")
def search_tool_old(query: str) -> str:
    """Search the web using DuckDuckGo with basic backoff to avoid rate limits."""
    delays = [0.8, 1.6]
    last_error = None
    for delay in delays:
        try:
            time.sleep(delay)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5, region="in-en", safesearch="moderate"))
            if not results:
                return "No results found."
            return _format_results(results, limit=3)
        except Exception as error:
            last_error = error
            continue
    return f"Search temporarily unavailable: {last_error}"

@tool("Web Search")
def search_tool(query: str) -> str:
    """Web search: prefer Tavily if TAVILY_API_KEY is set, else fall back to DuckDuckGo with backoff."""
    if os.getenv("TAVILY_API_KEY"):
        try:
            tavily = TavilySearchResults(max_results=3)
            return tavily.run(query)
        except Exception as e:
            # Fall back to DDG if Tavily fails
            pass
    # Fallback: DDG
    return search_tool_old(query)