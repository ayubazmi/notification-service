from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


class NotificationType(str, enum.Enum):
    ORDER_PLACED    = "order_placed"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_CANCELLED = "order_cancelled"
    WELCOME         = "welcome"


class NotificationCreate(BaseModel):
    user_id:  int
    type:     NotificationType
    message:  str
    order_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id:         str
    user_id:    int
    type:       NotificationType
    message:    str
    order_id:   Optional[int]
    is_read:    bool
    created_at: str
