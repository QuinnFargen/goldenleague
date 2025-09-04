import os
import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd




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
    WHERE draftor_id = :draftor_id
"""


##############################################
st.title(f"Your Current Rankings")
# st.logo("logo.png")

# Show authentication button if NOT logged in
if not st.session_state["draftor_name"] or not st.session_state["league_name"]:
    # Send them to login page
    st.switch_page("1_🥇_Golden.py")

else:
    if st.sidebar.button("Log out"):
        st.logout()
        st.rerun()
    st.sidebar.write(f"User Name: {st.session_state['draftor_name']}")
    st.sidebar.write(f"League Name: {st.session_state['league_name']}")
    st.sidebar.write(f"User ID: {st.session_state['draftor_id']}")



    ##############################################
    # Page

    if "rankings" not in st.session_state:
        st.session_state["rankings"] = run_query(
            draft_query, {"draftor_id": st.session_state['draftor_id']}
        )

    if st.button("Refresh Rankings"):
        st.session_state["rankings"] = run_query(
            draft_query, {"draftor_id": st.session_state['draftor_id']}
        )

    st.dataframe(st.session_state["rankings"])
