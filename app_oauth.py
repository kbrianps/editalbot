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

# Configuração do Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8502")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    st.error("❌ Credenciais do Google OAuth não encontradas.")
    st.info("Configure as variáveis de ambiente:")
    st.code("""
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
REDIRECT_URI=http://localhost:8502
    """)
    st.stop()

# Domínios permitidos da UNIRIO
ALLOWED_DOMAINS = ["edu.unirio.br", "uniriotec.br", "unirio.br"]

# Função para verificar se o email pertence a um domínio permitido
def is_allowed_domain(email):
    if not email:
        return False
    domain = email.split('@')[-1].lower()
    return domain in ALLOWED_DOMAINS

def generate_auth_url():
    """Gera a URL de autenticação do Google OAuth"""
    state = secrets.token_urlsafe(32)
    st.session_state.oauth_state = state
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'select_account',
        'hd': 'unirio.br,edu.unirio.br,uniriotec.br'  # Restringe aos domínios da UNIRIO
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(code, state):
    """Troca o código de autorização por um token de acesso"""
    if st.session_state.get('oauth_state') != state:
        st.error("❌ Estado OAuth inválido. Tente novamente.")
        return None
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"❌ Erro ao trocar código por token: {str(e)}")
        return None

def get_user_info(access_token):
    """Obtém informações do usuário usando o token de acesso"""
    user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
    
    try:
        response = requests.get(user_info_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"❌ Erro ao obter informações do usuário: {str(e)}")
        return None

def authenticate_with_google():
    """Sistema de autenticação com Google OAuth"""
    
    # Verificar se já está autenticado
    if st.session_state.get('authenticated', False):
        return True
    
    # Verificar se há um código de autorização na URL
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']
        
        # Trocar código por token
        token_data = exchange_code_for_token(code, state)
        
        if token_data and 'access_token' in token_data:
            # Obter informações do usuário
            user_info = get_user_info(token_data['access_token'])
            
            if user_info:
                email = user_info.get('email', '')
                name = user_info.get('name', '')
                
                # Verificar se o email é de um domínio permitido
                if is_allowed_domain(email):
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = name
                    st.session_state.user_picture = user_info.get('picture', '')
                    
                    # Limpar parâmetros da URL
                    st.query_params.clear()
                    st.success(f"✅ Bem-vindo(a), {name}!")
                    st.rerun()
                else:
                    st.error("❌ **Acesso Negado**")
                    st.warning(f"O email `{email}` não pertence aos domínios autorizados da UNIRIO.")
                    st.info("Apenas emails dos domínios @edu.unirio.br, @uniriotec.br e @unirio.br são permitidos.")
                    
                    if st.button("🔄 Tentar Novamente"):
                        st.query_params.clear()
                        st.rerun()
                    return False
        
        # Se chegou aqui, houve erro na autenticação
        st.error("❌ Erro na autenticação. Tente novamente.")
        if st.button("🔄 Tentar Novamente"):
            st.query_params.clear()
            st.rerun()
        return False
    
    # Mostrar tela de login
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
        
        # Botão de login com Google
        auth_url = generate_auth_url()
        
        google_login_html = f"""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    background-color: #4285f4;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 16px;
                    transition: background-color 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <svg style="margin-right: 12px;" width="20" height="20" viewBox="0 0 24 24">
                        <path fill="white" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="white" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="white" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="white" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Entrar com Google
                </div>
            </a>
        </div>
        """
        
        components.html(google_login_html, height=80)
    
    st.markdown("---")
    st.markdown("**🔒 Segurança:** Utilizamos OAuth 2.0 do Google para garantir a segurança dos seus dados.")
    return False

# Verificar autenticação
if not authenticate_with_google():
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
user_picture = st.session_state.get('user_picture', '')

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Usuário Logado")

# Mostrar foto do usuário se disponível
if user_picture:
    st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <img src="{user_picture}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;">
        <div>
            <strong>{user_name}</strong><br>
            <small>{user_email}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.write(f"**{user_name}**")
    st.sidebar.write(f"`{user_email}`")

if st.sidebar.button("🚪 Sair", type="secondary"):
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.user_picture = ""
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
