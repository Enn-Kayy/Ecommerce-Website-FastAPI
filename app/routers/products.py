from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, database, models
from ..utils import get_current_admin_user

router = APIRouter(prefix="/products")


@router.post("/", response_model=schemas.ProductOut,
             tags=["Products (Only admin)"])
def create_product(payload: schemas.ProductCreate,
                   db: Session = Depends(database.get_db),
                   admin: models.Users = Depends(get_current_admin_user)):
    return crud.create_product(db, payload)

@router.get("/products/",
            response_model=list[schemas.ProductOut],
            tags=["Products"])
def get_products(db: Session = Depends(database.get_db)):
    return crud.list_products(db)

@router.get("/products/{product_id}",
            response_model=schemas.ProductOut,
            tags=["Products"])
def get_product(product_id: int, db: Session = Depends(database.get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found")
    return product


@router.put("/{product_id}",
            response_model=schemas.ProductOut,
            tags=["Products (Only admin)"])
def update_product(product_id: int,
                   payload: schemas.ProductUpdate,
                   db: Session = Depends(database.get_db),
                   admin: models.Users = Depends(get_current_admin_user)):
    updated = crud.update_product(db, product_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found")
    return updated

# -------------------- DELETE PRODUCT --------------------


@router.delete("/{product_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               tags=["Products (Only admin)"])
def delete_product(product_id: int,
                   db: Session = Depends(database.get_db),
                   admin: models.Users = Depends(get_current_admin_user)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found")
    return