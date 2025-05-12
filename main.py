from functools import lru_cache
from fastapi import FastAPI, Body, Depends
from typing import Any, Annotated
from config import Settings
from utils.dbconn import create_session
from sqlmodel import select
from models import User
from routers import user, auth, post, friend, media, comment
from routers.auth import oauth2_scheme
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(friend.router)
app.include_router(media.router)
app.include_router(comment.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=["*"],
    allow_headers=["*"]
)

@lru_cache
def get_settings():
    return Settings()


@app.get("/test_auth")
def test_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/")
def health_check():
    return {"message": "Healthy"}

@app.get("/print/{x}")
def test(x):
    return {"message": x}

@app.post("/print")
def test_post(req: Any = Body(None)):
    return {"message": req["x"]}