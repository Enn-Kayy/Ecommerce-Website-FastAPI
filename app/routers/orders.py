from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/from-cart/{cart_id}", response_model=schemas.OrderOut)
def checkout_from_cart(
    cart_id: int,
    payload: schemas.CartCheckout,
    db: Session = Depends(get_db),
    user: models.Users = Depends(utils.get_current_user)
):
    # ✅ Validate the cart belongs to the logged in user
    cart = crud.get_or_create_cart_for_user(db, user)
    if cart.cart_id != cart_id:
        raise HTTPException(
            status_code=403,
            detail="Cart does not belong to user")

    try:
        order = crud.create_order_from_cart(
            db,
            user,
            shipping_address_id=payload.shipping_address_id,
            billing_address_id=payload.billing_address_id
        )
        return order

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/buy-now", response_model=schemas.OrderOut)
def buy_now(
    payload: schemas.BuyNowPayload,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    try:
        order = crud.create_order_buy_now(
            db,
            user,
            payload.product_id,
            payload.quantity,
            shipping_address_id=payload.shipping_address_id,
            billing_address_id=payload.billing_address_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order


@router.get("/", response_model=List[schemas.OrderOut])
def list_user_orders(
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    return crud.get_orders_for_user(db, user)


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    order = db.query(
        models.Orders).filter(
        models.Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # allow access only if owner or admin
    if order.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    return order
