import streamlit as st
import requests
import time

BACKEND_URL = "https://code-rag-backend.onrender.com/ask"

st.set_page_config(
    page_title="Code RAG Assistant",
    page_icon="🚀",
    layout="wide"
)

# ---------- GLOBAL CSS ----------
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
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.chat-bot {
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(10px);
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.metric-box {
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(8px);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.header {
    text-align: center;
    margin-bottom: 20px;
}

.header h1 {
    font-size: 42px;
    background: linear-gradient(90deg, #0ea5e9, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.small-text {
    font-size: 14px;
    color: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="header">
    <h1>🚀 Code RAG Assistant</h1>
    <p class="small-text">Powered by Pinecone + Groq + FastAPI</p>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("⚙ Settings")

    temperature = st.slider("Model Temperature", 0.0, 1.0, 0.3, 0.1)
    top_k = st.slider("Top-K Retrieval", 1, 10, 3)

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.session_state.token_usage = 0
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.write("Backend: 🟢 Online")
    st.write("Vector DB: Pinecone")
    st.write("Model: Groq LLM")

# ---------- SESSION ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_usage" not in st.session_state:
    st.session_state.token_usage = 0

# ---------- METRICS ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f'<div class="metric-box"><h4>Messages</h4><h2>{len(st.session_state.messages)//2}</h2></div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="metric-box"><h4>Estimated Tokens</h4><h2>{st.session_state.token_usage}</h2></div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'<div class="metric-box"><h4>Status</h4><h2>🟢 Live</h2></div>',
        unsafe_allow_html=True
    )

st.divider()

# ---------- CHAT ----------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ---------- INPUT ----------
if prompt := st.chat_input("Ask your coding question..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    start = time.time()

    with st.spinner("🧠 Thinking..."):
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

    elapsed = round(time.time() - start, 2)

    token_estimate = (len(prompt) + len(answer)) // 4
    st.session_state.token_usage += token_estimate

    final_answer = f"""
{answer}

---
⚡ Response Time: {elapsed}s  
🔢 Tokens (estimated): {token_estimate}
"""

    st.session_state.messages.append({"role": "assistant", "content": final_answer})

    st.rerun()