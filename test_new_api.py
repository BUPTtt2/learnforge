#!/usr/bin/env python3
"""测试新架构 API"""

import requests
import json

def main():
    # 测试 Part 规划
    print("测试 Part 规划...")
    r = requests.post(
        'http://localhost:5000/api/learning/plan',
        json={'knowledge_point': 'Python基础', 'learning_goal': '入门学习', 'scene': 'tech'},
        timeout=90
    )
    print(f"状态码: {r.status_code}")
    result = r.json()
    print(f"会话ID: {result.get('session_id')}")
    print(f"Part数量: {len(result.get('parts', []))}")
    
    # 获取会话ID和第一个Part
    session_id = result.get('session_id')
    parts = result.get('parts', [])
    
    if parts:
        part_id = parts[0].get('id')
        print(f"第一个Part ID: {part_id}")
        print(f"第一个Part标题: {parts[0].get('title')}")
        
        # 测试开始学习
        print("\n测试开始学习...")
        r2 = requests.post(
            'http://localhost:5000/api/learning/start_part',
            json={'session_id': session_id, 'part_id': part_id, 'learning_mode': 'simple'},
            timeout=90
        )
        print(f"状态码: {r2.status_code}")
        if r2.status_code == 200:
            result2 = r2.json()
            print(f"章节标题: {result2.get('chapter', {}).get('title')}")
            print("API 测试成功！")

if __name__ == "__main__":
    main()