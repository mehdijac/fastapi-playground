import re
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape

from news_agent.agent import run_agent
from news_agent.models import Digest
from news_agent.storage import get_latest_digest, save_digest

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AI Engineering News Agent")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def render_bold(text: str) -> Markup:
    escaped = str(escape(text))
    return Markup(_BOLD_RE.sub(r"<strong>\1</strong>", escaped))


templates.env.filters["render_bold"] = render_bold


@app.post("/digest/refresh", response_model=Digest)
async def refresh_digest() -> Digest:
    synthesis, items = await run_agent()
    return save_digest(synthesis, items)


@app.get("/digest/latest", response_model=Digest | None)
def latest_digest() -> Digest | None:
    return get_latest_digest()


@app.post("/refresh")
async def refresh_and_redirect() -> RedirectResponse:
    synthesis, items = await run_agent()
    save_digest(synthesis, items)
    return RedirectResponse(url="/", status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    digest = get_latest_digest()
    return templates.TemplateResponse(request, "index.html", {"digest": digest})
