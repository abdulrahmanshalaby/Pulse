

from fastapi import Depends,APIRouter, HTTPException,status
from redis import Redis
from Models.tweets import User
from schemas.schemas import UserMinimal
from services.follow import FollowService
from services.user import UserService
from dependencies.dependencies import get_current_user, get_db, get_redis_sync
from sqlalchemy.orm import Session

router=APIRouter(prefix="/api/follow",tags=["follows"])
@router.post("/")
def follow_user(user:UserMinimal, db:Session=Depends(get_db), current_user:User=Depends(get_current_user), redis_client:Redis=Depends(get_redis_sync)):
    follow_service = FollowService(db, redis_client)
    user_service = UserService(db)

    # validate target user exists
    target_user = user_service.get_user_profile(user.id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # cannot follow yourself
    if current_user.id == user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    # check if already following (use service/repo)
    try:
        following = follow_service.get_following(current_user.id)
        if any(f.id == user.id for f in following):
            raise HTTPException(status_code=400, detail="Already following this user")
    except HTTPException:
        raise
    except Exception:
        # if the quick check fails, continue and let follow_service handle duplicates
        pass

    try:
        # follow_service will perform DB write and commit; keep route thin
        result = follow_service.follow_service(user, current_user)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        # rollback if something escaped (safety)
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Internal server error")
@router.get("/followers}", response_model=list[UserMinimal])   
def get_followers(db: Session = Depends(get_db),current_user:User=Depends(get_current_user), redis_client: Redis = Depends(get_redis_sync)):
    follow_service = FollowService(db, redis_client)
    try:
        followers = follow_service.get_followers(current_user.id)
        return followers
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/following", response_model=list[UserMinimal])
def get_following(db: Session = Depends(get_db),current_user:User=Depends(get_current_user) ,redis_client: Redis = Depends(get_redis_sync)):
    follow_service = FollowService(db, redis_client)
    try:
        following = follow_service.get_following(current_user.id)
        return following
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")