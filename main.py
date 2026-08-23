from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Playground")


class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
    description: str | None = None
    tags: list[str] = []


db: dict[int, Item] = {}
next_id = 1


@app.get("/")
def root():
    return {"message": "Hello, FastAPI + Pydantic"}


@app.get("/items")
def list_items(q: Annotated[str | None, Query(max_length=50)] = None):
    if q is None:
        return db
    return {i: item for i, item in db.items() if q.lower() in item.name.lower()}


@app.post("/items", status_code=201)
def create_item(item: Item):
    global next_id
    db[next_id] = item
    next_id += 1
    return {"id": next_id - 1, **item.model_dump()}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]
