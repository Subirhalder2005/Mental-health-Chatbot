import streamlit as st
import uuid
from groq import Groq
from db import get_conn
from nlp_utils import detect_mood, is_crisis

client = Groq(api_key=None)  # reads from GROQ_API_KEY automatically
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are a calm, empathetic mental health support chatbot. "
    "Do not give medical diagnoses."
)

def new_chat():
    return str(uuid.uuid4()), {"title": "New Chat", "messages": []}

def chat_page():
    user = st.session_state.user

    if "chats" not in st.session_state:
        load_user_chats(user)

    with st.sidebar:
        st.title("🧠 Mental Health Bot")

        if st.button("➕ New Chat"):
            cid, chat = new_chat()
            st.session_state.chats[cid] = chat
            st.session_state.current_chat = cid
            save_chat(cid, user, "New Chat")
            st.rerun()

        for cid, chat in st.session_state.chats.items():
            if st.button(chat["title"], key=cid):
                st.session_state.current_chat = cid
                st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

    chat = st.session_state.chats[st.session_state.current_chat]
    st.title(chat["title"])

    for msg in chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        chat["messages"].append({"role": "user", "content": user_input})
        save_message(st.session_state.current_chat, "user", user_input)

        if chat["title"] == "New Chat":
            chat["title"] = user_input[:30] + "..."
            save_chat(st.session_state.current_chat, user, chat["title"])

        mood = detect_mood(user_input)

        if is_crisis(user_input):
            st.warning("⚠️ You are not alone. Please seek immediate help.")

        with st.chat_message("assistant"):
            response = call_llm(chat["messages"], mood)
            st.markdown(response)

        chat["messages"].append({"role": "assistant", "content": response})
        save_message(st.session_state.current_chat, "assistant", response)

def call_llm(history, mood):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"User mood: {mood}"}
    ] + history

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content


def save_chat(cid, user, title):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO chats VALUES (?, ?, ?)",
        (cid, user, title)
    )
    conn.commit()
    conn.close()

def save_message(cid, role, content):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (cid, role, content)
    )
    conn.commit()
    conn.close()

def load_user_chats(user):
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT id, title FROM chats WHERE user=?", (user,))
    chats = c.fetchall()

    st.session_state.chats = {}

    for cid, title in chats:
        c.execute(
            "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id",
            (cid,)
        )
        msgs = [{"role": r, "content": t} for r, t in c.fetchall()]
        st.session_state.chats[cid] = {"title": title, "messages": msgs}

    if chats:
        st.session_state.current_chat = chats[0][0]
    else:
        cid, chat = new_chat()
        st.session_state.chats[cid] = chat
        st.session_state.current_chat = cid
        save_chat(cid, user, "New Chat")

    conn.close()

