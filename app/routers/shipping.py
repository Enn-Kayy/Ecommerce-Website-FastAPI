from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/shipping", tags=["Shipping (Only Admin)"])


@router.post("/create")
def create_shipping(
    order_id: int,
    courier_name: str,
    tracking_number: str,
    db: Session = Depends(get_db),
    admin: models.Users = Depends(
        utils.get_current_admin_user)):
    order = db.query(
        models.Orders).filter(
        models.Orders.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    ship = models.Shipping(
        order_id=order.id,
        courier_name=courier_name,
        tracking_number=tracking_number,
        status="shipped")
    db.add(ship)
    order.status = "shipped"
    db.commit()
    db.refresh(ship)
    return ship


@router.get("/", response_model=List[schemas.OrderOut])
def list_shippable_orders(
    db: Session = Depends(get_db),
    admin: models.Users = Depends(
        utils.get_current_admin_user)):
    # admins can list orders for shipping
    return db.query(models.Orders).all()
