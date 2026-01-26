import streamlit as st
import base64
from db import init_db
from auth import login_page, register_page
from chat import chat_page

st.set_page_config(page_title="Mental Health Companion")

init_db()

if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login_page()
    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()

elif st.session_state.page == "register":
    register_page()

elif st.session_state.page == "chat":
    chat_page()

# ---------- Background Image ----------
def get_base64(background):
    with open(background, "rb") as f:
        return base64.b64encode(f.read()).decode()

bin_str = get_base64("background.png")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
