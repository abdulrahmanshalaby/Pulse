from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.schemas import CommentMinimal, commentinput
from dependencies.dependencies import get_current_user
from services.comments import add_comment, list_comments
from dependencies.dependencies import get_db
router=APIRouter(prefix="/api/comments",tags=["comments"])
@router.get("/{tweet_id}", response_model=List[CommentMinimal])
def get_comments(tweet_id: int, db: Session = Depends(get_db)):
    return list_comments(db, tweet_id)

@router.post("/", response_model=CommentMinimal)
def create_comment(comment:commentinput, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return add_comment(db, comment, current_user.id)