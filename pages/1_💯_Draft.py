import os
import streamlit as st
from streamlit_sortables import sort_items
from sqlalchemy import text
import pandas as pd

##############################################
st.title(f"The Draft Board")
# st.json(st.session_state)
# st.logo("logo.png")


# Show authentication button if NOT logged in
if not st.experimental_user.is_logged_in:
    # Send them to login page
    st.switch_page("1_🥇_Golden.py")

if st.experimental_user.is_logged_in:
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

def run_insert(query: str, params: dict = None):
    conn = init_connection()
    with conn.session as session:
        session.execute(text(query), params or {})
        session.commit()
    # Gave up on returning the ID that the query within does, messes up page



# --- Load CSV ---
teams_df = pd.read_csv("teams.csv")  # Make sure the CSV is in your app folder

st.subheader("Team Info From 2024")
st.caption("ESPN_FPI is a prediction ranking, so sorting by that column my be informative.")
st.dataframe(teams_df)


# 'Abbr' column will be used for sorting
team_abbrs = teams_df["ABBR"].tolist()

# Initialize session_state if needed
if "sorted_teams" not in st.session_state:
    st.session_state["sorted_teams"] = team_abbrs

st.subheader("Arrange These In Desired Order")
# --- Drag-and-drop widget ---
sorted_list = sort_items(st.session_state["sorted_teams"])
st.session_state["sorted_teams"] = sorted_list

st.caption("Sometimes page refreshes on movement. Make sure they end up where you want below.")
# --- Show current order as DataFrame ---
df_display = pd.DataFrame({
    "rank": list(range(1, len(sorted_list) + 1)),
    "team": sorted_list
})
st.dataframe(df_display, hide_index=True)

# --- Submit rankings ---
if st.button("Save Rankings"):
    user_id = st.session_state.get("bettor_id")  # From login/auth flow
    if user_id is None:
        st.error("You must be logged in to save rankings.")
    else:
        # Build insert values: [(user_id, team_abbr, rank), ...]
        values = [(user_id, team, rank) for rank, team in enumerate(sorted_list, start=1)]

        insert_query = """
        INSERT INTO odd.draft (league, bettor_id, team_abbr, rank)
        VALUES (:league, :bettor_id, :team_abbr, :rank)
        ON CONFLICT (league, bettor_id, team_abbr)
        DO UPDATE SET rank = EXCLUDED.rank, update_dt = NOW();
        """

        for row in values:
            run_insert(insert_query, {
                "league": st.session_state["league"],
                "bettor_id": row[0],
                "team_abbr": row[1],
                "rank": row[2]
            })

        st.success("✅ Rankings saved!")


