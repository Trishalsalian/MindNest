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
def get_users():
    cursor.execute("SELECT username, password FROM users")
    users = cursor.fetchall()

    credentials = {"usernames": {}}

    for user in users:
        credentials["usernames"][user[0]] = {
            "name": user[0],
            "password": user[1]
        }

    return credentials


credentials = get_users()

# ================= AUTH =================
authenticator = stauth.Authenticate(
    credentials,
    "mindnest_cookie",
    "abcdef",
    cookie_expiry_days=30
)

name, auth_status, username = authenticator.login(location="main")

# ================= SIGN UP UI =================
if not auth_status:

    st.title("🌙 MindNest")

    auth_mode = st.radio("Choose Option", ["Login", "Sign Up"])

    if auth_mode == "Sign Up":

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
                st.error("Username already exists.")

        st.stop()

# ================= LOGIN FAIL =================
if auth_status is False:
    st.error("Incorrect username or password")
    st.stop()

# ================= LOGIN SUCCESS =================
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
            st.success("Entry Saved!")

        st.subheader("Previous Entries")

        cursor.execute("SELECT * FROM diary ORDER BY id DESC")
        entries = cursor.fetchall()

        for entry in entries:
            col1, col2 = st.columns([8,1])

            with col1:
                st.write(f"📅 {entry[1]}")
                st.write(entry[2])

            with col2:
                if st.button("❌", key=f"diary_{entry[0]}"):
                    cursor.execute("DELETE FROM diary WHERE id=?", (entry[0],))
                    conn.commit()
                    st.rerun()

            st.markdown("---")

    # ================= TODO =================
    elif menu == "To-Do":
        st.header("To-Do List")

        task = st.text_input("New Task")

        if st.button("Add Task"):
            cursor.execute(
                "INSERT INTO todo (task, completed) VALUES (?, ?)",
                (task, 0)
            )
            conn.commit()

        cursor.execute("SELECT * FROM todo")
        tasks = cursor.fetchall()

        for t in tasks:
            col1, col2 = st.columns([8,1])

            with col1:
                checked = st.checkbox(
                    t[1],
                    value=bool(t[2]),
                    key=f"todo_{t[0]}"
                )

                cursor.execute(
                    "UPDATE todo SET completed=? WHERE id=?",
                    (1 if checked else 0, t[0])
                )
                conn.commit()

            with col2:
                if st.button("❌", key=f"delete_{t[0]}"):
                    cursor.execute("DELETE FROM todo WHERE id=?", (t[0],))
                    conn.commit()
                    st.rerun()

    # ================= TIMETABLE =================
    elif menu == "Timetable":
        st.header("Daily Timetable")

        time_slot = st.text_input("Time")
        activity = st.text_input("Activity")

        if st.button("Save Timetable"):
            cursor.execute(
                "INSERT INTO timetable (time_slot, activity) VALUES (?, ?)",
                (time_slot, activity)
            )
            conn.commit()

        cursor.execute("SELECT * FROM timetable")
        timetable = cursor.fetchall()

        for t in timetable:
            col1, col2 = st.columns([8,1])

            with col1:
                st.write(f"{t[1]} → {t[2]}")

            with col2:
                if st.button("❌", key=f"tt_{t[0]}"):
                    cursor.execute("DELETE FROM timetable WHERE id=?", (t[0],))
                    conn.commit()
                    st.rerun()

    # ================= MOOD =================
    elif menu == "Mood Tracker":
        st.header("Mood Tracker")

        mood = st.selectbox(
            "Today's Mood",
            ["😊 Happy", "😔 Sad", "😴 Tired", "😡 Angry"]
        )

        if st.button("Save Mood"):
            cursor.execute(
                "INSERT INTO mood (mood_date, mood) VALUES (?, ?)",
                (str(date.today()), mood)
            )
            conn.commit()
            st.success("Mood Saved!")

        st.subheader("Mood History")

        cursor.execute("SELECT * FROM mood ORDER BY id DESC")
        moods = cursor.fetchall()

        for m in moods:
            col1, col2 = st.columns([8,1])

            with col1:
                st.write(f"📅 {m[1]} → {m[2]}")

            with col2:
                if st.button("❌", key=f"mood_{m[0]}"):
                    cursor.execute("DELETE FROM mood WHERE id=?", (m[0],))
                    conn.commit()
                    st.rerun()