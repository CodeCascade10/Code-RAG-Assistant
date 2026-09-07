import streamlit as st
import requests
import time

import os

BACKEND_URL = st.secrets.get(
    "BACKEND_URL",
    "http://localhost:8000/ask"
)
TOKEN_LIMIT = 5000  # max tokens per session (you can change)

st.set_page_config(
    page_title="Code RAG Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-0: #05070d;
    --bg-1: #0a0e1a;
    --panel: rgba(255,255,255,0.045);
    --panel-border: rgba(255,255,255,0.08);
    --accent-a: #7c3aed;
    --accent-b: #06b6d4;
    --accent-c: #ec4899;
    --text-hi: #f1f5f9;
    --text-mid: #94a3b8;
    --text-low: #5b6577;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---------- App background ---------- */
.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(124,58,237,0.16), transparent 40%),
        radial-gradient(circle at 85% 0%, rgba(6,182,212,0.14), transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(236,72,153,0.10), transparent 50%),
        var(--bg-0);
    color: var(--text-hi);
}

/* Hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent-a), var(--accent-b));
    border-radius: 8px;
}

/* ---------- Header ---------- */
.hero {
    text-align: center;
    padding: 18px 0 8px 0;
}
.hero .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-mid);
    background: var(--panel);
    border: 1px solid var(--panel-border);
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 18px;
}
.hero .eyebrow .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 8px 2px rgba(52,211,153,0.7);
    animation: pulse 2s infinite ease-in-out;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.hero h1 {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    font-size: 46px;
    letter-spacing: -0.02em;
    margin: 0;
    background: linear-gradient(100deg, #ffffff 10%, var(--accent-b) 45%, var(--accent-a) 75%, var(--accent-c) 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 6s linear infinite;
}
@keyframes shine {
    to { background-position: 200% center; }
}
.hero p.sub {
    font-family: 'Inter', sans-serif;
    color: var(--text-mid);
    font-size: 15px;
    margin-top: 10px;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10,14,26,0.98), rgba(5,7,13,0.98));
    border-right: 1px solid var(--panel-border);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h3 {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    color: var(--text-hi);
}
.side-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-low);
    margin: 22px 0 8px 0;
}

/* ---------- Metric cards ---------- */
.metric-box {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    backdrop-filter: blur(14px);
    padding: 18px 16px;
    border-radius: 16px;
    text-align: left;
    position: relative;
    overflow: hidden;
}
.metric-box::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(124,58,237,0.10), transparent 60%);
    pointer-events: none;
}
.metric-box .label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: var(--text-mid);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-box .value {
    font-family: 'Sora', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-hi);
    margin-top: 4px;
}

/* ---------- Chat bubbles ---------- */
.chat-row {
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
    animation: fadeUp 0.35s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-row.user { flex-direction: row-reverse; }
.avatar {
    flex-shrink: 0;
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.avatar.user-av {
    background: linear-gradient(135deg, var(--accent-a), var(--accent-c));
}
.avatar.bot-av {
    background: linear-gradient(135deg, var(--accent-b), var(--accent-a));
    box-shadow: 0 0 16px rgba(6,182,212,0.35);
}
.bubble {
    max-width: 78%;
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 15px;
    line-height: 1.55;
}
.bubble.user {
    background: linear-gradient(135deg, var(--accent-a), #4f46e5);
    color: white;
    border-bottom-right-radius: 4px;
}
.bubble.bot {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    backdrop-filter: blur(14px);
    color: var(--text-hi);
    border-bottom-left-radius: 4px;
}
.bubble.bot code, .bubble.bot pre {
    font-family: 'JetBrains Mono', monospace;
}
.meta-line {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--panel-border);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-mid);
    display: flex;
    gap: 18px;
}

/* ---------- Chat input ---------- */
.stChatInput textarea, div[data-testid="stChatInput"] {
    background: var(--panel) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 16px !important;
}

/* ---------- Buttons ---------- */
.stButton button {
    background: linear-gradient(135deg, var(--accent-a), var(--accent-b)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(124,58,237,0.35);
}

/* ---------- Selectbox / progress ---------- */
div[data-baseweb="select"] > div {
    background: var(--panel) !important;
    border-color: var(--panel-border) !important;
    border-radius: 12px !important;
}
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-b), var(--accent-a)) !important;
    border-radius: 999px;
}
.stProgress > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 999px;
}

hr, div[data-testid="stDivider"] {
    border-color: var(--panel-border) !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_usage" not in st.session_state:
    st.session_state.token_usage = 0

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ✨ Code RAG")
    st.markdown('<div class="side-label">Language Mode</div>', unsafe_allow_html=True)

    language = st.selectbox(
        "Select Programming Language",
        ["All", "C", "C++", "Java", "Python"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="side-label">Session Usage</div>', unsafe_allow_html=True)
    st.progress(min(st.session_state.token_usage / TOKEN_LIMIT, 1.0))
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;font-family:JetBrains Mono, monospace;'
        f'font-size:12px;color:#94a3b8;margin-top:-6px;">'
        f'<span>{st.session_state.token_usage} used</span><span>{TOKEN_LIMIT} limit</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.token_usage >= TOKEN_LIMIT:
        st.error("Token limit reached 🚫")

    st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.token_usage = 0
        st.rerun()

# ---------------------------------------------------------------------------
# HERO HEADER
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow"><span class="dot"></span> AI-Powered Retrieval Engine</div>
        <h1>Code RAG Assistant</h1>
        <p class="sub">Ask anything about your codebase — grounded answers, instantly retrieved.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f'<div class="metric-box"><div class="label">💬 Messages</div>'
        f'<div class="value">{len(st.session_state.messages)//2}</div></div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f'<div class="metric-box"><div class="label">🟢 Status</div>'
        f'<div class="value">Live</div></div>',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f'<div class="metric-box"><div class="label">🌍 Mode</div>'
        f'<div class="value">{language}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'''
            <div class="chat-row user">
                <div class="avatar user-av">🧑‍💻</div>
                <div class="bubble user">{msg["content"]}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'''
            <div class="chat-row bot">
                <div class="avatar bot-av">✨</div>
                <div class="bubble bot">{msg["content"]}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------
if st.session_state.token_usage < TOKEN_LIMIT:
    if prompt := st.chat_input("Ask your coding question..."):

        display_prompt = prompt
        # Add language context if not "All"
        if language != "All":
            prompt = f"This question is specifically about {language}. {prompt}"

        st.session_state.messages.append({"role": "user", "content": display_prompt})

        start = time.time()

        loader = st.empty()
        loader.markdown(
            '<div class="chat-row bot"><div class="avatar bot-av">✨</div>'
            '<div class="bubble bot">🧠 Thinking<span style="opacity:.6;">...</span></div></div>',
            unsafe_allow_html=True,
        )

        try:
            response = requests.post(
                BACKEND_URL,
                json={"query": prompt},
                timeout=60,
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

        final_answer = f"""{answer}
<div class="meta-line"><span>⚡ {elapsed}s</span><span>🔢 {token_estimate} tokens</span></div>"""

        st.session_state.messages.append({"role": "assistant", "content": final_answer})

        st.rerun()
else:
    st.warning("🚫 You have reached your session token limit.")