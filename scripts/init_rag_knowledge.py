#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rag import rag_system

# ==================== 西班牙语学习知识库 ====================

spanish_knowledge = [
    {
        "content": """# 西班牙语发音基础

## 字母发音
西班牙语共有27个字母，其中5个元音(a, e, i, o, u)和22个辅音。

### 元音发音
- a: 发音如"啊"，开口较大
- e: 发音如"诶"，口型较小
- i: 发音如"伊"，口型最窄
- o: 发音如"喔"，嘴唇呈圆形
- u: 发音如"乌"，嘴唇收圆

### 辅音发音特点
- b/v: 在词首发[b]音，在词中发[β]音（双唇摩擦音）
- c/g: 在e/i前发软音[θ]/[x]，在a/o/u前发硬音[k]/[g]
- d: 在词首发[d]音，在词中发[ð]音（齿间摩擦音）
- ll/ñ: ll发[ʝ]音，ñ发[ɲ]音

## 重音规则
1. 词尾是元音、n或s时，重音在倒数第二个音节
2. 词尾是其他辅音时，重音在最后一个音节
3. 有重音符号(´)的音节为重读音节

## 连读现象
- 元音连读：两个相邻元音之间平滑过渡
- 辅音连读：如"buenos días"读作"buenosdías"

## 专四考试重点
- 听写部分重点考察重音和连读
- 听力部分注意区分b/v、c/z、g/j的发音""",
        "metadata": {"category": "spanish", "subcategory": "pronunciation", "exam": "专四"}
    },
    {
        "content": """# 西班牙语核心词汇

## 分类词汇
### 日常用语
- ser/estar: 都是"是"，ser表本质，estar表状态
- tener: 有；表示身体状况（tener hambre）
- hacer: 做；表示天气（hace calor）
- ir: 去；表示将来（voy a estudiar）
- querer: 想要；表示意愿（quiero aprender）

### 高频动词变位
- 现在时：hablo, hablas, habla, hablamos, habláis, hablamos
- 过去时：hablé, hablaste, habló, hablamos, hablasteis, hablaron
- 命令式：habla, hable, hablemos, hablad, hablen

## 专四词汇要求
- 大纲要求掌握约6000个词汇
- 重点掌握动词短语和固定搭配
- 注意近义词辨析（如saber/conocer）

## 记忆技巧
- 词根词缀记忆法
- 联想记忆法
- 语境记忆法""",
        "metadata": {"category": "spanish", "subcategory": "vocabulary", "exam": "专四"}
    },
    {
        "content": """# 西班牙语基础语法

## 名词与冠词
- 名词分阴阳性：-o结尾多为阳性，-a结尾多为阴性
- 冠词配合名词变化：el/la, los/las, un/una, unos/unas

## 形容词
- 形容词放在名词后面
- 形容词与名词保持性数一致
- 部分形容词放在名词前改变含义（如bueno/a）

## 动词时态
### 陈述式
- 现在时：描述经常性动作
- 简单过去时：描述一次性完成动作
- 未完成过去时：描述过去持续状态或背景
- 现在完成时：过去动作对现在的影响

### 虚拟式
- 表示愿望、怀疑、可能性
- 常用在que引导的从句中
- 需要记忆虚拟式变位规则

## 专四语法重点
- 时态一致问题
- 虚拟式用法
- 代词式动词
- 命令式变位""",
        "metadata": {"category": "spanish", "subcategory": "grammar", "exam": "专四"}
    },
    {
        "content": """# 西班牙语口语练习

## 日常对话场景
### 问候与介绍
- ¿Cómo estás? - Estoy bien, gracias.
- ¿Qué tal? - Muy bien.
- Me llamo... - Encantado/a de conocerte.

### 点餐
- ¿Qué recomiendas? - Recomiendo el paella.
- Quisiera... - ¿Con qué lo acompaña?

### 购物
- ¿Cuánto cuesta? - Cuesta 10 euros.
- ¿Tiene en talla M? - Sí, aquí tiene.

## 口语考试技巧
- 发音清晰，注意重音
- 使用连接词（pero, entonces, además）
- 保持自然语速
- 遇到不会的词可以换一种说法

## 专四口语考试
- 总分20分
- 包含朗读、问答、情景对话
- 重点考察发音和流利度""",
        "metadata": {"category": "spanish", "subcategory": "speaking", "exam": "专四"}
    },
    {
        "content": """# 西班牙语阅读与写作

## 阅读理解技巧
- 快速浏览了解大意
- 注意关键词和连接词
- 理解长难句的结构
- 推断作者意图

## 专四阅读题型
- 选择题（主旨题、细节题、推断题）
- 完形填空
- 句子排序

## 写作技巧
### 应用文写作
- 书信格式（日期、称呼、正文、结尾）
- 邮件写作规范
- 通知和便条

### 议论文写作
- 明确论点
- 分点论述
- 使用连接词
- 结论总结

## 专四写作评分标准
- 内容完整（40%）
- 语言准确（30%）
- 结构清晰（20%）
- 卷面整洁（10%）""",
        "metadata": {"category": "spanish", "subcategory": "reading_writing", "exam": "专四"}
    }
]

# ==================== Agent相关知识库 ====================

agent_knowledge = [
    {
        "content": """# Agent智能助手

## 什么是Agent
Agent（智能代理）是一种能够感知环境、做出决策并执行动作的人工智能系统。
与传统程序不同，Agent具有自主性、反应性和主动性。

## Agent的核心组件
### 感知模块
- 接收用户输入
- 理解自然语言
- 提取关键信息

### 决策模块
- 分析用户需求
- 制定行动计划
- 选择合适策略

### 执行模块
- 调用工具
- 生成响应
- 反馈结果

## Agent的工作流程
1. 接收用户请求
2. 理解用户意图
3. 规划执行步骤
4. 调用相应工具
5. 生成并返回结果

## LearnForge Agent架构
- Commander：中心调度Agent
- Planning Agent：任务规划
- Generation Agent：内容生成""",
        "metadata": {"category": "agent", "subcategory": "introduction"}
    },
    {
        "content": """# Multi-Agent系统设计

## 为什么需要Multi-Agent
单一Agent难以处理复杂任务，需要多个专业Agent协同工作。

## 常见架构模式
### 层级模式（Hierarchical）
- 中心Agent协调
- 下层Agent执行具体任务
- 优点：结构清晰，易于管理
- 缺点：中心节点可能成为瓶颈

### P2P模式（Peer-to-Peer）
- Agent之间直接通信
- 优点：分布式，无单点故障
- 缺点：可能产生任务重复，难以确定终止点

### 中心化调度模式（推荐）
- Commander作为中央调度器
- 规划Agent和生成Agent分工明确
- 避免任务重复
- 明确任务终止条件

## LearnForge的Multi-Agent设计
```
Commander（调度中心）
├── Planning Agent（任务规划）
│   ├── 章节划分
│   └── 任务分解
└── Generation Agent（内容生成）
    ├── 内容生成
    └── 习题生成
```""",
        "metadata": {"category": "agent", "subcategory": "multi_agent"}
    },
    {
        "content": """# LangGraph工作流编排

## LangGraph简介
LangGraph是LangChain生态中的工作流编排框架，支持构建复杂的Agent应用。

## 核心概念
### State（状态）
- 定义工作流的共享状态
- 支持状态更新和传递

### Node（节点）
- 代表一个具体操作
- 可以是函数或Agent

### Edge（边）
- 连接节点
- 定义工作流执行路径

### Conditional Edge（条件边）
- 根据状态动态选择路径
- 支持分支逻辑

## LearnForge中的应用
- 任务规划流程
- 内容生成流程
- 学习评估流程

## 示例：简单学习流程
```
State: {learning_goal, current_chapter, content}
  │
  ▼
┌─────────────────┐
│ Planning Node   │ → 划分章节
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generation Node │ → 生成内容
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Evaluation Node │ → 评估效果
└─────────────────┘
```""",
        "metadata": {"category": "agent", "subcategory": "langgraph"}
    }
]

# ==================== LLM大语言模型知识 ====================

llm_knowledge = [
    {
        "content": """# 大语言模型基础

## 什么是LLM
LLM（Large Language Model）是大规模语言模型的简称，是一种基于深度学习的自然语言处理模型。

## 主流模型架构
### Transformer架构
- 核心是自注意力机制（Self-Attention）
- 能够处理长序列依赖
- 支持并行计算

### 常见模型
- GPT系列（OpenAI）：生成能力强
- Claude系列（Anthropic）：安全对齐好
- LLaMA系列（Meta）：开源可商用
- Qwen系列（阿里）：中文支持优秀

## 模型参数规模
- 小型：1B-7B 参数，适合本地部署
- 中型：7B-70B 参数，需要高配GPU
- 大型：70B+ 参数，需要多卡集群

## 本地部署方案
### Ollama
- 支持多种开源模型
- 一键安装使用
- 支持量化压缩

### vLLM
- 高吞吐量推理
- 支持PagedAttention

### llama.cpp
- CPU推理首选
- 支持4-bit量化
- 内存占用低""",
        "metadata": {"category": "llm", "subcategory": "introduction"}
    },
    {
        "content": """# 模型推理优化

## 为什么需要优化
大模型推理需要大量计算资源和内存，优化可以：
- 降低延迟，提升用户体验
- 减少资源消耗
- 支持更多并发用户

## 常见优化技术
### 量化（Quantization）
- 将FP32转换为INT8/INT4
- 显著降低内存占用
- 保持大部分模型能力

### 加速库
- vLLM：PagedAttention优化
- TensorRT-LLM：NVIDIA专用优化
- FlashAttention：注意力机制高效实现

### 批处理优化
- 连续批处理（Continuous Batching）
- 动态批处理（Dynamic Batching）

## 本项目优化实践
- 使用qwen3:4b量化模型
- 4-bit量化压缩
- Ollama本地推理""",
        "metadata": {"category": "llm", "subcategory": "optimization"}
    },
    {
        "content": """# 模型微调技术

## 什么是微调
微调（Fine-tuning）是在预训练模型基础上，用特定领域数据进一步训练，使模型适应特定任务。

## 微调方法对比
### Full Fine-tuning
- 更新所有参数
- 效果最好
- 资源消耗最大

### LoRA（推荐）
- Low-Rank Adaptation
- 只更新少量参数
- 训练效率高
- 资源需求低

### QLoRA
- LoRA + 量化
- 进一步降低资源需求
- 4-bit量化 + LoRA

## LoRA配置参数
- r（秩）：8-16为宜
- alpha：通常设为r的2倍
- target_modules：需要训练的层
- lora_dropout：防止过拟合

## 本项目微调计划
- 使用LoRA适配语言学习场景
- 收集西语学习专业数据
- 在8GB显存下可训练""",
        "metadata": {"category": "llm", "subcategory": "fine_tuning"}
    }
]

# ==================== RAG检索增强生成知识 ====================

rag_knowledge = [
    {
        "content": """# RAG检索增强生成

## RAG原理
RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术架构。

## 工作流程
1. 用户提问
2. 检索阶段：从知识库检索相关信息
3. 生成阶段：将检索结果作为上下文输入LLM
4. 返回生成的回答

## 核心组件
### 向量数据库
- 存储文档的向量表示
- 支持语义相似度检索
- 常用：ChromaDB, Milvus, Qdrant

### Embedding模型
- 将文本转换为向量
- 决定检索质量
- 推荐：all-MiniLM-L6-v2

### 检索策略
- 相似度检索
- 混合检索（本地+外部）
- 重排序（Rerank）

## RAG优势
- 知识可更新，无需重新训练
- 减少幻觉，提高准确性
- 可追溯信息来源
- 支持领域定制""",
        "metadata": {"category": "rag", "subcategory": "principle"}
    },
    {
        "content": """# RAG高级优化技术

## ChunkRAG：块级过滤
核心思想：对检索到的每个chunk进行相关性评估，过滤无关内容。

### 实现步骤
1. 动态语义切分文档
2. 检索top-k个相关chunk
3. 用LLM评估每个chunk的相关性
4. 过滤低相关性chunk
5. 用剩余chunk生成回答

### 优势
- 减少无关信息干扰
- 提高生成质量
- 降低幻觉

## 混合检索策略
### 本地知识库检索
- 领域专业知识
- 稳定可靠
- 无网络依赖

### 外部搜索检索
- 最新信息
- 补充知识
- 扩展视野

## 搜索结果过滤
### 基于相似度
- 设置最低相似度阈值
- 过滤噪声结果

### 基于关键词
- 检查关键词匹配度
- 提升相关性

### 基于LLM判断
- 让LLM评估相关性
- 最准确但成本高""",
        "metadata": {"category": "rag", "subcategory": "optimization"}
    },
    {
        "content": """# 向量数据库选型

## 主流向量数据库对比

### ChromaDB（当前使用）
- 轻量级，易于部署
- 本地文件存储
- 适合中小规模
- 免费开源

### Qdrant（生产推荐）
- 支持分布式部署
- 性能优秀
- 云服务可用
- 适合生产环境

### Milvus
- 完全开源
- 支持大规模数据
- 部署复杂
- 适合企业级

### Pinecone
- 云服务
- 无需运维
- 付费使用

## Embedding模型选择
### 轻量级（推荐本地部署）
- all-MiniLM-L6-v2：384维，快速准确
- bge-small-en：512维，中文支持

### 中等规模
- all-mpnet-base-v2：768维，效果更好
- gte-small：512维，多语言支持

### 选择建议
- 8GB显存：all-MiniLM-L6-v2
- 中文为主：bge-small-en
- 多语言：gte-small""",
        "metadata": {"category": "rag", "subcategory": "vector_db"}
    }
]

def init_knowledge_base():
    """初始化知识库"""
    print("[RAG] 开始初始化知识库...")

    stats = rag_system.get_collection_stats()
    print(f"[RAG] 当前知识库文档数: {stats['document_count']}")

    all_knowledge = spanish_knowledge + agent_knowledge + llm_knowledge + rag_knowledge

    print(f"[RAG] 准备添加 {len(all_knowledge)} 篇文档...")

    documents = [item["content"] for item in all_knowledge]
    metadatas = [item["metadata"] for item in all_knowledge]

    if rag_system.add_documents(documents, metadatas):
        print("[RAG] 知识添加成功")
    else:
        print("[RAG] 知识添加失败")

    stats = rag_system.get_collection_stats()
    print(f"[RAG] 知识库初始化完成，共 {stats['document_count']} 篇文档")
    print(f"[RAG] 块数统计: {stats.get('chunk_count', 'N/A')}")

    return stats

def clear_and_rebuild():
    """清空并重建知识库"""
    print("[RAG] 清空知识库...")
    if rag_system.clear_collection():
        print("[RAG] 知识库已清空")
    else:
        print("[RAG] 清空失败")
    return init_knowledge_base()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="清空并重建知识库")
    args = parser.parse_args()

    if args.rebuild:
        clear_and_rebuild()
    else:
        init_knowledge_base()