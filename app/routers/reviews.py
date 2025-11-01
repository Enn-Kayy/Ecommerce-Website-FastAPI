from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=schemas.ReviewOut)
def add_review(
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    try:
        review = crud.create_review(db, user, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return review


@router.get("/product/{product_id}", response_model=List[schemas.ReviewOut])
def get_reviews_for_product(product_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(models.Reviews, models.Users.first_name)
          .join(models.Users, models.Reviews.user_id == models.Users.id)
          .filter(models.Reviews.product_id == product_id)
          .all()
    )

    return [
        {
            "review_id": review.review_id,  # <-- use review_id, not id
            "name": name,
            "rating": review.rating,
            "comment": review.comment,
            "product_id": review.product_id
        }
        for review, name in reviews
    ]
