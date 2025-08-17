from fastapi import HTTPException,status
from schemas.schemas import commentinput
from repository.comments import CommentRepository

from sqlalchemy.orm import Session
class CommentService:
    def __init__(self, db: Session):
        self.db = db
    def list_comments(self, tweet_id: int):
      comment_repo = CommentRepository(self.db)
      try:
       comments = comment_repo.get_comments_by_tweet(tweet_id)
    # You can add extra logic here if needed
       return comments
      except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    def add_comment(self, comment: commentinput, user_id: int):
      comment_repo = CommentRepository(self.db)
      try:
       comment_repo.create_comment(comment , user_id)
       self.db.commit()
       self.db.refresh(comment)
       return HTTPException(status_code=status.HTTP_201_CREATED)
      except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="couldnt create ")
    