from typing import Any, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderStats


class CRUDOrder:
    def get(self, db: Session, id: Any) -> Optional[Order]:
        """Fetch a single order by ID."""
        return db.query(Order).filter(Order.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Order]:
        """Fetch all orders, ordered by newest first with pagination."""
        return (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: OrderCreate) -> Order:
        """Create a new customer order with default 'Pending' status."""
        # Convert List[OrderItem] pydantic models to dicts for JSON database storage
        serialized_items = [item.model_dump() for item in obj_in.items]
        
        db_obj = Order(
            customer_name=obj_in.customer_name,
            customer_email=obj_in.customer_email,
            items=serialized_items,
            total_amount=obj_in.total_amount,
            status="Pending",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(self, db: Session, *, db_obj: Order, status: str) -> Order:
        """Update the status of an existing order."""
        db_obj.status = status
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_stats(self, db: Session) -> OrderStats:
        """Calculate counts of orders by status for the dashboard counts."""
        group_results = (
            db.query(Order.status, func.count(Order.id))
            .group_by(Order.status)
            .all()
        )
        
        stats_map = {
            "total_orders": 0,
            "pending_orders": 0,
            "approved_orders": 0,
            "completed_orders": 0,
            "rejected_orders": 0,
        }
        
        for status_name, count in group_results:
            stats_map["total_orders"] += count
            if status_name == "Pending":
                stats_map["pending_orders"] = count
            elif status_name == "Approved":
                stats_map["approved_orders"] = count
            elif status_name == "Completed":
                stats_map["completed_orders"] = count
            elif status_name == "Rejected":
                stats_map["rejected_orders"] = count
                
        return OrderStats(**stats_map)


crud_order = CRUDOrder()
