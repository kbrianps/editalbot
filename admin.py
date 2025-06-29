import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import db
import plotly.express as px
import plotly.graph_objects as go

def show_admin_page():
    """Admin dashboard to view user and usage statistics"""
    
    st.title("📊 EditalBot - Admin Dashboard")
    st.markdown("---")
    
    # Check if user is admin (basic check - you can enhance this)
    if not st.session_state.get('authenticated', False):
        st.error("❌ Você precisa estar logado para acessar esta página.")
        return
    
    # Get statistics
    stats = db.get_user_stats()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'])
    
    with col2:
        st.metric("Recent Users (7 days)", stats['recent_users'])
    
    with col3:
        st.metric("Total Messages", stats['total_messages'])
    
    with col4:
        avg_messages = stats['total_messages'] / max(stats['total_users'], 1)
        st.metric("Avg Messages/User", f"{avg_messages:.1f}")
    
    st.markdown("---")
    
    # Domain distribution
    st.subheader("👥 Users by Domain")
    if stats['domain_stats']:
        domain_df = pd.DataFrame(list(stats['domain_stats'].items()), 
                               columns=['Domain', 'Count'])
        
        fig = px.pie(domain_df, values='Count', names='Domain', 
                    title="User Distribution by Domain")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No domain data available yet.")
    
    # Recent users table
    st.subheader("👤 Recent Users")
    users = db.get_all_users(limit=20)
    
    if users:
        users_df = pd.DataFrame(users)
        users_df['last_access'] = pd.to_datetime(users_df['last_access'])
        users_df = users_df.sort_values('last_access', ascending=False)
        
        # Display table
        display_columns = ['name', 'email', 'domain', 'access_count', 'last_access', 'first_login']
        st.dataframe(
            users_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No users found.")
    
    # Notice usage
    st.subheader("📋 Notice Usage Statistics")
    notice_usage = db.get_notice_usage()
    
    if notice_usage:
        notice_df = pd.DataFrame(notice_usage)
        
        fig = px.bar(notice_df, x='notice_context', y='usage_count',
                    title="Most Consulted Notices")
        fig.update_xaxes(title="Notice")
        fig.update_yaxes(title="Number of Questions")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(notice_df, use_container_width=True, hide_index=True)
    else:
        st.info("No notice usage data available yet.")
    
    # User messages (for selected user)
    st.subheader("💬 User Messages")
    
    if users:
        user_emails = [f"{user['name']} ({user['email']})" for user in users[:20]]
        selected_user_display = st.selectbox("Select user to view messages:", 
                                           ["Select a user..."] + user_emails)
        
        if selected_user_display != "Select a user...":
            # Extract email from display string
            selected_email = selected_user_display.split('(')[1].split(')')[0]
            selected_user = next(user for user in users if user['email'] == selected_email)
            
            messages = db.get_user_messages(selected_user['id'])
            
            if messages:
                st.write(f"**Messages for {selected_user['name']}:**")
                
                for msg in messages:
                    with st.expander(f"📅 {msg['timestamp']} - Notice: {msg['notice_context'] or 'N/A'}"):
                        st.write("**User:**", msg['user_message'])
                        st.write("**Bot:**", msg['bot_response'])
            else:
                st.info("No messages found for this user.")
    
    # Database management
    st.markdown("---")
    st.subheader("🔧 Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Create Backup"):
            try:
                backup_path = db.backup_database()
                st.success(f"✅ Backup created: {backup_path}")
            except Exception as e:
                st.error(f"❌ Error creating backup: {str(e)}")
    
    with col2:
        if st.button("🧹 Cleanup Old Sessions"):
            try:
                db.cleanup_old_sessions(days=30)
                st.success("✅ Old sessions cleaned up (30+ days)")
            except Exception as e:
                st.error(f"❌ Error cleaning up: {str(e)}")


def main():
    """Main function to run the admin page"""
    st.set_page_config(
        page_title="EditalBot Admin",
        page_icon="📊",
        layout="wide"
    )
    
    show_admin_page()


if __name__ == "__main__":
    main()
