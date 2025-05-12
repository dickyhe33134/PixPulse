import jwt
from models import Comment, HasComment, Post
from sqlmodel import select, col
from fastapi import APIRouter, Body, HTTPException, Depends, status
from utils.dbconn import create_session
from routers.auth import ALGORITHM, SECRET_KEY, oauth2_scheme


router = APIRouter(prefix="/api/comment")

auth_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not authorize user")

@router.get("/")
def get_comment() -> list[Comment]:
    session = create_session()

    statement = select(Comment)
    result = session.exec(statement).all()

    session.close()
    return result

@router.post("/")
def query_comment(
    post_id: int = Body(..., embed=True),
) -> list[Comment]:
    session = create_session()

    relations = session.exec(select(HasComment).where(HasComment.post_id==post_id)).all()
    result = list(session.exec(select(Comment).where(col(Comment.comment_id).in_(relations))))

    result.sort(key=lambda x: x.commented_at, reverse=True)

    session.close()
    return result

@router.put("/")
def add_comment(post_id: int = Body(..., embed=True), comment: Comment = Body(..., embed=True), token: str = Depends(oauth2_scheme)):
    session = create_session()

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        userid = int(payload["sub"])
        if userid is None:
            return auth_exception
    except:
        return auth_exception
    
    if comment.userid!=userid:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "User ID does not match")

    posts = session.exec(select(Post).where(Post.post_id==post_id)).all()
    if len(posts)<1:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Post cannot be found")
    post = posts[0]

    session.add(comment)
    session.commit()
    session.refresh(comment)

    session.add(HasComment(comment_id=comment.comment_id, post_id=post.post_id))

    session.close()
    return {"message": "Successfully added comment"}

@router.delete("/")
def delete_comment(comment_id: int = Body(..., embed=True)):
    session = create_session()
    
    comments = session.exec(select(Comment).where(Comment.comment_id==comment_id)).all()
    if len(comments)<1:
        return HTTPException(status.HTTP_401_UNAUTHORIZED, "Comment does not exist")

    has_comments = session.exec(select(HasComment).where(HasComment.comment_id==comment_id)).all()
    for has_comment in has_comments:
        session.delete(has_comment)
    session.commit()

    session.delete(comments[0])
    session.commit()

    session.close()
    return {"message": "Successfully deleted comment"}

@router.patch("/")
def update_comment(comment: Comment = Body(..., embed=True)):
    session = create_session()

    result = session.exec(select(Comment).where(Comment.comment_id==comment.comment_id)).all()

    if len(result) == 0:
        return {"message": "Comment not found"}

    comment_to_update = result[0]
    comment_to_update.word_content = comment.word_content
    session.add(comment_to_update)

    session.commit()
    session.close()
    return {"message": "Successfully updated comment"}
