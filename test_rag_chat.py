#!/usr/bin/env python3
"""测试聊天历史参与 RAG 检索功能"""

import sys
sys.path.append('d:/Appt/大三下/学习/multi_Agent_智能日程/learnforge')

from utils.chat_history import chat_history_manager
from utils.rag import rag_system

def test_chat_to_rag():
    print("=== 测试聊天历史参与 RAG 检索 ===")
    
    # 清理之前的测试数据
    chat_history_manager.clear_all()
    
    # 创建对话并添加消息
    conv_id = chat_history_manager.create_conversation('test_session', 'RAG测试')
    print(f"1. 创建对话: {conv_id}")
    
    # 添加用户消息
    chat_history_manager.add_message(conv_id, 'user', '什么是 RAG 检索？')
    print(f"2. 添加用户消息")
    
    # 添加助手回复
    chat_history_manager.add_message(conv_id, 'assistant', 'RAG是检索增强生成，结合了信息检索和语言模型生成。')
    print(f"3. 添加助手回复")
    
    # 从 RAG 检索相关内容
    print(f"\n4. 从 RAG 检索 'RAG' 相关内容:")
    results = rag_system.search('RAG', top_k=5)
    
    chat_results = [r for r in results if r.get('metadata', {}).get('type') == 'chat']
    print(f"   检索到 {len(chat_results)} 条相关对话")
    
    for i, r in enumerate(chat_results):
        print(f"   {i+1}. {r['content'][:50]}...")
    
    # 验证检索结果
    if len(chat_results) > 0:
        print("\n✅ 测试通过：聊天历史成功存入并检索到 RAG")
        return True
    else:
        print("\n❌ 测试失败：未检索到聊天历史")
        return False

if __name__ == '__main__':
    success = test_chat_to_rag()
    sys.exit(0 if success else 1)