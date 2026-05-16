"""添加更多高质量 SFT 数据"""

import json

# 新添加的数据
new_data = [
    # ===== Agent 规划方法 =====
    {
        "instruction": "解释 Agent 的 LLM Compiler 规划方法",
        "input": "",
        "output": "LLM Compiler 是一种高效的 Agent 规划方法，核心思想是将复杂任务分解为可并行执行的子任务。\n\n**工作原理**：\n1. **任务分解**：将复杂任务解析为多个独立子任务\n2. **依赖分析**：识别子任务间的依赖关系\n3. **并行调度**：无依赖的子任务可以并行执行\n4. **结果汇总**：合并所有子任务的结果\n\n**优势**：\n- 提高执行效率\n- 支持复杂任务的高效处理\n- 自动处理任务依赖\n\n**适用场景**：\n- 需要调用多个工具的复杂任务\n- 需要多步骤推理的分析任务\n- 需要并行处理的批量任务"
    },
    {
        "instruction": "什么是 Agent 的 Tree of Thoughts 方法？",
        "input": "",
        "output": "Tree of Thoughts（ToT）是一种启发式搜索方法，让 Agent 能够探索多种推理路径。\n\n**核心思想**：\n1. **分支扩展**：在每个决策点生成多个可能的推理路径\n2. **前瞻评估**：评估每条路径的可行性\n3. **回溯搜索**：如果某条路径失败，可以回溯尝试其他路径\n4. **深度优先搜索**：优先探索最有希望的路径\n\n**实现方式**：\n- 使用 BFS 或 DFS 搜索策略\n- 维护候选路径的优先级队列\n- 支持剪枝策略减少搜索空间\n\n**优势**：\n- 提高复杂推理任务的成功率\n- 支持探索多种解决方案\n- 能够处理需要试错的任务"
    },
    {
        "instruction": "如何实现 Agent 的工具选择机制？",
        "input": "",
        "output": "Agent 的工具选择机制是决定何时调用工具以及调用哪个工具的核心能力。\n\n**实现步骤**：\n1. **工具描述**：为每个工具提供详细的自然语言描述\n2. **意图识别**：分析用户请求，识别需要调用工具的意图\n3. **工具匹配**：根据意图匹配最合适的工具\n4. **参数生成**：生成工具调用所需的参数\n5. **结果解析**：解析工具返回的结果\n\n**关键技术**：\n- Prompt Engineering：设计有效的工具选择提示\n- Few-shot Learning：提供工具调用示例\n- 强化学习：通过奖励机制优化工具选择\n\n**评估指标**：\n- 工具选择准确率\n- 参数生成准确率\n- 任务完成率"
    },
    
    # ===== Transformer 架构 =====
    {
        "instruction": "解释 MHA、GQA、MQA 的区别",
        "input": "",
        "output": "MHA（多头注意力）、GQA（分组查询注意力）和 MQA（多查询注意力）是三种不同的注意力机制实现方式。\n\n**MHA（Multi-Head Attention）**：\n- 每个头有独立的 Q、K、V 矩阵\n- 计算复杂度高，但表达能力强\n- 适用于小模型或需要高精度的场景\n\n**GQA（Grouped Query Attention）**：\n- 将多个头分组共享 K、V 矩阵\n- 平衡计算效率和模型效果\n- 是 MHA 和 MQA 的折中方案\n- 被 GPT-3.5/4 和 Qwen 系列采用\n\n**MQA（Multi-Query Attention）**：\n- 所有头共享同一个 K、V 矩阵\n- 最高的计算效率\n- 但可能损失一些表达能力\n- 适用于推理阶段的优化\n\n**选择建议**：\n- 训练阶段：使用 MHA 或 GQA\n- 推理阶段：使用 GQA 或 MQA\n- 内存受限场景：优先考虑 GQA"
    },
    {
        "instruction": "什么是 RoPE 位置编码？",
        "input": "",
        "output": "RoPE（Rotary Position Embedding）是一种动态位置编码方法，通过旋转操作将位置信息注入到注意力计算中。\n\n**核心公式**：\n```\nQ_rot = Q * cos(mθ) + rotate(Q) * sin(mθ)\nK_rot = K * cos(mθ) + rotate(K) * sin(mθ)\n```\n\n**关键特性**：\n1. **相对位置编码**：编码相对位置而非绝对位置\n2. **外推能力**：模型可以处理训练时未见过的更长序列\n3. **无额外参数**：不增加模型参数数量\n4. **复杂度不变**：不增加计算复杂度\n\n**实现细节**：\n- θ 是预定义的频率参数\n- rotate 操作是将向量的偶数位置和奇数位置交换\n- 支持线性和非线性插值外推\n\n**优势**：\n- 提升长文本处理能力\n- 支持上下文长度外推\n- 保持模型效率"
    },
    {
        "instruction": "SwiGLU 激活函数的优势是什么？",
        "input": "",
        "output": "SwiGLU（Swish-Gated Linear Unit）是一种门控激活函数，结合了 Swish 激活和线性门控机制。\n\n**公式**：\n```\nSwiGLU(x) = Swish(xW1 + b1) * (xW2 + b2)\n```\n\n**与其他激活函数的对比**：\n\n| 激活函数 | 优点 | 缺点 |\n|---------|------|------|\n| ReLU | 简单高效 | 存在死亡神经元问题 |\n| GELU | 平滑、表现好 | 计算稍慢 |\n| SwiGLU | 门控机制、表达能力强 | 计算复杂度较高 |\n\n**优势**：\n1. **门控机制**：通过门控动态调整信息流动\n2. **自适应激活**：根据输入动态调整激活强度\n3. **表达能力强**：能够学习更复杂的模式\n4. **梯度稳定**：避免梯度消失问题\n\n**应用场景**：\n- 大型语言模型的前馈网络\n- 需要高精度的推理任务\n- 复杂模式学习任务"
    },
    
    # ===== RAG 技术 =====
    {
        "instruction": "RAG 检索策略有哪些？",
        "input": "",
        "output": "RAG（检索增强生成）的检索策略直接影响最终生成质量，常用策略包括：\n\n**1. 语义检索**：\n- 使用向量相似度匹配\n- 基于语义理解检索\n- 适用于开放域问答\n\n**2. 关键词检索**：\n- 基于 BM25 等传统检索算法\n- 精确匹配关键词\n- 适用于文档密集型场景\n\n**3. 混合检索**：\n- 结合语义检索和关键词检索\n- 取两者的并集或加权融合\n- 平衡召回率和精确率\n\n**4. 分层检索**：\n- 先粗粒度检索候选文档\n- 再细粒度检索相关段落\n- 提高检索效率和精度\n\n**5. 多模态检索**：\n- 支持文本、图像、音频等多模态数据\n- 跨模态语义理解\n- 适用于多模态问答场景\n\n**优化方向**：\n- 使用重排序模型提升检索精度\n- 动态调整检索参数\n- 结合上下文信息"
    },
    {
        "instruction": "如何评估 RAG 系统的性能？",
        "input": "",
        "output": "评估 RAG 系统需要从多个维度进行：\n\n**1. 检索质量**：\n- 召回率：正确文档被检索到的比例\n- 精确率：检索到的文档中有多少是相关的\n- NDCG：归一化折损累计增益\n\n**2. 生成质量**：\n- 事实一致性：生成内容与参考文档的一致性\n- 相关性：回答与问题的相关性\n- 完整性：是否覆盖所有关键点\n\n**3. 端到端指标**：\n- 问答准确率\n- 人类评估分数\n- 推理速度\n\n**4. 常用数据集**：\n- MSMARCO：大规模检索数据集\n- BEIR：跨域检索基准\n- HotpotQA：多跳推理问答\n\n**评估方法**：\n1. 自动评估：使用指标如 R@k、MRR、BLEU\n2. 人工评估：由标注者评分\n3. A/B 测试：对比不同配置的效果"
    },
    
    # ===== 微调技术 =====
    {
        "instruction": "LoRA 和 QLoRA 的区别是什么？",
        "input": "",
        "output": "LoRA 和 QLoRA 都是参数高效微调方法，但在实现方式和适用场景上有所不同。\n\n**LoRA（Low-Rank Adaptation）**：\n- 在原始权重矩阵上添加低秩分解矩阵\n- 只训练低秩矩阵，冻结原始权重\n- 秩 r 通常取 8-64\n- 需要完整的模型权重\n\n**QLoRA（Quantized LoRA）**：\n- 在量化后的模型上应用 LoRA\n- 通常使用 4-bit 或 8-bit 量化\n- 显著减少显存占用\n- 适合资源受限场景\n\n**对比**：\n\n| 特性 | LoRA | QLoRA |\n|------|------|-------|\n| 量化 | 否 | 是（4-bit） |\n| 显存占用 | 高 | 低 |\n| 精度损失 | 无 | 轻微 |\n| 适用场景 | 显存充足 | 显存受限 |\n| 模型大小 | 完整模型 | 量化模型 |\n\n**选择建议**：\n- 如果有足够显存（>16GB）：使用 LoRA\n- 如果显存有限（8GB左右）：使用 QLoRA\n- 两者都能有效提升任务性能"
    },
    {
        "instruction": "什么是 PEFT 方法？",
        "input": "",
        "output": "PEFT（Parameter-Efficient Fine-Tuning）是一类参数高效微调方法的总称，旨在用少量可训练参数实现有效的模型微调。\n\n**常见 PEFT 方法**：\n\n**1. LoRA**：\n- 低秩矩阵注入\n- 适用于 Transformer 注意力层\n- 最常用的 PEFT 方法\n\n**2. Adapter**：\n- 在 Transformer 层中插入小型网络\n- 增加少量参数\n- 对模型结构有一定侵入性\n\n**3. Prefix Tuning**：\n- 优化前缀向量\n- 不修改模型权重\n- 适合生成任务\n\n**4. Prompt Tuning**：\n- 优化软提示嵌入\n- 参数最少\n- 适用于小数据集\n\n**5. BitFit**：\n- 只微调偏置项\n- 参数最少\n- 效果相对较弱\n\n**选择原则**：\n- 数据集较小：使用 Prompt Tuning\n- 需要较好效果：使用 LoRA\n- 需要跨任务迁移：使用 Adapter\n- 资源极度受限：使用 BitFit"
    },
    
    # ===== 推理优化 =====
    {
        "instruction": "什么是 Speculative Decoding？",
        "input": "",
        "output": "Speculative Decoding（投机解码）是一种加速大模型推理的技术，通过使用小模型辅助生成来减少大模型的计算量。\n\n**工作原理**：\n1. **草稿模型**：使用小模型快速生成多个候选 token\n2. **验证阶段**：大模型验证这些候选 token\n3. **接受或拒绝**：如果验证通过，接受多个 token；否则只接受第一个正确的 token\n4. **重复**：继续直到生成结束\n\n**关键参数**：\n- 草稿模型大小：通常是大模型的 1/4 到 1/10\n- 候选 token 数量：通常取 3-5\n- 接受率：影响加速比的关键指标\n\n**加速效果**：\n- 理论加速比：可达 2-3 倍\n- 实际加速比：1.5-2 倍（取决于接受率）\n- 质量损失：通常小于 1%（困惑度）\n\n**适用场景**：\n- 高延迟敏感场景\n- 需要批量处理的服务\n- 资源受限的部署环境"
    },
    {
        "instruction": "如何优化大模型的推理速度？",
        "input": "",
        "output": "优化大模型推理速度需要从多个层面入手：\n\n**1. 模型层面**：\n- 量化：4-bit/8-bit 量化\n- 蒸馏：训练小模型模仿大模型\n- 剪枝：移除冗余参数\n\n**2. 推理引擎**：\n- 使用优化框架：vLLM、TGI、TensorRT-LLM\n- KV Cache 优化：PagedAttention\n- 算子融合：合并多个操作\n\n**3. 并行策略**：\n- 张量并行：拆分模型到多个 GPU\n- 流水线并行：按层划分到多个 GPU\n- 动态批处理：合并多个请求\n\n**4. 部署优化**：\n- 使用高性能硬件：GPU、TPU\n- 优化内存访问：数据预取、缓存\n- 使用异步推理：减少等待时间\n\n**5. 算法优化**：\n- Speculative Decoding\n- MQA/GQA 注意力\n- 动态停止条件\n\n**常用工具**：\n- vLLM：高吞吐量推理\n- TGI：HuggingFace 推理服务\n- ONNX Runtime：跨平台推理"
    },
    
    # ===== 对齐技术 =====
    {
        "instruction": "RLHF 和 DPO 的区别是什么？",
        "input": "",
        "output": "RLHF（强化学习人类反馈）和 DPO（直接偏好优化）是两种主流的大模型对齐方法。\n\n**RLHF（Reinforcement Learning from Human Feedback）**：\n\n**流程**：\n1. 收集人类偏好数据\n2. 训练奖励模型（RM）\n3. 使用强化学习优化策略\n4. 迭代优化\n\n**优势**：\n- 效果好\n- 成熟的技术栈\n\n**缺点**：\n- 复杂，需要多阶段训练\n- 不稳定，容易模式崩溃\n- 计算成本高\n\n**DPO（Direct Preference Optimization）**：\n\n**流程**：\n1. 收集偏好数据（成对比较）\n2. 直接优化偏好损失\n3. 单阶段训练完成\n\n**优势**：\n- 简单，单阶段训练\n- 稳定，不易崩溃\n- 计算效率高\n\n**缺点**：\n- 理论基础相对较新\n- 某些场景效果略逊于 RLHF\n\n**对比**：\n\n| 特性 | RLHF | DPO |\n|------|------|-----|\n| 训练阶段 | 多阶段 | 单阶段 |\n| 稳定性 | 较低 | 较高 |\n| 计算成本 | 高 | 低 |\n| 实现复杂度 | 高 | 低 |\n\n**选择建议**：\n- 追求极致效果：RLHF\n- 追求效率和稳定性：DPO\n- 资源受限：DPO"
    },
    
    # ===== 评估指标 =====
    {
        "instruction": "常用的大模型评估指标有哪些？",
        "input": "",
        "output": "评估大模型需要使用多种指标，涵盖不同维度：\n\n**1. 语言建模指标**：\n- Perplexity（PPL）：困惑度，衡量预测下一个 token 的能力\n- BLEU：机器翻译评估指标\n- ROUGE：文本摘要评估指标\n- METEOR：综合评估指标\n\n**2. 推理能力指标**：\n- GSM8K：数学推理\n- MMLU：多任务理解\n- HumanEval：代码生成\n- MBPP：Python 代码生成\n\n**3. 事实准确性指标**：\n- FactScore：事实一致性\n- TruthfulQA：真实性\n- FEVER：事实核查\n\n**4. 安全指标**：\n- SafetyBench：安全性评估\n- RealToxicityPrompts：毒性检测\n- BiasEval：偏见检测\n\n**5. 效率指标**：\n- 推理延迟\n- 吞吐量\n- 显存占用\n\n**评估框架**：\n- HuggingFace Evaluate\n- OpenAI Evals\n- EleutherAI LM Evaluation Harness\n\n**评估策略**：\n- 使用多个基准测试\n- 结合人工评估\n- 关注特定任务性能"
    }
]

print(f"新增 {len(new_data)} 条数据")

# 读取现有增强数据
with open(r"D:\LLaMA-Factory\data\merged_sft_data_augmented.jsonl", 'r', encoding='utf-8') as f:
    existing_data = [json.loads(line) for line in f if line.strip()]

print(f"现有数据: {len(existing_data)} 条")

# 合并数据
combined = existing_data + new_data

# 去重
seen = set()
unique_data = []
for item in combined:
    key = item['instruction']
    if key not in seen:
        seen.add(key)
        unique_data.append(item)

print(f"去重后: {len(unique_data)} 条")

# 保存
with open(r"D:\LLaMA-Factory\data\merged_sft_data_final.jsonl", 'w', encoding='utf-8') as f:
    for item in unique_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"\n✅ 最终数据已保存: merged_sft_data_final.jsonl")
