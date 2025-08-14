

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import UserWithTweets
from dependencies.dependencies import get_db
from services.user import get_user_profile


router=APIRouter(prefix="/api/user",tags=["users"])
@router.get("/users/{user_id}", response_model=UserWithTweets)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return get_user_profile(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
