

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from services.user import UserService
from repository.user import UserRepository
from schemas.schemas import UserMinimal, UserWithTweets, useroutput
from dependencies.dependencies import get_db


router=APIRouter(prefix="/api/user",tags=["users"])
@router.get("/users/{user_id}", response_model=useroutput)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    # Fetch user profile by user_id
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    if user_id == 0:
        raise HTTPException(status_code=400, detail="User ID cannot be zero")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    try:
        return user_service.get_user_profile(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/search/users")
def search_users(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return repo.search_users(q)