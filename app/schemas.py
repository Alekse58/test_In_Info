from pydantic import BaseModel


class ItemCreate(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    photo_id: int


class ItemUpdate(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    photo_id: int


class ItemResponse(BaseModel):
    id: int
    x1: float
    y1: float
    x2: float
    y2: float
    photo_id: int
