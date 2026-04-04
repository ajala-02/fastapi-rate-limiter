from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import secrets
import random
from db.database import get_db
from db import models
from core.config import settings
from core.rate_limit import get_limiter
from datetime import datetime, timedelta

router = APIRouter()

# ── Public Data ──────────────────────────────────────────
JOKES = [
    {"joke": "Why do programmers prefer dark mode?", "punchline": "Because light attracts bugs!"},
    {"joke": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem."},
    {"joke": "Why do Java developers wear glasses?", "punchline": "Because they don't C#!"},
    {"joke": "A SQL query walks into a bar...", "punchline": "...walks up to two tables and asks: 'Can I join you?'"},
    {"joke": "Why was the JavaScript developer sad?", "punchline": "Because he didn't Node how to Express himself."},
    {"joke": "What's a computer's favorite snack?", "punchline": "Microchips!"},
    {"joke": "Why did the developer go broke?", "punchline": "Because he used up all his cache."},
    {"joke": "What do you call a programmer from Finland?", "punchline": "Nerdic."},
]

QUOTES = [
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"quote": "In order to be irreplaceable, one must always be different.", "author": "Coco Chanel"},
    {"quote": "Java is to JavaScript what car is to Carpet.", "author": "Chris Heilmann"},
    {"quote": "Knowledge is power.", "author": "Francis Bacon"},
    {"quote": "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code.", "author": "Dan Salomon"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
]

FACTS = [
    {"fact": "The first computer bug was an actual bug — a moth found in a Harvard Mark II computer in 1947."},
    {"fact": "The average smartphone today has more computing power than NASA used to send men to the moon."},
    {"fact": "The first 1GB hard disk drive was announced in 1980 and weighed 550 pounds."},
    {"fact": "Python was named after Monty Python, not the snake."},
    {"fact": "The word 'robot' comes from the Czech word 'robota', meaning forced labor."},
    {"fact": "About 90% of the world's currency exists only on computers, not as physical cash."},
    {"fact": "The first computer virus was created in 1983 and was called the 'Elk Cloner'."},
    {"fact": "There are over 700 programming languages in existence today."},
]

# ── Public rate-limited endpoints ────────────────────────
PUBLIC_LIMIT = 10  # requests per minute per IP

def get_client_ip(request: Request):
    return request.client.host

def public_rate_limit(request: Request):
    ip = get_client_ip(request)
    limiter = get_limiter("token", f"public_{ip}")
    if not limiter.consume(1):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Max 10 requests/minute per IP."
        )

@router.get("/joke", tags=["Public API"])
def get_joke(request: Request):
    public_rate_limit(request)
    return random.choice(JOKES)

@router.get("/quote", tags=["Public API"])
def get_quote(request: Request):
    public_rate_limit(request)
    return random.choice(QUOTES)

@router.get("/fact", tags=["Public API"])
def get_fact(request: Request):
    public_rate_limit(request)
    return random.choice(FACTS)

@router.get("/health", tags=["Public API"])
def health_check():
    return {"status": "ok", "message": "Rate limiter is live!"}

# ── Key management ───────────────────────────────────────
class KeyCreate(BaseModel):
    owner: str

@router.post("/generate-key", tags=["Keys"])
def generate_api_key(key_data: KeyCreate, db: Session = Depends(get_db)):
    new_key = f"ak_{secrets.token_urlsafe(32)}"
    db_key = models.ApiKey(
        key=new_key,
        owner=key_data.owner,
        bucket_capacity=settings.DEFAULT_BUCKET_CAPACITY,
        refill_rate=settings.DEFAULT_REFILL_RATE
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return {
        "message": "API key generated successfully",
        "owner": db_key.owner,
        "api_key": db_key.key,
        "capacity": db_key.bucket_capacity,
        "refill_rate": db_key.refill_rate
    }

def verify_and_limit(request: Request, api_key: str = Query(...), algo: str = Query("token"), db: Session = Depends(get_db)):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.key == api_key).first()
    if not db_key:
        log = models.RequestLog(endpoint=request.url.path, status_code=401, allowed=False)
        db.add(log)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid API Key")

    limiter = get_limiter(algo, api_key)

    if limiter.consume(1):
        log = models.RequestLog(key_id=db_key.id, endpoint=request.url.path, status_code=200, allowed=True)
        db.add(log)
        db.commit()
        return db_key
    else:
        log = models.RequestLog(key_id=db_key.id, endpoint=request.url.path, status_code=429, allowed=False)
        db.add(log)
        db.commit()
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

@router.get("/data", tags=["Protected endpoints"])
def get_protected_data(key_info: models.ApiKey = Depends(verify_and_limit)):
    return {
        "message": f"Hello {key_info.owner}, your request was allowed!",
        "data": [1, 2, 3, 4, 5]
    }

@router.get("/usage", tags=["Analytics"])
def get_usage(api_key: str = Query(...), algo: str = Query("token"), db: Session = Depends(get_db)):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.key == api_key).first()
    if not db_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    limiter = get_limiter(algo, api_key)
    remaining = limiter.get_tokens()

    allowed_count = db.query(func.count(models.RequestLog.id)).filter(
        models.RequestLog.key_id == db_key.id, models.RequestLog.allowed == True
    ).scalar()

    blocked_count = db.query(func.count(models.RequestLog.id)).filter(
        models.RequestLog.key_id == db_key.id, models.RequestLog.allowed == False
    ).scalar()

    return {
        "owner": db_key.owner,
        "tokens_remaining": remaining,
        "total_allowed": allowed_count,
        "total_blocked": blocked_count
    }

@router.get("/analytics", tags=["Analytics"])
def get_analytics(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    total_keys = db.query(func.count(models.ApiKey.id)).scalar()
    recent_logs = db.query(models.RequestLog).order_by(models.RequestLog.timestamp.desc()).limit(10).all()

    allowed_recent = db.query(func.count(models.RequestLog.id)).filter(
        models.RequestLog.timestamp >= one_hour_ago, models.RequestLog.allowed == True
    ).scalar()
    blocked_recent = db.query(func.count(models.RequestLog.id)).filter(
        models.RequestLog.timestamp >= one_hour_ago, models.RequestLog.allowed == False
    ).scalar()

    log_data = []
    for log in recent_logs:
        log_data.append({
            "timestamp": log.timestamp.strftime("%H:%M:%S"),
            "status_code": log.status_code,
            "allowed": log.allowed
        })

    return {
        "total_keys": total_keys,
        "allowed_last_hour": allowed_recent,
        "blocked_last_hour": blocked_recent,
        "recent_logs": log_data
    }