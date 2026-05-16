from agents.讲解师 import explainer

print("Testing local model integration...")
print("="*60)

knowledge_points = [
    "Agent 的规划能力",
    "ReAct 推理方法",
    "Transformer 架构"
]

for kp in knowledge_points:
    print(f"\n📚 Testing: {kp}")
    print("-"*40)
    
    try:
        result = explainer.generate_explanation(kp, mode="simple")
        print(f"模式: {result['mode_name']}")
        print(f"解释:\n{result['explanation'][:300]}...")
        print("✅ Success")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
print("Integration test completed!")