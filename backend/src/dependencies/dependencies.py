import json
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from kafka import KafkaProducer
from redis import Redis
from sqlalchemy.orm import Session
import redis.asyncio as aioredis 
from Models.models import User
from authorization import auth
from database.database import SessionLocal
from dotenv import load_dotenv
load_dotenv

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")
TOPIC_NOTIFICATIONS = os.getenv("TOPIC_NOTIFICATIONS")

_producer: KafkaProducer | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_redis_sync() -> Redis:
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_redis_async() -> aioredis.Redis:
    return aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_kafka_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
        )
    return _producer



def publish_notification(payload: dict, topic: str = TOPIC_NOTIFICATIONS):
    producer = get_kafka_producer()
    producer.send(topic, value=payload)


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:  # no token = guest
        return None

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user
