from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from services.user import register_user
from schemas.schemas import UserMinimal, userinput,useroutput
from Models.tweets import User
from authorization.auth import create_access_token, hash_password, verify_password
from dependencies import get_db
from dependencies.dependencies import get_current_user
router=APIRouter(prefix="/api/auth",tags=["auth"])

@router.post("/register", response_model=UserMinimal)
def register_endpoint(user_data: userinput, db: Session = Depends(get_db)):
    try:
        return register_user(db, user_data.dict())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=useroutput)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user