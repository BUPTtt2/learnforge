"""统一记忆管理器 - 分离短期和长期记忆"""

import time
from typing import Dict, Any, Optional

class MemoryManager:
    def __init__(self):
        # 短期记忆（内存存储，会话结束后清空）
        self.short_term = {
            "chat_context": {},  # 对话上下文 {conversation_id: {messages}}
            "current_session": None,  # 当前会话ID
            "rag_results": {},  # 临时RAG检索结果
            "learning_state": {}  # 当前学习状态
        }
        
        # 长期记忆（持久化存储）
        from memory.knowledge_graph import knowledge_graph
        from utils.storage import storage
        self.knowledge_graph = knowledge_graph
        self.storage = storage
    
    def add_short_term(self, key: str, value: Any, conversation_id: Optional[str] = None) -> None:
        """添加短期记忆"""
        if conversation_id:
            if conversation_id not in self.short_term["chat_context"]:
                self.short_term["chat_context"][conversation_id] = {}
            self.short_term["chat_context"][conversation_id][key] = value
        else:
            self.short_term[key] = value
    
    def get_short_term(self, key: str, conversation_id: Optional[str] = None) -> Any:
        """获取短期记忆"""
        if conversation_id:
            return self.short_term["chat_context"].get(conversation_id, {}).get(key)
        return self.short_term.get(key)
    
    def clear_short_term(self, conversation_id: Optional[str] = None) -> None:
        """清除短期记忆"""
        if conversation_id:
            self.short_term["chat_context"].pop(conversation_id, None)
        else:
            self.short_term = {
                "chat_context": {}, 
                "current_session": None, 
                "rag_results": {},
                "learning_state": {}
            }
    
    def set_current_session(self, session_id: str) -> None:
        """设置当前会话"""
        self.short_term["current_session"] = session_id
    
    def get_current_session(self) -> Optional[str]:
        """获取当前会话"""
        return self.short_term.get("current_session")
    
    def cache_rag_results(self, query: str, results: list, conversation_id: str) -> None:
        """缓存RAG检索结果到短期记忆"""
        if conversation_id not in self.short_term["rag_results"]:
            self.short_term["rag_results"][conversation_id] = {}
        self.short_term["rag_results"][conversation_id][query] = {
            "results": results,
            "timestamp": time.time()
        }
    
    def get_cached_rag(self, query: str, conversation_id: str) -> Optional[list]:
        """获取缓存的RAG检索结果"""
        if conversation_id in self.short_term["rag_results"]:
            cached = self.short_term["rag_results"][conversation_id].get(query)
            if cached and time.time() - cached["timestamp"] < 300:  # 5分钟内有效
                return cached["results"]
        return None
    
    def add_long_term(self, knowledge_point: str, properties: Dict = None) -> bool:
        """添加长期记忆（知识图谱）"""
        try:
            self.knowledge_graph.add_node(knowledge_point, properties=properties)
            self.knowledge_graph.save()
            return True
        except Exception as e:
            print(f"[MemoryManager] 添加长期记忆失败: {e}")
            return False
    
    def update_long_term(self, knowledge_point: str, properties: Dict) -> bool:
        """更新长期记忆"""
        try:
            self.knowledge_graph.update_node(knowledge_point, properties)
            self.knowledge_graph.save()
            return True
        except Exception as e:
            print(f"[MemoryManager] 更新长期记忆失败: {e}")
            return False
    
    def update_mastery(self, knowledge_point: str, increment: float) -> bool:
        """更新知识点掌握度"""
        try:
            node = self.knowledge_graph.get_node(knowledge_point)
            if node:
                current_level = node.get('properties', {}).get('mastery_level', 0.0)
                new_level = min(1.0, current_level + increment)
                self.knowledge_graph.update_mastery_level(knowledge_point, new_level)
                self.knowledge_graph.save()
                return True
            return False
        except Exception as e:
            print(f"[MemoryManager] 更新掌握度失败: {e}")
            return False
    
    def get_long_term(self, knowledge_point: str) -> Optional[Dict]:
        """获取长期记忆"""
        return self.knowledge_graph.get_node(knowledge_point)
    
    def get_mastery(self, knowledge_point: str) -> float:
        """获取知识点掌握度"""
        node = self.knowledge_graph.get_node(knowledge_point)
        if node:
            return node.get('properties', {}).get('mastery_level', 0.0)
        return 0.0
    
    def summarize_memory(self, conversation_id: str) -> str:
        """生成记忆摘要"""
        context = self.get_short_term("chat_context", conversation_id)
        if context:
            return f"会话记忆: {len(context)} 条消息"
        return "暂无会话记忆"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        short_term_chats = len(self.short_term["chat_context"])
        kg_stats = self.knowledge_graph.get_stats()
        
        return {
            "short_term": {
                "active_conversations": short_term_chats,
                "current_session": self.short_term["current_session"]
            },
            "long_term": {
                "categories": kg_stats["categories"],
                "knowledge_nodes": kg_stats["knowledge_nodes"],
                "relations": kg_stats["relations"]
            }
        }


memory_manager = MemoryManager()