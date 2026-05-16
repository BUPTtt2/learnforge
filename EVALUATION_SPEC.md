# RAG系统评估指标规范

## 1. 评估指标架构

### 1.1 检索层评估指标 (Retrieval Evaluation)

#### 1.1.1 相关性指标
| 指标名称 | 计算方法 | 取值范围 | 说明 |
|---------|---------|---------|------|
| `similarity_score` | 余弦相似度 | [0, 1] | 向量检索的相似度分数 |
| `keyword_match_rate` | 匹配关键词数 / 查询总词数 | [0, 1] | 关键词匹配程度 |
| `semantic_relevance` | 综合相似度和匹配率 | [0, 1] | 加权综合评分 |

#### 1.1.2 召回指标
| 指标名称 | 计算方法 | 取值范围 | 说明 |
|---------|---------|---------|------|
| `recall@k` | 相关文档在Top-K中的比例 | [0, 1] | K=3,5,10 |
| `hit_rate` | 至少命中1个相关文档的比例 | [0, 1] | 二元命中指标 |
| `mrr` | 首个相关文档排名的倒数均值 | [0, 1] | Mean Reciprocal Rank |

#### 1.1.3 排序质量指标
| 指标名称 | 计算方法 | 取值范围 | 说明 |
|---------|---------|---------|------|
| `ndcg@k` | 折损累计增益 | [0, 1] | K=3,5,10 |
| `position_bias` | 前排结果质量权重 | [0, 1] | 位置偏差校正 |

### 1.2 生成层评估指标 (Generation Evaluation)

#### 1.2.1 答案质量指标
| 指标名称 | 计算方法 | 取值范围 | 说明 |
|---------|---------|---------|------|
| `answer_relevance` | 答案与问题的相关性 | [0, 1] | 基于嵌入相似度 |
| `retrieval_match_rate` | 答案引用检索内容的比例 | [0, 1] | 答案对检索的利用程度 |
| `completeness` | 答案完整程度 | [0, 1] | 是否涵盖问题的各个方面 |

#### 1.2.2 用户反馈指标
| 指标名称 | 计算方法 | 取值范围 | 说明 |
|---------|---------|---------|------|
| `user_rating` | 用户1-5星评分 | [1, 5] | 直接用户反馈 |
| `user_feedback_score` | 正负反馈转换为分数 | [-1, 1] | thumbs up/down |
| `feedback_weighted_score` | 综合评分和反馈的加权分数 | [0, 1] | 动态调整 |

### 1.3 反馈纳入评估机制

```
最终质量分 = α × 生成质量分 + β × 用户反馈分

其中:
- α + β = 1.0
- α, β 可动态调整
- 反馈越多，β权重越高（置信度提升）
```

## 2. 评估指标数据结构

### 2.1 检索评估结果
```python
class RetrievalMetrics:
    query: str
    top_k: int
    results: List[RetrievalResult]

    metrics:
        - avg_similarity: float
        - keyword_match_rate: float
        - recall@k: Dict[int, float]
        - hit_rate: float
        - mrr: float
        - ndcg@k: Dict[int, float]
```

### 2.2 生成评估结果
```python
class GenerationMetrics:
    query: str
    answer: str
    retrieved_contexts: List[str]

    metrics:
        - answer_relevance: float
        - retrieval_match_rate: float
        - completeness: float

    feedback:
        - user_rating: Optional[int]
        - user_feedback: Optional[str]
        - feedback_timestamp: datetime

    combined_score: float
```

### 2.3 综合评估结果
```python
class ComprehensiveMetrics:
    session_id: str
    timestamp: datetime

    retrieval_metrics: RetrievalMetrics
    generation_metrics: GenerationMetrics

    overall_score: float  # 综合检索和生成
    improvement_suggestions: List[str]
```

## 3. 实现优先级

### 第一阶段（立即实现）
1. ✅ 检索层基础指标：相似度分数、关键词匹配率
2. ✅ 生成层基础指标：答案相关性、检索匹配率
3. ✅ 用户反馈收集机制

### 第二阶段（后续实现）
1. 高级排序指标：NDCG、MRR
2. 答案完整性评估
3. 实时反馈调整机制

## 4. 反馈集成策略

### 4.1 即时反馈
- 每次交互后收集用户反馈
- 反馈立即影响同会话的后续生成

### 4.2 历史反馈
- 累计历史反馈更新全局质量参数
- 识别常见问题模式

### 4.3 反馈权重自适应
```
初始权重: α=0.8, β=0.2
反馈积累: 随着反馈增加，β逐渐提升至0.5
高质量反馈: 权重大，反馈少：权重小
```
