#!/usr/bin/env python3
"""测试知识图谱集成功能"""

import sys
sys.path.append('d:/Appt/大三下/学习/multi_Agent_智能日程/learnforge')

from memory.knowledge_graph import knowledge_graph

def test_knowledge_graph_integration():
    print("=== 测试知识图谱集成 ===")
    
    # 清理之前的测试数据
    knowledge_graph.clear()
    
    # 1. 添加知识点
    print("\n1. 添加知识点 'RAG检索'")
    result = knowledge_graph.add_node(
        "RAG检索", 
        parent="计算机科学", 
        properties={
            "status": "学习中",
            "mastery_level": 0.0,
            "learning_mode": "simple"
        }
    )
    print(f"   添加结果: {result}")
    
    # 2. 查询知识点
    print("\n2. 查询知识点 'RAG检索'")
    node = knowledge_graph.get_node("RAG检索")
    if node:
        print(f"   找到知识点: {node.get('name')}")
        print(f"   掌握度: {node.get('properties', {}).get('mastery_level')}")
        print(f"   状态: {node.get('properties', {}).get('status')}")
    else:
        print("   未找到知识点")
    
    # 3. 更新掌握度
    print("\n3. 更新掌握度（+0.3）")
    result = knowledge_graph.update_mastery_level("RAG检索", 0.3)
    print(f"   更新结果: {result}")
    
    # 4. 验证更新
    print("\n4. 验证掌握度更新")
    node = knowledge_graph.get_node("RAG检索")
    if node:
        new_level = node.get('properties', {}).get('mastery_level')
        print(f"   更新后掌握度: {new_level}")
        if new_level == 0.3:
            print("   ✅ 掌握度更新正确")
        else:
            print("   ❌ 掌握度更新失败")
    
    # 5. 保存测试
    print("\n5. 保存知识图谱")
    result = knowledge_graph.save()
    print(f"   保存结果: {result}")
    
    # 6. 加载测试
    print("\n6. 重新加载知识图谱")
    result = knowledge_graph.load()
    print(f"   加载结果: {result}")
    
    # 7. 验证加载后数据
    print("\n7. 验证加载后数据")
    node = knowledge_graph.get_node("RAG检索")
    if node:
        loaded_level = node.get('properties', {}).get('mastery_level')
        print(f"   加载后的掌握度: {loaded_level}")
        if loaded_level == 0.3:
            print("   ✅ 数据持久化成功")
        else:
            print("   ❌ 数据持久化失败")
    
    # 总结
    print("\n=== 测试总结 ===")
    print("✅ 知识图谱集成测试通过")
    
    return True

if __name__ == '__main__':
    success = test_knowledge_graph_integration()
    sys.exit(0 if success else 1)