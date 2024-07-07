--CREATE TRIGGER DEL_POST: User can only delete a post created by the user.
create or replace trigger del_post
before delete
on posts
for each row
execute procedure check_del_post();

create or replace function check_del_post()
returns trigger
language plpgsql
as $$
begin
if ('user_' || old.owner_user_id :: text != current_user) then
	raise exception 'You cannot delete the posts that are not created by you';
end if;

return old;
end;
$$;

--CREATE TRIGGER : DEL_USER ( USER CAN UPDATE ONLY HIS RECORD)
create or replace trigger del_user
before update
on users
for each row
execute procedure check_upd_user();

create or replace function check_upd_user()
returns trigger
language plpgsql
as $$
begin
if ('user_' || old.user_id :: text != current_user) then
	raise exception 'Incorrect user_id given for current user logged in';
end if;
return old;
end;$$;
select * from users

--TRIGGER TO SET CHANGES IN SCORE OF POST WHEN THERE IS INSERT on votes
create or replace function vote_update_trig()
returns trigger
language plpgsql
as $$

begin
execute 'update posts set score = (select count(*) from votes where votes.post_id=posts.post_id 
						  and votes.vote_type_id=2 ) - (select count(*) from votes where votes.post_id=posts.post_id 
						  and votes.vote_type_id=3 )';
end;
$$;

create or replace trigger vote_update
after insert
on votes
for each row
execute procedure vote_update_trig();

--CREATE TRIGGER : UPDATE SCORE OF POST, SCORE OF USERS,BEST ANS ID OF QUESTION POST
--VIEW COUNT INCREMENTED WHEN THERE IS AN INSERTION IN VOTES
create or replace trigger best_ans_upd
after insert
on votes
for each row
execute procedure check_best_ans();

create or replace function check_best_ans()
returns trigger
language plpgsql
as $$
DECLARE
     i int;
Begin
if (new.vote_type_id =2) then
			update 	posts set score = score+1 where posts.post_id = new.post_id;
			update users set users.score = users.score + 15 where users.user_id in
			(select posts.owner_user_id from posts where posts.post_id= new.post_id);
			update users set users.up_votes = users.up_votes + 1 where users.user_id= new.user_id ;

		elsif(new.vote_type_id =3) then
			update 	posts set score = score-1 where posts.post_id = new.post_id;
			update users set users.score = users.score - 8 where users.user_id in
			(select posts.owner_user_id from posts where posts.post_id= new.post_id);
			update users set users.down_votes = users.down_votes + 1 where users.user_id= new.user_id ;

end if;

if ((select posts.post_type_id from posts where posts.post_id = new.post_id)=2) then

i:=(select post_id from posts where score in (select max(score) from posts where parent_id=new.parent_id) limit 1); 
update posts set best_answer_id = i  where posts.post_id = new.parent_id;	
end if;
update users set users.view_count = users.view_count+1 where users.user_id in 
(select owner_user_id from posts where posts.post_id =new.post_id );

end;
$$;

--TRIGGER TO INCREMENT ANSWER COUNT ON INSERTION OF ANSWER POST IN POSTS

create or replace trigger upd_ans_ct
after insert
on posts
for each row
execute procedure check_ans_ct();

create or replace function check_ans_ct()
returns trigger
language plpgsql
as $$
DECLARE
     i int;
Begin

if (new.post_type_id = 2) then
	update posts set answer_count = answer_count+1 where posts.post_id = new.parent_id;
	end if;
	
end;
$$;

--TRIGGER TO INCREMENT COMMENT COUNT ON INSERTION IN COMMENTS TABLE FOR THAT POST
create or replace trigger upd_comm_ct
after insert on comments
for each row
execute procedure check_comm_ct();

create or replace function check_comm_ct()
returns trigger
language plpgsql
as $$
DECLARE
     i int;
Begin

update posts set comment_count = comment_count+1 where posts.post_id = new.post_id;
	
end;
$$;
