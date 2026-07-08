from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_order import crud_order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStats, OrderUpdateStatus

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: OrderCreate,
) -> Any:
    """
    Submit a customer order.
    This is a public endpoint accessible by the React Native client app.
    """
    try:
        return crud_order.create(db=db, obj_in=order_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[OrderResponse])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all orders.
    Requires Admin/Superuser authentication.
    """
    return crud_order.get_multi(db=db, skip=skip, limit=limit)


@router.get("/stats", response_model=OrderStats)
def read_order_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve dashboard statistics for order counts.
    Requires Admin/Superuser authentication.
    """
    return crud_order.get_stats(db=db)


@router.get("/{order_id}", response_model=OrderResponse)
def read_order_by_id(
    order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve details of a specific order by ID.
    Requires Admin/Superuser authentication.
    """
    order = crud_order.get(db=db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    *,
    order_id: int,
    db: Session = Depends(deps.get_db),
    status_in: OrderUpdateStatus,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update the status of an order.
    Requires Admin/Superuser authentication.
    """
    order = crud_order.get(db=db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return crud_order.update_status(db=db, db_obj=order, status=status_in.status)
