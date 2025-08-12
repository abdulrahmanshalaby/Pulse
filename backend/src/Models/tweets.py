import datetime
import string
from typing import List
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





class userinput(BaseModel):

    username:str
    password:str

class useroutput(BaseModel):
    id : int
    username:str
    gender:str
    age:str
    bio:str
    tweets: List["Tweetoutput"] = [] 
    followers_count: int
    following_count: int

    class Config:
        orm_mode = True


class CommentRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: useroutput  # commenter info

    class Config:
        orm_mode = True
class LikeRead(BaseModel):
    user: useroutput  # user who liked

    class Config:
        orm_mode = True

class Tweetoutput(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: useroutput
    class Config:
        orm_mode = True



class TweetWithComments(Tweetoutput):
    comments: List[CommentRead] = []

class TweetWithLikes(Tweetoutput):
    likers: List[useroutput] = []

class TweetWithLikesAndComments(TweetWithLikes):
    comments: List[CommentRead] = []
class Retweetoutput(BaseModel):
    id: int
    created_at: datetime
    tweet: Tweetoutput  # the original tweet that was reposted

    class Config:
        orm_mode = True


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

useroutput.model_rebuild()
Tweetoutput.model_rebuild()