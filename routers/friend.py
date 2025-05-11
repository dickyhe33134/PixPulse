from models import User
from sqlmodel import select, col, or_, delete
from utils.dbconn import create_session
from fastapi import APIRouter, Body, Response, HTTPException, status
from routers.auth import get_password_hash
from models import HasFriend, SafeUser, FriendRequest
import heapq

router = APIRouter(prefix="/api/friend")


# Builds adjacency list of users and their friends
# @router.get("/graph")
def build_user_graph() -> dict[int, list[tuple[int]]:]:
    session = create_session()

    # Gets all the edges and vertices in the graph (Friends and Users)
    edges = session.exec(select(HasFriend)).all()
    users = session.exec(select(User.userid)).all()

    # Creates a adjacency list of the graph
    graph = {}
    for user in users:
        graph[user] = []

    # The graph is directed as users1 can be friends with user2 but not vice versa
    for has_friend in edges:
        user1 = has_friend.userid
        user2 = has_friend.friend_id
        close = has_friend.is_close_friend

        dist = 1 if close else 3
        graph[user1].append((user2, dist))

    # Close session after building the graph
    session.close()
    return graph

# Get social distance between users
@router.post("/distance")
def get_social_distance(
    userid: int = Body(..., embed=True), friend_id: int = Body(..., embed=True)
) -> int:
    
    distance = get_all_social_distance(userid)
    return distance.get(friend_id, -1)

@router.post("/all_distancte")
def get_all_social_distance(userid: int = Body(..., embed=True)) -> dict[int, int]:
    # Initialize the graph and heap
    graph = build_user_graph()
    visited = set()
    heap = [(0, userid)]
    distance = {userid: 0}

    # Dijkstra to find the shortest path
    while heap:
        dist, user = heapq.heappop(heap)
        visited.add(user)

        for friend, cost in graph[user]:
            if friend not in visited:
                heapq.heappush(heap, (dist+cost, friend))
                visited.add(friend)
                distance[friend] = dist+cost
            else:
                distance[friend] = min(distance[friend], dist+cost)
    
    del distance[userid]
    return distance


@router.post("/")
def get_friends(userid: int = Body(..., embed=True)) -> list[SafeUser]:
    session = create_session()

    result = session.exec(
        select(User).where(col(User.userid).in_(select(HasFriend.friend_id)))
    )
    result = [SafeUser.model_validate(x) for x in result]

    session.close()
    return result

@router.patch("/add_close")
def get_close_friends(userid: int = Body(..., embed=True)) -> list[SafeUser]:
    session = create_session()

    result = session.exec(
        select(User).where(
            (col(User.userid).in_(select(HasFriend.friend_id))) &
            (HasFriend.is_close_friend == True)
        )
    )
    result = [SafeUser.model_validate(x) for x in result]

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
def get_friend_requests(userid: int = Body(..., embed=True)) -> list[int]:
    session = create_session()

    result = session.exec(
        select(FriendRequest.sender).where(FriendRequest.receiver==userid)
    ).all()

    session.close()
    return result

@router.put("/requests/send")
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

@router.delete("/requests/reject")
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

@router.delete("/remove")
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