


import json
import time
from typing import List
from fastapi import Query
from fastapi import APIRouter, Depends
from fastapi.params import Depends
from redis import Redis
from sqlalchemy.orm import Session
from Models.tweets import User
from schemas.schemas import TweetMinimal
from repository.timeline import TimelineRepository
from services.timeline import TimelineService
from dependencies.dependencies import get_current_user, get_db, get_redis_sync
# Make sure this import path is correct
CACHE_TTL_SECONDS=60

router= APIRouter(prefix="/api/timeline", tags=["timeline"])
@router.get("/", response_model=List[TweetMinimal])
def get_user_timeline(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_sync),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)  # Assuming you have a dependency to get the current user
):
    timeline_repo = TimelineRepository(db)
    time_line_service=TimelineService(db,redis)
    key = time_line_service.cache_key(current_user.id, limit, offset)
    raw = redis.get(key)
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            # fall through to recompute on corrupted cache
            pass

    timeline = timeline_repo.get_user_timeline(user_id=current_user.id, limit=limit, offset=offset)

    # timeline is list[dict] suitable for JSON serialization / TimelineResponse
    redis.set(key, json.dumps(timeline), ex=CACHE_TTL_SECONDS)
    return timeline
