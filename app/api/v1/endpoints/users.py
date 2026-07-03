from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.crud.crud_order import crud_order
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.order import OrderResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all users. Superuser privileges required.
    """
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new user. Superuser privileges required.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username/email already exists.",
        )
    return crud_user.create(db, obj_in=user_in)


@router.post("/signup", response_model=UserResponse)
def signup_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Public endpoint for self-registration.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )
    # Ensure public signup doesn't allow registering a superuser directly
    user_in.is_superuser = False
    return crud_user.create(db, obj_in=user_in)


@router.post("/admin", response_model=UserResponse)
def create_admin_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    x_admin_creation_key: Optional[str] = Header(None),
) -> Any:
    """
    Create a new admin user.
    Allows creation if the database is currently empty (contains no users)
    or if the provided x-admin-creation-key matches settings.ADMIN_CREATION_KEY or settings.SECRET_KEY.
    """
    # Check if database is empty
    user_count = db.query(User).count()
    
    # Check if creation key is valid
    key_is_valid = False
    if x_admin_creation_key:
        if settings.ADMIN_CREATION_KEY and x_admin_creation_key == settings.ADMIN_CREATION_KEY:
            key_is_valid = True
        elif x_admin_creation_key == settings.SECRET_KEY:
            key_is_valid = True

    # Allow if database is empty OR valid key is provided
    if user_count > 0 and not key_is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin creation is forbidden. Please provide a valid X-Admin-Creation-Key header or use the CLI script.",
        )

    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username/email already exists.",
        )
    
    # Force superuser to be True
    user_in.is_superuser = True
    return crud_user.create(db, obj_in=user_in)


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get details of the currently authenticated user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own profile settings.
    """
    return crud_user.update(db, db_obj=current_user, obj_in=user_in)


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get user details by ID. Superuser privileges required.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist.",
        )
    return user


@router.get("/{user_id}/orders", response_model=List[OrderResponse])
def read_user_orders(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all orders belonging to a specific user by userid.
    Accessible by the user themselves or by a superuser.
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this ID does not exist.",
        )
    return crud_order.get_by_email(db, email=user.email)
