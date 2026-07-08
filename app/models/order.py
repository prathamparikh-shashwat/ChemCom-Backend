import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True, nullable=False)
    customer_email = Column(String, index=True, nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="Pending", index=True, nullable=False)  # Pending, Approved, Rejected, Completed
    created_at = Column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc), 
        nullable=False
    )

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

