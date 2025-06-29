# Configuração do Google OAuth para o EditalBot

Este documento explica como configurar a autenticação Google OAuth para restringir o acesso apenas aos domínios da UNIRIO.

## 📋 Pré-requisitos

1. Conta do Google (preferencialmente institucional da UNIRIO)
2. Acesso ao [Google Cloud Console](https://console.cloud.google.com/)

## 🔧 Configuração do Google Cloud Console

### Passo 1: Criar/Selecionar Projeto

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o nome do projeto

### Passo 2: Habilitar APIs

1. No menu lateral, vá para **APIs & Services > Library**
2. Procure e habilite as seguintes APIs:
   - **Google+ API** (ou **People API**)
   - **Google OAuth2 API**

### Passo 3: Configurar OAuth Consent Screen

1. Vá para **APIs & Services > OAuth consent screen**
2. Escolha **Internal** se for para uso dentro da organização UNIRIO
3. Preencha as informações obrigatórias:
   - **App name**: EditalBot UNIRIO
   - **User support email**: seu.email@unirio.br
   - **Developer contact information**: seu.email@unirio.br
4. Clique em **Save and Continue**

### Passo 4: Criar Credenciais OAuth

1. Vá para **APIs & Services > Credentials**
2. Clique em **+ CREATE CREDENTIALS**
3. Selecione **OAuth 2.0 Client IDs**
4. Configure:
   - **Application type**: Web application
   - **Name**: EditalBot UNIRIO
   - **Authorized JavaScript origins**: 
     - `http://localhost:8500` (desenvolvimento)
     - `https://seu-dominio.com` (produção)
   - **Authorized redirect URIs**:
     - `http://localhost:8500` (desenvolvimento)
     - `https://seu-dominio.com` (produção)

5. Clique em **CREATE**
6. **ANOTE** o **Client ID** e **Client Secret**

## 🔐 Configuração das Variáveis de Ambiente

### Método 1: Arquivo .env (Recomendado para desenvolvimento)

1. No diretório do projeto, edite o arquivo `.env`:

```bash
# Google API Key para o Gemini
GOOGLE_API_KEY=sua_api_key_do_gemini_aqui

# Google OAuth Credentials
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui

# Redirect URI (deve corresponder ao configurado no Google Console)
REDIRECT_URI=http://localhost:8500
```

### Método 2: Streamlit Secrets (Recomendado para produção)

1. Crie o arquivo `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "sua_api_key_do_gemini_aqui"
GOOGLE_CLIENT_ID = "seu_client_id_aqui"
GOOGLE_CLIENT_SECRET = "seu_client_secret_aqui"
REDIRECT_URI = "http://localhost:8500"
```

## 🚀 Testando a Configuração

1. Execute o aplicativo:
```bash
streamlit run app.py --server.port 8500
```

2. Acesse `http://localhost:8500`

3. Você deve ver a tela de login com o botão "Entrar com Google"

4. Clique no botão e faça login com uma conta dos domínios permitidos:
   - @edu.unirio.br
   - @uniriotec.br  
   - @unirio.br

## 🔍 Solução de Problemas

### Erro "redirect_uri_mismatch"
- Verifique se a URI de redirecionamento no Google Console corresponde exatamente à configurada no `.env`

### Erro "access_denied"
- Verifique se o email usado pertence aos domínios permitidos da UNIRIO
- Confirme se o OAuth consent screen está configurado corretamente

### Erro "invalid_client"
- Verifique se o Client ID e Client Secret estão corretos
- Confirme se as credenciais não expiraram

## 🛡️ Segurança

### Restrições Implementadas

1. **Domínios Permitidos**: Apenas emails @edu.unirio.br, @uniriotec.br, @unirio.br
2. **Validação de Estado**: Proteção contra ataques CSRF
3. **Tokens Seguros**: Gerenciamento seguro de tokens OAuth
4. **Hosted Domain**: Parâmetro `hd` no OAuth para restringir organizações

### Boas Práticas

- ✅ Nunca compartilhe o Client Secret
- ✅ Use HTTPS em produção
- ✅ Configure domínios autorizados no Google Console
- ✅ Monitore logs de acesso
- ✅ Revogue credenciais comprometidas imediatamente

## 📞 Suporte

Para problemas relacionados à autenticação ou configuração, entre em contato com a equipe de TI da UNIRIO ou consulte a documentação oficial do Google OAuth 2.0.
