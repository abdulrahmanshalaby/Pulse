from sqlalchemy.orm import Session
from Models.tweets import Comment
from schemas.schemas import commentinput
class CommentRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_comments_by_tweet(self, tweet_id: int):
     return self.db.query(Comment).filter(Comment.tweet_id == tweet_id).all()

    def create_comment(self,comment:commentinput, user_id: int):
      comment = Comment(user_id=user_id, tweet_id=comment.tweet_id, content=comment.content)
      self.db.add(comment)
      return comment