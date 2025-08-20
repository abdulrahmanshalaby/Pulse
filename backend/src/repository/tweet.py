from sqlalchemy import exists, or_
from sqlalchemy.orm import Session
from Models.models import Media, MediaAttachment, Tweet,likes_table
from schemas.schemas import tweetinput
class tweetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_tweet_by_id(self, tweet_id: int,current_user_id: int = None):
    # Query tweet and media in one go
     result = (
        self.db.query(Tweet, Media)
        .outerjoin(MediaAttachment, MediaAttachment.target_id == Tweet.id)
        .outerjoin(Media, Media.id == MediaAttachment.media_id)
        .filter(Tweet.id == tweet_id, (MediaAttachment.target_type == "tweet") | (MediaAttachment.target_type == None))
        .all()
     )

     if not result:
        raise Exception("Tweet not found")

     tweet = result[0][0]
     tweet.media_files = [media.file_url for _, media in result if media]
     if current_user_id:
        liked = (
            self.db.query(exists().where(
                (likes_table.c.tweet_id == tweet.id) & (likes_table.c.user_id == current_user_id)
            ))
            .scalar()
        )
        tweet.liked_by_me = liked
     else:
        tweet.liked_by_me = False
     return tweet
    def create_tweet(self, tweet:tweetinput, user_id: int):
     tweet = Tweet(user_id=user_id,content=tweet.content)
     self.db.add(tweet)

     return tweet

    def get_tweets_by_user(self, user_id: int, limit: int = 20, offset: int = 0):
     rows = (
        self.db.query(Tweet, Media)
        .outerjoin(MediaAttachment, MediaAttachment.target_id == Tweet.id)
        .outerjoin(Media, Media.id == MediaAttachment.media_id)
        .filter(Tweet.user_id == user_id, or_(MediaAttachment.target_type == "tweet", MediaAttachment.target_type == None))
        .order_by(Tweet.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
     )

     tweets_dict = {}
     ordered_ids = []
     for tweet, media in rows:
        if tweet.id not in tweets_dict:
            tweet.media_files = []
            tweets_dict[tweet.id] = tweet
            ordered_ids.append(tweet.id)
        if media:
            tweet.media_files.append(media.file_url)

     # preserve ordering as returned by ordered_ids
     return [tweets_dict[t_id] for t_id in ordered_ids]