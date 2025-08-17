from typing import List
from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import or_
from Models.tweets import Media, MediaAttachment, Tweet
from repository.follow import FollowRepository


class TimelineRepository:
    def __init__(self, db: Session):
        self.db = db

    def _serialize_tweet(self, tweet: Tweet) -> Dict:
        return {
            "id": tweet.id,
            "content": getattr(tweet, "content", None),
            "user_id": tweet.user_id,
            "created_at": tweet.created_at.isoformat() if isinstance(tweet.created_at, datetime) else tweet.created_at,
            "media_files": getattr(tweet, "media_files", []),
        }

    def get_user_timeline(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        #  gather following ids
        follow_service = FollowRepository(self.db)
        following_rows = follow_service.get_following(user_id)
        following_ids = [r.id for r in following_rows]
        user_ids = following_ids + [user_id]  # include self

        # fetch tweets with optional media (outerjoin)
        rows = (
            self.db.query(Tweet, Media)
            .outerjoin(MediaAttachment, MediaAttachment.target_id == Tweet.id)
            .outerjoin(Media, Media.id == MediaAttachment.media_id)
            .filter(Tweet.id.in_(user_ids), or_(MediaAttachment.target_type == "tweet", MediaAttachment.target_type == None))
            .order_by(Tweet.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        # 3) aggregate media per tweet (joins duplicate tweet rows)
        tweets_map: Dict[int, Tweet] = {}
        ordered_ids: List[int] = []
        for tweet, media in rows:
            if tweet.id not in tweets_map:
                tweet.media_files = []
                tweets_map[tweet.id] = tweet
                ordered_ids.append(tweet.id)
            if media:
                tweet.media_files.append(media.file_url)

        # 4) produce serialized list preserving order (newest -> oldest)
        ordered = [self._serialize_tweet(tweets_map[t_id]) for t_id in ordered_ids]
        return ordered
