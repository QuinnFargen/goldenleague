import os
import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

##############################################
st.title(f"Your Current Rankings")
# st.logo("logo.png")


# Show authentication button if NOT logged in
if not st.user.is_logged_in:
    # Send them to login page
    st.switch_page("1_🥇_Golden.py")

if st.user.is_logged_in:
    if st.sidebar.button("Log out"):
        st.logout()
        st.experimental_rerun()
    st.sidebar.write(f"Your League: {st.session_state['league']}")
    st.sidebar.write(f"Your User ID: {st.session_state['bettor_id']}")



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
        return conn.query(query, params=params, ttl=300)  # Streamlit built-in query method
    else:
        return conn.query(query, ttl=300)




##############################################
# Queries
draft_query = """
    SELECT team_abbr, rank
    FROM odd.draft
    WHERE bettor_id = :bettor_id
"""


##############################################
# Page

current_rank = run_query(draft_query, {"bettor_id": st.session_state['bettor_id']})
st.dataframe(current_rank)
