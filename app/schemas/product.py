from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    price: float = Field(..., gt=0.0, description="Price of the product")
    photo_url: Optional[str] = Field(None, description="URL of the product photo stored in Cloudinary")
    is_active: bool = Field(True, description="Whether the product is currently active")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    price: Optional[float] = Field(None, gt=0.0, description="Price of the product")
    photo_url: Optional[str] = Field(None, description="URL of the product photo")
    is_active: Optional[bool] = Field(None, description="Whether the product is active")


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
