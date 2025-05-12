from email.policy import HTTP
from fastapi import APIRouter, Depends, HTTPException, status
from models import LikedBy, Post
from routers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM, auth_exception
from utils.dbconn import create_session
from sqlmodel import select
import jwt

router = APIRouter(prefix="/api/like")

@router.get("/")
def if_liked_post(post_id: int, token: str = Depends(oauth2_scheme)) -> bool:

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return auth_exception
    except:
        return auth_exception

    session = create_session()

    likes = session.exec(select(LikedBy).where(LikedBy.post_id==post_id, LikedBy.userid==userid)).all()

    return len(likes)>0

@router.patch("/")
def toggle_like_post(post_id: int, token: str = Depends(oauth2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return auth_exception
    except:
        return auth_exception

    session = create_session()

    posts = session.exec(select(Post).where(Post.post_id==post_id)).all()
    if len(posts)<1:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Post does not exist")
    
    post = posts[0]
    post.like_count -= 1
    session.add(post)


    likes = session.exec(select(LikedBy).where(LikedBy.post_id==post_id, LikedBy.userid==userid)).all()
    if len(likes)<1:
        session.add(LikedBy(post_id=post_id, userid=userid))
    else:
        session.delete(likes[0])

    session.commit()
    return {"message": "Toggled successfully"}