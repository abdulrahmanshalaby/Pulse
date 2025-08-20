import json
import os
from re import M
from redis import Redis

from Models.models import Tweet
from sqlalchemy.orm import Session
from dependencies.dependencies import publish_notification
from repository.likes import LikeRepository
MAX_NOTIFICATIONS = int(os.getenv("MAX_NOTIFICATIONS"))

class LikeService:
    def __init__(self, db: Session, redis_client: Redis):
        self.db = db
        self.redis = redis_client
        self.repo = LikeRepository(db)

    async def like(self, user_id: int, tweet_id: int):
        # ensure tweet exists
        tweet = self.db.query(Tweet).filter_by(id=tweet_id).first()
        if not tweet:
            raise ValueError("Tweet not found")
        self.repo.add_like(user_id, tweet_id)
        payload = {"type": "tweet_liked", "tweet_id": tweet_id, "user_id": user_id, "author_id": tweet.user_id}
        try:
            # publish realtime to tweet author channel
            self.redis.publish(f"notifications:{tweet.user_id}", json.dumps(payload))
            await self.redis_client.rpush(f"notifications_list:{tweet.user_id}", json.dumps(payload))
            await self.redis_client.ltrim(f"notifications_list:{tweet.user_id}", -MAX_NOTIFICATIONS, -1)
        except Exception:
            pass
       
    def unlike(self, user_id: int, tweet_id: int):
        self.repo.remove_like(user_id, tweet_id)
        count = self.repo.count_likes(tweet_id)
        return {"likes_count": count}