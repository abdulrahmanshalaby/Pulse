from sqlalchemy.orm import Session
from Models.tweets import Tweet
from backend.src.schemas.schemas import tweetinput
def get_tweet_by_id(db: Session, tweet_id: int):
    return db.query(Tweet).filter(Tweet.id == tweet_id).first()

def create_tweet(db: Session, tweet:tweetinput, user_id: int):
    tweet = Tweet(user_id=user_id,content=tweet.content,media_urls=tweetinput.media_urls)
    db.add(tweet)

    return tweet

def get_tweets_by_user(db: Session, user_id: int):
    return db.query(Tweet).filter(Tweet.user_id == user_id).all()
