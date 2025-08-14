from sqlalchemy.orm import Session
from Models.tweets import Comment, commentinput
def get_comments_by_tweet(db: Session, tweet_id: int):
    return db.query(Comment).filter(Comment.tweet_id == tweet_id).all()

def create_comment(db: Session,comment:commentinput, user_id: int):
    comment = Comment(user_id=user_id, tweet_id=comment.tweet_id, content=comment.content)
    db.add(comment)
    return comment