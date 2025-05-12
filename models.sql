CREATE TABLE Users (
  userid serial PRIMARY KEY,
  username text NOT NULL unique,
  hashed_password text NOT NULL,
  email text NOT NULL unique,
  phone_no varchar(8),
  admin boolean NOT NULL,
  created_at timestamp
);

CREATE TABLE Posts (
    post_id BIGSERIAL PRIMARY KEY,
    userid serial NOT NULL REFERENCES users(userid),
    word_content TEXT NOT NULL,
    like_count NUMERIC default 0,
    created_at timestamp
);

CREATE TABLE HasFriends (
    userid BIGSERIAL,
    friend_id BIGSERIAL,
    PRIMARY KEY (userid, friend_id),
    FOREIGN KEY (userid) REFERENCES users(userid),
    FOREIGN KEY (friend_id) REFERENCES users(userid)
);

CREATE TABLE FriendRequests (
    sender BIGSERIAL NOT NULL REFERENCES users(userid),
    receiver BIGSERIAL NOT NULL REFERENCES users(userid),
    PRIMARY KEY (sender, receiver),
);

CREATE TABLE Media (
    media_id BIGSERIAL PRIMARY KEY,
    userid serial references users(userid),
    image_name TEXT,
    image_data BYTEA
);

CREATE TABLE HasMedia (
    post_id BIGSERIAL,
    media_id BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (media_id) REFERENCES media(media_id)
);

CREATE TABLE Comments (
    comment_id BIGSERIAL PRIMARY KEY,
    userid SERIAL NOT NULL REFERENCES users(userid),
    word_content TEXT NOT NULL,
    like_count NUMERIC default 0,
    commented_at timestamp
);

CREATE TABLE HasComments (
    comment_id BIGSERIAL PRIMARY KEY REFERENCES comments(comment_id),
    post_id BIGSERIAL REFERENCES posts(post_id),
    userid SERIAL REFERENCES users(userid)
);