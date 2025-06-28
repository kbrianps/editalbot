import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role

def fetch_gemini_response(user_query):
    response = st.session_state.chat_session.model.generate_content(user_query)
    return response.parts[0].text

def get_available_editais():
    # Aqui você pode implementar a lógica para buscar os editais de um banco de dados ou API
    # Por enquanto, vamos usar uma lista fixa como exemplo
    return ['Edital 001/2025', 'Edital 002/2025', 'Edital 003/2025']    

supabase: Client = create_client(url, key)

def salvarMensagem(texto):
    data = {
        "message": texto
    }
    print("Enviando para o Supabase",data)
    resposta = supabase.table("messages").insert(data).execute()
    return resposta
