# main.py
import asyncio
from fastapi import APIRouter, FastAPI, Depends, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, selectinload
from Models.tweets import Tweet, User, Timeline, Hashtag, tweet_hashtag, Base, userinput, useroutput
# from utils import extract_mentions, extract_hashtags
from authorization.auth import create_access_token, hash_password, verify_password
from dependencies.dependencies import get_current_user
from database.database import get_db  # your session factory
import json
import redis
REDIS_URL = "redis://localhost:6379"


redis_client = redis.Redis()  # sync redis; for async use redis.asyncio

app = FastAPI()
router=APIRouter()
app.include_router(router)

# def fanout_to_followers(db: Session, tweet_id: int, author_id: int):
#     # naive: find followers and insert Timeline entries
#     # (You may have a properly indexed follows table; adapt the query)
#     followers = db.execute(
#         "SELECT follower_id FROM follows WHERE following_id=:id",
#         {"id": author_id}
#     ).fetchall()
#     # followers is a list of rows, extract ids:
#     follower_ids = [r[0] for r in followers]
#     timelines = [Timeline(user_id=f, tweet_id=tweet_id) for f in follower_ids]
#     if timelines:
#         db.bulk_save_objects(timelines)
#         db.commit()
#     # publish to redis channels for real-time if you want:
#     payload = json.dumps({"type":"tweet", "tweet_id": tweet_id})
#     for f in follower_ids:
#         redis_client.publish(f"feed:{f}", payload)

# @app.post("/tweets")
# def create_tweet(content: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     # 1. create tweet
#     tweet = Tweet(content=content, user_id=current_user.id)
#     db.add(tweet)
#     db.commit()
#     db.refresh(tweet)

#     # 2. mentions
#     mentions = extract_mentions(content)
#     for username in mentions:
#         mentioned_user = db.query(User).filter_by(username=username).first()
#         if mentioned_user:
#             # create a notification row or mention row - implement as needed
#             db.execute("INSERT INTO mentions (tweet_id, mentioned_user_id) VALUES (:t,:u)", {"t":tweet.id, "u":mentioned_user.id})
#     db.commit()

#     # 3. hashtags: create if not exists and join table
#     hashtags = extract_hashtags(content)
#     for tag in hashtags:
#         ht = db.query(Hashtag).filter_by(tag=tag).first()
#         if not ht:
#             ht = Hashtag(tag=tag)
#             db.add(ht)
#             db.commit()
#             db.refresh(ht)
#         db.execute(tweet_hashtag.insert().values(tweet_id=tweet.id, hashtag_id=ht.id))
#     db.commit()

#     # 4. fanout in background
#     background_tasks.add_task(fanout_to_followers, db, tweet.id, current_user.id)

#     return {"id": tweet.id}


# @app.get("/users/{user_id}/timeline")
def get_timeline(user_id: int, db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    # join Timeline -> Tweet -> User
    q = db.query(Timeline).filter(Timeline.user_id==user_id).order_by(Timeline.created_at.desc()).limit(limit).offset(offset)
    tweet_ids = [row.tweet_id for row in q]
    tweets = db.query(Tweet).filter(Tweet.id.in_(tweet_ids)).options(selectinload(Tweet.user)).all()
    # map and return with your Pydantic TweetRead
    return tweets

# @router.websocket("/ws/feed/{user_id}")
# async def feed_ws(websocket: WebSocket, user_id: int):
#     await websocket.accept()

#     # Connect to Redis (async)
#     redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
#     pubsub = redis.pubsub()
#     await pubsub.subscribe(f"feed:{user_id}")

#     try:
#         while True:
#             message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
#             if message:
#                 # Send the tweet data to the client
#                 await websocket.send_text(message["data"])
#             await asyncio.sleep(0.1)  # prevent busy loop
#     except WebSocketDisconnect:
#         print(f"User {user_id} disconnected from WS")
#     finally:
#         await pubsub.unsubscribe(f"feed:{user_id}")
#         await pubsub.close()
#         await redis.close()
@app.post("/register", response_model=useroutput)
def register(user_data: userinput, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=useroutput)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user