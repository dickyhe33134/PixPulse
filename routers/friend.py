from models import User
from sqlmodel import select, col, or_, delete
from utils.dbconn import create_session
from fastapi import APIRouter, Body, Response, HTTPException
from routers.auth import get_password_hash
from models import HasFriend, SafeUser, FriendRequest

router = APIRouter(prefix="/api/friend")


# Builds adjacency list of users and their friends
@router.get("/graph")
def build_user_graph() -> dict[int, list[int]]:
    session = create_session()

    # Gets all the edges and vertices in the graph (Friends and Users)
    edges = session.exec(select(HasFriend.userid, HasFriend.friend_id)).all()
    users = session.exec(select(User.userid)).all()

    # Creates a adjacency list of the graph
    graph = {}
    for user in users:
        graph[user] = []
    for user1, user2 in edges:
        graph[user1].append(user2)

    # Close session after building the graph
    session.close()
    return graph

@router.post("/")
def get_friends(userid: int = Body(..., embed=True)) -> list[User]:
    session = create_session()

    result = session.exec(
        select(User).where(col(User.userid).in_(select(HasFriend.friend_id)))
    ).all()

    return result

@router.patch("/add_close")
def get_close_friends(userid: int = Body(..., embed=True)) -> list[User]:
    session = create_session()

    result = session.exec(
        select(User).where(
            (col(User.userid).in_(select(HasFriend.friend_id))) &
            (HasFriend.is_close_friend == True)
        )
    ).all()

    session.close()
    return result

@router.put("/add")
def add_friend(userid: int = Body(..., embed=True), friend_id: int = Body(..., embed=True)):
    session = create_session()

    # Check if the user and friend are valid users
    user = session.exec(select(User).where(User.userid == userid)).first()
    friend = session.exec(select(User).where(User.userid == friend_id)).first()
    if user is None or friend is None:
        session.close()
        return HTTPException(
            status_code=400,
            detail="User or friend does not exist"
        )

    # Add the friend to the database
    has_friend = HasFriend(userid=userid, friend_id=friend_id, is_close_friend=False)
    session.add(has_friend)
    session.commit()

    session.close()
    return {"message": "Successfully added friend"}

# Get all friend requests sent to a user
@router.post("/requests")
def get_friend_requests(userid: int = Body(..., embed=True)) -> list[User]:
    session = create_session()

    result = session.exec(
        select(FriendRequest).where(FriendRequest.receiver==userid)
    ).all()

    session.close()
    return result

@router.put("/request/send")
def send_friend_request(sender: int = Body(..., embed=True), receiver: int = Body(..., embed=True)):
    session = create_session()

    # Check if the sender and receiver are valid users
    sender_user = session.exec(select(User).where(User.userid == sender)).first()
    receiver_user = session.exec(select(User).where(User.userid == receiver)).first()
    if sender_user is None or receiver_user is None:
        session.close()
        return HTTPException(
            status_code=400,
            detail="Sender or receiver does not exist"
        )
    # Check if the sender and receiver are not the same user
    if sender == receiver:
        session.close()
        return HTTPException(
            status_code=400,
            detail="Sender and receiver cannot be the same user"
        )
    # Check if the sender and receiver are already friends
    result = session.exec(select(HasFriend).where(
        (HasFriend.userid == sender) & (HasFriend.friend_id == receiver)
    )).all()
    if len(result) > 0:
        return HTTPException(
            status_code=400,
            detail="Already friends"
        )

    # Check if the friend request already exists
    result = session.exec(select(FriendRequest).where(
        (FriendRequest.sender == sender) & (FriendRequest.receiver == receiver)
    )).all()
    if len(result) > 0:
        return HTTPException(
            status_code=400,
            detail="Friend request already exists"
        )

    # Add the friend request to the database
    friend_request = FriendRequest(sender=sender, receiver=receiver)
    session.add(friend_request)
    session.commit()

    session.close()
    return {"message": "Successfully sent friend request"}

@router.put("/requests/accept")
def accept_friend_request(sender: int = Body(..., embed=True), receiver: int = Body(..., embed=True)):
    session = create_session()

    # Query for the friend request
    friend_request = session.exec(
        select(FriendRequest).where(
            (FriendRequest.sender == sender) & (FriendRequest.receiver == receiver)
        )
    ).first()

    if friend_request is None:
        return HTTPException(
            status_code=400,
            detail="Friend request does not exist"
        )
    
    # Add the friend to the database
    friend = HasFriend(userid=sender, friend_id=receiver, is_close_friend=False)
    session.add(friend)
    session.delete(friend_request)

    session.commit()
    session.close()
    return {"message": "Successfully accepted friend request"}

@router.delete("/friends/requests/reject")
def reject_friend_request(sender: int = Body(..., embed=True), receiver: int = Body(..., embed=True)):
    session = create_session()

    # Query for the friend request
    friend_request = session.exec(
        select(FriendRequest).where(
            (FriendRequest.sender == sender) & (FriendRequest.receiver == receiver)
        )
    ).first()

    if friend_request is None:
        return HTTPException(
            status_code=400,
            detail="Friend request does not exist"
        )

    # Delete the friend request from the database
    session.delete(friend_request)
    session.commit()

    session.close()
    return {"message": "Successfully rejected friend request"}

@router.delete("/friends/remove")
def remove_friend(userid: int = Body(..., embed=True), friend_id: int = Body(..., embed=True)):
    session = create_session()

    # Remove the friend from the database
    result = session.exec(select(HasFriend).where(
        (HasFriend.userid == userid) & (HasFriend.friend_id == friend_id)
    )).all()
    if len(result) < 0:
        return HTTPException(
            status_code=400,
            detail="User or friend does not exist"
        )
    
    session.delete(result[0])
    session.commit()
    session.close()
    return {"message": "Successfully removed friend"}