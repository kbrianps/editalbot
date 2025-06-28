import os
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as gpt
from functions import map_role, fetch_gemini_response, get_available_editais, salvarMensagem

st.set_page_config(
    page_title="EditalBot - UNIRIO",
    page_icon="📒",
    layout="wide",
)

load_dotenv()
# st.secrets.get("GOOGLE_API_KEY") or
API_KEY =  os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API_KEY não encontrada. Verifique o arquivo .env ou o secrets.toml.")
    st.stop()

# Configurar a API do Gemini
gpt.configure(api_key=API_KEY)
model = gpt.GenerativeModel('gemini-1.5-flash')

# Função para mapear o papel do usuário
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ===== Interface =====
# Barra superior
st.markdown("""
    <div style='background-color: #333; padding: 15px; border-radius: 10px; text-align: center; color: white; font-size: 24px;'>
        📒 EditalBot - UNIRIO
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("static/logo2.png", width=200, use_container_width="True")
st.sidebar.title("📑 Editais Disponíveis")

# Exemplo: Você pode buscar os editais de um banco de dados ou de uma função
# Adicona hardcode para fins de demonstração

editais = get_available_editais()  # Exemplo: ['Edital 001/2025', 'Edital 002/2025']

selected_edital = st.sidebar.radio("Selecione um edital para consulta:", editais)

st.sidebar.markdown("---")
st.sidebar.info("💬 Use o chat para tirar dúvidas sobre o edital selecionado!")

# dividir o espaço em duas colunas
col1, col2 = st.columns([1, 3], gap="large")

# Exibir mensagem de boas-vindas se não houver histórico
if len(st.session_state.chat_session.history) == 0:
    with st.chat_message("assistant"):
        st.markdown("👋 Olá! Eu sou o **EditalBot da UNIRIO**! Como posso te ajudar hoje? Você pode me fazer perguntas sobre editais, concursos, processos seletivos e muito mais!")

for msg in st.session_state.chat_session.history:
    with st.chat_message(map_role(msg["role"])):
        st.markdown(msg["content"])


user_input = st.chat_input("")
if user_input:
    st.chat_message("user").markdown(user_input)
    gemini_response = fetch_gemini_response(user_input)

    with st.chat_message("assistant"):
        st.markdown(gemini_response)

    st.session_state.chat_session.history.append({"role": "user", "content": user_input})
    st.session_state.chat_session.history.append({"role": "model", "content": gemini_response})

    # Salvar mensagem do usuário
    salvarMensagem(user_input)

