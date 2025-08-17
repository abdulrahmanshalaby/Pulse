from Models.tweets import User
from sqlalchemy.orm import Session

from authorization.auth import hash_password
from schemas.schemas import userinput
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int):
       return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str):
      return self.db.query(User).filter(User.username == username).first()

    def create_user(self,data:userinput ):
      pwd=hash_password(data.password)
      user = User(username=data.username,hashed_password=pwd)
      self.db.add(user)
   
      return user