import os
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as gpt
from functions import map_role, fetch_gemini_response, get_available_editais, register_user_login, end_user_session, save_user_message
import re
import json
import base64
import hashlib
import secrets
from urllib.parse import urlencode
import requests
import tempfile
import time

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

# Lista de administradores autorizados
ADMIN_EMAILS = [
    "brianpravato@edu.unirio.br",
    "victormalvao15@edu.unirio.br", 
    "matheusgazitua@edu.unirio.br",
    "pedro.l.nascimento@edu.unirio.br"
]

# Função para verificar se o email pertence a um domínio permitido
def is_allowed_domain(email):
    if not email:
        return False
    domain = email.split('@')[-1].lower()
    return domain in ALLOWED_DOMAINS

def is_admin_user(email):
    """Verifica se o usuário é um administrador autorizado"""
    return email.lower() in [admin.lower() for admin in ADMIN_EMAILS]

def save_oauth_state(state):
    """Salva o estado OAuth em um arquivo temporário"""
    temp_dir = tempfile.gettempdir()
    state_file = os.path.join(temp_dir, f"streamlit_oauth_state_{state}.txt")
    try:
        with open(state_file, 'w') as f:
            f.write(f"{time.time()},{state}")
        return state_file
    except Exception as e:
        st.error(f"❌ Erro ao salvar estado OAuth: {str(e)}")
        return None

def validate_oauth_state(state):
    """Valida o estado OAuth verificando se existe e não expirou"""
    if not state:
        return False
        
    temp_dir = tempfile.gettempdir()
    state_file = os.path.join(temp_dir, f"streamlit_oauth_state_{state}.txt")
    
    if not os.path.exists(state_file):
        return False
    
    try:
        with open(state_file, 'r') as f:
            content = f.read().strip()
            if ',' not in content:
                # Formato antigo, remover arquivo
                os.remove(state_file)
                return False
            
            timestamp_str, saved_state = content.split(',', 1)
            timestamp = float(timestamp_str)
        
        # Verificar se o state bate
        if saved_state != state:
            os.remove(state_file)
            return False
        
        # Verificar se não expirou (15 minutos)
        if time.time() - timestamp > 900:
            os.remove(state_file)
            return False
        
        # Remover arquivo após validação bem-sucedida
        os.remove(state_file)
        return True
    except Exception as e:
        # Em caso de erro, remover arquivo e retornar False
        try:
            if os.path.exists(state_file):
                os.remove(state_file)
        except:
            pass
        return False

def generate_auth_url():
    """Gera a URL de autenticação do Google OAuth"""
    state = secrets.token_urlsafe(32)
    
    # Salvar estado em arquivo temporário
    save_oauth_state(state)
    
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
    if not validate_oauth_state(state):
        st.error("❌ Estado OAuth inválido ou expirado. Tente novamente.")
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
                    
                    # Registrar usuário no banco de dados
                    register_user_login(email, name, user_info.get('picture', ''))
                    
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
        
        st.markdown("#### 🔐 Fazer Login")
        st.markdown("Clique no botão abaixo para fazer login com sua conta Google institucional:")
        
        # Link estilizado como botão vermelho
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    background-color: #ff4b4b;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 16px;
                    transition: background-color 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    cursor: pointer;
                ">
                    🔑 Entrar com Google
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações sobre o processo
        st.info("💡 **Como funciona:** Você será redirecionado para o Google, fará login com sua conta institucional da UNIRIO, e retornará automaticamente para o EditalBot.")
    
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
    # Finalizar sessão no banco de dados
    end_user_session()
    
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

# Admin access - apenas para usuários autorizados
current_user_email = st.session_state.get('user_email', '')

if is_admin_user(current_user_email):
    st.sidebar.markdown("---")
    st.sidebar.success("🔧 **Admin Access Available**")
    
    # Inicializar admin_mode se não existir
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False
    
    # Botão toggle profissional com cores customizadas
    current_mode = st.session_state.get('admin_mode', False)
    
    if current_mode:
        # Admin mode ativo - botão vermelho para desativar
        st.sidebar.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #ff4b4b;
            color: white;
            border: none;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🔴 Admin Mode ACTIVE", 
                           use_container_width=True,
                           help="Click to disable admin mode"):
            st.session_state.admin_mode = False
            st.rerun()
    else:
        # Admin mode inativo - botão verde para ativar
        st.sidebar.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #00cc00;
            color: white;
            border: none;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🟢 Admin Mode INACTIVE", 
                           use_container_width=True,
                           help="Click to enable admin mode"):
            st.session_state.admin_mode = True
            st.rerun()
else:
    # Se não é admin, garantir que admin_mode está desabilitado
    st.session_state.admin_mode = False

# Check if admin mode is enabled
if st.session_state.get('admin_mode', False):
    # Import and show admin dashboard
    from admin import show_admin_page
    show_admin_page()
    st.stop()  # Para não mostrar o chat quando em modo admin

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

    # Salvar mensagem no banco de dados
    save_user_message(user_input, gemini_response, selected_edital)

    st.session_state.chat_session.history.append({"role": "user", "content": user_input})
    st.session_state.chat_session.history.append({"role": "model", "content": gemini_response})
