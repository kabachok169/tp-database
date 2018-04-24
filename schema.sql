CREATE EXTENSION IF NOT EXISTS CITEXT;

CREATE TABLE users
(
id BIGSERIAL UNIQUE,
nickname VARCHAR COLLATE ucs_basic PRIMARY KEY,
about TEXT,
email CITEXT NOT NULL UNIQUE,
fullname CITEXT
);

CREATE TABLE forum
(
id BIGSERIAL primary key,
slug CITEXT not null unique,
title CITEXT,
author VARCHAR references users(nickname),
threads INTEGER DEFAULT 0,
posts INTEGER DEFAULT 0
);

CREATE TABLE thread
(
id BIGSERIAL PRIMARY KEY,
slug CITEXT UNIQUE,
created TIMESTAMP WITH TIME ZONE,
message TEXT,
title TEXT,
author VARCHAR REFERENCES users (nickname),
forum TEXT,
votes BIGINT DEFAULT 0
);

CREATE TABLE messages (
id SERIAL NOT NULL PRIMARY KEY,
author VARCHAR NOT NULL REFERENCES users(nickname),
created TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
forum VARCHAR,
isEdited BOOLEAN DEFAULT FALSE,
message TEXT NOT NULL,
parent INTEGER DEFAULT 0,
thread INTEGER NOT NULL REFERENCES thread(id),
path BIGINT ARRAY
);

CREATE TABLE votes
(
voice INT CHECK (voice in (1, -1)),
nickname VARCHAR REFERENCES users (nickname),
thread BIGINT REFERENCES thread (id)
-- CONSTRAINT unique_vote UNIQUE (userid, threadid)
);

CREATE TABLE usersForums (
author VARCHAR REFERENCES users(nickname) NOT NULL,
forum CITEXT REFERENCES forum(slug) NOT NULL
);