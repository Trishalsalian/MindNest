import streamlit as st
import streamlit_authenticator as stauth
from database import conn, cursor
from datetime import date

st.set_page_config(page_title="MindNest", layout="wide")

# ================= USER TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# ================= LOAD USERS =================
def get_credentials():
    cursor.execute("SELECT username, password FROM users")
    users = cursor.fetchall()

    credentials = {"usernames": {}}

    for u in users:
        credentials["usernames"][u[0]] = {
            "name": u[0],
            "password": u[1]
        }

    return credentials


credentials = get_credentials()

authenticator = stauth.Authenticate(
    credentials,
    "mindnest_cookie",
    "abcdef",
    cookie_expiry_days=30
)

# ================= LOGIN HANDLING =================
authenticator.login(location="main")

name = st.session_state.get("name")
auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# ================= NOT LOGGED IN =================
if auth_status is None or auth_status is False:

    st.title("🌙 MindNest")

    option = st.radio("Choose Option", ["Login", "Sign Up"])

    # ---------- SIGN UP ----------
    if option == "Sign Up":

        new_username = st.text_input("Create Username")
        new_password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):

            hashed_password = stauth.Hasher([new_password]).generate()[0]

            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (new_username, hashed_password)
                )
                conn.commit()
                st.success("Account Created!")

            except:
                st.error("Username already exists")

        st.stop()

    # ---------- LOGIN FAIL ----------
    if auth_status is False:
        st.error("Wrong username or password")

    st.stop()

# ================= LOGGED IN =================
if auth_status:

    authenticator.logout("Logout", "sidebar")

    st.title(f"🌙 MindNest — Welcome {name}")

    menu = st.sidebar.radio(
        "Navigate",
        ["Diary", "To-Do", "Timetable", "Mood Tracker"]
    )

    # ================= DIARY =================
    if menu == "Diary":
        st.header("My Diary")

        diary_text = st.text_area("Write your thoughts")

        if st.button("Save Entry"):
            cursor.execute(
                "INSERT INTO diary (entry_date, content) VALUES (?, ?)",
                (str(date.today()), diary_text)
            )
            conn.commit()
            st.success("Saved!")

        cursor.execute("SELECT * FROM diary ORDER BY id DESC")
        for e in cursor.fetchall():
            st.write(f"📅 {e[1]}")
            st.write(e[2])
            st.markdown("---")

    # ================= TODO =================
    elif menu == "To-Do":
        st.header("To-Do List")

        task = st.text_input("New Task")

        if st.button("Add Task"):
            cursor.execute("INSERT INTO todo (task, completed) VALUES (?, ?)", (task, 0))
            conn.commit()

        cursor.execute("SELECT * FROM todo")
        for t in cursor.fetchall():
            col1, col2 = st.columns([8,1])

            with col1:
                checked = st.checkbox(t[1], value=bool(t[2]), key=f"todo_{t[0]}")
                cursor.execute("UPDATE todo SET completed=? WHERE id=?", (1 if checked else 0, t[0]))
                conn.commit()

            with col2:
                if st.button("❌", key=f"del_{t[0]}"):
                    cursor.execute("DELETE FROM todo WHERE id=?", (t[0],))
                    conn.commit()
                    st.rerun()

    # ================= TIMETABLE =================
    elif menu == "Timetable":
        st.header("Timetable")

        time_slot = st.text_input("Time")
        activity = st.text_input("Activity")

        if st.button("Save"):
            cursor.execute("INSERT INTO timetable (time_slot, activity) VALUES (?, ?)", (time_slot, activity))
            conn.commit()

        cursor.execute("SELECT * FROM timetable")
        for t in cursor.fetchall():
            st.write(f"{t[1]} → {t[2]}")

    # ================= MOOD =================
    elif menu == "Mood Tracker":
        st.header("Mood Tracker")

        mood = st.selectbox("Mood", ["😊 Happy", "😔 Sad", "😴 Tired", "😡 Angry"])

        if st.button("Save Mood"):
            cursor.execute("INSERT INTO mood (mood_date, mood) VALUES (?, ?)", (str(date.today()), mood))
            conn.commit()

        cursor.execute("SELECT * FROM mood ORDER BY id DESC")
        for m in cursor.fetchall():
            st.write(f"📅 {m[1]} → {m[2]}")