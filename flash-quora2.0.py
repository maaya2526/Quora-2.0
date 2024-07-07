import streamlit as st
import psycopg2
import pandas as pd


def authenticate(username, password):
    conn=None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="project",
            user=username,
            password=password,
            host="localhost",
            port="5432"
        )

        # If connection successful, return True
    except (Exception, psycopg2.Error) as error:
        st.error("Invalid username or password. Please try again.")
    return conn
def user_info(id,conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Users where user_id = {id}")
    info = cursor.fetchall()
    cursor.close()
    return info

def get_all_feat_posts(conn):
    cursor = conn.cursor()
    cursor.execute('''SELECT featured_questions.post_id, users.user_name,featured_questions.body FROM 
                   featured_questions,users 
                   where users.user_id = featured_questions.owner_user_id ''')
    posts = cursor.fetchall()
    cursor.close()
    return posts


def get_all_answers(p_id ,conn):
    cursor = conn.cursor()
    temp_str1 = f'''SELECT posts.post_id, users.user_name,posts.body FROM 
                    posts,users 
                    where users.user_id = posts.owner_user_id and posts.parent_id={p_id} 
                    and posts.post_type_id=2'''
    cursor.execute(temp_str1)
    
    posts = cursor.fetchall()
    cursor.close()
    return posts




def get_all_posts(p_id ,u_id,p_t,conn):
    cursor = conn.cursor()
    temp_str1 = '''SELECT posts.post_id, users.user_name,posts.body,posts.score,posts.upvotes,posts.downvotes FROM 
                    posts,users 
                    where users.user_id = posts.owner_user_id'''
    if p_id:
        temp_str1 += f''' and posts.post_id={p_id} '''
    if u_id:
        temp_str1 += f''' and posts.owner_user_id={u_id} '''
    if p_t:
        temp_str1 += f''' and posts.post_type_id={p_t} '''
    # if p_id :
     #     cursor.execute(temp_str)
    #     temp=cursor.fetchall()
    # elif p_id : 
    #      cursor.execute(f'''SELECT posts.post_id, users.user_name,posts.body FROM 
    #                 posts,users 
    #                 where users.user_id = posts.owner_user_id  and  posts.post_id = {p_id} ''')
    # elif u_id : 
    #      cursor.execute(f'''SELECT posts.post_id, users.user_name,posts.body FROM 
    #                 posts,users 
    #                 where users.user_id = posts.owner_user_id  and  posts.owner_user_id = {u_id} ''')
    cursor.execute(temp_str1)
    posts = cursor.fetchall()
    cursor.close()
    return posts


def get_all_users(u_id ,u_name,loc,conn):
    cursor = conn.cursor()
    temp_str1 = ''' SELECT * from users  where '''
    s1=""
    s2=""
    s3=""
    fl=[0,0,0]
    if u_id:
        s1 += f''' user_id={u_id} '''
        fl[0]=1
    if u_name:
        s2 += f''' user_name=%s'''
        fl[1]=1
    if loc:
        s3 += f''' location= %s ''' 
        fl[2]=1
    print(u_name)
    temp_arr=[]
    if sum(fl) ==3 : 
         temp_str1 = temp_str1  + s1 + " and " + s2 + " and " + s3
         cursor.execute(temp_str1,(u_name,loc))
    elif sum(fl)==1:
         temp_str1 = temp_str1  + s1 + s2 +  s3
         for i in range(3):
              if fl[i]==1:
                   if i==1:
                    cursor.execute(temp_str1,(u_name,))
                   elif i==2:
                    cursor.execute(temp_str1,(loc,))
    elif sum(fl)==2:
         if fl[0] ==1 and fl[1]==1:
              temp_str1 = temp_str1  + s1 + " and " + s2 
              cursor.execute(temp_str1,(u_name,))
         elif fl[1] ==1 and fl[2]==1:
              temp_str1 = temp_str1  + s2 + " and " + s3
              cursor.execute(temp_str1,(u_name,loc))
         elif fl[0] ==1 and fl[2]==1:
              temp_str1 = temp_str1  + s1 + " and " + s3
              cursor.execute(temp_str1,(loc,))
   
    
    
    posts = cursor.fetchall()
    cursor.close()
    return posts

def get_tag_view(conn) :
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM top5_tags")
        tags = cursor.fetchall()
        cursor.close()
        return tags
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error fetching tag data: {error}")
        return None


def get_lb(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, score FROM leader_board")
        users = cursor.fetchall()
        cursor.close()
        return users
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error fetching leaderboard data: {error}")
        return None
    

def get_upvotes(p_id,conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM votes where post_id={p_id} and vote_type_id  =2")
        votes = cursor.fetchall()
        cursor.close()
        return votes
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error fetching users data: {error}")
        return None
def get_downvotes(p_id,conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM votes where post_id={p_id} and vote_type_id  =3")
        votes = cursor.fetchall()
        cursor.close()
        return votes
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error fetching users data: {error}")
        return None
    
def put_vote(p_id,v_typ,conn):
        cursor = conn.cursor()
        cursor.execute(f"call create_vote({p_id},{v_typ})")
        conn.commit()
        cursor.close()
def create_post (p_type,txt,par_id,tag,conn) :
        cursor = conn.cursor()
        temp_str = f"call create_new_post({p_type},%s"
        if tag:
             temp_str=temp_str+f" ,{tag}"
        if par_id:
             temp_str=temp_str+f" ,{par_id}"
        temp_str+=")"
        cursor.execute(temp_str,(txt,))
        conn.commit()
        cursor.close()

def main():
    st.title("Quora 2.0 Login")
    # Login button
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
            conn = authenticate(username, password)

    
        
    
    conn = authenticate(username, password)
    if conn:
        st.markdown('# Home')
        u_id =0
        if username.startswith("user"):
            for i in range (len(username)):
                if username[i]=='_':
                    u_id =  int(username[i+1:])
                    break
            inf = user_info(u_id,conn)
            st.markdown('##### Userid')
            st.markdown(inf[0][0],unsafe_allow_html=True)
            st.markdown('##### Username')
            st.markdown(inf[0][1],unsafe_allow_html=True)
            st.markdown('##### User Bio')
            st.markdown(inf[0][7],unsafe_allow_html=True)

            st.markdown('##### Statistics ')

            sel_us = [(i[2],i[3],i[4],i[5]) for i in inf]
            df = pd.DataFrame(sel_us, columns=["Score","Views","Downvotes Casted","Upvotes Casted"])
            st.dataframe(df)
            st.markdown('##### Location')
            st.markdown(inf[0][6],unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('# Views')
        col1, col2, col3 = st.columns(3)

   
        with col1:
            b1 = st.button("Featured Questions")
        with col2:
            b2 = st.button("Leaderboard")
        with col3:
            b3 = st.button("Top tags")
        if b1:
            posts = get_all_feat_posts(conn)
            if posts:
                    for post in posts : 
                        # st.markdown(f'##### {post[1]}')
                        # st.markdown(f'##### {post[0]}')
                        st.markdown(f"""
                            <div style="display: flex;">
                                <h2 style="margin-right: 20px;font-size: 28px;"> {post[0]}</h2>
                                <h2 style="margin-right: 20px;font-size: 28px;"> {post[1]}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(post[2], unsafe_allow_html=True)
                    #with st.expander("View Featured"):
                    # df = pd.DataFrame(posts, columns=["body"])
                    # st.dataframe(df)
                        
            else:
                    st.write("No entries found.")
        if b2:
                users= get_lb(conn) 
                df = pd.DataFrame(users, columns=["Name","score"])
                st.dataframe(df)
        if b3:
                users= get_tag_view(conn) 
                df = pd.DataFrame(users, columns=["Name","count"])
                st.dataframe(df)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('# Posts')
        
        p_id = st.text_input("Post_id")

        if "b8_pressed" not in st.session_state:
            st.session_state.b8_pressed = False
        b8  = st.button("Get Details")
        if b8:
                     st.session_state.b8_pressed = True
        if st.session_state.b8_pressed :
                     posts = get_all_posts(p_id,False,False,conn)
                     if posts:
                            for post in posts :
                                # st.markdown(f'##### {post[1]}')
                                    # st.markdown(f'##### {post[0]}')
                                    st.markdown(f"""
                                        <div style="display: flex;">
                                            <h2 style="margin-right: 20px;font-size: 28px;"> {post[0]}</h2>
                                            <h2 style="margin-right: 20px;font-size: 28px;"> {post[1]}</h2>
                                            
                                        </div>
                                    """, unsafe_allow_html=True)
                                    vote_key = f"vote_{post[0]}"
                                    vote_options = ["","Upvote", "Downvote"]
                                    up_users = get_upvotes(p_id,conn)
                                    down_users = get_downvotes(p_id,conn)
                                    default_vote = ""
                                    for i in up_users: 
                                         if i[0]==u_id:
                                            default_vote = "Upvote"
                                    for i in down_users: 
                                        if i[0]==u_id:
                                            default_vote = "Downvote"
                                    vote = st.radio("Vote:", options=vote_options,index=vote_options.index(default_vote), key=vote_key)
                                    if vote == "Upvote" and default_vote!="Upvote":
                                        put_vote(p_id,2,conn)
                                    elif vote == "Downvote" and default_vote!="Downvote":
                                        put_vote(p_id,3,conn)
                                    st.markdown(post[2], unsafe_allow_html=True)
                     answers = get_all_answers(p_id,conn)
                     for ans in answers:
                                st.markdown(f"""
                                        <div style="display: flex;">
                                            <h2 style="margin-right: 20px;font-size: 20px;"> {ans[0]}</h2>
                                            <h2 style="margin-right: 20px;font-size: 20px;"> {ans[1]}</h2>
                                        </div>
                                    """, unsafe_allow_html=True)
                                vote_key = f"vote_{ans[0]}"
                                vote_options = ["","Upvote", "Downvote"]
                                up_users = get_upvotes(ans[0],conn)
                                down_users = get_downvotes(ans[0],conn)
                                default_vote = ""
                                for i in up_users: 
                                         if i[0]==u_id:
                                            default_vote = "Upvote"
                                for i in down_users: 
                                        if i[0]==u_id:
                                            default_vote = "Downvote"
                                vote2 = st.radio("Vote:", options=vote_options,index=vote_options.index(default_vote), key=vote_key)
                                if vote2 == "Upvote" and default_vote!="Upvote":
                                        put_vote(p_id,2,conn)
                                elif vote2 == "Downvote" and default_vote!="Downvote":
                                        put_vote(p_id,3,conn)
                                st.markdown(ans[2], unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # option = st.radio("Post type", options=["Question", "Answer"])
        # p_type=0
        # # Check if an option is selected
        # if option=="Question":
        #     p_type=2
        # elif option=="Answer":
        #     p_type=3
        p_type = st.text_input("Post_type")
        txt = st.text_input("Text")
        par_id = st.text_input("Parent Post")
        tag=st.text_input("Tag")


        b9  = st.button("Create post")
        if b9:
                     if ((p_type and txt) or par_id or tag) :
                          print("yooo")
                          create_post (p_type,txt,par_id,tag,conn) 

        st.sidebar.write("Search for posts : ")
        post_id = st.sidebar.text_input("Post id")
        owner_user_id =st.sidebar.text_input("Owner userid")
        post_type =st.sidebar.text_input("Post type")
        b4 = st.sidebar.button("Search posts")
        if (post_id or owner_user_id or post_type ) and b4: 
            posts = get_all_posts(post_id,owner_user_id,post_type,conn)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## Search Results ")
            if posts:
                    for post in posts : 
                        # st.markdown(f'##### {post[1]}')
                        # st.markdown(f'##### {post[0]}')
                        st.markdown(f"""
                            <div style="display: flex;">
                                <h2 style="margin-right: 20px;font-size: 28px;"> {post[0]}</h2>
                                <h2 style="margin-right: 20px;font-size: 28px;"> {post[1]}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        sel_us = [(post[3],post[4],post[5]) ]
                        df = pd.DataFrame(sel_us, columns=["Score","Downvotes ","Upvotes "])
                        st.dataframe(df)
                        st.markdown(post[2], unsafe_allow_html=True)
                        
                             
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                    
            else : st.markdown("#### No records exists :( ")
        st.sidebar.write("Search for users : ")
        
        user_id =st.sidebar.text_input("User id")
        user_name = st.sidebar.text_input("Name")
        loc =st.sidebar.text_input("Location")
        b5 = st.sidebar.button("Search Users")
        if (user_id or user_name or loc ) and b5: 
            users = get_all_users(user_id,user_name,loc,conn)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## Search Results ")
            if users :
                
                for inf in users : 
                    st.markdown('##### Userid')
                    st.markdown(inf[0],unsafe_allow_html=True)
                    st.markdown('##### Username')
                    st.markdown(inf[1],unsafe_allow_html=True)
                    st.markdown('##### User Bio')
                    st.markdown(inf[7],unsafe_allow_html=True)

                    st.markdown('##### Statistics ')

                    sel_us = [(inf[2],inf[3],inf[4],inf[5])]
                    df = pd.DataFrame(sel_us, columns=["Score","Views","Downvotes Casted","Upvotes Casted"])
                    st.dataframe(df)
                    st.markdown('##### Location ')
                    st.markdown(inf[6],unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else : st.markdown("#### No records exists :( ")
        
        
            
             
             
        

if __name__ == "__main__":
    main()