# Notification Service — ShopFlow

> User notifications stored in Redis. No SQL DB — Redis hi storage hai.

## Overview

Ye service **PostgreSQL use nahi karti** — sirf **Redis**. Notifications temporary hoti hain (24hr expiry), isliye Redis perfect fit hai. Koi bhi service (Order Service, User Service) isko call karke user ko notify kar sakti hai.

**Tech stack:** FastAPI · Redis · Docker

---

## Redis me Data Kaise Store Hota Hai

```
notification:{uuid}           → ek notification ka JSON (24hr TTL)
user_notifications:{user_id}  → us user ke notification IDs ki list
```

Example:
```
notification:abc-123  →  {"id":"abc-123","user_id":1,"type":"order_confirmed",...}
user_notifications:1  →  ["abc-123", "xyz-456", "def-789"]  ← latest pehle
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notifications/` | Notification banao |
| GET | `/api/notifications/user/{user_id}` | User ki notifications |
| GET | `/api/notifications/user/{user_id}/unread-count` | Unread count |
| PATCH | `/api/notifications/{id}/read` | Read mark karo |
| DELETE | `/api/notifications/user/{user_id}` | Sab clear karo |
| GET | `/health` | Health check (Redis ping bhi karta hai) |

---

## Notification Types

```
order_placed     → Order place hua
order_confirmed  → Order confirm hua (stock reduce hua)
order_cancelled  → Order cancel hua
welcome          → New user register hua
```

---

## Request / Response Examples

### Notification banao
```bash
curl -X POST http://localhost:8004/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "type": "order_confirmed",
    "message": "Your order #1 has been confirmed! Total: Rs. 5999.98",
    "order_id": 1
  }'
```

### User ki notifications fetch karo
```bash
curl http://localhost:8004/api/notifications/user/1
```

### Unread count
```bash
curl http://localhost:8004/api/notifications/user/1/unread-count
# {"user_id": 1, "unread_count": 3}
```

### Read mark karo
```bash
curl -X PATCH http://localhost:8004/api/notifications/{notification_id}/read
```

---

## Project Structure

```
notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + health (Redis ping)
│   ├── redis_client.py  # Redis connection pool
│   ├── schemas.py       # Pydantic schemas + NotificationType enum
│   └── routes.py        # All route handlers
├── Dockerfile           # Multi-stage (gcc nahi chahiye — redis-py pure Python)
├── docker-compose.yml   # notification-service + Redis
├── Jenkinsfile
├── requirements.txt
└── .env.example
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis connection URL |

---

## Running Locally

```bash
cd notification-service
docker compose up -d --build

# Health check — Redis bhi check karta hai
curl http://localhost:8004/health
# {"status":"healthy","service":"notification-service","redis":"connected"}

# Welcome notification banao
curl -X POST http://localhost:8004/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"type":"welcome","message":"Welcome to ShopFlow!"}'

# Fetch karo
curl http://localhost:8004/api/notifications/user/1
```

---

## Redis directly dekho

```bash
# Redis container ke andar jao
docker exec -it shopflow-redis redis-cli

# Saari keys dekho
KEYS *

# Ek notification dekho
GET notification:{id}

# User ki notification list dekho
LRANGE user_notifications:1 0 -1

# Exit
exit
```

---

## Port Reference

| Container | Host Port |
|-----------|-----------|
| notification-service | 8004 |
| shopflow-redis | 6379 |

---

## Design Decisions

- **Redis only, no PostgreSQL** — Notifications temporary hoti hain. 24hr baad expire — Redis ka TTL feature perfect hai.
- **Connection Pool** — `redis.ConnectionPool` use kiya — har request pe naya connection nahi banta, pool se leta hai. Performance better.
- **lpush + ltrim** — Latest notifications pehle aati hain. Max 50 per user — memory waste nahi hoti.
- **Health check Redis ping karta hai** — Sirf service up hai ye nahi check — Redis connection bhi verify hoti hai.
