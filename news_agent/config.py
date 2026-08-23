import os

FEEDS = {
    "arXiv cs.AI": "http://export.arxiv.org/rss/cs.AI",
    "Hacker News (AI/LLM)": "https://hnrss.org/newest?q=LLM+OR+agent+OR+%22AI+engineering%22",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
}

OLLAMA_MODEL = "llama3.2"
OLLAMA_BASE_URL = "http://127.0.0.1:11434"

ITEMS_PER_FEED = 5
DB_PATH = "news_agent.db"

PHOENIX_ENDPOINT = "http://127.0.0.1:6006/v1/traces"
PHOENIX_PROJECT_NAME = "ai-news-agent"
ENABLE_OBSERVABILITY = os.getenv(
    "NEWS_AGENT_ENABLE_OBSERVABILITY", "true"
).lower() not in (
    "false",
    "0",
    "",
)
