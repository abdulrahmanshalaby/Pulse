import json
import os
from re import M
from fastapi import HTTPException,status
from redis import Redis
from requests import Session
from dependencies.dependencies import publish_notification
from repository.tweet import tweetRepository
from repository.media_attachment import MediaRepository
from schemas.schemas import tweetinput
MAX_NOTIFICATIONS = os.getenv("MAX_NOTIFICATIONS")
class TweetService:
    def __init__(self, db:Session,redis_client:Redis):
        self.db = db
        self.redis_client=redis_client
    def get_tweet(self, tweet_id: int, current_user_id: int = None):
      tweet_repo = tweetRepository(self.db)
      tweet = tweet_repo.get_tweet_by_id(tweet_id,current_user_id)
      if not tweet:
        raise Exception("Tweet not found")
      return tweet

    def get_user_tweets(self, user_id: int):
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")
        tweet_repo = tweetRepository(self.db)
        return tweet_repo.get_tweets_by_user(user_id)

    async def post_tweet(self, tweet:tweetinput , user_id: int):
      tweet_repo = tweetRepository(self.db)
      media_repo = MediaRepository(self.db)
      content = tweet.content
      media_urls = tweet.media_urls

      if not content and not media_urls:
        raise ValueError("Tweet must have text or media.")

      if len(content) > 280:
        raise ValueError("Tweet exceeds 280 characters.")

    # Create tweet
      tweet = tweet_repo.create_tweet(tweet,user_id)

    # Attach media if any
      if media_urls:
        medias=media_repo.add_media(media_urls)
        for media in medias:
         media_repo.attach_media(media.id, target_type="tweet", target_id=tweet.id)

    # 3️⃣ Commit everything
      self.db.commit()
      payload = {
            "type": "tweet_created",
            "tweet_id": tweet.id,
            "author_id": user_id,
            "created_at": tweet.created_at.isoformat(),
            "content_preview": (tweet.content or "")[:200],
        }

        
      try:
 
            followers =self.redis_client.smembers(f"followers:{user_id}")

    # Publish to each follower's channel
            for follower_id in followers:
             self.redis_client.publish(f"notifications:{follower_id}", json.dumps(payload))
             await self.redis_client.rpush(f"notifications_list:{follower_id}", json.dumps(payload))
             await self.redis_client.ltrim(f"notifications_list:{follower_id}", -MAX_NOTIFICATIONS, -1)

      except Exception:
            # swallow to avoid breaking API if Redis is down
            pass



      return tweet
    
    