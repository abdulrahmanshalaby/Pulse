from backend.src.Models.tweets import Media
from sqlalchemy.orm import Session

def add_media(db: Session, media_urls: list):
    media_objects = [
        Media(file_url=url, file_type=url.split('.')[-1])
        for url in media_urls
    ]
    db.add_all(media_objects)
    return media_objects
