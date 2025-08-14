from backend.src.Models.tweets import MediaAttachment
from sqlalchemy.orm import Session

def attach_media(db: Session, media_id: int, target_type: str, target_id: int) -> MediaAttachment:
    attachment = MediaAttachment(
        media_id=media_id,
        target_type=target_type,
        target_id=target_id
    )
    db.add(attachment)
    return attachment