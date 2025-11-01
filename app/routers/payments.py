from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=schemas.OrderOut)
def create_payment(
    payload: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    # very simple flow: mark payment and return order
    order = db.query(
        models.Orders).filter(
        models.Orders.id == payload.order_id).first()
    if not order or order.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Order not found or not yours")
    pay = models.Payments(
        order_id=order.id,
        payment_method=payload.payment_method,
        amount=payload.amount,
        status="completed")
    db.add(pay)
    order.status = "paid"
    db.commit()
    db.refresh(order)
    return order
