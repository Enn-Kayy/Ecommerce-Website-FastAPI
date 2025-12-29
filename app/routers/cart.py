from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/items", response_model=schemas.CartItemOut)
def add_cart_item(
    payload: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    try:
        item = crud.add_item_to_cart(
            db, user, payload.product_id, payload.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(item)
    return item


@router.get("/", response_model=schemas.CartOut)
def get_cart(
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    cart = crud.get_or_create_cart_for_user(db, user)
    items = crud.list_cart_items(db, user)
    cart.cart_items = items
    cart = crud.get_or_create_cart_for_user(db, user)
    return cart


@router.delete("/items/{cart_item_id}")
def remove_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    ok = crud.remove_item_from_cart(db, user, cart_item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}