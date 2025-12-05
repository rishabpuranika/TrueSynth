import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "chat_history.db"

def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Create messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            metadata TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_chats() -> List[Dict]:
    """Get all chat sessions ordered by date"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM chats ORDER BY created_at DESC')
    rows = c.fetchall()
    
    chats = []
    for row in rows:
        chats.append({
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return chats

def get_chat_messages(chat_id: str) -> List[Dict]:
    """Get all messages for a specific chat"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp ASC', (chat_id,))
    rows = c.fetchall()
    
    messages = []
    for row in rows:
        messages.append({
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
            "timestamp": row["timestamp"]
        })
    
    conn.close()
    return messages

def create_chat(title: str = None) -> str:
    """Create a new chat session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    chat_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    if not title:
        title = "New Chat"
        
    c.execute('INSERT INTO chats (id, title, created_at) VALUES (?, ?, ?)',
              (chat_id, title, created_at))
    
    conn.commit()
    conn.close()
    return chat_id

def add_message(chat_id: str, role: str, content: str, metadata: Dict = None):
    """Add a message to a chat"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    msg_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None
    
    c.execute('''
        INSERT INTO messages (id, chat_id, role, content, metadata, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (msg_id, chat_id, role, content, metadata_json, timestamp))
    
    conn.commit()
    conn.close()

def update_chat_title(chat_id: str, title: str):
    """Update the title of a chat"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE chats SET title = ? WHERE id = ?', (title, chat_id))
    conn.commit()
    conn.close()

def delete_chat(chat_id: str):
    """Delete a chat and all its messages"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Delete messages first (manual cascade)
    c.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    
    # Delete the chat
    c.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    
    conn.commit()
    conn.close()
