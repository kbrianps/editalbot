# 🤖 EditalBot - UNIRIO

Este é um chatbot baseado em LLM (Large Language Model), desenvolvido com **Gemini 1.5 Flash** e uma interface web usando **Streamlit**. Seu objetivo é **ajudar alunos da UNIRIO a ler e compreender editais acadêmicos** de maneira simples e acessível.

## � Autenticação

**Acesso Restrito à Comunidade UNIRIO**

O EditalBot possui autenticação integrada com Google OAuth, permitindo acesso apenas para usuários com emails dos domínios oficiais da UNIRIO:

- **@edu.unirio.br** (estudantes)
- **@uniriotec.br** (técnicos)
- **@unirio.br** (docentes e servidores)

## �📚 Funcionalidades

- 🔐 **Autenticação Google OAuth** com restrição de domínio
- 📄 Upload de editais em PDF  
- 💬 Perguntas e respostas em linguagem natural  
- 🔍 Explicações simplificadas sobre regras, prazos e documentos exigidos  
- 🧠 Baseado no modelo LLM Gemini 1.5 Flash (Google AI)

---

## 🚀 Como executar o projeto

### Pré-requisitos

- Python 3.9 ou superior  
- API key do **Gemini 1.5 Flash** (via Google AI Studio)
- **Google OAuth App** configurado no Google Cloud Console
- Ambiente virtual (recomendado)

### Configuração do Google OAuth

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google+ API** ou **People API**
4. Vá para **APIs & Services > Credentials**
5. Clique em **Create Credentials > OAuth 2.0 Client IDs**
6. Configure:
   - **Application type**: Web application
   - **Authorized redirect URIs**: `http://localhost:8500` (ou sua URL de produção)
7. Anote o **Client ID** e **Client Secret**

### Instalação

```bash
git clone https://github.com/kbrianps/chatbot-unirio-editais.git
cd chatbot-unirio-editais
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuração das Variáveis de Ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e configure as variáveis:
```bash
# Google API Key para o Gemini
GOOGLE_API_KEY=sua_api_key_do_gemini_aqui

# Google OAuth Credentials
GOOGLE_CLIENT_ID=seu_client_id_do_google_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_do_google_aqui

# Redirect URI (deve corresponder ao configurado no Google Console)
REDIRECT_URI=http://localhost:8500
```

### Executar o Projeto

```bash
streamlit run app.py --server.port 8500
```

O aplicativo estará disponível em: `http://localhost:8500`

---

## 🔒 Segurança

- **Autenticação OAuth 2.0**: Integração segura com Google
- **Restrição de Domínio**: Apenas emails da UNIRIO são permitidos
- **Validação de Estado**: Proteção contra ataques CSRF
- **Tokens Seguros**: Gerenciamento seguro de tokens de acesso

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **Streamlit** - Interface web
- **Google Generative AI (Gemini)** - Modelo de linguagem
- **Google OAuth 2.0** - Autenticação
- **python-dotenv** - Gerenciamento de variáveis de ambiente

---

## 📝 Licença

Este projeto está sob a licença MIT.
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
