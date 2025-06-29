import os
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as gpt
from functions import map_role, fetch_gemini_response, get_available_editais
import re
import json
import base64
import hashlib
import secrets
from urllib.parse import urlencode
import requests

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

# Domínios permitidos da UNIRIO
ALLOWED_DOMAINS = ["edu.unirio.br", "uniriotec.br", "unirio.br"]

# Função para verificar se o email pertence a um domínio permitido
def is_allowed_domain(email):
    if not email:
        return False
    domain = email.split('@')[-1].lower()
    return domain in ALLOWED_DOMAINS

# Função para validar formato de email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Sistema de autenticação simplificado
def authenticate_user():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""

    if not st.session_state.authenticated:
        st.markdown("""
            <div style='background-color: #333; padding: 15px; border-radius: 10px; text-align: center; color: white; font-size: 24px;'>
                📒 EditalBot - UNIRIO
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔐 Acesso Restrito - Comunidade UNIRIO")
        st.info("**Este sistema é exclusivo para a comunidade acadêmica da UNIRIO.**")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("**Domínios autorizados:**")
            st.markdown("- 🎓 **@edu.unirio.br** (estudantes)")
            st.markdown("- 🔧 **@uniriotec.br** (técnicos)")
            st.markdown("- 👨‍🏫 **@unirio.br** (docentes e servidores)")
            
            st.markdown("---")
            
            # Formulário de login simplificado
            with st.form("login_form"):
                st.markdown("#### 📧 Digite seu email institucional:")
                email = st.text_input("Email", placeholder="seu.email@unirio.br")
                name = st.text_input("Nome completo", placeholder="Seu Nome Completo")
                submitted = st.form_submit_button("🔑 Acessar Sistema", use_container_width=True)
                
                if submitted:
                    if not email or not name:
                        st.error("❌ Por favor, preencha todos os campos.")
                    elif not is_valid_email(email):
                        st.error("❌ Por favor, digite um email válido.")
                    elif not is_allowed_domain(email):
                        st.error(f"❌ O email `{email}` não pertence aos domínios autorizados da UNIRIO.")
                        st.warning("Apenas emails dos domínios @edu.unirio.br, @uniriotec.br e @unirio.br são permitidos.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.success(f"✅ Bem-vindo(a), {name}!")
                        st.rerun()
        
        st.markdown("---")
        st.markdown("**� Dica:** Este é um sistema de demonstração. Em produção, seria integrado com o sistema de autenticação institucional da UNIRIO.")
        return False
    
    return True

# Verificar autenticação
if not authenticate_user():
    st.stop()

# Usuário autenticado e autorizado - continuar com a aplicação

# Configurar a API do Gemini
gpt.configure(api_key=API_KEY)
model = gpt.GenerativeModel('gemini-1.5-flash')

# ===== Interface Principal =====
# Barra superior
st.markdown("""
    <div style='background-color: #333; padding: 15px; border-radius: 10px; text-align: center; color: white; font-size: 24px;'>
        📒 EditalBot - UNIRIO
    </div>
""", unsafe_allow_html=True)

# Função para mapear o papel do usuário
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Sidebar
st.sidebar.image("logo.png", width=200, use_container_width="True")

# Informações do usuário logado
user_name = st.session_state.get('user_name', 'Usuário')
user_email = st.session_state.get('user_email', '')

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Usuário Logado")
st.sidebar.write(f"**{user_name}**")
st.sidebar.write(f"`{user_email}`")

if st.sidebar.button("🚪 Sair", type="secondary"):
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.rerun()

st.sidebar.markdown("---")
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
