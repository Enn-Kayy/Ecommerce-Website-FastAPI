from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import UserCreate  # ✅ Correct import
from app import crud, utils
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", summary="Create a new user")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(user.password)
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_pw)
    return {"message": "User created successfully", "email": new_user.email}


@router.post("/login", summary="User Login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not utils.verify_password(
            form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password")

    token = utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
