import stat
from fastapi import HTTPException,status
from schemas.schemas import commentinput
from repository.comments import create_comment, get_comments_by_tweet

from sqlalchemy.orm import Session
def list_comments(db: Session, tweet_id: int):
    comments = get_comments_by_tweet(db, tweet_id)
    # You can add extra logic here if needed
    return comments
def add_comment(db, comment: commentinput, user_id: int):
    try:
      create_comment(db,comment , user_id)
      db.commit()
      db.refresh(comment)
      return HTTPException(status_code=status.HTTP_201_CREATED)
    except:
       raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="couldnt create ")
    