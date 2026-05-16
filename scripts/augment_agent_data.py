"""分析当前数据主题分布并补充 Agent 相关数据"""

import json

# 读取现有数据
with open(r"D:\LLaMA-Factory\data\merged_sft_data.jsonl", 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f if line.strip()]

print(f"现有数据量: {len(data)} 条")

# 主题统计
topics = []
for item in data:
    instr = str(item.get('instruction', '')).lower()
    if any(k in instr for k in ['agent', 'react', 'plan-and-solve', 'self-planning', 'tool calling', 'langchain', 'langgraph']):
        topics.append('Agent')
    elif any(k in instr for k in ['transformer', 'attention', 'mha', 'gqa', 'rope']):
        topics.append('Transformer')
    elif any(k in instr for k in ['rag', 'retrieval', 'vector', 'embedding']):
        topics.append('RAG')
    elif any(k in instr for k in ['lora', 'sft', 'peft', 'fine-tune']):
        topics.append('Fine-tuning')
    elif any(k in instr for k in ['diffusion', 'stable', 'ddpm']):
        topics.append('Diffusion')
    else:
        topics.append('Other')

from collections import Counter
topic_counts = Counter(topics)
print("\n当前主题分布:")
for topic, count in topic_counts.items():
    print(f"  {topic}: {count} 条 ({round(count/len(data)*100, 1)}%)")

# 生成更多 Agent 相关数据
agent_topics = [
    {"instruction": "解释 Agent 的 ReAct 模式工作原理", "input": "", "output": "ReAct（Reasoning + Acting）是一种让 Agent 交替进行推理和行动的框架。核心原理是让模型在每个步骤中先思考（Reasoning）下一步应该做什么，然后执行相应的动作（Acting）。\n\n工作流程：\n1. **推理阶段**：Agent 分析当前状态和目标，决定下一步行动\n2. **行动阶段**：执行工具调用或生成响应\n3. **观察阶段**：获取行动结果\n4. **循环**：重复直到任务完成\n\nReAct 的优势在于提高了推理的可解释性，让模型的决策过程更加透明。"},
    {"instruction": "什么是 Plan-and-Solve 规划方法？", "input": "", "output": "Plan-and-Solve 是一种两阶段规划方法：\n\n**规划阶段**：\n- 将复杂任务分解为子目标\n- 制定执行计划和步骤顺序\n- 考虑子任务之间的依赖关系\n\n**求解阶段**：\n- 按计划顺序执行每个子任务\n- 处理子任务间的依赖\n- 必要时调整计划\n\n这种方法适合处理需要多步骤推理的复杂问题，如数学证明、代码生成等。"},
    {"instruction": "Self-Planning 与 ReAct 的区别是什么？", "input": "", "output": "Self-Planning 和 ReAct 都是 Agent 规划方法，但存在关键区别：\n\n**ReAct**：\n- 推理和行动交替进行\n- 每步都需要显式推理\n- 适合需要即时反馈的任务\n\n**Self-Planning**：\n- 先完整生成执行计划\n- 再按计划执行\n- 适合结构清晰的任务\n\n选择哪种方法取决于任务复杂度和环境反馈需求。"},
    {"instruction": "如何实现 Agent 的工具调用能力？", "input": "", "output": "实现 Agent 的工具调用能力需要以下步骤：\n\n1. **工具定义**：定义可用工具的描述和参数\n2. **工具选择**：让模型根据当前状态选择合适工具\n3. **参数生成**：生成工具调用所需的参数\n4. **执行调用**：调用工具并获取结果\n5. **结果处理**：解析工具返回结果\n6. **总结回答**：基于结果生成最终回答\n\n关键技术包括：工具描述的结构化表示、调用格式的标准化、错误处理机制。"},
    {"instruction": "什么是 Agent 的记忆系统？", "input": "", "output": "Agent 的记忆系统是存储和检索信息的机制，通常分为三类：\n\n**短期记忆**：\n- 存储当前对话上下文\n- 支持实时推理\n- 使用向量检索实现\n\n**长期记忆**：\n- 存储跨会话的知识\n- 使用知识库或向量数据库\n- 支持知识的持久化和更新\n\n**情境记忆**：\n- 存储任务执行的上下文\n- 支持任务恢复和继续\n- 记录决策历史\n\n良好的记忆系统能显著提升 Agent 的长期任务处理能力。"},
    {"instruction": "LangGraph 如何实现工作流编排？", "input": "", "output": "LangGraph 是一个用于构建多 Agent 工作流的框架：\n\n**核心概念**：\n- **节点（Node）**：执行具体任务的单元\n- **边（Edge）**：定义节点间的数据流\n- **条件分支**：根据条件选择执行路径\n- **循环**：支持迭代执行\n\n**编排方式**：\n1. 定义状态对象\n2. 创建节点函数\n3. 定义边和条件\n4. 编译图结构\n5. 运行执行\n\nLangGraph 支持同步和异步执行，适合构建复杂的多步骤工作流。"},
    {"instruction": "什么是 Agent 的反思机制？", "input": "", "output": "Agent 的反思机制让模型能够回顾和评估自己的推理过程：\n\n**反思类型**：\n- **自我检查**：检查回答是否正确\n- **错误修正**：发现错误后重新推理\n- **计划评估**：评估执行计划的有效性\n\n**实现方法**：\n1. 在生成回答后添加反思步骤\n2. 使用专门的反思提示词\n3. 让模型对比多种可能的答案\n4. 基于反馈进行修正\n\n反思机制能显著提高复杂推理任务的准确性。"},
    {"instruction": "如何评估 Agent 的性能？", "input": "", "output": "评估 Agent 性能需要考虑多个维度：\n\n**任务完成率**：\n- 能否正确完成给定任务\n- 解决问题的步骤数\n\n**推理质量**：\n- 决策的合理性\n- 中间步骤的正确性\n\n**工具使用**：\n- 工具选择的准确性\n- 参数生成的正确性\n\n**效率指标**：\n- 响应时间\n- 资源消耗\n\n常用评估方法包括人工评估、标准基准测试和自动指标计算。"},
    {"instruction": "什么是 Agent 的角色定义？", "input": "", "output": "Agent 的角色定义是指为 Agent 设定特定的身份、目标和行为准则：\n\n**角色类型**：\n- **专家型**：特定领域的专业知识\n- **助手型**：提供帮助和支持\n- **创意型**：生成创意内容\n- **分析型**：进行数据分析和推理\n\n**角色定义要素**：\n1. 角色名称和身份\n2. 专业领域\n3. 行为准则\n4. 语言风格\n5. 能力边界\n\n清晰的角色定义能让 Agent 的行为更加一致和专业。"},
    {"instruction": "如何实现多 Agent 协作？", "input": "", "output": "多 Agent 协作需要解决以下关键问题：\n\n**角色分配**：\n- 根据任务分配不同角色\n- 定义角色间的职责边界\n\n**通信机制**：\n- 消息传递协议\n- 共享状态管理\n- 冲突解决策略\n\n**协调策略**：\n- 集中式协调\n- 去中心化协调\n- 市场机制协调\n\n常见模式包括：领导者-追随者模式、专家协作模式、分工协作模式。"},
]

print(f"\n新增 {len(agent_topics)} 条 Agent 相关数据")

# 合并数据
combined = data + agent_topics

# 保存
with open(r"D:\LLaMA-Factory\data\merged_sft_data_augmented.jsonl", 'w', encoding='utf-8') as f:
    for item in combined:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"\n✅ 增强后数据已保存，共 {len(combined)} 条")
