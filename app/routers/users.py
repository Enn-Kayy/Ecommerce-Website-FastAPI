from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models, utils
from ..database import get_db

router = APIRouter(prefix="/users")

# Get current logged-in user


@router.get("/me", response_model=schemas.UserOut, tags=["Users"])
def read_current_user(
    current_user: models.Users = Depends(
        utils.get_current_user)):
    return current_user


# Update a user
@router.patch("/{user_id}", response_model=schemas.UserOut, tags=["Users"])
def update_user(user_id: int, payload: schemas.UserCreate,
                db: Session = Depends(get_db),
                current_user: models.Users = Depends(utils.get_current_user)):
    # allow update for self or admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")

    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # update fields
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.phone_number = payload.phone_number
    db.commit()
    db.refresh(user)
    return user

# Delete a user (admin only)


@router.delete("/{user_id}", tags=["Users"])
def delete_user(user_id: int,
                db: Session = Depends(get_db),
                admin: models.Users = Depends(utils.get_current_admin_user)):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}


# List all users (admin only)
@router.get("/",
            response_model=List[schemas.UserOut],
            tags=["Users (Only admin)"])
def list_users(skip: int = 0, limit: int = 50,
               db: Session = Depends(get_db),
               admin: models.Users = Depends(utils.get_current_admin_user)):
    users = db.query(models.Users).offset(skip).limit(limit).all()
    return users
