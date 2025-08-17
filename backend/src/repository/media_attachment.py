from Models.tweets import Media, MediaAttachment
from sqlalchemy.orm import Session
class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_media_by_id(self, media_id: int):
        media = self.db.query(MediaAttachment).filter(MediaAttachment.id == media_id).first()
        if not media:
            raise Exception("Media not found")
        return media

    def create_media(self, file_url: str):
        media = MediaAttachment(file_url=file_url)
        self.db.add(media)
        return media
    def attach_media(self, media_id: int, target_type: str, target_id: int) -> MediaAttachment:
      attachment = MediaAttachment(
        media_id=media_id,
        target_type=target_type,
        target_id=target_id
    )
      self.db.add(attachment)
      return attachment
    def add_media(self, media_urls: list):
     media_objects = [
        Media(file_url=url, file_type=url.split('.')[-1])
        for url in media_urls
    ]
     self.db.add_all(media_objects)
     return media_objects
