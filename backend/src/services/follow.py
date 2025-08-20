
from calendar import c
import json
import os
from fastapi import HTTPException
from datetime import datetime
from redis import Redis
from dependencies.dependencies import publish_notification
from repository.follow import FollowRepository
from schemas.schemas import  UserMinimal
from Models.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
MAX_NOTIFICATIONS = int(os.getenv("MAX_NOTIFICATIONS"))

class FollowService:
    def __init__(self, db: Session,redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def get_followers(self, user_id: int):
        follow_Repository = FollowRepository(self.db)
        followers = follow_Repository.get_followers(user_id)
        if not followers:   
            raise HTTPException(status_code=404, detail="No followers found")   
        return followers

    def get_following(self, user_id: int):
        follow_repository= FollowRepository(self.db)
        following = follow_repository.get_following(user_id)
        return following  
    def follow_service(self,user: UserMinimal , current_user: User):
      follow_repository = FollowRepository(self.db)
      if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")

        # create DB relation and commit; handle duplicate gracefully
      try:
        follow=follow_repository.add_follow_relation(current_user.id, user.id)
        self.db.commit()
      except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Already following this user")
      except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=422, detail=e)

        # update quick Redis sets for follower lists (kept for quick checks)
      try:
            self.redis_client.sadd(f"followers:{user.id}", current_user.id)
            self.redis_client.sadd(f"following:{current_user.id}", user.id)
      except Exception:
            # don't fail the request if Redis is down
            pass

        # publish a realtime notification to the followed user (for websockets)
      payload = {
            "type": "follow",
            "follower_id": current_user.id,
            "following_id": user.id,
            "created_at": follow.created_at.isoformat()
        }
      try:
            self.redis_client.publish(f"notifications:{user.id}", json.dumps(payload))
            self.redis_client.rpush(f"notifications_list:{user.id}", json.dumps(payload))
            self.redis_client.ltrim(f"notifications_list:{user.id}", -MAX_NOTIFICATIONS, -1)
      except Exception:
            pass

        # publish durable event to Kafka for background consumers (cache invalidation / fan-out)
      try:
            publish_notification(payload)
      except Exception:
            pass
      return follow