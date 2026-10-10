import streamlit as st
import requests
import os
import base64
from dotenv import load_dotenv

# Load .env untuk local testing
load_dotenv()

# Ambil API credentials
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://rootsys.cloud/v1")

# Senarai model yang support vision
VISION_MODELS = [
    "hy3-tencent",
    "glm-5.3-flash",
    "glm-5.3-flashhx",
    "kimi-k2.7",
    "kimi-k3",
    "deepseek-v4.1-flash",
    "minimax-m3"
]

# Semua model
ALL_MODELS = [
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
]

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
8. Kalau user bagi gambar, tolong describe atau respond tentang gambar tu dalam BM.

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

st.title("💬 Kawan Sembang AI")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Tetapan")
    
    selected_model = st.selectbox(
        "🤖 Pilih Model AI",
        ALL_MODELS,
        index=0
    )
    
    # Check kalau model support vision
    is_vision = selected_model in VISION_MODELS
    
    if is_vision:
        st.success(f"✅ `{selected_model}` support gambar!")
    else:
        st.warning(f"⚠️ `{selected_model}` **TIDAK** support gambar. Upload gambar akan diabaikan.")
    
    st.divider()
    
    # Upload gambar (max 10)
    if is_vision:
        st.subheader("🖼️ Upload Gambar")
        st.caption("Max 10 gambar sekali hantar")
        
        uploaded_files = st.file_uploader(
            "Pilih gambar",
            type=["jpg", "jpeg", "png", "gif", "webp"],
            accept_multiple_files=True,
            help="Boleh pilih multiple gambar sekaligus"
        )
        
        if uploaded_files:
            if len(uploaded_files) > 10:
                st.error(f"⚠️ Max 10 gambar je! Kau pilih {len(uploaded_files)} gambar.")
                uploaded_files = uploaded_files[:10]
            
            st.session_state.uploaded_images = []
            for file in uploaded_files:
                # Convert ke base64
                file_bytes = file.read()
                file_base64 = base64.b64encode(file_bytes).decode("utf-8")
                
                # Detect content type
                content_type = file.type if file.type else "image/jpeg"
                
                st.session_state.uploaded_images.append({
                    "name": file.name,
                    "base64": file_base64,
                    "content_type": content_type
                })
            
            st.success(f"✅ {len(st.session_state.uploaded_images)} gambar sedia untuk dihantar")
    
    st.divider()
    
    temperature = st.slider(
        " Kreativiti (Temperature)",
        min_value=0.1,
        max_value=1.0,
        value=0.8,
        step=0.1
    )
    
    st.divider()
    
    if st.button("🗑️ Padam Sejarah Sembang", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.uploaded_images = []
        st.rerun()
    
    st.divider()
    st.caption(f"🔌 Endpoint: `{BASE_URL}`")
    st.caption(f" Model: `{selected_model}`")

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            content = message.get("content", "")
            if isinstance(content, list):
                # Handle vision message (list of content)
                for item in content:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"], width=300)
            else:
                st.markdown(content)

# Function to call API
def get_ai_response(prompt, model, temp, images=None):
    if not API_KEY:
        return "⚠️ API_KEY tak dijumpai. Sila check settings."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build message content
    if images and len(images) > 0:
        # Format dengan gambar (vision)
        content = [{"type": "text", "text": prompt}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['content_type']};base64,{img['base64']}"
                }
            })
        user_message = {"role": "user", "content": content}
    else:
        # Format text sahaja
        user_message = {"role": "user", "content": prompt}
    
    # Build messages list
    messages = [m for m in st.session_state.messages if m["role"] != "system"]
    messages.append(user_message)
    
    data = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "temperature": temp,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=120  # Vision model mungkin ambil masa lebih lama
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Error API: {response.status_code}\n\n{response.text}"
    except requests.exceptions.Timeout:
        return "⏰ Timeout - AI ambil masa terlalu lama. Cuba lagi."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Display uploaded images preview before sending
if st.session_state.uploaded_images:
    st.subheader("📎 Gambar Yang Akan Dihantar:")
    cols = st.columns(min(len(st.session_state.uploaded_images), 3))
    for idx, img in enumerate(st.session_state.uploaded_images):
        col_idx = idx % 3
        with cols[col_idx]:
            st.image(
                f"data:{img['content_type']};base64,{img['base64']}",
                caption=img["name"],
                width=150
            )

# Chat input
if prompt := st.chat_input("Apa cerita hari ni? Taip je kat sini..."):
    if not API_KEY:
        st.error("⚠️ API_KEY tak dijumpai!")
        st.stop()
    
    images = st.session_state.uploaded_images.copy()
    
    # Save user message with images
    if images:
        content = [{"type": "text", "text": prompt}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['content_type']};base64,{img['base64']}"
                }
            })
        st.session_state.messages.append({"role": "user", "content": content})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if images:
            for img in images:
                st.image(
                    f"data:{img['content_type']};base64,{img['base64']}",
                    width=200
                )
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Tengah fikir..."):
            response = get_ai_response(prompt, selected_model, temperature, images)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear uploaded images after sending
    st.session_state.uploaded_images = []
    
    # Limit history
    if len(st.session_state.messages) > 31:
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-30:]
    
    st.rerun()
