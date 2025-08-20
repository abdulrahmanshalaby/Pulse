from typing import List
from fastapi import Depends, HTTPException, Query
from fastapi.routing import APIRouter
from redis import Redis
from sqlalchemy.orm import Session
from Models.models import User
from backend.src.utils.utils import extract_mentions
from services.tweets import TweetService
from schemas.schemas import TweetMinimal, TweetWithComments, tweetinput
from dependencies.dependencies import get_current_user, get_current_user_optional, get_redis_sync
from dependencies.dependencies import get_db


router=APIRouter(prefix="/api/tweet", tags=["tweets"])
@router.get("/{tweet_id}", response_model=TweetWithComments)
def read_tweet(tweet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional), redis_client: Redis = Depends(get_redis_sync)):
    tweet_service= TweetService(db,redis_client)
    try:
        return tweet_service.get_tweet(tweet_id, current_user.id if current_user else None)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=TweetMinimal)
def create_tweet(tweet:tweetinput, db: Session = Depends(get_db), current_user:User=Depends(get_current_user),redis_client:Redis=Depends(get_redis_sync)):
    tweet_service = TweetService(db,redis_client)
    # Ensure the user is authenticated  
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not tweet.content:
        raise HTTPException(status_code=400, detail="Content is required")
    if len(tweet.content) > 280:
        raise HTTPException(status_code=400, detail="Content exceeds 280 characters limit")
    try:
        tweet=tweet_service.post_tweet(tweet, current_user.id)
        mentioned_usernames = extract_mentions(tweet.content)
       #lookup valid users
        mentioned_users = db.query(User).filter(User.username.in_(mentioned_usernames)).all()
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
@router.get("/user/{user_id}", response_model=List[TweetMinimal])
def get_tweets_by_user(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    redis_client:Redis=Depends(get_redis_sync)
):
    tweet_service = TweetService(db,redis_client)
    try:
        return tweet_service.get_user_tweets(user_id=user_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
