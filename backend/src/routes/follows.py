

from fastapi import Depends,APIRouter, HTTPException,status
from schemas.schemas import User, UserMinimal
from backend.src.services.follow import follow_service
from services.user import get_user_profile
from dependencies.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session

router=APIRouter(prefix="/api/follow",tags=["follows"])

def follow_user(user:UserMinimal,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    target_user=get_user_profile(db,user.id)
    if not target_user:
        raise HTTPException(404, "User not found")
    if current_user.id == user.id:
        raise ValueError("You cannot follow yourself")

    # Check if already following (assume current_user.following is a list of User ORM objects)
    if any(followed.id == user.id for followed in current_user.following):
        raise ValueError("Already following this user")
 
    try:
        follow_service(user,db,current_user)
        db.commit()  # commit once after all service logic
        return {"message": f"Followed user {target_user.username}"}
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail=f"Couldn't Follow{user.username}, Please try again" )
    
