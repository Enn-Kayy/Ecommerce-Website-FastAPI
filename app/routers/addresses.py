from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, utils, models
from ..database import get_db

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=schemas.AddressOut)
def create_address(
    payload: schemas.AddressCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    addr = models.Addresses(user_id=user.id,
                            street=payload.street,
                            city=payload.city,
                            state=payload.state,
                            country=payload.country,
                            postal_code=payload.postal_code,
                            is_default_shipping=payload.is_default_shipping,
                            is_default_billing=payload.is_default_billing)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.get("/", response_model=List[schemas.AddressOut])
def list_addresses(
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    return db.query(models.Addresses).filter(
        models.Addresses.user_id == user.id).all()


@router.patch("/{address_id}", response_model=schemas.AddressOut)
def update_address(
    address_id: int,
    payload: schemas.AddressCreate,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    addr = db.query(
        models.Addresses).filter(
        models.Addresses.address_id == address_id,
        models.Addresses.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(addr, k, v)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    user: models.Users = Depends(
        utils.get_current_user)):
    addr = db.query(
        models.Addresses).filter(
        models.Addresses.address_id == address_id,
        models.Addresses.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(addr)
    db.commit()
    return {"ok": True}
