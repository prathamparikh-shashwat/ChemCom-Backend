from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)  # Snapshot of product name at order time
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Snapshot of product price at order time

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
