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
summary_query = """
select 
	a.draftor as "LEAGUE TEAM"
	,SUM(case when a.won then 1 else 0 end) as WINS
	,SUM(case when not a.won then 1 else 0 end) as LOSSES
    --,COUNT(*) as Games
	,SUM(a.team) * 1.0 / COUNT(*) as "Avg Points Off"
	,SUM(a.opp) * 1.0 / COUNT(*) as "Avg Points Def"
from odd.golden_sched a
where current_date > a.game_dt
group by a.draftor;
"""

summary_team_query = """
select
    A.team_abbr as "NFL TEAM"
	,a.draftor as "LEAGUE TEAM"
	,SUM(case when a.won then 1 else 0 end) as WINS
	,SUM(case when not a.won then 1 else 0 end) as LOSSES
    --,COUNT(*) as Games
	,SUM(a.team) * 1.0 / COUNT(*) as "Avg Points Off"
	,SUM(a.opp) * 1.0 / COUNT(*) as "Avg Points Def"
from odd.golden_sched a
where current_date > a.game_dt
group by a.draftor, A.team_abbr;
"""

this_week_query = """
select g.game_dt, g.draftor as home, g.opp_draftor as away, g.team_abbr || ' @ ' || g.opp_abbr as game
from odd.golden_sched g
join ball.sched s on g.sched_id = s.sched_id
join ball.week w on s.week_id = w.week_id
where current_date between w.week_start_dt and w.week_end_dt
    and s.home = true;
"""

last_week_query = """
select g.game_dt, g.draftor as home, g.opp_draftor as away, g.team_abbr || ' @ ' || g.opp_abbr as game, s.team, s.opp
from odd.golden_sched g
join ball.sched s on g.sched_id = s.sched_id
join ball.week w on s.week_id = w.week_id
where current_date - 7 between w.week_start_dt and w.week_end_dt
    and s.home = true;
"""

##############################################
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

    if "summary" not in st.session_state:
        st.session_state["summary"] = run_query(
            summary_query
        )
    if "summaryteam" not in st.session_state:
        st.session_state["summaryteam"] = run_query(
            summary_team_query
        )
        


    if "thisweek" not in st.session_state:
        st.session_state["thisweek"] = run_query(
            this_week_query        )

    if "lastweek" not in st.session_state:
        st.session_state["lastweek"] = run_query(
            last_week_query        )


    st.title(f"League Standing")
    st.dataframe(st.session_state["summary"])
    st.dataframe(st.session_state["summaryteam"])
    st.header(f"This Week's Games")
    st.dataframe(st.session_state["thisweek"])
    st.header(f"Last Week's Games")
    st.dataframe(st.session_state["lastweek"])
