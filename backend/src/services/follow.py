
from schemas.schemas import  UserMinimal
from Models.tweets import User
from sqlalchemy.orm import Session

from backend.src.repository.follow import add_follow_relation

def follow_service(user: UserMinimal,db:Session , current_user: User):

    add_follow_relation(db, current_user.id, user.id)
    