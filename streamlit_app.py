import streamlit as st
import requests
import time

BACKEND_URL = "https://code-rag-backend.onrender.com/ask"
TOKEN_LIMIT = 5000  # max tokens per session (you can change)

st.set_page_config(
    page_title="Code RAG Assistant",
    page_icon="🚀",
    layout="wide"
)

# ---------- CSS ----------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #111827);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
    color: #e2e8f0;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.chat-user {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    color: white;
}

.chat-bot {
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(10px);
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
}

.metric-box {
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(8px);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
}

.header h1 {
    text-align: center;
    font-size: 42px;
    background: linear-gradient(90deg, #0ea5e9, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="header"><h1>🚀 Code RAG Assistant</h1></div>', unsafe_allow_html=True)

# ---------- SESSION ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_usage" not in st.session_state:
    st.session_state.token_usage = 0

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🌍 Language Mode")

    language = st.selectbox(
        "Select Programming Language",
        ["All", "C", "C++", "Java", "Python"]
    )

    st.markdown("---")
    st.title("📊 Usage")

    st.progress(min(st.session_state.token_usage / TOKEN_LIMIT, 1.0))

    st.write(f"Used: {st.session_state.token_usage}")
    st.write(f"Limit: {TOKEN_LIMIT}")

    if st.session_state.token_usage >= TOKEN_LIMIT:
        st.error("Token limit reached 🚫")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.session_state.token_usage = 0
        st.rerun()

# ---------- METRICS ----------
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f'<div class="metric-box"><h4>Messages</h4><h2>{len(st.session_state.messages)//2}</h2></div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="metric-box"><h4>Status</h4><h2>🟢 Live</h2></div>',
        unsafe_allow_html=True
    )

st.divider()

# ---------- CHAT HISTORY ----------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ---------- INPUT ----------
if st.session_state.token_usage < TOKEN_LIMIT:
    if prompt := st.chat_input("Ask your coding question..."):

        # Add language context if not "All"
        if language != "All":
            prompt = f"This question is specifically about {language}. {prompt}"

        st.session_state.messages.append({"role": "user", "content": prompt})

        start = time.time()

        loader = st.empty()
        loader.markdown("🧠 AI is thinking...")

        try:
            response = requests.post(
                BACKEND_URL,
                json={"query": prompt},
                timeout=60
            )

            if response.status_code == 200:
                answer = response.json().get("answer", "No response.")
            else:
                answer = f"Error {response.status_code}"

        except Exception as e:
            answer = f"Connection error: {e}"

        loader.empty()

        elapsed = round(time.time() - start, 2)

        token_estimate = (len(prompt) + len(answer)) // 4
        st.session_state.token_usage += token_estimate

        final_answer = f"""
{answer}

---
⚡ Response Time: {elapsed}s  
🔢 Tokens used: {token_estimate}
"""

        st.session_state.messages.append({"role": "assistant", "content": final_answer})

        st.rerun()
else:
    st.warning("🚫 You have reached your session token limit.")