from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.utils import get_current_admin_user
from app import crud, schemas, database
router = APIRouter(prefix="/categories")


# Create a category
@router.post("/", response_model=schemas.CategoryOut,
             tags=["Categories (Only admin)"])
def create_category(payload: schemas.CategoryCreate,
                    db: Session = Depends(get_db),
                    admin: models.Users = Depends(get_current_admin_user)):
    # Check if category exists
    existing = db.query(models.Categories).filter(
        models.Categories.category_name == payload.category_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Categories(
        category_name=payload.category_name,
        description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category  # Make sure this exists in crud.py

# Get all categories


@router.get("/categories/",
            response_model=list[schemas.CategoryOut],
            tags=["Categories"])
def get_categories(db: Session = Depends(database.get_db)):
    return crud.get_all_categories(db)  # <-- Use the correct function name


@router.get("/{category_id}",
            response_model=schemas.CategoryOut,
            tags=["Categories"])
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}",
            response_model=schemas.CategoryOut,
            tags=["Categories (Only admin)"])
def update_category(
        category_id: int,
        payload: schemas.CategoryCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)):
    updated = crud.update_category(db, category_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@router.delete("/{category_id}", tags=["Categories (Only admin)"])
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)):
    success = crud.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
