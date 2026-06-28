import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from .redis_client import get_redis
from .schemas import NotificationCreate, NotificationResponse, NotificationType

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Redis me data kaise store hoga:
# Key:   "notification:{notification_id}"      → ek notification ka data
# Key:   "user_notifications:{user_id}"        → us user ke saare notification IDs (list)


@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(data: NotificationCreate):
    """
    Order Service ya koi bhi service ye endpoint call karega
    jab user ko notify karna ho.
    """
    r = get_redis()

    notification_id = str(uuid.uuid4())
    created_at      = datetime.now(timezone.utc).isoformat()

    notification = {
        "id":         notification_id,
        "user_id":    data.user_id,
        "type":       data.type.value,
        "message":    data.message,
        "order_id":   data.order_id,
        "is_read":    False,
        "created_at": created_at,
    }

    # Redis me store karo
    # 1. Notification ka data (24 hour expiry)
    r.setex(
        f"notification:{notification_id}",
        86400,                          # 24 hours in seconds
        json.dumps(notification),
    )

    # 2. User ki notification list me ID add karo (latest pehle)
    r.lpush(f"user_notifications:{data.user_id}", notification_id)

    # List max 50 notifications rakhega per user
    r.ltrim(f"user_notifications:{data.user_id}", 0, 49)

    return notification


@router.get("/user/{user_id}", response_model=list[NotificationResponse])
def get_user_notifications(user_id: int, limit: int = 20):
    """User ki saari notifications fetch karo"""
    r = get_redis()

    # User ke notification IDs lo (latest pehle)
    ids = r.lrange(f"user_notifications:{user_id}", 0, limit - 1)

    if not ids:
        return []

    notifications = []
    for nid in ids:
        raw = r.get(f"notification:{nid}")
        if raw:                          # expired nahi hua
            n = json.loads(raw)
            notifications.append(n)

    return notifications


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: str):
    """Notification ko read mark karo"""
    r = get_redis()

    raw = r.get(f"notification:{notification_id}")
    if not raw:
        raise HTTPException(404, "Notification not found or expired")

    notification          = json.loads(raw)
    notification["is_read"] = True

    # Update karo — same TTL nahi milega, isliye getex se TTL lo pehle
    ttl = r.ttl(f"notification:{notification_id}")
    if ttl > 0:
        r.setex(f"notification:{notification_id}", ttl, json.dumps(notification))
    else:
        r.set(f"notification:{notification_id}", json.dumps(notification))

    return notification


@router.delete("/user/{user_id}", status_code=204)
def clear_user_notifications(user_id: int):
    """User ki saari notifications clear karo"""
    r = get_redis()

    ids = r.lrange(f"user_notifications:{user_id}", 0, -1)
    for nid in ids:
        r.delete(f"notification:{nid}")
    r.delete(f"user_notifications:{user_id}")


@router.get("/user/{user_id}/unread-count")
def unread_count(user_id: int):
    """Unread notifications ka count"""
    r = get_redis()

    ids = r.lrange(f"user_notifications:{user_id}", 0, -1)
    count = 0
    for nid in ids:
        raw = r.get(f"notification:{nid}")
        if raw:
            n = json.loads(raw)
            if not n["is_read"]:
                count += 1

    return {"user_id": user_id, "unread_count": count}
