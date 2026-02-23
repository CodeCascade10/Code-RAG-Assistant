import streamlit as st
import requests
import time

# ----------------------------------
# 🔗 BACKEND URL (CHANGE THIS)
# ----------------------------------
BACKEND_URL = "https://your-backend-name.onrender.com"

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="Code RAG Assistant",
    page_icon="💻",
    layout="wide"
)

# ----------------------------------
# Custom Styling
# ----------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 16px;
    color: #9ca3af;
    margin-bottom: 25px;
}

.token-box {
    background-color: #1f2937;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Sidebar
# ----------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    language = st.selectbox(
        "Select Language",
        ["All", "Python", "C++", "Java", "SQL"]
    )

    st.markdown("### 🤖 Model Info")
    st.markdown("""
    - Embedding: MiniLM-L6-v2  
    - Vector DB: Pinecone  
    - LLM: Llama-3.1-8B (Groq)  
    """)

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.session_state.token_count = 0
        st.rerun()

# ----------------------------------
# Title
# ----------------------------------
st.markdown('<div class="main-title">💻 Code RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask programming-related questions only.</div>', unsafe_allow_html=True)

# ----------------------------------
# Session State
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_count" not in st.session_state:
    st.session_state.token_count = 0

# ----------------------------------
# Display Chat History
# ----------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------
# Chat Input
# ----------------------------------
if prompt := st.chat_input("Ask a programming question..."):

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.token_count += len(prompt.split())

    # Call Backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"query": prompt},
                    timeout=60
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]
                else:
                    answer = "⚠️ Backend returned an error."

            except Exception as e:
                answer = f"⚠️ Could not connect to backend.\n\n{e}"

        # Streaming Animation
        streamed_text = ""
        placeholder = st.empty()

        for word in answer.split():
            streamed_text += word + " "
            time.sleep(0.02)
            placeholder.markdown(streamed_text)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.session_state.token_count += len(answer.split())

# ----------------------------------
# Token Counter
# ----------------------------------
st.markdown("---")
st.markdown(
    f'<div class="token-box">Approx Tokens Used: {st.session_state.token_count}</div>',
    unsafe_allow_html=True
)