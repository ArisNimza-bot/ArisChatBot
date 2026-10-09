import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load API key dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# System prompt untuk AI kau
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
st.set_page_config(page_title="Kawan Sembang AI", page_icon="💬", layout="centered")
st.title(" Kawan Sembang AI")

# Sidebar untuk pilih model dan settings
with st.sidebar:
    st.header("⚙️ Tetapan")
    
    # Dropdown pilih model
    selected_model = st.selectbox(
        "Pilih Model AI",
        ["deepseek-v4-pro", "glm-5.3", "minimax-m3"],
        index=0
    )
    
    st.divider()
    
    # Butang clear chat
    if st.button("️ Padam Sejarah Sembang", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
        
    st.caption(f"API Endpoint: `{BASE_URL}`")

# Initialize chat history dalam session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Paparkan sejarah chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Fungsi untuk call API
def get_ai_response(prompt, model):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": st.session_state.messages,
        "temperature": 0.8,
        "max_tokens": 1000
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Error API: {response.status_code} - {response.text}"

# Chat input box
if prompt := st.chat_input("Apa cerita hari ni? Taip je kat sini..."):
    # Simpan message user
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call AI dan paparkan response
    with st.chat_message("assistant"):
        with st.spinner("Tengah fikir..."):
            response = get_ai_response(prompt, selected_model)
            st.markdown(response)
            
    # Simpan message AI
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Limit history supaya tak berat sangat (last 30 messages)
    if len(st.session_state.messages) > 30:
        # Keep system prompt + last 30 messages
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-30:]