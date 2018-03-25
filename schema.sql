CREATE EXTENSION IF NOT EXISTS CITEXT;

create table users
(
  id bigserial primary key,
  nickname citext collate ucs_basic not null unique,
  about text,
  email citext not null unique,
  fullname text
)
;

create table forum
(
  id bigserial primary key,
  slug citext not null unique,
  title text,
  user_name CITEXT references users(nickname)
)
;

create table thread
(
  id         BIGSERIAL PRIMARY KEY,
  slug       CITEXT,
  created_on TIMESTAMP,
  message    TEXT,
  title      TEXT,
  author_id   BIGINT REFERENCES users (id),
  forum_id    BIGINT REFERENCES forum (id)
)
;

create table message
(
  id         BIGSERIAL PRIMARY KEY,
  created_on TIMESTAMP,
  message    TEXT,
  is_edited   BOOLEAN,
  author_name   CITEXT REFERENCES users (nickname),
--   parent_id   BIGINT REFERENCES message (id) DEFAULT 0,
  thread_id   BIGINT REFERENCES thread (id),
  forum_id    BIGINT REFERENCES forum (id),
  parent_tree BIGINT[] DEFAULT '{0}'

)
;

create table vote
(
  voice      INT CHECK (voice in (1, -1)),
  userid     BIGINT REFERENCES users (id),
  threadid   BIGINT REFERENCES thread (id),
  CONSTRAINT unique_vote UNIQUE (userid, threadid)
)
;

-- alter table message add parenttree bigint ARRAY;
