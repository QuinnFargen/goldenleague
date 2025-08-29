import streamlit as st
from sqlalchemy import text
import pandas as pd

st.set_page_config(layout="wide")

##############################################
# Database connection
@st.cache_resource
def init_connection():
    conn = st.connection("neondb", type="sql")
    return conn

@st.cache_data(ttl=300)
def run_query(query: str, params: tuple = None):
    conn = init_connection()
    if params:
        return conn.query(query, params=params, ttl=300)
    else:
        return conn.query(query, ttl=300)  

def run_insert(query: str, params: dict = None):
    conn = init_connection()
    with conn.session as session:
        session.execute(text(query), params or {})
        session.commit()
    # Gave up on returning the ID that the query within does, messes up page

##############################################
# Queries
def upsert_user(user):
    query = """
    INSERT INTO odd.bettor (google_sub, google_email, google_name, last_login)
    VALUES (:google_sub, :google_email, :google_name, NOW())
    ON CONFLICT (google_sub)
    DO UPDATE SET last_login = NOW(), google_name = EXCLUDED.google_name, google_email = EXCLUDED.google_email
    RETURNING bettor_id;
    """
    return run_insert(query, {
        "google_sub": user["sub"],
        "google_email": user["email"],
        "google_name": user.get("name", "")
    })

bettor_query = """
    SELECT bettor_id
    FROM odd.bettor
    WHERE google_sub = :google_sub
"""


st.title("The Golden League")

# Show authentication button if NOT logged in
if not st.user.is_logged_in:
    st.subheader("Authentication")
    if st.button("Google Authenticate"):
        # st.login("auth0")
        st.login("google")


if st.user.is_logged_in:
    upsert_user(st.user)
    # st.json(st.user)
    # st.json(st.session_state)
    st.header(f"Hello {st.user.name}")
    # st.image(st.user.picture)
    
    bet_df = run_query(bettor_query, {"google_sub": st.user.sub})
    if not bet_df.empty:
        st.session_state["bettor_id"] = bet_df.iloc[0, 0].item()  # get the scalar value
    else:
        st.session_state["bettor_id"] = None  # or handle missing user

    if st.sidebar.button("Log out"):
        st.logout()
        st.rerun()

    league = st.text_input("League Code", "Cousins")
    if st.button("Submit"):
        st.session_state["league"] = league
        st.sidebar.write(f"Your League: {league}")
        st.sidebar.write(f"Your User ID: {st.session_state['bettor_id']}")
