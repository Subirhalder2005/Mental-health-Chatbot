import streamlit as st
import hashlib
from db import get_conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email=?", (email,))
        row = c.fetchone()
        conn.close()

        if row and row[0] == hash_pw(password):
            st.session_state.user = email
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.error("Invalid credentials")

def register_page():
    st.title("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users VALUES (?, ?)",
                (email, hash_pw(password))
            )
            conn.commit()
            st.success("Account created! Please login.")
            st.session_state.page = "login"
            st.rerun()
        except:
            st.warning("User already exists")
        conn.close()
