from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    source: str
    title: str
    link: str
    summary: str
    published: str


class Digest(BaseModel):
    id: int | None = None
    created_at: datetime
    synthesis: str
    items: list[NewsItem]
