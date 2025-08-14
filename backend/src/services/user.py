from pydantic import create_model
from backend.src.repository.media import add_media
from backend.src.repository.media_attachment import attach_media
import repository.user as user_repo
from sqlalchemy.orm import Session 
def get_user_profile(db:Session, user_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise Exception("User not found")
    return user

def register_user(db: Session, data: dict):
    username = data.get("username")
    password = data.get("password")
    avatar_url = data.get("avatar_url")  # optional, from pre-signed upload

    if not username or not password:
        raise ValueError("Username and password are required")

    # 1️⃣ Create user
    user = user_repo.create_user(db, username=username, password=password)

    # 2️⃣ If avatar provided, create media and attach
    # Attach media if any
    target_type="user"
    if avatar_url:
       medias=add_media(db, avatar_url)
    for media in medias:
        attach_media(db, media.id, target_type, target_id=user.id)
    db.commit()
    return {"user_id": user.id, "username": user.username, "avatar_url": avatar_url}
