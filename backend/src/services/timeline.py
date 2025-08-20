from redis import Redis
from sqlalchemy.orm import Session
class TimelineService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis

    def cache_key(self,user_id: int, limit: int, offset: int) -> str:
     return f"timeline:page:{user_id}:{limit}:{offset}"