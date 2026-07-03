from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field


class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the item")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    price: float = Field(..., ge=0.0, description="Price per item")


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Name of the customer")
    customer_email: Optional[EmailStr] = Field(None, description="Email of the customer")
    items: List[OrderItem] = Field(..., min_length=1, description="List of items ordered")
    total_amount: float = Field(..., ge=0.0, description="Total order amount")


class OrderCreate(OrderBase):
    pass


class OrderUpdateStatus(BaseModel):
    status: Literal["Pending", "Approved", "Rejected", "Completed"] = Field(
        ..., description="New status of the order"
    )


class OrderResponse(OrderBase):
    id: int
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
