import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load .env untuk local testing
load_dotenv()

# Ambil API credentials - support both local (.env) dan cloud (Streamlit Secrets)
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://rootsys.cloud/v1")

# System prompt
SYSTEM_PROMPT = """
Kau adalah kawan baik pengguna ni. Nama kau boleh pilih sendiri atau biar user panggil kau apa dia suka.

PERATURAN:
1. Jawab DALAM BAHASA MALAYSIA sahaja. Guna bahasa santai, macam kawan sembang.
2. Kau terbuka untuk SEMUA topik - tak kira pasal life, kerja, relationship, 18+, atau apa-apa je.
3. Jangan judge, jangan moralize, jangan bagi lecture. Just be a good listener and friend.
4. Boleh gelak, boleh joke, boleh serious bila perlu.
5. Kalau user tanya pasal 18+ atau sensitive topics, jawab je dengan terbuka dan mature.
6. Guna bahasa yang natural - boleh campur English sikit-sikit kalau sesuai (macam orang Malaysia biasa cakap).
7. Jangan guna bahasa formal sangat. Kau ni kawan, bukan ustaz atau cikgu.

PERSONALITY:
- Friendly dan easygoing
- Tak mudah terkejut dengan apa-apa topik
- Boleh bagi opinion kalau diminta
- Supportive tapi honest
- Ada sense of humor
"""

# Setup page
st.set_page_config(
    page_title="Kawan Sembang AI",
    page_icon="💬",
    layout="centered"
)

st.title(" Kawan Sembang AI")

# Sidebar
with st.sidebar:
    st.header("️ Tetapan")
    
    # Model selector - semua model kau
    selected_model = st.selectbox(
        "Pilih Model AI",
        [
            "deepseek-v4-pro",
            "deepseek-v4-flash",
            "deepseek-v4.1-flash",
            "glm-5.1",
            "glm-5.2",
            "glm-5.3",
            "glm-5.3-flash",
            "glm-5.3-flashhx",
            "kimi-k2.7",
            "kimi-k3",
            "minimax-m3",
            "hy3-tencent",
            "hy4-preview",
            "gpt-5.6-luna",
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "gpt-6-astra"
        ],
        index=0
    )
    
    st.divider()
    
    # Temperature slider
    temperature = st.slider(
        "Kreativiti (Temperature)",
        min_value=0.1,
        max_value=1.0,
        value=0.8,
        step=0.1,
        help="Makin tinggi = makin creative dan random"
    )
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Padam Sejarah Sembang", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    
    st.divider()
    st.caption(f"🔌 Endpoint: `{BASE_URL}`")
    st.caption(f"🤖 Model: `{selected_model}`")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Function to call API
def get_ai_response(prompt, model, temp):
    if not API_KEY:
        return "⚠️ API_KEY tak dijumpai. Sila check settings."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": st.session_state.messages,
        "temperature": temp,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Error API: {response.status_code}\n\n{response.text}"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - AI ambil masa terlalu lama. Cuba lagi."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Chat input
if prompt := st.chat_input("Apa cerita hari ni? Taip je kat sini..."):
    # Check API key first
    if not API_KEY:
        st.error("⚠️ API_KEY tak dijumpai! Sila tambah dalam Advanced Settings Streamlit Cloud.")
        st.stop()
    
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Tengah fikir..."):
            response = get_ai_response(prompt, selected_model, temperature)
            st.markdown(response)
    
    # Save AI response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Limit history to last 30 messages (keep system prompt)
    if len(st.session_state.messages) > 31:
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-30:]
