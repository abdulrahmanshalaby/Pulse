from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from services.user import UserService
from schemas.schemas import UserMinimal, userinput,useroutput
from Models.models import User
from authorization.auth import create_access_token ,verify_password
from dependencies.dependencies import get_db
from dependencies.dependencies import get_current_user
router=APIRouter(prefix="/api/auth",tags=["auth"])

@router.post("/register", response_model=UserMinimal)
async def register_endpoint(user_data: userinput, db: Session = Depends(get_db)):
    user_service = UserService(db)
    # Register a new user           
    if not user_data.username or not user_data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    try:    
        return user_service.register_user(user_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print("Register error:", e)   
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    if len(form_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    # Check if user exists and password is correct
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=useroutput)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user