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
def upsert_user():
    query = """
    INSERT INTO odd.draftor (draftor_name, league_name, last_login)
    VALUES (:draftor_name, :league_name, NOW())
    ON CONFLICT (draftor_name)
    DO UPDATE SET last_login = NOW()
    RETURNING draftor_id;
    """
    return run_insert(query, {
        "draftor_name": st.session_state["draftor_name"],
        "league_name": st.session_state["league_name"]
    })

bettor_query = """
    SELECT draftor_id
    FROM odd.draftor
    WHERE draftor_name = :draftor_name
        and league_name = :league_name
"""


st.title("The Golden League")


# Initialize session state values
if "draftor_name" not in st.session_state:
    st.session_state["draftor_name"] = None
if "league_name" not in st.session_state:
    st.session_state["league_name"] = None

st.title("🏈 League Login")

# If user not logged in yet
if not st.session_state["draftor_name"] or not st.session_state["league_name"]:
    with st.form("login_form"):
        username = st.text_input("Enter your username")
        league = st.text_input("Enter your league name", "Cousins")

        submitted = st.form_submit_button("Login")

        if submitted:
            if username.strip() and league.strip():
                st.session_state["draftor_name"] = username.strip()
                st.session_state["league_name"] = league.strip()
                upsert_user()
                st.rerun()
            else:
                st.error("Please fill in both fields.")
else:
    st.success(f"✅ Logged in as **{st.session_state['draftor_name']}** in league **{st.session_state['league_name']}**")

    bet_df = run_query(bettor_query, {"draftor_name": st.session_state["draftor_name"], "league_name": st.session_state["league_name"]})
    if not bet_df.empty:
        st.session_state["draftor_id"] = bet_df.iloc[0, 0].item()  # get the scalar value
    else:
        st.session_state["draftor_id"] = None  # or handle missing user

    st.sidebar.write(f"User Name: {st.session_state['draftor_name']}")
    st.sidebar.write(f"League Name: {st.session_state['league_name']}")
    st.sidebar.write(f"User ID: {st.session_state['draftor_id']}")

    if st.button("Logout"):
        st.session_state["draftor_name"] = None
        st.session_state["league_name"] = None
        st.rerun()


# Show authentication button if NOT logged in
# if not st.user.is_logged_in:
#     st.subheader("Authentication")
#     if st.button("Google Authenticate"):
#         # st.login("auth0")
#         st.login("google")


# if st.user.is_logged_in:
#     upsert_user(st.user)
#     # st.json(st.user)
#     # st.json(st.session_state)
#     st.header(f"Hello {st.user.name}")
#     # st.image(st.user.picture)
    
#     bet_df = run_query(bettor_query, {"google_sub": st.user.sub})
#     if not bet_df.empty:
#         st.session_state["bettor_id"] = bet_df.iloc[0, 0].item()  # get the scalar value
#     else:
#         st.session_state["bettor_id"] = None  # or handle missing user

#     if st.sidebar.button("Log out"):
#         st.logout()
#         st.rerun()

#     league = st.text_input("League Code", "Cousins")
#     if st.button("Submit"):
#         st.session_state["league"] = league
#         st.sidebar.write(f"Your League: {league}")
#         st.sidebar.write(f"Your User ID: {st.session_state['bettor_id']}")
