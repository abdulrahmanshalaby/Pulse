# main.py
import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from utils.utils import _get_current_user_from_token
from dependencies.dependencies import  get_db , get_redis_async
from database.database import create_tables
from routes.comments import router as commentsrouter
from routes.timeline import router as timelinerouter
from routes.tweets import router as tweetsrouter
from routes.user import router as usersrouter
from routes.auth import router as authrouter
from routes.likes import router as likesrouter
import asyncio
from routes.follows import router as followsrouter
from routes.media import router as media_router
from redis import Redis
CACHE_TTL_SECONDS = 60



app = FastAPI()
load_dotenv() 
MAX_NOTIFICATIONS = int(os.getenv("MAX_NOTIFICATIONS"))
app.include_router(authrouter)
app.include_router(usersrouter)
app.include_router(tweetsrouter)
app.include_router(commentsrouter)
app.include_router(followsrouter)
app.include_router(timelinerouter)
app.include_router(media_router)
app.include_router(likesrouter)
create_tables()




@app.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket,db:Session=Depends(get_db), redis_client: Redis = Depends(get_redis_async)):
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=1008)
        return
    token = auth_header.split(" ")[1]
    try:
        user = _get_current_user_from_token(token, db)
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"notifications:{user.id}"
    await pubsub.subscribe(channel)

    # 1) Fetch missed notifications from Redis list
    notification_list_key = f"notifications_list:{user.id}"
    missed = await redis_client.lrange(notification_list_key, 0, -1)
    for notif in missed:
        await websocket.send_text(notif.decode() if isinstance(notif, bytes) else notif)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                data = message["data"]
                if not isinstance(data, str):
                    data = json.dumps(data)
                # Send live notification
                await websocket.send_text(data)

                # Append to Redis list for later reconnects
                await redis_client.rpush(notification_list_key, data)
                # Trim list to MAX_NOTIFICATIONS
                await redis_client.ltrim(notification_list_key, -MAX_NOTIFICATIONS, -1)

            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()