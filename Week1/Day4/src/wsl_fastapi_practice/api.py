from __future__ import annotations
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Week 1 Day 4 - FastAPI Basics")


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
    # Override FastAPI RequestValidationError
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_type="validation_error",
            message="Request data is invalid",
            details=exc.errors(),
        ).model_dump(),
    )


# -------------------------
# Routes
# -------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


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


@app.post("/math/divide", response_model=DivideResponse)
async def divide(payload: DivideRequest):
    if payload.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return DivideResponse(result=payload.a / payload.b)
