# 🗄️ Database Documentation - EditalBot

This document describes the SQLite database implementation for the EditalBot system.

## 📊 Database Schema

### Tables Overview

The database consists of three main tables:

1. **`users`** - Store user information and authentication data
2. **`user_sessions`** - Track user sessions and usage patterns  
3. **`messages`** - Store chat conversations and responses

---

## 📋 Table Structures

### 1. Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_picture_url TEXT,
    domain VARCHAR(50) NOT NULL,           -- edu.unirio.br, uniriotec.br, unirio.br
    first_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Store user profile information and login statistics

**Key Fields:**
- `email`: Unique identifier (institutional email)
- `domain`: UNIRIO domain classification
- `access_count`: Number of times user has logged in
- `last_access`: Most recent login timestamp

### 2. User Sessions Table
```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Purpose:** Track individual user sessions for analytics

**Key Fields:**
- `user_id`: Reference to users table
- `session_start/end`: Session duration tracking
- `ip_address`: For security and analytics
- `user_agent`: Browser/device information

### 3. Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT,
    notice_context VARCHAR(255),           -- Which notice was being consulted
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Purpose:** Store all chat conversations for analysis and support

**Key Fields:**
- `user_message`: User's question/input
- `bot_response`: AI-generated response
- `notice_context`: Which notice/edital was selected during conversation

---

## 🔧 Database Operations

### Core Functions (database.py)

#### User Management
```python
# Create or update user on login
user = db.get_or_create_user(email, name, profile_picture_url)

# Get user statistics
stats = db.get_user_stats()

# Get all users with pagination
users = db.get_all_users(limit=100)
```

#### Session Tracking
```python
# Start new session
session_id = db.create_session(user_id, ip_address, user_agent)

# End session
db.end_session(session_id)
```

#### Message Storage
```python
# Save conversation
db.save_message(user_id, user_message, bot_response, notice_context)

# Get user's message history
messages = db.get_user_messages(user_id, limit=50)
```

#### Analytics
```python
# Notice usage statistics
usage = db.get_notice_usage()

# Cleanup old data
db.cleanup_old_sessions(days=30)

# Create backup
backup_path = db.backup_database()
```

---

## 📈 Admin Dashboard Features

The admin dashboard (`admin.py`) provides:

### 📊 Overview Metrics
- Total registered users
- Recent users (last 7 days)
- Total messages sent
- Average messages per user

### 👥 User Analytics
- User distribution by domain (edu.unirio.br, uniriotec.br, unirio.br)
- Recent users table with access counts
- Individual user message history

### 📋 Notice Analytics
- Most consulted notices/editais
- Usage frequency charts
- Question patterns

### 🔧 Database Management
- Create database backups
- Cleanup old sessions
- Data integrity checks

---

## 🚀 Usage Examples

### Starting the Application
```bash
# Main application
streamlit run app.py --server.port 8500

# Admin dashboard
streamlit run admin.py --server.port 8501
```

### Database Integration Flow

1. **User Login**: OAuth authentication creates/updates user record
2. **Session Start**: New session record created with timestamp
3. **Chat Interaction**: Each message pair saved to messages table
4. **Session End**: Logout updates session end time
5. **Analytics**: Admin can view all data through dashboard

---

## 🔒 Data Privacy & Security

### LGPD Compliance Considerations
- **Data Minimization**: Only collect necessary information
- **Consent**: Users implicitly consent by using institutional login
- **Access Control**: Admin dashboard restricted to authorized users
- **Data Retention**: Implement cleanup for old sessions
- **Backup Security**: Ensure backup files are protected

### Security Features
- **Domain Restriction**: Only UNIRIO domains allowed
- **Session Tracking**: Monitor for unusual access patterns
- **Data Encryption**: SQLite supports encryption (can be enabled)
- **Audit Trail**: Complete log of user actions

---

## 🛠️ Maintenance

### Regular Tasks
```python
# Weekly cleanup
db.cleanup_old_sessions(days=7)

# Monthly backup
backup_path = db.backup_database()

# Monitor growth
stats = db.get_user_stats()
print(f"Database has {stats['total_users']} users")
```

### Database Location
- **File**: `editalbot.db` (in application directory)
- **Backups**: `editalbot_backup_YYYYMMDD_HHMMSS.db`

### Performance Considerations
- **Indexing**: SQLite automatically indexes primary keys
- **Cleanup**: Regular cleanup prevents database bloat
- **Backup**: Scheduled backups ensure data safety

---

## 🔍 Troubleshooting

### Common Issues

**Database locked**
```python
# Ensure connections are properly closed
with sqlite3.connect(db_path) as conn:
    # operations here
    pass  # connection auto-closed
```

**Missing tables**
```python
# Reinitialize database
db = Database()  # Creates tables if missing
```

**Performance slow**
```python
# Cleanup old data
db.cleanup_old_sessions(days=30)
```

---

## 📊 Sample Queries

### User Statistics
```sql
-- Users by domain
SELECT domain, COUNT(*) as count 
FROM users 
WHERE is_active = 1 
GROUP BY domain;

-- Most active users
SELECT name, email, access_count 
FROM users 
ORDER BY access_count DESC 
LIMIT 10;
```

### Usage Analytics
```sql
-- Messages per day
SELECT DATE(timestamp) as date, COUNT(*) as message_count
FROM messages 
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Popular notices
SELECT notice_context, COUNT(*) as usage_count
FROM messages 
WHERE notice_context IS NOT NULL
GROUP BY notice_context
ORDER BY usage_count DESC;
```
