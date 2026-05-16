#!/usr/bin/env python3
"""测试 LearnForge 主链路功能"""

import requests
import json
import time

def test_api_health():
    """测试 API 健康检查"""
    print("=== 测试 API 健康检查 ===")
    try:
        r = requests.get('http://localhost:5000/', timeout=10)
        if r.status_code == 200:
            print("[OK] API 服务正常运行")
            return True
        else:
            print(f"[FAIL] API 服务异常: {r.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] 无法连接到 API: {e}")
        return False

def test_part_planning():
    """测试 Part 规划功能"""
    print("\n=== 测试 Part 规划 ===")
    try:
        data = {
            "knowledge_point": "Python基础",
            "learning_goal": "入门学习",
            "scene": "tech"
        }
        r = requests.post('http://localhost:5000/api/learning/plan', json=data, timeout=60)
        if r.status_code == 200:
            result = r.json()
            session_id = result.get('session_id')
            parts = result.get('parts', [])
            print("[OK] Part 规划成功")
            print(f"  - 会话ID: {session_id}")
            print(f"  - Part数量: {len(parts)}")
            for i, part in enumerate(parts):
                print(f"    Part {i+1}: {part.get('title')} ({part.get('difficulty')}, {part.get('estimated_time')})")
            return session_id, parts
        else:
            print(f"[FAIL] Part 规划失败: {r.status_code} - {r.text}")
            return None, None
    except Exception as e:
        print(f"[FAIL] Part 规划异常: {e}")
        return None, None

def test_start_part(session_id, part_id):
    """测试开始学习 Part"""
    print("\n=== 测试开始学习 ===")
    try:
        data = {
            "session_id": session_id,
            "part_id": part_id,
            "learning_mode": "simple"
        }
        r = requests.post('http://localhost:5000/api/learning/start_part', json=data, timeout=90)
        if r.status_code == 200:
            result = r.json()
            chapter = result.get('chapter', {})
            print("[OK] 开始学习成功")
            print(f"  - 章节ID: {chapter.get('id')}")
            print(f"  - 章节标题: {chapter.get('title')}")
            content = chapter.get('content', {})
            if content:
                print(f"  - 内容类型: {type(content)}")
                if isinstance(content, dict) and 'explanation' in content:
                    preview = content['explanation'][:100] if len(content['explanation']) > 100 else content['explanation']
                    print(f"  - 讲解内容预览: {preview}...")
            return True
        else:
            print(f"[FAIL] 开始学习失败: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[FAIL] 开始学习异常: {e}")
        return False

def test_generate_next(session_id, part_id):
    """测试生成下一章节"""
    print("\n=== 测试生成下一章节 ===")
    try:
        data = {
            "session_id": session_id,
            "part_id": part_id,
            "learning_mode": "simple"
        }
        r = requests.post('http://localhost:5000/api/learning/generate_next', json=data, timeout=90)
        if r.status_code == 200:
            result = r.json()
            chapter = result.get('chapter', {})
            print("[OK] 生成下一章节成功")
            print(f"  - 章节ID: {chapter.get('id')}")
            print(f"  - 章节标题: {chapter.get('title')}")
            return True
        elif r.status_code == 400 and 'No more chapters' in r.text:
            print("[OK] 没有更多章节需要生成")
            return True
        else:
            print(f"[FAIL] 生成下一章节失败: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[FAIL] 生成下一章节异常: {e}")
        return False

def test_input_validation():
    """测试输入验证"""
    print("\n=== 测试输入验证 ===")
    
    # 测试缺少必需字段
    print("1. 测试缺少必需字段...")
    r = requests.post('http://localhost:5000/api/learning/plan', 
                      json={"learning_goal": "入门"}, 
                      timeout=10)
    if r.status_code == 400:
        print("   [OK] 正确拒绝缺少必需字段的请求")
    else:
        print(f"   [FAIL] 应该返回 400，实际返回 {r.status_code}")
    
    # 测试无效 session
    print("2. 测试无效 session...")
    r = requests.post('http://localhost:5000/api/learning/start_part',
                      json={"session_id": "invalid_session_123", "part_id": "part_1"},
                      timeout=10)
    if r.status_code == 404:
        print("   [OK] 正确拒绝无效 session")
    else:
        print(f"   [FAIL] 应该返回 404，实际返回 {r.status_code}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("LearnForge 主链路功能测试")
    print("=" * 60)
    
    # 测试 API 健康检查
    if not test_api_health():
        print("\nAPI 服务未运行，请先启动后端服务")
        return
    
    # 测试输入验证
    test_input_validation()
    
    # 测试 Part 规划
    session_id, parts = test_part_planning()
    if not session_id or not parts:
        print("\nPart 规划失败，无法继续测试")
        return
    
    # 测试开始学习
    first_part = parts[0]
    success = test_start_part(session_id, first_part.get('id'))
    if not success:
        print("\n开始学习失败")
        return
    
    # 测试生成下一章节
    test_generate_next(session_id, first_part.get('id'))
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n前端服务地址: http://localhost:3001/")
    print("后端 API 地址: http://localhost:5000/")

if __name__ == "__main__":
    main()