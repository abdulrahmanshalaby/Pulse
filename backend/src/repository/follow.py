
import traceback

from fastapi import HTTPException
from Models.tweets import Follow, User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class FollowRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_followers(self, user_id: int):
        return self.db.query(User).join(Follow, Follow.follower_id == User.id).filter(Follow.following_id == user_id).all()

    def get_following(self, user_id: int):
        return self.db.query(User).join(Follow, Follow.following_id == User.id).filter(Follow.follower_id == user_id).all()
    def add_follow_relation(self, follower_id: int, following_id: int):
    
        # 1️⃣ Insert follow relation
     new_follow = Follow(
    follower_id=follower_id,
    following_id=following_id
) 

     self.db.add(new_follow)
     self.db.commit()
     return new_follow

