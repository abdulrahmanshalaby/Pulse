from  datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class commentinput( BaseModel):
    content:str
    tweet_id:int

class tweetinput(BaseModel):
    content:str
    media_urls: Optional[List[str]] = None

class userinput(BaseModel):

    username:str
    password:str
    avatar_url:Optional[str]=None

class UserMinimal(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
class useroutput(UserMinimal):
    gender:str
    age:str
    bio:str
    followers_count: int
    following_count: int

    class Config:
        orm_mode = True
class CommentMinimal(BaseModel):
    id: int
    content: str
    user: UserMinimal

    class Config:
        orm_mode = True

class TweetMinimal(BaseModel):
    id: int
    content: str
    created_at: datetime
    likes_count: int 
    media_urls: List[str]=[]
    liked_by_me: bool = False


    class Config:
        orm_mode = True

class TweetWithComments(TweetMinimal):
    comments: List[CommentMinimal] = []
   
class UserWithTweets(useroutput):
    tweets: List[TweetMinimal] = []

    class Config:
        orm_mode = True
class PresignRequest(BaseModel):
    file_name: str
    file_type: str

class PresignResponse(BaseModel):
    upload_url: str
    file_url: str

class FinalizeUploadRequest(BaseModel):
    file_url: str
    file_type: str

class FinalizeUploadResponse(BaseModel):
    media_id: int

class CreateTweetRequest(BaseModel):
    text: Optional[str]
    media_ids: Optional[List[int]] = []
    
class TimelineResponse(BaseModel):
    tweet: dict
    added_at: Optional[datetime] = None

    class Config:
        orm_mode = True

useroutput.model_rebuild()