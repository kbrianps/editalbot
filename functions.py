import streamlit as st

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