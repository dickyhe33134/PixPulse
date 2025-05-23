from datetime import datetime
from enum import Enum
from sys import stderr
from sqlmodel import Field, Session, SQLModel, UniqueConstraint, create_engine, select
from datetime import timezone


class User(SQLModel, table=True):

    __tablename__ = "users"

    # User id generated by Postgres, DO NOT DECLARE
    userid: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: str
    phone_no: str | None
    admin: bool
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SafeUser(SQLModel):

    # User id generated by Postgres, DO NOT DECLARE
    userid: int | None
    username: str
    email: str
    phone_no: str | None
    admin: bool
    created_at: datetime | None

class UserInfo(SQLModel, table=True):

    userid: int | None = Field(default=None, primary_key=True, foreign_key="users.userid")
    bio: str | None
    profile_pic: bytes | None

class Post(SQLModel, table=True):

    __tablename__ = "posts"

    # ID generated by database. DO NOT DECLARE
    post_id: int | None = Field(default=None, primary_key=True)
    uploader: int = Field(foreign_key="users.userid")
    posturl: str | None
    word_content: str | None
    like_count: int | None
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class HasFriend(SQLModel, table=True):

    __tablename__ = "hasfriends"

    userid: int | None = Field(
        default=None, primary_key=True, foreign_key="users.userid"
    )
    friend_id: int = Field(default=None, primary_key=True, foreign_key="users.userid")
    is_close_friend: bool = Field(default=False)


class FriendRequest(SQLModel, table=True):

    __tablename__ = "friendrequests"
    request_id: int | None = Field(default=None, primary_key=True)
    sender: int = Field(foreign_key="users.userid")
    receiver: int = Field(foreign_key="users.userid")


class HasComment(SQLModel, table=True):
    __tablename__="hascomments"
    comment_id: int | None=Field(default=None, primary_key=True, foreign_key="comments.comment_id")
    post_id:int=Field(foreign_key="posts.post_id")
    userid:int=Field(foreign_key="users.userid")
    commented_at:datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))

class Comment(SQLModel, table=True):

    __tablename__ = "comments"

    comment_id: int | None = Field(default=None, primary_key=True)
    userid: int = Field(foreign_key="users.userid")
    word_content: str
    like_count: int = Field(default=0)
    commented_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class HasMedia(SQLModel, table=True):

    post_id: int = Field(foreign_key="posts.post_id")
    media_id: int = Field(primary_key=True, foreign_key="media.media_id")


class LikedBy(SQLModel,table=True):
    __tablename__="likedby"
    post_id:int | None=Field(default=None, foreign_key="posts.post_id")
    comment_id:int | None=Field(default=None, foreign_key="comments.comment_id")
    userid:int | None=Field(default=None, foreign_key="users.userid",primary_key=True)

class Media(SQLModel, table=True):

    media_id: int | None = Field(default=None, primary_key=True)
    userid: int = Field(foreign_key="users.userid")
    image_data: bytes