import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatHistoryManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../data/chat_history.db')
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                topic TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, session_id: str, topic: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (session_id, created_at, updated_at, topic, message_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now(), datetime.now(), topic, 0))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def add_message(self, conversation_id: int, role: str, content: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, role, content, datetime.now()))
        
        cursor.execute('''
            UPDATE conversations 
            SET updated_at = ?, message_count = message_count + 1
            WHERE id = ?
        ''', (datetime.now(), conversation_id))
        
        conn.commit()
        conn.close()
        
        # 新增：将对话内容存入 RAG 向量库，以便后续检索
        try:
            from utils.rag import rag_system
            metadata = {
                "type": "chat",
                "conversation_id": conversation_id,
                "role": role,
                "timestamp": datetime.now().isoformat()
            }
            rag_system.add_document(content, metadata)
        except Exception as e:
            print(f"[Warning] Failed to add chat message to RAG: {e}")
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations WHERE id = ?
        ''', (conversation_id,))
        
        conv = cursor.fetchone()
        if not conv:
            conn.close()
            return None
        
        cursor.execute('''
            SELECT role, content, timestamp FROM messages 
            WHERE conversation_id = ? ORDER BY timestamp
        ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        
        return {
            'id': conv[0],
            'session_id': conv[1],
            'created_at': conv[2],
            'updated_at': conv[3],
            'topic': conv[4],
            'message_count': conv[5],
            'messages': messages
        }
    
    def get_conversations_by_session(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations WHERE session_id = ? 
            ORDER BY updated_at DESC LIMIT ?
        ''', (session_id, limit))
        
        convs = cursor.fetchall()
        conversations = []
        
        for conv in convs:
            cursor.execute('''
                SELECT role, content, timestamp FROM messages 
                WHERE conversation_id = ? ORDER BY timestamp LIMIT 5
            ''', (conv[0],))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2]
                })
            
            conversations.append({
                'id': conv[0],
                'session_id': conv[1],
                'created_at': conv[2],
                'updated_at': conv[3],
                'topic': conv[4],
                'message_count': conv[5],
                'preview': messages
            })
        
        conn.close()
        return conversations
    
    def delete_conversation(self, conversation_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
        cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def clear_all(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages')
        cursor.execute('DELETE FROM conversations')
        
        conn.commit()
        conn.close()

chat_history_manager = ChatHistoryManager()

if __name__ == '__main__':
    manager = ChatHistoryManager()
    
    conv_id = manager.create_conversation('test_session', '测试对话')
    print(f'创建对话: {conv_id}')
    
    manager.add_message(conv_id, 'user', '你好')
    manager.add_message(conv_id, 'assistant', '你好！有什么我可以帮助你的？')
    
    conv = manager.get_conversation(conv_id)
    print(f'对话内容: {json.dumps(conv, indent=2, ensure_ascii=False)}')
    
    convs = manager.get_conversations_by_session('test_session')
    print(f'会话列表: {len(convs)}')
