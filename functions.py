import streamlit as st

def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role

def fetch_gemini_response(user_query):
    response = st.session_state.chat_session.model.generate_content(user_query)
    return response.parts[0].text