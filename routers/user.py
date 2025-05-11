from typing import Annotated
from models import User
from sqlmodel import select, col, or_, delete
from utils.dbconn import create_session
from fastapi import APIRouter, Body, HTTPException, status
from routers.auth import get_password_hash
from models import Post, HasFriend, SafeUser, FriendRequest
import bcrypt

bcrypt.__about__ = bcrypt

router = APIRouter(prefix="/api/user")


# Get a list of all of the users
@router.get("/")
def get_user() -> list[User]:
    session = create_session()

    statement = select(User)
    query_result = session.exec(statement).all()

    session.close()
    return query_result


# Query for user using userid
@router.post("/")
def query_user(uids: list[int] = Body(..., embed=True)) -> list[User]:
    try:
        session = create_session()

        statement = select(User).where(col(User.userid).in_(uids))
        result = session.exec(statement).all()

        session.close()
        return result
    except Exception as e:
        print(e)
        return {"message": "Error when querying for users", "error": e}


# Add the given users in to the database
@router.put("/")
def add_user(users: list[User] = Body(..., embed=True)):
    try:
        session = create_session()

        for user in users:
            user.hashed_password = get_password_hash(user.hashed_password)
            session.add(user)
        session.commit()

        session.close()
        return {"message": "Successfully added user"}
    except Exception as e:
        print(e)
        return {"message": "Error when adding users", "error": e}


# Delete the users from the database
@router.delete("/")
def delete_user(uids: list[int] = Body(..., embed=True)):
    try:
        session = create_session()

        statement = delete(User).where(col(User.userid).in_(uids))
        session.exec(statement)
        session.commit()

        session.close()
        return {"message": "Successfully deleted users"}
    except Exception as e:
        print(e)
        return {"message": "Error when deleting users", "error": e}


@router.patch("/")
def update_user(user: User = Body(..., embed=True)) -> list[Post]:
    try:
        session = create_session()

        statement = select(User).where(User.userid == user.userid)
        query_result = session.exec(statement)
        result = list(query_result)

        user_to_update = result[0]
        user_to_update.username = user.username
        user_to_update.email = user.email
        user_to_update.phone_no = user.phone_no
        user_to_update.admin = user.admin
        user_to_update.hashed_password = get_password_hash(user.hashed_password)

        session.add(user)
        session.commit()
        session.close()
        return {"message": "Successfully updated user"}
    except Exception as e:
        print(e)
        return {"message": "Error when updating users", "error": e}
