from typing import Any, List, Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct:
    def get(self, db: Session, id: Any) -> Optional[Product]:
        """Fetch a single product by ID."""
        return db.query(Product).filter(Product.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """Fetch all active products with pagination."""
        return (
            db.query(Product)
            .filter(Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_all(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        """Fetch all products (active or not) for admin views with pagination."""
        return (
            db.query(Product)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """Create a new product."""
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            photo_url=obj_in.photo_url,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        """Update an existing product."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate(self, db: Session, *, db_obj: Product) -> Product:
        """Deactivate a product (soft delete)."""
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


crud_product = CRUDProduct()
