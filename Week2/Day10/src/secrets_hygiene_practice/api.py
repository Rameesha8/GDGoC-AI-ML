from __future__ import annotations
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# -------------------------
# Your project imports
# -------------------------
from secrets_hygiene_practice.settings import get_settings
from secrets_hygiene_practice.db import get_db
from secrets_hygiene_practice.models import Item
from sqlalchemy.orm import Session
import psycopg
from qdrant_client import QdrantClient

# -------------------------
# App & settings
# -------------------------
settings = get_settings()
app = FastAPI(title=settings.app_name)


# -------------------------
# Pydantic models
# -------------------------
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    in_stock: bool = True


class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool
    created_at: str | None = None  # for DB items


class DivideRequest(BaseModel):
    a: float
    b: float


class DivideResponse(BaseModel):
    result: float


class ErrorResponse(BaseModel):
    error_type: str
    message: str
    details: list[dict] | None = None


# -------------------------
# In-memory "database"
# -------------------------
_items: Dict[int, ItemOut] = {}
_next_id = 1


# -------------------------
# Error handling
# -------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_type="validation_error",
            message="Request data is invalid",
            details=exc.errors(),
        ).model_dump(),
    )


# -------------------------
# Basic routes
# -------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# -------------------------
# In-memory routes
# -------------------------
@app.post("/items", response_model=ItemOut, status_code=201)
async def create_item(payload: ItemCreate):
    global _next_id
    item = ItemOut(id=_next_id, **payload.model_dump())
    _items[_next_id] = item
    _next_id += 1
    return item


@app.get("/items", response_model=List[ItemOut])
async def list_items():
    return list(_items.values())


@app.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return _items[item_id]


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
    return None


# -------------------------
# DB-backed routes
# -------------------------
@app.post("/db/items", status_code=201)
async def create_db_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(
        name=payload.name,
        price=payload.price,
        in_stock=payload.in_stock,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "in_stock": item.in_stock,
        "created_at": item.created_at,
    }


@app.get("/db/items")
async def list_db_items(db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.id.asc()).all()
    return [
        {
            "id": x.id,
            "name": x.name,
            "price": x.price,
            "in_stock": x.in_stock,
            "created_at": x.created_at,
        }
        for x in items
    ]


# -------------------------
# Math route
# -------------------------
@app.post("/math/divide", response_model=DivideResponse)
async def divide(payload: DivideRequest):
    if payload.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return DivideResponse(result=payload.a / payload.b)


# -------------------------
# Config route
# -------------------------
@app.get("/config")
async def show_config():
    s = get_settings()
    return {
        "app_name": s.app_name,
        "environment": s.environment,
        "debug": s.debug,
        "host": s.host,
        "port": s.port,
        "allowed_origins": s.allowed_origins,
    }


# -------------------------
# Secure data route
# -------------------------
@app.get("/secure-data")
async def secure_data(x_api_key: str | None = Header(default=None)):
    s = get_settings()
    if x_api_key != s.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"secret_data": "approved"}


# -------------------------
# Postgres health
# -------------------------
@app.get("/db/health")
async def db_health():
    s = get_settings()
    try:
        with psycopg.connect(s.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                _ = cur.fetchone()
        return {"postgres": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"postgres not ready: {e}")


# -------------------------
# Qdrant health
# -------------------------
@app.get("/qdrant/health")
async def qdrant_health():
    s = get_settings()
    try:
        client = QdrantClient(url=s.qdrant_url)
        _ = client.get_collections()
        return {"qdrant": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"qdrant not ready: {e}")
