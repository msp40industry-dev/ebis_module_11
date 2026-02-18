import base64
from datetime import datetime
import requests
from io import BytesIO
from pathlib import Path
import streamlit as st


HOST = "http://127.0.0.1:8000"


def call_backend(messages):
    endpoint = "/chat_with_history"
    url = HOST + endpoint
    input_data = {"chat_history": messages}
    response = requests.post(url, json=input_data)
    print(response)
    return response.json()['response']


def call_transcribe(wav_path: str) -> str:
    endpoint = "/transcribe"
    url = HOST + endpoint
    data = {"recording_path": wav_path}
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json().get("text", "")


def b64_to_bytesio(b64_string):
    if b64_string.startswith('data:image'):
        b64_string = b64_string.split(',')[1]
    image_bytes = base64.b64decode(b64_string)
    return BytesIO(image_bytes)


def show_message(msg):
    with chat_box:
        is_content_img = isinstance(msg["content"], list)
        msg_content = msg["content"]
        with st.chat_message(msg["role"]):
            text_content = msg_content if not is_content_img else msg_content[0]["text"]
            st.write(text_content)
            if is_content_img:
                base64_image_url = msg_content[1]["image_url"]["url"]
                image_io = b64_to_bytesio(base64_image_url)
                st.image(image_io)


# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente Python · POC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

/* ── Ocultar header y footer de Streamlit ── */
#MainMenu, header[data-testid="stHeader"], footer {
    display: none !important;
}

/* ── Layout fijo ── */
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    overflow: hidden;
}

/* ── Background ── */
.stApp {
    background-color: #0d0d0d;
    color: #e8e8e8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #2a2a2a;
}

[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}

/* ── Header principal ── */
.main-header {
    text-align: center;
    padding: 1rem 0 0.75rem 0;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 0.75rem;
}

.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin: 0;
}

.main-header h1 span {
    color: #4ade80;
}

.main-header p {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #555;
    margin-top: 0.4rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Badge POC ── */
.poc-badge {
    display: inline-block;
    background: #1a1a1a;
    border: 1px solid #4ade80;
    color: #4ade80 !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── Sidebar feature cards ── */
.feature-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #4ade80;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
}

.feature-card .feature-title {
    font-weight: 700;
    font-size: 0.85rem;
    color: #ffffff;
    margin-bottom: 0.3rem;
}

.feature-card .feature-desc {
    font-size: 0.78rem;
    color: #888;
    line-height: 1.5;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Sidebar section title ── */
.sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #444 !important;
    margin: 1.2rem 0 0.6rem 0;
}

/* ── Chat container ── */
[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
    border-radius: 6px;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 6px !important;
    margin-bottom: 0.5rem;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] div {
    color: #e8e8e8 !important;
}

/* ── Input area ── */
[data-testid="stChatInput"] {
    background: #1f1f1f !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 6px !important;
    color: #ffffff !important;
}

[data-testid="stChatInput"] input {
    color: #ffffff !important;
}

[data-testid="stChatInput"]::placeholder {
    color: #888 !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #4ade80 !important;
}

/* ── Warning/info boxes ── */
.stAlert {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e8e8 !important;
    border-radius: 4px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #4ade80; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="poc-badge">POC Interna · v0.1</div>', unsafe_allow_html=True)
    st.markdown("## 🤖 Asistente Python")
    st.markdown("Prototipo de chatbot con RAG, historial de conversación y transcripción de voz.")

    st.markdown('<div class="sidebar-section">Funcionalidades</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💬 Chat con historial</div>
        <div class="feature-desc">El modelo recuerda el contexto completo de la conversación en cada turno.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🔍 RAG sobre FAQ</div>
        <div class="feature-desc">Recupera respuestas relevantes desde una base vectorial (Pinecone Local) antes de generar.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🖼️ Soporte de imágenes</div>
        <div class="feature-desc">Adjunta capturas de código PNG y el modelo las analiza junto a tu pregunta.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🎙️ Voz a texto</div>
        <div class="feature-desc">Graba tu pregunta con el micrófono. Transcripción local con Vosk (sin enviar audio a la nube).</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Monitorización</div>
        <div class="feature-desc">Cada llamada queda registrada en MLflow: parámetros, trazas y métricas por ejecución.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Stack técnico</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #555; line-height: 2;">
        FastAPI · OpenAI GPT-4o<br>
        Pinecone Local · Vosk<br>
        MLflow · Streamlit
    </div>
    """, unsafe_allow_html=True)


# ── Topbar ───────────────────────────────────────────────────
st.markdown("""
<div style="
    background: #111;
    border-bottom: 1px solid #2a2a2a;
    padding: 0.4rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
">
    <div style="display:flex; align-items:center; gap: 0.6rem;">
        <span style="font-size:1.1rem;">🐍</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#4ade80; letter-spacing:0.1em; text-transform:uppercase;">
            Python Assistant
        </span>
    </div>
    <div style="display:flex; gap: 1.5rem; align-items:center;">
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#444; letter-spacing:0.08em;">
            RAG · VOSK · GPT-4o · MLFLOW
        </span>
        <span style="
            background:#0d2b14;
            border: 1px solid #4ade80;
            color:#4ade80;
            font-family:'JetBrains Mono',monospace;
            font-size:0.6rem;
            padding: 0.15rem 0.5rem;
            border-radius:2px;
            letter-spacing:0.1em;
        ">● LIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>Asistente de dudas sobre <span>Python</span></h1>
    <p>Prueba de concepto interna · Generación aumentada por recuperación</p>
</div>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None


# ── Chat box ──────────────────────────────────────────────────
chat_box = st.container(height=600)

with chat_box:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 0; color: #666;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🐍</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; letter-spacing: 0.1em; color: #888;">
                PREGUNTA ALGO SOBRE PYTHON
            </div>
        </div>
        """, unsafe_allow_html=True)
    for message in st.session_state.messages:
        show_message(message)


# ── Input row ─────────────────────────────────────────────────
col1, col2 = st.columns([0.10, 0.90])

with col1:
    audio_file = st.audio_input("", label_visibility="collapsed")

with col2:
    user_query = st.chat_input(
        "Escribe tu pregunta sobre Python...",
        accept_file=True,
        file_type=["png"],
    )


# ── Handle text / image input ─────────────────────────────────
if user_query:
    user_text = user_query.text if user_query.text else ""
    user_content = user_text

    if user_query["files"]:
        uploaded_file = user_query["files"][0]
        image_bytes = uploaded_file.read()
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
        user_content = [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img_b64}}
        ]

    user_message = {"role": "user", "content": user_content}
    st.session_state.messages.append(user_message)
    show_message(user_message)

    with chat_box:
        with st.spinner("Pensando..."):
            response = call_backend(st.session_state.messages)

    assistant_message = {"role": "assistant", "content": response}
    st.session_state.messages.append(assistant_message)
    show_message(assistant_message)


# ── Handle audio input ────────────────────────────────────────
if audio_file is not None and st.session_state.last_processed_audio != audio_file:
    audio_bytes = audio_file.getvalue()

    with chat_box:
        st.audio(audio_bytes, format="audio/wav")

    recordings_dir = Path("recordings")
    recordings_dir.mkdir(exist_ok=True)

    wav_path = recordings_dir / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    print(str(wav_path))

    with open(wav_path, "wb") as f:
        f.write(audio_bytes)

    with st.spinner("Transcribiendo audio..."):
        transcription = call_transcribe(str(wav_path))

    if transcription == "":
        with chat_box:
            st.warning("Necesitas hablar en el audio. Prueba otra vez.")
    else:
        user_message = {"role": "user", "content": transcription}
        st.session_state.messages.append(user_message)
        show_message(user_message)

        with chat_box:
            with st.spinner("Pensando..."):
                response = call_backend(st.session_state.messages)

        assistant_message = {"role": "assistant", "content": response}
        st.session_state.messages.append(assistant_message)
        show_message(assistant_message)

        st.session_state.last_processed_audio = audio_file