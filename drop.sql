drop table users CASCADE
;

drop table forum CASCADE
;

drop table thread CASCADE
;

drop table messages CASCADE
;

drop table votes CASCADE
;

drop table usersForums CASCADE
;

DROP INDEX IF EXISTS indexUniqueEmail;
DROP INDEX IF EXISTS indexUniqueNickname;
DROP INDEX IF EXISTS indexUniqueNicknameLow;

DROP INDEX IF EXISTS indexForumsUser;
DROP INDEX IF EXISTS indexUniqueSlugForums;

DROP INDEX IF EXISTS indexThreadUser;
DROP INDEX IF EXISTS indexThreadForum;
DROP INDEX IF EXISTS indexUniqueSlugThread;

DROP INDEX IF EXISTS indexPostAuthor;
DROP INDEX IF EXISTS indexPostForum;
DROP INDEX IF EXISTS indexPostThread;
DROP INDEX IF EXISTS indexPostCreated;
DROP INDEX IF EXISTS indexPostThreadCreateId;
DROP INDEX IF EXISTS indexPostParentThreadId;
DROP INDEX IF EXISTS indexPostIdThread;
DROP INDEX IF EXISTS indexPostThreadPath;
DROP INDEX IF EXISTS indexPostPath;

DROP INDEX IF EXISTS indexUsersForumsUser;
DROP INDEX IF EXISTS indexUsersForumsForum;
DROP INDEX IF EXISTS indexUsersForumsUserLow;