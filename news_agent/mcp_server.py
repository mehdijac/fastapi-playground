import re

import feedparser
from mcp.server.fastmcp import FastMCP

from news_agent.config import FEEDS, ITEMS_PER_FEED

mcp = FastMCP("ai-news-feeds")

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


@mcp.tool()
def fetch_ai_news() -> list[dict]:
    """Fetch recent AI engineering news items from a curated set of RSS/Atom
    feeds (arXiv cs.AI, Hacker News, Hugging Face Blog, Simon Willison, Google
    AI Blog). Returns a list of items with source, title, link, summary, and
    published date.
    """
    items = []
    for source, url in FEEDS.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:ITEMS_PER_FEED]:
            items.append(
                {
                    "source": source,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": _strip_html(entry.get("summary", ""))[:500],
                    "published": entry.get("published", entry.get("updated", "")),
                }
            )
    return items


if __name__ == "__main__":
    mcp.run()
