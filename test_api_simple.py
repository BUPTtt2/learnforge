#!/usr/bin/env python3
"""测试 API 服务器是否正常响应"""
import requests
import json

def test_api():
    base_url = "http://localhost:5000"

    # 测试健康检查
    print("测试健康检查...")
    try:
        resp = requests.get(f"{base_url}/", timeout=5)
        print(f"  状态码: {resp.status_code}")
        print(f"  响应: {resp.json()}")
    except Exception as e:
        print(f"  错误: {e}")
        return False

    # 测试 history API
    print("\n测试 history API...")
    try:
        resp = requests.get(f"{base_url}/api/learning/history", timeout=5)
        print(f"  状态码: {resp.status_code}")
        print(f"  响应: {resp.json()}")
    except Exception as e:
        print(f"  错误: {e}")
        return False

    print("\n所有测试通过！")
    return True

if __name__ == "__main__":
    test_api()