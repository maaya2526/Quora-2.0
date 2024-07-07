--VIEW 1: TOP 50 IN LEADERBOARD
create or replace view leader_board
as 
select users.user_id,users.user_name,users.score,badges.class,users.user_bio 
from users, badges where users.user_id = badges.user_id order by users.score desc limit 50;

select * from leader_board
select * from users

--View 2: top 15 HIGH SCORED QUESTIONS
create or replace view featured_questions
as 
select posts.post_id,posts.owner_user_id , posts.body, posts.score, posts.tags
from posts where posts.post_type_id=1 order by posts.score desc limit 15;
select * from featured_questions

--View 3
