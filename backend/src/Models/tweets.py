import datetime
import enum
import string
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Nullable, String, Table, UniqueConstraint, column, false
from database.database import base
from sqlalchemy.orm import relationship


likes_table = Table(
    "likes",
    base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("tweet_id", Integer, ForeignKey("tweets.id"))
)







class Tweet(base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    content=column(string,Nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="tweets")
    likers = relationship("User", secondary=likes_table, back_populates="liked_tweets")



class Retweet(base):
    __tablename__ = "retweets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)       # who reposted
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)     # original tweet
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="retweets")
    tweet = relationship("Tweet")


class Follow(base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ensure the same person can't follow another twice
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="_follower_following_uc"),)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")  

class User(base):
   __tablename__="Users"
   id = Column(Integer, primary_key=True, index=True)
   username = Column(String, unique=True, index=True, nullable=False)
   hashed_password = Column(String, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow)
   gender = Column(String, nullable=True)
   age = Column(Integer, nullable=True)
   bio = Column(String, nullable=True)
   tweets = relationship("Tweet", back_populates="user")
   retweets = relationship("Retweet", back_populates="user")
   liked_tweets = relationship("Tweet", secondary=likes_table, back_populates="likers")
   following = relationship(
        "Follow",
        foreign_keys="[Follow.follower_id]",
        back_populates="follower",
        cascade="all, delete-orphan"
    )

   followers = relationship(
        "Follow",
        foreign_keys="[Follow.following_id]",
        back_populates="following",
        cascade="all, delete-orphan"
    )


class Timeline(base):
    __tablename__ = "timelines"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # subscriber
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Media(base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # e.g., image/png, video/mp4
    created_at = Column(DateTime, default=datetime.utcnow)


class MediaAttachment(base):
    """
    Links a media item to any entity (tweet, DM, user profile pic).
    Uses 'target_type' to know what entity it belongs to.
    """
    __tablename__ = "media_attachments"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False)
    target_type = Column(String, nullable=False)  # 'tweet', 'dm', 'user_avatar'
    target_id = Column(Integer, nullable=False)   # ID of Tweet, DM, or User

    media = relationship("Media")


