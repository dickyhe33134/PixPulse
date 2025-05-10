from datetime import datetime
from sqlmodel import select, col, or_
from fastapi import APIRouter, Body, Query, HTTPException
from models import Post, HasFriend
from utils.dbconn import create_session

router = APIRouter(prefix="/api/post")


@router.get("/")
def get_post():
    session = create_session()

    statement = select(Post)
    query_result = session.exec(statement)
    result = list(query_result)

    session.close()
    return {"message": "Successfully got posts", "result": result}


@router.post("/")
def query_post(
    post_ids: list[int] | None = Body(..., embed=True),
    uploaders: list[int] | None = Body(..., embed=True),
) -> list[Post]:
    session = create_session()

    statement = select(Post).where(or_(col(Post.post_id).in_(post_ids), col(Post.uploader).in_(uploaders)))
    query_result = session.exec(statement)
    result = list(query_result)

    session.close()
    return {"message": "Successfully queried for posts", "result": result}

@router.put("/")
def add_post(posts: list[Post] = Body(..., embed=True)):
    session = create_session()

    for post in posts:
        session.add(post)
    session.commit()

    session.close()
    return {"message": "Successfully added posts"}

@router.delete("/")
def delete_post(post_ids: list[int] = Body(..., embed=True)):
    session = create_session()

    statement = select(Post).where(col(Post.post_id).in_(post_ids))
    query_result = session.exec(statement)
    result = list(query_result)

    for post in result:
        session.delete(post)
    session.commit()

    session.close()
    return {"message": "Successfully deleted posts"}

@router.patch("/")
def update_post(post: Post = Body(..., embed=True)):
    session = create_session()

    statement = select(Post).where(Post.post_id == post.post_id)
    query_result = session.exec(statement)
    result = list(query_result)

    if len(result) == 0:
        return {"message": "Post not found"}

    post_to_update = result[0]
    post_to_update.uploader = post.uploader
    post_to_update.posturl = post.posturl
    post_to_update.word_content = post.word_content

    session.add(post_to_update)
    session.commit()
    session.close()
    return {"message": "Successfully updated post"}

@router.get("/recommendations")
def recommend_posts(
    user_id: int = Query(..., description="Target user ID"),
    min_likes: int = Query(50, description="Minimum likes threshold")
):
    session = create_session()
    try:
        # Get friend IDs
        friend_ids = session.exec(
            select(HasFriend.friend_id)
            .where(HasFriend.userid == user_id)
        ).scalars().all()

        # Get posts from friends OR popular posts
        posts = session.exec(select(Post).where(or_(Post.uploader.in_(friend_ids),Post.like_count >= min_likes))).scalars().all()
        return {
            "message": "Success" if posts else "No posts found",
            "results": posts
        }

    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        session.close()