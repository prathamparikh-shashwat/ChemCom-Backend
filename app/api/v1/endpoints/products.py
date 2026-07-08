from typing import Any, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.crud.crud_product import crud_product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.post("/", response_model=ProductResponse)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    is_active: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new product.
    Requires Admin/Superuser authentication.
    If a photo file is uploaded, it is stored on Cloudinary.
    """
    photo_url = None
    if file:
        if not settings.CLOUDINARY_URL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cloudinary is not configured. Please set CLOUDINARY_URL in your .env file.",
            )
        try:
            import cloudinary.uploader
            
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder="products"
            )
            photo_url = upload_result.get("secure_url")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to Cloudinary: {str(e)}"
            )

    product_in = ProductCreate(
        name=name,
        description=description,
        price=price,
        photo_url=photo_url,
        is_active=is_active,
    )
    return crud_product.create(db=db, obj_in=product_in)


@router.get("/", response_model=List[ProductResponse])
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active products.
    Public endpoint.
    """
    return crud_product.get_multi(db=db, skip=skip, limit=limit)


@router.get("/all", response_model=List[ProductResponse])
def read_all_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all products (active and inactive).
    Requires Admin/Superuser authentication.
    """
    return crud_product.get_multi_all(db=db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product_by_id(
    product_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve details of a specific product by ID.
    Public endpoint.
    """
    product = crud_product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    *,
    product_id: int,
    db: Session = Depends(deps.get_db),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    is_active: Optional[bool] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a product.
    Requires Admin/Superuser authentication.
    If a new photo file is uploaded, it replaces the existing photo on Cloudinary.
    """
    product = crud_product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    photo_url = None
    if file:
        if not settings.CLOUDINARY_URL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cloudinary is not configured. Please set CLOUDINARY_URL in your .env file.",
            )
        try:
            import cloudinary.uploader
            
            cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder="products"
            )
            photo_url = upload_result.get("secure_url")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to Cloudinary: {str(e)}"
            )

    product_update = ProductUpdate(
        name=name,
        description=description,
        price=price,
        is_active=is_active,
    )
    if photo_url:
        product_update.photo_url = photo_url

    return crud_product.update(db=db, db_obj=product, obj_in=product_update)


@router.delete("/{product_id}", response_model=ProductResponse)
def deactivate_product(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Deactivate a product (soft delete).
    Requires Admin/Superuser authentication.
    """
    product = crud_product.get(db=db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return crud_product.deactivate(db=db, db_obj=product)
