import streamlit as st
from database import db

def map_role(role):
    if role == "model":
        return "assistant"
    else:
        return role

def fetch_gemini_response(user_query):
    response = st.session_state.chat_session.model.generate_content(user_query)
    return response.parts[0].text

def get_available_notices():
    # Changed from 'editais' to 'notices' as requested
    # Here you can implement the logic to fetch notices from database or API
    # For now, using a fixed list as example
    return ['Notice 001/2025', 'Notice 002/2025', 'Notice 003/2025']

def save_user_message(user_message: str, bot_response: str, notice_context: str = None):
    """Save user message and bot response to database"""
    if 'user_id' in st.session_state:
        db.save_message(
            user_id=st.session_state.user_id,
            user_message=user_message,
            bot_response=bot_response,
            notice_context=notice_context
        )

def register_user_login(email: str, name: str, profile_picture_url: str = None):
    """Register user login in database"""
    user = db.get_or_create_user(email, name, profile_picture_url)
    if user:
        st.session_state.user_id = user['id']
        st.session_state.user_db_info = user
        
        # Create session
        session_id = db.create_session(user['id'])
        st.session_state.session_id = session_id
        
        return user
    return None

def end_user_session():
    """End current user session"""
    if 'session_id' in st.session_state:
        db.end_session(st.session_state.session_id)
        del st.session_state.session_id

# Legacy function name for compatibility
def get_available_editais():
    return get_available_notices()    