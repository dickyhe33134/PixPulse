from functools import lru_cache
from fastapi import FastAPI, Body, Depends
from typing import Any, Annotated
from config import Settings
from utils.dbconn import create_session
from sqlmodel import select
from models import User
from routers import user, auth, post, friend
from routers.auth import oauth2_scheme

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(post.router)
app.include_router(friend.router)



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

@app.get("/insert")
def test_insert():
    session = create_session()

    tmp = User(username="user", email="user@user.com" ,hashed_password="1234")
    session.add(tmp)

    session.commit()
    session.close()
    return {"message": "Successfully added user"}


@app.get("/check")
def test_query():
    session = create_session()

    tmp = User(username="user")
    statement = select(User)
    query_results = session.exec(statement)
    results = [x for x in query_results]

    session.close()
    return {"message": "Successful", "content": results}