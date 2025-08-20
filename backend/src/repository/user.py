from Models.models import User
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
    def search_users(self, query: str, limit: int = 10):
        """
        Search users by username or display name (case-insensitive, partial match).
        Returns a list of dicts with id, username, display_name, and profile_image_url.
        """
        results = (
            self.db.query(User.id, User.username, User.display_name, User.profile_image_url)
            .filter(
                (User.username.ilike(f"%{query}%")) |
                (User.display_name.ilike(f"%{query}%"))
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "id": u.id,
                "username": u.username,
                "display_name": u.display_name,
                "profile_image_url": u.profile_image_url,
            }
            for u in results
        ]