
from Models.tweets import Follow, User
from sqlalchemy.orm import Session

def add_follow_relation(db: Session, follower_id: int, following_id: int):
    # Insert follow relation
    db.execute(
        Follow.insert().values(follower_id=follower_id, following_id=following_id)
    )
    # Update counts
    db.query(User).filter(User.id == follower_id).update({
        User.following_count: User.following_count + 1
    })
    db.query(User).filter(User.id == following_id).update({
        User.followers_count: User.followers_count + 1
    })
