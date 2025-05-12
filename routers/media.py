from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from models import Media, HasMedia
from sqlmodel import select, col
from utils.dbconn import create_session
from routers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
import jwt

router = APIRouter(prefix="/api/media")

# Gets image of a certain media_id
@router.get("/")
def get_media(media_id: int):
    session = create_session()

    media = session.exec(select(Media).where(Media.media_id==media_id)).all()
    if len(media)<1:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "No such media")
    
    media = media[0]
    return Response(media.image_data, media_type="image/png")


# Upload media to database
@router.put("/")
def add_media(media_bytes: bytes = Body(..., embed=True), token: str = Depends(oauth2_scheme)) -> Media:
    session = create_session()

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")
    except:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")

    media = Media(image_data=media_bytes)
    session.add(media)
    session.commit()
    session.refresh(media)

    return media

# Deletes Media
@router.delete("/")
def delete_media(media_id: int = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")
    except:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")


    # Get media that matches media_id and userid
    result = session.exec(select(Media).where(Media.media_id==media_id, Media.userid==userid)).all()
    if (len(result)<1):
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Media by this user does not exist.")

    # Get related posts
    posts = session.exec(select(HasMedia).where(HasMedia.media_id==media_id)).all()
    if (len(posts)<1):
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Posts cannot have no media.")
    
    # Extract the related post and the media
    post = posts[0]
    media = result[0]

    # Delete the link between the post and media and the media itself
    session.delete(post)
    session.delete(media)
    session.commit()

    session.close()
    return {"message": "Successfully deleted media"}


@router.patch("/")
def update_media(media: Media = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")
    except:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Can't authenticate user.")
    
    if userid!=media.userid:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "User id of post does not match token.")

    # Get media that matches media_id and userid
    result = session.exec(select(Media).where(Media.media_id==media.media_id, Media.userid==userid)).all()

    if (len(result)<1):
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Media not related to user or media does not exist.")
    
    new_media = result[0]
    new_media.image_data = media.image_data

    session.add(new_media)
    session.commit()

    session.close()
    return {"message": "Update successful"}
