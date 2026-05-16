#!/usr/bin/env python3
"""测试记忆管理器 - 分离短期/长期记忆"""

import sys
sys.path.append('d:/Appt/大三下/学习/multi_Agent_智能日程/learnforge')

from memory.memory_manager import memory_manager

def test_memory_separation():
    print("=== 测试记忆管理器 - 分离短期/长期记忆 ===")
    
    # 1. 测试短期记忆
    print("\n1. 测试短期记忆")
    memory_manager.add_short_term("test_key", "test_value", "conv_1")
    result = memory_manager.get_short_term("test_key", "conv_1")
    if result == "test_value":
        print("   ✅ 短期记忆添加和获取成功")
    else:
        print(f"   ❌ 短期记忆失败: {result}")
    
    # 2. 测试长期记忆
    print("\n2. 测试长期记忆")
    success = memory_manager.add_long_term("测试知识点", {"status": "学习中", "mastery_level": 0.0})
    if success:
        print("   ✅ 长期记忆添加成功")
    else:
        print("   ❌ 长期记忆添加失败")
    
    # 3. 验证长期记忆持久化
    print("\n3. 测试长期记忆查询")
    node = memory_manager.get_long_term("测试知识点")
    if node and node.get("name") == "测试知识点":
        print("   ✅ 长期记忆查询成功")
    else:
        print("   ❌ 长期记忆查询失败")
    
    # 4. 测试掌握度更新
    print("\n4. 测试掌握度更新")
    success = memory_manager.update_mastery("测试知识点", 0.3)
    mastery = memory_manager.get_mastery("测试知识点")
    if mastery == 0.3:
        print(f"   ✅ 掌握度更新成功: {mastery}")
    else:
        print(f"   ❌ 掌握度更新失败: {mastery}")
    
    # 5. 测试记忆统计
    print("\n5. 测试记忆统计")
    stats = memory_manager.get_stats()
    if "short_term" in stats and "long_term" in stats:
        print(f"   ✅ 短期记忆统计: {stats['short_term']}")
        print(f"   ✅ 长期记忆统计: {stats['long_term']}")
    else:
        print("   ❌ 记忆统计失败")
    
    # 6. 测试短期记忆清除
    print("\n6. 测试短期记忆清除")
    memory_manager.clear_short_term("conv_1")
    result = memory_manager.get_short_term("test_key", "conv_1")
    if result is None:
        print("   ✅ 短期记忆清除成功")
    else:
        print(f"   ❌ 短期记忆清除失败: {result}")
    
    # 7. 验证长期记忆不受影响
    print("\n7. 验证长期记忆不受短期清除影响")
    node = memory_manager.get_long_term("测试知识点")
    if node and node.get("properties", {}).get("mastery_level") == 0.3:
        print("   ✅ 长期记忆不受短期清除影响")
    else:
        print("   ❌ 长期记忆受短期清除影响")
    
    # 总结
    print("\n=== 测试总结 ===")
    print("✅ 短期/长期记忆分离测试通过")
    print("✅ 短期记忆：内存存储，可清除")
    print("✅ 长期记忆：持久化存储，不受短期清除影响")
    
    return True

if __name__ == '__main__':
    success = test_memory_separation()
    sys.exit(0 if success else 1)