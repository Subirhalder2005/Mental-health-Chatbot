import streamlit as st
import base64
from openai import OpenAI

# ----------------- OpenAI Client -----------------
client = OpenAI()  # API key loaded from environment

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are a calm, empathetic mental health support chatbot.
You listen carefully, respond kindly, and never give medical diagnoses.
If the user seems in crisis, gently encourage professional help.
"""

st.set_page_config(page_title="Mental Health Chatbot", layout="centered")

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

# ---------- Session State ----------
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# ---------- Helper Function ----------
def call_llm(messages):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=350
    )
    return response.choices[0].message.content

# ---------- Chat Response ----------
def generate_response(user_input):
    st.session_state.conversation_history.append(
        {"role": "user", "content": user_input}
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.conversation_history)

    try:
        ai_response = call_llm(messages)
    except Exception as e:
        st.error("Cloud AI service unavailable. Please check your internet or API key.")
        ai_response = "Sorry — I’m having trouble connecting to the AI service right now."

    st.session_state.conversation_history.append(
        {"role": "assistant", "content": ai_response}
    )

    return ai_response

# ---------- Extra Features ----------
def generate_affirmation():
    prompt = "Give a short, kind, positive affirmation for someone feeling stressed."
    try:
        return call_llm([{"role": "user", "content": prompt}])
    except:
        return "Sorry — I can't generate an affirmation right now."

def generate_meditation_guide():
    prompt = "Write a calming 5-minute guided meditation to reduce stress."
    try:
        return call_llm([{"role": "user", "content": prompt}])
    except:
        return "Sorry — I can't generate a meditation right now."

# ---------- UI ----------
st.title("🧠 Mental Health Support Agent")

st.info(
    "⚠️ This chatbot is not a replacement for professional mental health care. "
    "If you feel unsafe or overwhelmed, please contact a mental health professional."
)

# Show chat history
for msg in st.session_state.conversation_history:
    role = "You" if msg["role"] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")

user_message = st.text_input("How can I help you today?")

if user_message:
    with st.spinner("Thinking..."):
        ai_response = generate_response(user_message)
        st.markdown(f"**AI:** {ai_response}")

# ---------- Buttons ----------
col1, col2 = st.columns(2)

with col1:
    if st.button("🌟 Give me a Positive Affirmation"):
        st.markdown(f"**Affirmation:** {generate_affirmation()}")

with col2:
    if st.button("🧘 Give me a Guided Meditation"):
        st.markdown(f"**Guided Meditation:** {generate_meditation_guide()}")
