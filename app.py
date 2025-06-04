import os
import streamlit as st
import google.generativeai as gpt
from functions import*

st.set_page_config(
    page_title="EditalBot - UNIRIO",
    page_icon="📒",
    layout="centered",
)

st.markdown(
r"""
<style>
.stAppDeployButton {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True
)

API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

gpt.configure(api_key=API_KEY)
model = gpt.GenerativeModel('gemini-1.5-flash')

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

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