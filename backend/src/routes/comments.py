from calendar import c
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import CommentMinimal, commentinput
from dependencies.dependencies import get_current_user
from services.comments import CommentService
from dependencies.dependencies import get_db
router=APIRouter(prefix="/api/comments",tags=["comments"])
@router.get("/{tweet_id}", response_model=List[CommentMinimal])
def get_comments(tweet_id: int, db: Session = Depends(get_db)):
    comment_service = CommentService(db)
    # Fetch comments for the given tweet_id
    comments = comment_service.list_comments(tweet_id)
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    return comments

@router.post("/", response_model=CommentMinimal)
def create_comment(comment:commentinput, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    comment_service = CommentService(db)
    # Add a new comment for the current user
    # Ensure the user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not comment.tweet_id or not comment.content:
        raise HTTPException(status_code=400, detail="Tweet ID and content are required")

    # Call the service to add the comment
    return comment_service.add_comment(comment, current_user.id)
        
    return add_comment(db, comment, current_user.id)