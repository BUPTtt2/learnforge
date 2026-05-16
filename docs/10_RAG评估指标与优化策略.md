# RAG评估指标与优化策略

## 一、RAG系统架构

### 1.1 三种RAG模式

| RAG模式 | 功能 | 来源 |
|---------|------|------|
| **本地RAG (search_local)** | 向量搜索 + 关键词混合 | Chroma 向量库 |
| **外部RAG (search_external)** | 联网搜索 | Tavily 搜索引擎 |
| **混合RAG (hybrid_search)** | 智能决策是否联网 | 本地 + 外部 |

### 1.2 混合搜索的决策逻辑

```
用户提问 → 先搜本地 RAG
    │
    ▼
评估检索质量 (quality_score)
    │
    ├─ 本地无结果 → 必须联网
    ├─ quality_score < 0.5 → 联网补充
    ├─ avg_vector_score < 0.3 → 联网补充
    └─ 无高相关结果 (vector < 0.5) → 联网
    │
    └─ 不满足 → 只用本地结果
    │
    ▼
联网搜索结果自动添加到本地知识库 (auto_add_to_knowledge)
```

### 1.3 分数计算

- **向量分数** = 1 / (1 + distance)
- **关键词分数** = 匹配词数 / 总词数
- **最终分数** = 向量×0.6 + 关键词×0.4

---

## 二、RAG评估指标

### 2.1 检索层指标 (RetrievalMetrics)

| 指标 | 计算方式 | 含义 | 目标值 |
|------|---------|------|--------|
| **avg_similarity** | 平均相似度分数 | 检索结果的整体相关性 | ≥ 0.6 |
| **keyword_match_rate** | 关键词匹配率 | 检索结果与查询的关键词重叠度 | ≥ 0.4 |
| **recall@k** | Recall@3/5/10 | topk结果包含多少相关文档 | @3≥0.7, @5≥0.85 |
| **hit_rate** | 是否命中至少1条相关 | 0或1 | ≥ 0.9 |
| **mrr** | Mean Reciprocal Rank | 第一个相关结果的倒数位置 | ≥ 0.7 |
| **ndcg@k** | Normalized Discounted Cumulative Gain | 考虑排序的归一化增益 | @3≥0.6, @5≥0.7 |

### 2.2 生成层指标 (GenerationMetrics)

| 指标 | 计算方式 | 含义 | 目标值 |
|------|---------|------|--------|
| **answer_relevance** | 答案与query的embedding相似度 | 答案是否切题 | ≥ 0.7 |
| **retrieval_match_rate** | 答案与检索内容的重叠率 | 答案是否用到了检索结果 | ≥ 0.5 |
| **completeness** | 关键词覆盖率 + 检索提示覆盖率 | 答案是否完整 | ≥ 0.6 |
| **combined_score** | 0.8*base + 0.2*反馈分 | 综合得分 | ≥ 0.65 |

### 2.3 综合指标

- **overall_score** = 0.4*retrieval + 0.6*generation

---

## 三、提升召回精度的优化策略

### 3.1 调整检索参数

| 参数 | 当前值 | 建议调整 | 预期效果 |
|------|--------|---------|---------|
| **top_k 候选数** | local_k*3 | 增加到4-5倍 | 召回更全面，再排序选优 |
| **向量/关键词权重** | 0.6/0.4 | 可调0.7/0.3 或 0.5/0.5 | 适配不同类型查询 |
| **min_score过滤** | 0.3 | 降低到0.2 | 提升召回（可能引入噪声） |
| **quality_threshold** | 0.5 | 降低到0.4 | 更容易触发外部搜索 |
| **vector_threshold** | 0.3 | 可调0.2-0.4 | 控制本地检索质量要求 |

### 3.2 优化文档分块

| 参数 | 当前值 | 建议 |
|------|--------|------|
| **chunk_size** | 512 | 根据文档类型可调384-768 |
| **chunk_overlap** | 50 | 可调30-100（防止关键信息在边界） |
| **分块方式** | RecursiveCharacterTextSplitter | 考虑语义分块（按段落/章节） |

### 3.3 查询改写 (Query Rewriting)

#### 方案1：Query Expansion
- 用LLM扩展query为多个变体
- 所有变体分别搜索，结果合并去重
- 适用场景：查询表述不够完整

#### 方案2：HyDE (Hypothetical Document Embedding)
- 先用LLM生成一个假设性答案
- 用这个假设答案去检索
- 适用场景：检索结果不够相关

### 3.4 重排序 (Rerank)

- 候选召回后，用更轻量的模型再排序
- 候选数：先召回10-20条，再排序到topk
- 可选模型：
  - CrossEncoder（效果好但慢）
  - BM25 + 向量混合打分（平衡）
  - 本地小模型（快）

### 3.5 知识库补充策略

- **auto_add_to_knowledge=true**：自动把联网搜索结果加入本地库
- 定期用评估脚本检查，缺什么补什么
- 可手动添加优质文档

---

## 四、数据流转

### 4.1 文档存储流程

```
add_document(content)
    │
    ▼
split_document()  // chunk_size=512, overlap=50
    │
    ▼
embed_query()  // 每块分别向量化
    │
    ▼
存入 Chroma 向量库 (learnforge_knowledge collection)
    │
    └─ 同时写入 metadata（chunk_index, total_chunks等）
```

### 4.2 检索流程

```
search_local(query)
    │
    ▼
向量化 query
    │
    ▼
Chroma 搜索 k*3 条候选
    │
    ▼
混合分数计算 (vector*0.6 + keyword*0.4)
    │
    ▼
重排序，返回 topk
```

---

## 五、相关文件

| 文件 | 功能 |
|------|------|
| `utils/rag.py` | RAG系统核心实现 |
| `utils/evaluation.py` | RAG评估指标库 |
| `test_rag.py` | RAG基础测试 |
| `test_evaluation.py` | RAG评估测试 |
| `eval_query.py` | 查询评估脚本 |
