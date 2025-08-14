from fastapi import HTTPException,status
from repository.media_attachment import attach_media
from schemas.schemas import tweetinput
import repository.tweet as tweet_repo
from repository.media import add_media

def get_tweet(db, tweet_id: int):
    tweet = tweet_repo.get_tweet_by_id(db, tweet_id)
    if not tweet:
        raise Exception("Tweet not found")
    return tweet

def get_user_tweets(db, user_id: int):
    return tweet_repo.get_tweets_by_user(db, user_id)

def post_tweet(db, tweet:tweetinput , user_id: int):
    content = tweet.content
    media_urls = tweet.media_urls

    if not content and not media_urls:
        raise ValueError("Tweet must have text or media.")

    if len(content) > 280:
        raise ValueError("Tweet exceeds 280 characters.")

    # Create tweet
    tweet = tweet_repo.create_tweet(db,tweet,user_id)

    # Attach media if any
    if media_urls:
       medias=add_media(db, media_urls)
    for media in medias:
        attach_media(db, media.id, target_type="tweet", target_id=tweet.id)

    # 3️⃣ Commit everything
    db.commit()
    return {
        "tweet_id": tweet.id,
        "content": tweet.content,
        "media": media_urls
    }
    
  