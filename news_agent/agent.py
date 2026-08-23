import json
from typing import TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from news_agent.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from news_agent.models import NewsItem

MCP_SERVER_PARAMS = {
    "ai-news": {
        "command": "uv",
        "args": ["run", "python", "-m", "news_agent.mcp_server"],
        "transport": "stdio",
    }
}


class AgentState(TypedDict):
    items: list[dict]
    synthesis: str


def _unwrap_tool_result(result) -> list[dict]:
    if isinstance(result, str):
        return json.loads(result)
    items = []
    for entry in result:
        if isinstance(entry, dict) and "text" in entry:
            items.append(json.loads(entry["text"]))
        elif isinstance(entry, dict):
            items.append(entry)
        else:
            items.append(json.loads(entry))
    return items


async def collect_node(state: AgentState) -> AgentState:
    client = MultiServerMCPClient(MCP_SERVER_PARAMS)
    tools = await client.get_tools()
    fetch_tool = next(t for t in tools if t.name == "fetch_ai_news")
    result = await fetch_tool.ainvoke({})
    items = _unwrap_tool_result(result)
    return {"items": items, "synthesis": ""}


def _build_synthesis_prompt(items: list[dict]) -> str:
    lines = [f"- [{it['source']}] {it['title']}: {it['summary'][:200]}" for it in items]
    joined = "\n".join(lines)
    return (
        "You are an AI engineering news analyst. Below is a list of recent items "
        "collected from AI/ML news sources (arXiv, Hacker News, company blogs).\n\n"
        f"{joined}\n\n"
        "Write a concise synthesis (4-6 sentences) of the most notable trends, "
        "announcements, or research directions visible across these items. "
        "Group related items together and do not invent facts that aren't present above."
    )


async def synthesize_node(state: AgentState) -> AgentState:
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.3)
    prompt = _build_synthesis_prompt(state["items"])
    response = await llm.ainvoke(prompt)
    return {"items": state["items"], "synthesis": response.content}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("collect", collect_node)
    graph.add_node("synthesize", synthesize_node)
    graph.set_entry_point("collect")
    graph.add_edge("collect", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


async def run_agent() -> tuple[str, list[NewsItem]]:
    app = build_graph()
    result = await app.ainvoke({"items": [], "synthesis": ""})
    items = [NewsItem(**it) for it in result["items"]]
    return result["synthesis"], items
