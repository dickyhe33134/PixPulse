from sqlmodel import select, col, or_
from fastapi import APIRouter, Body, Query, HTTPException, Depends, status
from models import Post, HasFriend, Media, HasMedia
from utils.dbconn import create_session
from routers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from routers.friend import get_all_social_distance
import jwt

router = APIRouter(prefix="/api/post")

auth_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not authorize user")

# Get all posts
@router.get("/")
def get_post() -> list[Post]:
    session = create_session()

    statement = select(Post)
    result = list(session.exec(statement))
    result.sort(key=lambda x: x.created_at, reverse=True)

    session.close()
    return result

# Get all the posts that is posted by current user
@router.get("/self")
def get_self_posts(token: str = Depends(oauth2_scheme)) -> list[Post]:
    session = create_session()

    # Get userid from token
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = payload["sub"]
        if userid is None:
            return auth_exception
    except:
        return auth_exception

    # Get all related posts
    result = session.exec(select(Post).where(Post.uploader==userid)).all()
    result = list(result)
    result.sort(key=lambda x: x.created_at, reverse=True)

    session.close()
    return result

# Query for posts
@router.post("/")
def query_post(
    uploader: int = Body(..., embed=True),
) -> list[Post]:
    session = create_session()

    statement = select(Post).where(Post.uploader==uploader)
    result = list(session.exec(statement))

    result.sort(key=lambda x: x.created_at, reverse=True)
    session.close()
    return result

# Get media ids of posts
@router.get("/media")
def get_post_media(
    post_id: int | None,
) -> list[int]:
    session = create_session()

    links = session.exec(select(HasMedia).where(HasMedia.post_id==post_id)).all()
    media_ids = [link.media_id for link in links]

    session.close()
    return media_ids


# Add posts
@router.put("/")
def add_post(post: Post = Body(..., embed=True), media_id_list: list[int] = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = int(payload["sub"])
        if userid is None:
            return auth_exception
    except Exception as e:
        return auth_exception
    
    if post.uploader!=userid:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "User id does not match.")
    
    # Add post
    session.add(post)
    session.commit()
    session.refresh(post)

    # Add media
    for id in media_id_list:
        session.add(HasMedia(post_id=post.post_id, media_id=id))
    session.commit()

    session.close()
    return {"message": "Successfully added posts"}

# Delete posts
@router.delete("/")
def delete_post(post_id: int = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()
    # Extract userid
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = int(payload["sub"])
        if userid is None:
            return auth_exception
    except:
        return auth_exception

    posts = session.exec(select(Post).where(Post.post_id==post_id)).all()
    
    if len(posts)<1:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "No such post")
    
    post = posts[0]
    if post.uploader!=userid:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Cannot delete posts of another user")

    # Get relavant media
    has_media_list = session.exec(select(HasMedia).where(HasMedia.post_id==post_id)).all()
    media_id_list = [has_media.media_id for has_media in has_media_list]
    media_list = session.exec(select(Media).where(col(Media.media_id).in_(media_id_list))).all()

    # Delete the related media
    for has_media in has_media_list:
        session.delete(has_media)
    session.commit()
    for media in media_list:
        session.delete(media)
    session.commit()

    # Delete the post at last
    session.delete(post)
    session.commit()

    session.close()
    return {"message": "Successfully deleted posts"}

# Update posts
@router.patch("/")
def update_post(post: Post = Body(..., embed=True), media_id_list: list[int] = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()

    statement = select(Post).where(Post.post_id == post.post_id)
    result = session.exec(statement).all()

    if len(result) == 0:
        return {"message": "Post not found"}

    post_to_update = result[0]
    post_to_update.uploader = post.uploader
    post_to_update.posturl = post.posturl
    post_to_update.word_content = post.word_content
    post_to_update.like_count = post.like_count
    
    old_has_media_list = session.exec(select(HasMedia).where(HasMedia.post_id==post.post_id)).all()
    old_media_id_list = [has_media.media_id for has_media in old_has_media_list]

    intersection = set(old_media_id_list)&set(media_id_list)
    for media_id in media_id_list:
        if media_id not in intersection:
            session.add(HasMedia(post_id=post.post_id, media_id=media_id))
    session.commit()

    for has_media in old_has_media_list:
        if has_media.media_id not in intersection:
            session.delete(has_media)
            session.delete(session.exec(select(Media).where(Media.media_id==has_media.media_id)).one())
    session.commit()

    session.add(post_to_update)
    session.commit()
    session.close()
    return {"message": "Successfully updated post"}

# Recommend posts based on user distance and likes
@router.get("/recommendations")
def post_recommendations(
    number_of_posts: int,
    token: str = Depends(oauth2_scheme),
) -> list[Post]:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    # Get userid from token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    userid = int(payload["sub"])
    if userid is None:
        raise credentials_exception

    # Start session
    session = create_session()

    # Build the distance array
    distance = get_all_social_distance(userid)
    distance_list = [(friend, distance[friend]) for friend in distance if distance[friend] < 10]

    # Calculate score of the posts
    posts: list[tuple[Post | int]] = []
    for user, dist in distance_list:
        user_posts = session.exec(
            select(Post).where(Post.uploader==user)
        ).all()

        for post in user_posts:
            posts.append((post, float(post.like_count)*(1/dist)))

    # Rank the score of posts
    posts.sort(key=lambda x:x[1], reverse=True)
    
    recommended_posts = [post[0] for post in posts[:number_of_posts]]
    recommended_posts.sort(key=lambda x: x.created_at, reverse=True)
    return recommended_posts