import json
import os
import sys
import time
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockContentGenerator:
    """Mock 内容生成器 - 使用预定义模板生成多样化数据"""

    TOPIC_TEMPLATES = {
        "Python": {
            "装饰器原理": """# Python 装饰器原理深度解析

## 一、核心概念

装饰器是一种设计模式，它允许在不修改函数代码的情况下扩展函数功能。

**装饰器本质**：函数作为参数传递，返回一个新函数。

## 二、基本实现

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@decorator
def hello():
    print("Hello World")
```

## 三、应用场景

1. **日志记录**：自动记录函数调用日志
2. **性能监控**：统计函数执行时间
3. **权限验证**：检查用户权限
4. **缓存装饰**：缓存函数返回值

## 四、高级特性

- 带参数的装饰器
- 类装饰器
- 装饰器叠加

## 面试要点

- `functools.wraps` 的作用
- 装饰器与闭包的关系
- 装饰器如何处理带参数的函数""",

            "生成器与迭代器": """# Python 生成器与迭代器

## 一、迭代器协议

```python
class MyIterator:
    def __init__(self, max_val):
        self.max_val = max_val
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.max_val:
            raise StopIteration
        self.current += 1
        return self.current
```

## 二、生成器函数

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

for num in fibonacci(10):
    print(num)
```

## 三、生成器表达式

```python
# 列表推导式（立即求值）
squares = [x**2 for x in range(10)]

# 生成器表达式（延迟求值）
squares_gen = (x**2 for x in range(10))
```

## 四、优势对比

| 特性 | 列表 | 生成器 |
|------|------|--------|
| 内存 | 全部加载 | 按需生成 |
| 速度 | 慢 | 快 |
| 适用 | 小数据集 | 大数据流 |""",

            "GIL机制详解": """# Python GIL 机制详解

## 一、什么是 GIL

GIL（Global Interpreter Lock）是 CPython 中的互斥锁，确保同一时刻只有一个线程执行 Python 字节码。

## 二、GIL 的影响

```python
import threading

count = 0

def increment():
    global count
    for _ in range(1000000):
        count += 1

threads = [threading.Thread(target=increment) for _ in range(4)]
```

## 三、突破 GIL 的方法

1. **多进程**：`multiprocessing` 模块
2. **C 扩展**：使用 C/C++ 编写性能关键代码
3. **异步编程**：`asyncio`（IO 密集型）
4. **其他解释器**：PyPy、Jython""",

            "并发编程 asyncio": """# Python asyncio 并发编程

## 一、协程基础

```python
import asyncio

async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    task1 = asyncio.create_task(fetch_data("https://api.example.com"))
    task2 = asyncio.create_task(fetch_data("https://api.example.org"))
    
    result1 = await task1
    result2 = await task2
    
    print(result1, result2)

asyncio.run(main())
```

## 二、事件循环

事件循环是 asyncio 的核心：
- 管理协程的执行
- 处理 IO 事件
- 调度任务

## 三、并发模式

1. **任务并发**：`asyncio.create_task()`
2. **等待所有**：`asyncio.gather()`
3. **超时控制**：`asyncio.wait_for()`""",

            "内存管理与垃圾回收": """# Python 内存管理与垃圾回收

## 一、内存分配机制

```
┌─────────────────────────────────────┐
│        Python 内存管理架构          │
├─────────────────────────────────────┤
│  Python 对象分配器 (PyMalloc)       │
├─────────────────────────────────────┤
│      操作系统内存管理器             │
└─────────────────────────────────────┘
```

## 二、引用计数

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2
```

## 三、垃圾回收算法

1. **引用计数**：立即回收
2. **标记清除**：处理循环引用
3. **分代回收**：按对象年龄分层"""
        },

        "JavaScript": {
            "事件循环": """# JavaScript 事件循环机制

## 一、核心概念

事件循环是 JavaScript 实现异步的核心机制。

```javascript
console.log('1');

setTimeout(() => {
    console.log('2');
}, 0);

Promise.resolve().then(() => {
    console.log('3');
});

console.log('4');
// 输出顺序: 1, 4, 3, 2
```

## 二、宏任务 vs 微任务

| 特性 | 宏任务 | 微任务 |
|------|--------|--------|
| 优先级 | 低 | 高 |
| 示例 | setTimeout | Promise |""",

            "闭包原理": """# JavaScript 闭包原理

## 一、什么是闭包

闭包是指函数能够访问其词法作用域之外的变量：

```javascript
function outer() {
    const message = "Hello";
    
    function inner() {
        console.log(message);
    }
    
    return inner;
}

const fn = outer();
fn();  // 输出: Hello
```

## 二、闭包的用途

1. **数据封装**：私有变量
2. **函数工厂**：批量生成函数
3. **回调函数**：异步操作""",

            "原型链与继承": """# JavaScript 原型链与继承

## 一、原型对象

```javascript
function Person(name) {
    this.name = name;
}

Person.prototype.sayHello = function() {
    console.log(`Hello, ${this.name}`);
};

const p1 = new Person("Alice");
p1.sayHello();
```

## 二、ES6 Class

```javascript
class Student extends Person {
    constructor(name, grade) {
        super(name);
        this.grade = grade;
    }
}
```"""
        },

        "AI": {
            "RAG 检索增强生成": """# RAG 检索增强生成详解

## 一、核心概念

RAG（Retrieval-Augmented Generation）是一种结合检索和生成的 AI 技术。

```python
from langchain.document_loaders import TextLoader
from langchain.vectorstores import Chroma

loader = TextLoader("docs/tech_doc.txt")
docs = loader.load_and_split()

db = Chroma.from_documents(docs)
```

## 二、实现流程

1. **加载文档** → 2. **创建向量数据库** → 3. **检索相关知识** → 4. **生成回答**

## 三、检索策略

- 语义检索：基于向量相似度
- 混合检索：关键词 + 语义""",

            "Agent 智能体架构": """# Agent 智能体架构设计

## 一、核心组件

```
┌─────────────────────────────────────────────┐
│               Agent 智能体                  │
├─────────────┬─────────────┬───────────────┤
│   Planner   │   Executor  │   Memory      │
└─────────────┴─────────────┴───────────────┘
```

## 二、关键技术

1. **ReAct 模式**：Reasoning + Action
2. **长短期记忆**：记忆机制
3. **工具调用**：API 调用能力""",

            "Transformer 注意力机制": """# Transformer 注意力机制

## 一、架构概览

Transformer 由编码器和解码器组成，核心是自注意力机制。

## 二、自注意力计算

```python
def scaled_dot_product_attention(Q, K, V):
    scores = Q @ K.transpose(-2, -1)
    attn_weights = scores.softmax(dim=-1)
    output = attn_weights @ V
    return output
```

## 三、多头注意力

多头注意力允许模型同时关注输入的不同部分。

## 四、位置编码

位置编码为模型提供序列的顺序信息。"""
        },

        "机器学习": {
            "梯度下降优化": """# 梯度下降优化算法

## 一、梯度下降原理

梯度下降是一种迭代优化算法：

```python
def gradient_descent(X, y, learning_rate=0.01, epochs=100):
    theta = np.zeros(X.shape[1])
    for _ in range(epochs):
        gradient = (1/m) * X.T @ (X @ theta - y)
        theta -= learning_rate * gradient
    return theta
```

## 二、优化变体

| 算法 | 特点 |
|------|------|
| SGD | 随机采样 |
| Adam | 自适应学习率 |
| Momentum | 加速收敛 |""",

            "神经网络正则化": """# 神经网络正则化技术

## 一、L2 正则化

```python
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu',
                         kernel_regularizer=tf.keras.regularizers.l2(0.01))
])
```

## 二、Dropout

```python
model.add(tf.keras.layers.Dropout(0.5))
```

## 三、早停法

```python
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=5
)
```""",

            "卷积神经网络": """# 卷积神经网络 (CNN)

## 一、卷积操作

```python
conv = nn.Conv2d(
    in_channels=3, out_channels=32,
    kernel_size=3, stride=1, padding=1
)
```

## 二、池化操作

```python
max_pool = nn.MaxPool2d(kernel_size=2, stride=2)
```

## 三、经典架构

- LeNet-5
- AlexNet
- ResNet
- Transformer"""
        },

        "数据库": {
            "B+树索引": """# B+树索引原理

## 一、B+树结构

B+树是一种平衡树，所有数据存储在叶子节点。

## 二、查询过程

```sql
SELECT * FROM users WHERE id = 15;
```

查询路径：根节点 → 中间节点 → 叶子节点

## 三、插入操作

插入时如果节点满，需要分裂节点并更新父节点。

## 四、B+树 vs B树

| 特性 | B树 | B+树 |
|------|-----|------|
| 数据存储 | 所有节点 | 仅叶子节点 |
| 范围查询 | 需要回溯 | 链表遍历 |""",

            "事务隔离级别": """# 数据库事务隔离级别

## 一、ACID 原则

| 特性 | 说明 |
|------|------|
| Atomicity | 原子性 |
| Consistency | 一致性 |
| Isolation | 隔离性 |
| Durability | 持久性 |

## 二、隔离级别对比

| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|------|------------|------|
| READ UNCOMMITTED | ✅ | ✅ | ✅ |
| READ COMMITTED | ❌ | ✅ | ✅ |
| REPEATABLE READ | ❌ | ❌ | ✅ |
| SERIALIZABLE | ❌ | ❌ | ❌ |""",

            "分布式事务": """# 分布式事务处理

## 一、CAP 定理

- Consistency（一致性）
- Availability（可用性）
- Partition Tolerance（分区容错性）

## 二、两阶段提交 (2PC)

1. **准备阶段**：协调者询问所有参与者
2. **提交阶段**：协调者决定提交或回滚

## 三、最终一致性

使用消息队列实现异步数据同步。"""
        },

        "系统设计": {
            "微服务架构": """# 微服务架构设计

## 一、架构对比

| 特性 | 单体架构 | 微服务架构 |
|------|----------|------------|
| 部署 | 单一单元 | 独立部署 |
| 扩展 | 整体扩展 | 按需扩展 |

## 二、服务间通信

- REST API
- gRPC
- 消息队列

## 三、关键技术

1. **服务发现**：Consul/Eureka
2. **API网关**：Kong/APISIX
3. **服务网格**：Istio"""
        },

        "网络": {
            "TCP 协议详解": """# TCP 协议详解

## 一、三次握手

```
客户端                     服务器
  │                          │
  │─── SYN ─────────────────>│
  │<── SYN+ACK ──────────────│
  │─── ACK ─────────────────>│
```

## 二、四次挥手

```
客户端                     服务器
  │                          │
  │─── FIN ─────────────────>│
  │<── ACK ─────────────────│
  │<── FIN ─────────────────│
  │─── ACK ─────────────────>│
```

## 三、滑动窗口

滑动窗口实现流量控制，提高网络利用率。

## 四、拥塞控制

- 慢启动
- 拥塞避免
- 快速重传
- 快速恢复"""
        },

        "安全": {
            "OAuth2.0 认证": """# OAuth2.0 认证协议

## 一、授权流程

```
用户 → 应用 → 授权服务器 → 资源服务器
```

## 二、授权模式

| 模式 | 适用场景 |
|------|----------|
| Authorization Code | Web应用 |
| Implicit | SPA/移动端 |
| Password | 信任应用 |

## 三、JWT 令牌

```python
import jwt

token = jwt.encode({'user_id': 1}, 'secret', algorithm='HS256')
```"""
        },

        "算法": {
            "动态规划": """# 动态规划详解

## 一、核心思想

动态规划是一种将复杂问题分解为子问题的方法。

## 二、解题步骤

1. **定义状态**：确定 dp[i] 的含义
2. **状态转移方程**：dp[i] = f(dp[i-1], ...)
3. **初始条件**：dp[0], dp[1] 的值
4. **计算顺序**：从前向后或从后向前

## 三、经典例题

### 斐波那契数列

```python
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

### 最长递增子序列

```python
def length_of_lis(nums):
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

## 四、动态规划类型

| 类型 | 特点 | 示例 |
|------|------|------|
| 线性 DP | 一维状态 | 斐波那契、LIS |
| 区间 DP | 区间状态 | 最长回文子串 |
| 背包 DP | 选择状态 | 0-1背包 |

## 五、优化技巧

1. 滚动数组优化空间
2. 二分查找优化时间
3. 状态压缩"""
        }
    }

    def generate_content(self, topic: str, sub_topic: str) -> str:
        if topic in self.TOPIC_TEMPLATES:
            if sub_topic in self.TOPIC_TEMPLATES[topic]:
                return self.TOPIC_TEMPLATES[topic][sub_topic]
        return self._generate_default_content(topic, sub_topic)

    def _generate_default_content(self, topic: str, sub_topic: str) -> str:
        return f"""# {topic} - {sub_topic}

## 一、核心概念

{topic}是一个重要的技术概念。

## 二、主要特点

1. **特点一**：{sub_topic}的核心特性
2. **特点二**：实际应用场景

## 三、实现方法

```python
# {topic} {sub_topic} 示例代码
def example():
    pass
```

## 四、应用场景

- 场景一：具体应用案例
- 场景二：行业实践

## 五、总结

{topic}的{sub_topic}是重要知识点。"""


class SFTDataQualityAssessor:
    """SFT 数据质量评估器"""

    def __init__(self):
        self.min_content_length = 300
        self.max_content_length = 8000

    def assess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        messages = data.get("messages", [])
        if len(messages) < 3:
            return {"score": 0, "level": "reject", "reasons": ["消息格式不完整"]}

        assistant_content = messages[-1].get("content", "")
        scores = []
        reasons = []

        length_score, length_reason = self._check_length(assistant_content)
        scores.append(length_score)
        reasons.append(length_reason)

        format_score, format_reason = self._check_format(assistant_content)
        scores.append(format_score)
        reasons.append(format_reason)

        code_score, code_reason = self._check_code(assistant_content)
        scores.append(code_score)
        reasons.append(code_reason)

        repeat_score, repeat_reason = self._check_repetition(assistant_content)
        scores.append(repeat_score)
        reasons.append(repeat_reason)

        diversity_score, diversity_reason = self._check_diversity(assistant_content)
        scores.append(diversity_score)
        reasons.append(diversity_reason)

        structure_score, structure_reason = self._check_structure(assistant_content)
        scores.append(structure_score)
        reasons.append(structure_reason)

        total_score = sum(scores) / len(scores) * 100

        if total_score >= 80:
            level = "accept"
        elif total_score >= 60:
            level = "revise"
        else:
            level = "reject"

        return {
            "score": round(total_score, 1),
            "level": level,
            "reasons": reasons,
            "details": {
                "length": length_score,
                "format": format_score,
                "code": code_score,
                "repeat": repeat_score,
                "diversity": diversity_score,
                "structure": structure_score
            }
        }

    def _check_length(self, content: str) -> Tuple[float, str]:
        length = len(content)
        if length < self.min_content_length:
            return 0.3, f"内容太短 ({length}字符)"
        elif length > self.max_content_length:
            return 0.7, f"内容过长 ({length}字符)"
        else:
            score = min(1.0, length / 1500)
            return score, f"长度正常 ({length}字符)"

    def _check_format(self, content: str) -> Tuple[float, str]:
        format_markers = ["#", "##", "**", "*", "1.", "2.", "- ", "```"]
        found_markers = sum(1 for marker in format_markers if marker in content)
        if found_markers >= 5:
            return 1.0, "格式丰富"
        elif found_markers >= 3:
            return 0.8, "格式基本合格"
        elif found_markers >= 1:
            return 0.5, "格式单一"
        else:
            return 0.2, "缺少格式标记"

    def _check_code(self, content: str) -> Tuple[float, str]:
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        code_length = sum(len(block) for block in code_blocks)
        code_ratio = code_length / len(content) if len(content) > 0 else 0
        if code_ratio >= 0.1:
            return 1.0, f"代码比例适中 ({code_ratio:.0%})"
        elif code_ratio > 0:
            return 0.6, f"代码比例较低 ({code_ratio:.0%})"
        else:
            return 0.5, "无代码块"

    def _check_repetition(self, content: str) -> Tuple[float, str]:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 3:
            return 0.5, "内容过短无法判断重复"
        unique_lines = len(set(lines))
        repeat_ratio = 1 - (unique_lines / len(lines))
        if repeat_ratio > 0.3:
            return 0.3, f"重复度较高 ({repeat_ratio:.0%})"
        else:
            return 1.0, f"重复度正常 ({repeat_ratio:.0%})"

    def _check_diversity(self, content: str) -> Tuple[float, str]:
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', content)
        if len(words) < 20:
            return 0.5, "内容过短无法评估"
        unique_words = set(word.lower() for word in words)
        diversity_ratio = len(unique_words) / len(words)
        if diversity_ratio >= 0.6:
            return 1.0, f"词汇多样 ({diversity_ratio:.0%})"
        else:
            return 0.7, f"词汇多样性一般 ({diversity_ratio:.0%})"

    def _check_structure(self, content: str) -> Tuple[float, str]:
        has_h1 = bool(re.search(r'^#\s+\S+', content, re.MULTILINE))
        has_h2 = bool(re.search(r'^##\s+\S+', content, re.MULTILINE))
        has_list = bool(re.search(r'^\s*[-*\d]+\s+\S', content, re.MULTILINE))
        structure_score = 0
        if has_h1:
            structure_score += 0.3
        if has_h2:
            structure_score += 0.3
        if has_list:
            structure_score += 0.4
        if structure_score >= 0.8:
            return 1.0, "结构完整"
        else:
            return 0.7, "结构基本合理"


class SFTDataDiagnostics:
    """数据诊断工具"""

    @staticmethod
    def diagnose_file(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data)
        assessor = SFTDataQualityAssessor()

        level_counts = {"accept": 0, "revise": 0, "reject": 0}
        total_score = 0
        score_distributions = {"90+": 0, "80-90": 0, "70-80": 0, "60-70": 0, "<60": 0}

        topic_distribution = {}
        length_distribution = {"<300": 0, "300-800": 0, "800-1500": 0, "1500-3000": 0, ">3000": 0}

        for item in data:
            result = assessor.assess(item)
            level_counts[result["level"]] += 1
            total_score += result["score"]

            score = result["score"]
            if score >= 90:
                score_distributions["90+"] += 1
            elif score >= 80:
                score_distributions["80-90"] += 1
            elif score >= 70:
                score_distributions["70-80"] += 1
            elif score >= 60:
                score_distributions["60-70"] += 1
            else:
                score_distributions["<60"] += 1

            metadata = item.get("metadata", {})
            topic = metadata.get("topic", "unknown")
            topic_distribution[topic] = topic_distribution.get(topic, 0) + 1

            content_length = len(item["messages"][-1]["content"])
            if content_length < 300:
                length_distribution["<300"] += 1
            elif content_length < 800:
                length_distribution["300-800"] += 1
            elif content_length < 1500:
                length_distribution["800-1500"] += 1
            elif content_length < 3000:
                length_distribution["1500-3000"] += 1
            else:
                length_distribution[">3000"] += 1

        avg_score = total_score / total if total > 0 else 0

        return {
            "file": file_path,
            "total": total,
            "avg_score": round(avg_score, 1),
            "level_counts": level_counts,
            "accept_rate": level_counts["accept"] / total * 100,
            "score_distributions": score_distributions,
            "topic_distribution": dict(sorted(topic_distribution.items(), key=lambda x: x[1], reverse=True)),
            "length_distribution": length_distribution
        }


class MockSFTDataGenerator:
    """Mock SFT 数据生成器 - 不调用 API"""

    SYSTEM_PROMPT = """你是一位资深技术教育专家，擅长用简洁专业的方式讲解复杂的技术概念。"""

    def __init__(self):
        self.content_generator = MockContentGenerator()
        self.generated_count = 0

    def generate_single(self, topic: str, sub_topic: str, difficulty: str = "基础", learning_goal: str = "技术学习") -> Dict[str, Any]:
        user_message = f"""请用{difficulty}级别讲解{topic}的{sub_topic}，学习目标：{learning_goal}。"""
        content = self.content_generator.generate_content(topic, sub_topic)

        data = {
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": content}
            ],
            "metadata": {
                "topic": topic,
                "sub_topic": sub_topic,
                "difficulty": difficulty,
                "learning_goal": learning_goal,
                "generated_at": datetime.now().isoformat(),
                "source": "mock"
            }
        }

        self.generated_count += 1
        return data

    def generate_batch(self, topics: List[Dict[str, Any]], output_path: str) -> List[Dict[str, Any]]:
        results = []
        total = len(topics)
        assessor = SFTDataQualityAssessor()

        print(f"\n[SFT Mock Generator] 开始批量生成，共 {total} 条数据")
        print(f"[SFT Mock Generator] 输出路径: {output_path}")
        print("=" * 60)

        for i, topic_config in enumerate(topics, 1):
            topic = topic_config.get("topic")
            sub_topic = topic_config.get("sub_topic")
            difficulty = topic_config.get("difficulty", "基础")

            print(f"\n[{i}/{total}] 生成: {topic} - {sub_topic} ({difficulty})")

            data = self.generate_single(topic, sub_topic, difficulty, topic_config.get("learning_goal", "技术学习"))
            result = assessor.assess(data)
            data["_quality_score"] = result["score"]
            data["_quality_level"] = result["level"]

            print(f"  质量评分: {result['score']} ({result['level']})")
            results.append(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("[SFT Mock Generator] 生成完成!")
        print(f"  成功: {self.generated_count}")

        return results


DIVERSE_TOPICS = [
    {"topic": "Python", "sub_topic": "装饰器原理", "difficulty": "进阶", "learning_goal": "面试准备"},
    {"topic": "Python", "sub_topic": "生成器与迭代器", "difficulty": "基础", "learning_goal": "技术学习"},
    {"topic": "Python", "sub_topic": "GIL机制详解", "difficulty": "高级", "learning_goal": "深入理解"},
    {"topic": "Python", "sub_topic": "并发编程 asyncio", "difficulty": "进阶", "learning_goal": "项目实战"},
    {"topic": "Python", "sub_topic": "内存管理与垃圾回收", "difficulty": "进阶", "learning_goal": "深入理解"},
    {"topic": "JavaScript", "sub_topic": "事件循环", "difficulty": "进阶", "learning_goal": "面试准备"},
    {"topic": "JavaScript", "sub_topic": "闭包原理", "difficulty": "进阶", "learning_goal": "面试准备"},
    {"topic": "JavaScript", "sub_topic": "原型链与继承", "difficulty": "进阶", "learning_goal": "深入理解"},
    {"topic": "AI", "sub_topic": "RAG 检索增强生成", "difficulty": "进阶", "learning_goal": "项目实战"},
    {"topic": "AI", "sub_topic": "Agent 智能体架构", "difficulty": "高级", "learning_goal": "AI架构"},
    {"topic": "AI", "sub_topic": "Transformer 注意力机制", "difficulty": "高级", "learning_goal": "深入理解"},
    {"topic": "机器学习", "sub_topic": "梯度下降优化", "difficulty": "进阶", "learning_goal": "算法学习"},
    {"topic": "机器学习", "sub_topic": "神经网络正则化", "difficulty": "进阶", "learning_goal": "深度学习"},
    {"topic": "机器学习", "sub_topic": "卷积神经网络", "difficulty": "进阶", "learning_goal": "计算机视觉"},
    {"topic": "数据库", "sub_topic": "B+树索引", "difficulty": "进阶", "learning_goal": "面试准备"},
    {"topic": "数据库", "sub_topic": "事务隔离级别", "difficulty": "进阶", "learning_goal": "深入理解"},
    {"topic": "数据库", "sub_topic": "分布式事务", "difficulty": "高级", "learning_goal": "架构设计"},
    {"topic": "系统设计", "sub_topic": "微服务架构", "difficulty": "进阶", "learning_goal": "架构设计"},
    {"topic": "网络", "sub_topic": "TCP 协议详解", "difficulty": "进阶", "learning_goal": "网络基础"},
    {"topic": "安全", "sub_topic": "OAuth2.0 认证", "difficulty": "进阶", "learning_goal": "安全实践"},
    {"topic": "算法", "sub_topic": "动态规划", "difficulty": "进阶", "learning_goal": "算法学习"},
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SFT Mock 数据生成工具")
    parser.add_argument("--output", "-o", default="./sft_data/generated.json", help="输出文件路径")
    parser.add_argument("--count", "-c", type=int, default=10, help="生成数量")
    parser.add_argument("--diagnose", help="诊断数据文件")

    args = parser.parse_args()

    if args.diagnose:
        result = SFTDataDiagnostics.diagnose_file(args.diagnose)
        print(f"\n📊 数据诊断报告: {result['file']}")
        print(f"📈 总体评分: {result['avg_score']}/100")
        print(f"📦 总数据量: {result['total']} 条")
        print(f"✅ 合格率: {result['accept_rate']:.1f}%")
        print(f"\n📚 主题分布:")
        for topic, count in result['topic_distribution'].items():
            print(f"  {topic}: {count} 条")
        exit(0)

    topics = DIVERSE_TOPICS[:args.count]

    generator = MockSFTDataGenerator()
    results = generator.generate_batch(topics, args.output)

    print(f"\n[SFT] 数据已保存到: {args.output}")

    diag_result = SFTDataDiagnostics.diagnose_file(args.output)
    print(f"[诊断] 平均质量分: {diag_result['avg_score']}")
    print(f"[诊断] 合格率: {diag_result['accept_rate']:.1f}%")