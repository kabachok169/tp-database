CREATE EXTENSION IF NOT EXISTS CITEXT;

CREATE TABLE users
(
id BIGSERIAL UNIQUE,
nickname VARCHAR PRIMARY KEY,
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
author_id BIGSERIAL REFERENCES users (id),
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
nickname CITEXT REFERENCES users (nickname)
-- threadid BIGINT REFERENCES threads (id),
-- CONSTRAINT unique_vote UNIQUE (userid, threadid)
);