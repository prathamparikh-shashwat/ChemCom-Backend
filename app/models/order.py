import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, JSON

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True, nullable=False)
    customer_email = Column(String, index=True, nullable=True)
    items = Column(JSON, nullable=False)  # Stores array of items e.g., [{"name": "item", "quantity": 1, "price": 10.0}]
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="Pending", index=True, nullable=False)  # Pending, Approved, Rejected, Completed
    created_at = Column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc), 
        nullable=False
    )
