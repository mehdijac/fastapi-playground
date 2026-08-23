import importlib

import pytest
from fastapi.testclient import TestClient

from news_agent.agent import _unwrap_tool_result
from news_agent.mcp_server import _strip_html
from news_agent.models import NewsItem


def test_strip_html():
    assert _strip_html("<p>Hello <a href='x'>world</a></p>") == "Hello world"


def test_unwrap_tool_result_json_string():
    result = '[{"source": "A", "title": "T"}]'
    assert _unwrap_tool_result(result) == [{"source": "A", "title": "T"}]


def test_unwrap_tool_result_text_blocks():
    result = [{"type": "text", "text": '{"source": "A"}', "id": "1"}]
    assert _unwrap_tool_result(result) == [{"source": "A"}]


def test_unwrap_tool_result_plain_dicts():
    result = [{"source": "A"}]
    assert _unwrap_tool_result(result) == [{"source": "A"}]


@pytest.fixture
def news_item():
    return NewsItem(
        source="Test Source",
        title="Test Title",
        link="https://example.com/article",
        summary="Test summary",
        published="Mon, 01 Jan 2026 00:00:00 +0000",
    )


@pytest.fixture
def api_module(tmp_path, monkeypatch):
    import news_agent.config as config

    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "test.db"))

    import news_agent.storage as storage

    importlib.reload(storage)

    import news_agent.api as api

    monkeypatch.setattr(api, "get_latest_digest", storage.get_latest_digest)
    monkeypatch.setattr(api, "save_digest", storage.save_digest)
    return api


def test_index_with_no_digest(api_module):
    client = TestClient(api_module.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "No digest yet" in response.text


def test_digest_latest_empty(api_module):
    client = TestClient(api_module.app)
    response = client.get("/digest/latest")
    assert response.status_code == 200
    assert response.json() is None


def test_refresh_and_index(api_module, news_item, monkeypatch):
    async def fake_run_agent():
        return "A **bold** synthesis.", [news_item]

    monkeypatch.setattr(api_module, "run_agent", fake_run_agent)
    client = TestClient(api_module.app)

    response = client.post("/refresh", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

    index = client.get("/")
    assert "<strong>bold</strong>" in index.text
    assert "Test Title" in index.text
    assert "https://example.com/article" in index.text

    latest = client.get("/digest/latest").json()
    assert latest["synthesis"] == "A **bold** synthesis."
    assert latest["items"][0]["title"] == "Test Title"


def test_render_bold_escapes_html():
    from news_agent.api import render_bold

    result = render_bold("<script>alert(1)</script> **bold**")
    assert "<script>" not in str(result)
    assert "<strong>bold</strong>" in str(result)


def test_observability_disabled_by_default_in_tests():
    from news_agent.config import ENABLE_OBSERVABILITY

    assert ENABLE_OBSERVABILITY is False


def test_setup_observability_is_noop_when_disabled(monkeypatch):
    import news_agent.observability as observability

    monkeypatch.setattr(observability, "ENABLE_OBSERVABILITY", False)
    monkeypatch.setattr(observability, "_instrumented", False)

    from fastapi import FastAPI

    app = FastAPI()
    observability.setup_observability(app)

    assert observability._instrumented is False
