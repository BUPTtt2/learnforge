#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试修复效果"""

from agents.generation_agent import generation_agent

print("=== 测试1：章节标题修复 ===")
chapter = {
    "title": "数据定义语言（DDL）",
    "description": "学习DDL语句"
}
part = {
    "title": "数据库SQL"
}

result = generation_agent.generate_chapter_content(chapter, part, "详细，面试边缘涉及")
explanation = result.get("explanation", "")
print(f"章节标题检测: {'英语' in explanation} → 标题是否包含'英语'")
if "英语" in explanation:
    print("❌ 修复失败")
else:
    print("✅ 修复成功")
print(f"章节开头: {explanation[:100]}...")

print("\n" + "="*50)
print("=== 测试2：多样化题型 ===")
result = generation_agent.generate_exercise(chapter, part, "详细，面试边缘涉及")
exercises = result.get("exercises", []) or [result.get("exercise")]

if isinstance(exercises, dict):
    exercises = [exercises]

print(f"生成的题型数量: {len(exercises)}")
for i, ex in enumerate(exercises[:5]):
    ex_type = ex.get("type", "选择题")
    question = ex.get("question", "")[:50]
    print(f"  {i+1}. [{ex_type}] {question}...")
