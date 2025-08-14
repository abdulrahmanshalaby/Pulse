from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from schemas.schemas import TweetWithComments, tweetinput
from dependencies.dependencies import get_current_user
from dependencies.dependencies import get_db
from services.tweets import get_tweet, post_tweet


router=APIRouter(prefix="/api/tweets")
@router.get("/{tweet_id}", response_model=TweetWithComments)
def read_tweet(tweet_id: int, db: Session = Depends(get_db)):
    try:
        return get_tweet(db, tweet_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/tweets", response_model=TweetWithComments)
def create_tweet(tweet:tweetinput, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return post_tweet(db, tweet, current_user.id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
