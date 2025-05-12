from models import Comments, HasComments
from sqlmodel import select, col, or_
from fastapi import APIRouter, Body, Query, HTTPException, Depends
from utils.dbconn import create_session


router = APIRouter(prefix="/api/comment")


@router.get("/")
def get_comment() -> list[Comments]:
    session = create_session()

    statement = select(Comments)
    result = session.exec(statement).all()

    session.close()
    return result

@router.get("/")
def query_comment(
    comment_ids: list[int] | None = Body(..., embed=True),
    posts: list[int] | None = Body(..., embed=True),
) -> list[Comments]:
    session = create_session()

    statement = select(Comments).where(or_(col(Comments.comment_id).in_(comment_ids), col(HasComments.post_id).in_(posts)))
    result = session.exec(statement).all()

    session.close()
    return result

@router.post("/")
def add_comment(comment:Comments=Body(...,embed=True)):
    session=create_session()
    session.add(comment)
    session.commit()
    session.close()
    return {"message": "Successfully added comments"}

@router.delete("/")
def delete_comment(comment_id:int=Body(..., embed=True)):
    session = create_session()
    statement=select(Comments).where(Comments.comment_id==comment_id)
    result=session.exec(statement).all()
    session.delete(result)
    session.commit()

    session.close()
    return {"message": "Successfully deleted posts"}

@router.patch("/")
def update_comment(comment: Comments = Body(..., embed=True)):
    session = create_session()

    statement = select(Comments).where(comment.post_id == comment.post_id)
    result = session.exec(statement).all()

    if len(result) == 0:
        return {"message": "Comment not found"}

    comment_to_update = result[0]
    comment_to_update.image_name = comment.image_name
    comment_to_update.image_data = comment.image_data
    comment_to_update.word_content = comment.word_content
    session.add(comment_to_update)
    session.commit()
    session.close()
    return {"message": "Successfully updated comment"}
