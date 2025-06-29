import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List
import hashlib

class Database:
    def __init__(self, db_path: str = "editalbot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    profile_picture_url TEXT,
                    domain VARCHAR(50) NOT NULL,
                    first_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_end TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Messages table (conversations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT,
                    notice_context VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    def get_or_create_user(self, email: str, name: str, profile_picture_url: str = None) -> Dict:
        """Get existing user or create new one"""
        domain = email.split('@')[1].lower()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user:
                # Update last access and increment access count
                cursor.execute("""
                    UPDATE users 
                    SET last_access = CURRENT_TIMESTAMP, 
                        access_count = access_count + 1,
                        name = ?,
                        profile_picture_url = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                """, (name, profile_picture_url, email))
                
                # Get updated user
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (email, name, profile_picture_url, domain)
                    VALUES (?, ?, ?, ?)
                """, (email, name, profile_picture_url, domain))
                
                # Get created user
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
            
            conn.commit()
            return dict(user) if user else None
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> int:
        """Create a new user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions (user_id, ip_address, user_agent)
                VALUES (?, ?, ?)
            """, (user_id, ip_address, user_agent))
            conn.commit()
            return cursor.lastrowid
    
    def end_session(self, session_id: int):
        """End a user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_sessions 
                SET session_end = CURRENT_TIMESTAMP 
                WHERE id = ? AND session_end IS NULL
            """, (session_id,))
            conn.commit()
    
    def save_message(self, user_id: int, user_message: str, bot_response: str, notice_context: str = None):
        """Save a message conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (user_id, user_message, bot_response, notice_context)
                VALUES (?, ?, ?, ?)
            """, (user_id, user_message, bot_response, notice_context))
            conn.commit()
    
    def get_user_stats(self) -> Dict:
        """Get general user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
            total_users = cursor.fetchone()[0]
            
            # Users by domain
            cursor.execute("""
                SELECT domain, COUNT(*) as count 
                FROM users 
                WHERE is_active = 1 
                GROUP BY domain
            """)
            domain_stats = dict(cursor.fetchall())
            
            # Recent users (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent 
                FROM users 
                WHERE last_access >= datetime('now', '-7 days') AND is_active = 1
            """)
            recent_users = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute("SELECT COUNT(*) as total FROM messages")
            total_messages = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'domain_stats': domain_stats,
                'recent_users': recent_users,
                'total_messages': total_messages
            }
    
    def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Get all users with pagination"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users 
                WHERE is_active = 1 
                ORDER BY last_access DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get messages for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_notice_usage(self) -> List[Dict]:
        """Get statistics about notice usage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notice_context, COUNT(*) as usage_count
                FROM messages 
                WHERE notice_context IS NOT NULL 
                GROUP BY notice_context 
                ORDER BY usage_count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_sessions 
                WHERE session_start < datetime('now', '-{} days')
            """.format(days))
            conn.commit()
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"editalbot_backup_{timestamp}.db"
        
        with sqlite3.connect(self.db_path) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)
        
        return backup_path


# Global database instance
db = Database()
