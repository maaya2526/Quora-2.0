--create group role -client_user
create role client_user login password 'postgres';

-- grant prieveleges to client_user 
grant select, insert on users to client_user;
 grant select on badges to client_user;
 grant all on comments to client_user;
 grant select, insert, delete on posts to client_user;
 grant insert on votes to client_user;
 
-- create group role - managers
create role managers;
--create two manager roles 
create role leaderboard_manager;
create role moderator;

--grant prieveleges to manager
grant select on all tables in schema "public" to managers;

grant managers to leaderboard_manager;
grant update on badges to leaderboard_manager;

grant managers to moderator;
grant delete on users,posts to moderator;

