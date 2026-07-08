from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field


class OrderItem(BaseModel):
    product_id: int = Field(..., description="ID of the ordered product")
    name: str = Field(..., min_length=1, description="Name of the item")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    price: float = Field(..., ge=0.0, description="Price per item")

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., description="ID of the product to order")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Name of the customer")
    customer_email: Optional[EmailStr] = Field(None, description="Email of the customer")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of items to order")


class OrderUpdateStatus(BaseModel):
    status: Literal["Pending", "Approved", "Rejected", "Completed"] = Field(
        ..., description="New status of the order"
    )


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: Optional[EmailStr] = None
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    approved_orders: int
    completed_orders: int
    rejected_orders: int

