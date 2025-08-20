
from httpx import delete
from sqlalchemy import insert, text,select
from sqlalchemy.orm import Session
from Models.models import likes_table

class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_like(self, user_id: int, tweet_id: int):
        # check exists
        q = select(likes_table).where(likes_table.c.user_id == user_id, likes_table.c.tweet_id == tweet_id)
        if self.db.execute(q).first():
            raise ValueError("Already liked")
        stmt = insert(likes_table).values(user_id=user_id, tweet_id=tweet_id)
        self.db.execute(stmt)
        self.db.execute(
        text("UPDATE tweets SET likes_count = likes_count + 1 WHERE id = :tweet_id"),
        {"tweet_id": tweet_id}
    )
        self.db.commit()

    def remove_like(self, user_id: int, tweet_id: int):
        stmt = delete(likes_table).where(likes_table.c.user_id == user_id, likes_table.c.tweet_id == tweet_id)
        res = self.db.execute(stmt)
        if res.rowcount:  # only decrement if something was deleted
         self.db.execute(
            text("UPDATE tweets SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = :tweet_id"),
            {"tweet_id": tweet_id}
        )
        self.db.commit()
    

   