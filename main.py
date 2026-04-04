from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from db.database import engine, Base
from api import routes
import os

# Create all models (tables)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Production API Rate Limiter",
    description="A full-stack API rate limiter using FastAPI, SQLite, and an in-memory Token Bucket.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Important logic: we mount /static but we also want the root to serve static/index.html easily.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/static/index.html")
