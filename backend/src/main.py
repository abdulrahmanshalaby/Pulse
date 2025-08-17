# main.py
import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, selectinload
from Models.tweets import Tweet, Timeline 
from utils.utils import _get_current_user_from_token
from dependencies.dependencies import  get_db ,get_current_user, get_redis_async, get_redis_sync
from database.database import create_tables
from kafka import KafkaProducer
from routes.comments import router as commentsrouter
from routes.timeline import router as timelinerouter
from routes.tweets import router as tweetsrouter
from routes.user import router as usersrouter
from routes.auth import router as authrouter
import asyncio
from routes.follows import router as followsrouter
from routes.media import router as media_router
from redis import Redis
CACHE_TTL_SECONDS = 60



app = FastAPI()
load_dotenv() 
app.include_router(authrouter)
app.include_router(usersrouter)
app.include_router(tweetsrouter)
app.include_router(commentsrouter)
app.include_router(followsrouter)
app.include_router(timelinerouter)
app.include_router(media_router)
create_tables()




# async client for websockets

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
@app.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket,db:Session=Depends(get_db), redis_client: Redis = Depends(get_redis_async)):
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=1008)
        return
    token = auth_header.split(" ")[1]
    try:
        user = _get_current_user_from_token(token,db)  
    except Exception:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"notifications:{user.id}"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                data = message["data"]
                if not isinstance(data, str):
                    data = json.dumps(data)
                await websocket.send_text(data)
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()