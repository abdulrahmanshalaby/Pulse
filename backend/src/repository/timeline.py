from typing import List
from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import or_
from Models.models import Media, MediaAttachment, Tweet,likes_table
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
            "likes_count": tweet.likes_count,
            "media_files": getattr(tweet, "media_files", []),
             "author": {
            "id": tweet.user.id,
            "username": tweet.user.username
        }
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
            .filter(Tweet.user_id.in_(user_ids), or_(MediaAttachment.target_type == "tweet", MediaAttachment.target_type == None))
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
        tweet_ids = list(tweets_map.keys())
        liked_tweet_ids = (
          self.db.query(likes_table.c.tweet_id)
         .filter(likes_table.c.user_id == user_id, likes_table.c.tweet_id.in_(tweet_ids))
         .all()
     )
        liked_tweet_ids = {row[0] for row in liked_tweet_ids}  # convert to set for fast lookup

    # 5) mark liked_by_me on each tweet
        for t_id, tweet in tweets_map.items():
         tweet.liked_by_me = t_id in liked_tweet_ids

    # 6) return ordered list (newest -> oldest)
        ordered = [self._serialize_tweet(tweets_map[t_id]) for t_id in ordered_ids]
        return ordered

     
