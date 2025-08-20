from fastapi import APIRouter, Depends, HTTPException

from Models.models import User
from services.likes import LikeService
from sqlalchemy.orm import Session
from dependencies.dependencies import get_current_user, get_db, get_redis_sync


router = APIRouter(prefix="/api/tweet", tags=["likes"])

@router.post("/{tweet_id}/like")
def like_tweet(tweet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), redis_client = Depends(get_redis_sync)):
    svc = LikeService(db, redis_client)
    try:
        return svc.like(current_user.id, tweet_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error{str(e)}")
@router.delete("/{tweet_id}/like")
def unlike_tweet(tweet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), redis_client = Depends(get_redis_sync)):
    svc = LikeService(db, redis_client)
    try:
        return svc.unlike(current_user.id, tweet_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")    