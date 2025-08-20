from pydantic import create_model
from authorization.auth import hash_password
from repository.user import UserRepository
from schemas.schemas import userinput
from repository.media_attachment import MediaRepository
from sqlalchemy.orm import Session 
class UserService:
    def __init__(self, db: Session):
        self.db = db
    def get_user_profile(self, user_id: int):
        user_repo = UserRepository(self.db)
        user = user_repo.get_user_by_id(user_id)
        if not user:
         raise Exception("User not found")
        return user

    def register_user(self, data: userinput):
      user_repo = UserRepository(self.db)
      media_repo = MediaRepository(self.db)

    # Validate input
      if not data.username or not data.password:
        raise ValueError("Username and password are required")

    # Check if username already exists
      existing_user = user_repo.get_user_by_username(data.username)
      if existing_user:
        raise ValueError("Username already exists")

    # Handle avatar_url
      data.avatar_url = data.avatar_url or None
 # optional, from pre-signed upload

      if not data.username or not data.password:
        raise ValueError("Username and password are required")
    # 1️⃣ Create user
      user = user_repo.create_user(data)
      self.db.commit()
      self.db.refresh(user)

    # 2️⃣ If avatar provided, create media and attach
    # Attach media if any
      target_type="user"
      if data.avatar_url:
       medias=media_repo.add_media(data.avatar_url)
       for media in medias:
         media_repo.attach_media(media.id, target_type, target_id=user.id)
      self.db.commit()
      return user
