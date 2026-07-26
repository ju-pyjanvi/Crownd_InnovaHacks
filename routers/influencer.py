from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from datetime import timedelta

router = APIRouter()

@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_ig = db.query(models.User).filter(models.User.instagram_handle == user.instagram_handle).first()
    if existing_ig:
        raise HTTPException(status_code=400, detail="Instagram handle already registered")

    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        instagram_handle=user.instagram_handle,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    wallet = models.Wallet(user_id=new_user.id)
    db.add(wallet)

    score = models.CrowndScore(user_id=new_user.id)
    db.add(score)

    db.commit()
    return new_user

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = auth.create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.get("/score", response_model=schemas.CrowndScoreOut)
def get_score(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    score = db.query(models.CrowndScore).filter(models.CrowndScore.user_id == current_user.id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score