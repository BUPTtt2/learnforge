# LearnForge 🎓

基于多智能体的AI学习助手系统，帮助用户高效学习新知识。

## ✨ 功能特性

- **多Agent协作**: 讲解师、审查师等专业Agent协同完成学习任务
- **智能学习路径**: 根据知识点掌握度动态调整学习内容
- **知识图谱**: 长期记忆存储，追踪学习进度
- **语义缓存**: 智能缓存机制，提升响应速度
- **安全风控**: 输入/输出双重安全检查

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Ollama (本地模型运行)
- Node.js 18+ (前端)

### 安装依赖

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd ui/react
npm install
```

### 配置环境

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥（如需使用云端模型）
```

### 启动服务

```bash
# 启动后端服务（端口5000）
python run.py

# 启动前端服务（端口3000）
cd ui/react
npm run dev
```

### 访问地址

- **前端**: http://localhost:3000
- **后端API**: http://localhost:5000

## 📁 项目结构

```
LearnForge/
├── agents/              # Agent组件
│   ├── commander.py     # 指挥官 - 任务调度
│   ├── 讲解师.py        # 讲解师 - 内容生成
│   └── 审查师.py        # 审查师 - 质量评估
├── memory/              # 记忆系统
│   ├── memory_manager.py # 记忆管理器
│   └── knowledge_graph.py # 知识图谱
├── ui/                  # 前端与API
│   ├── react/           # React前端
│   ├── api.py           # API接口
│   └── app.py           # Flask应用
├── utils/               # 工具模块
│   ├── cache.py         # 缓存系统
│   ├── safety.py        # 安全检查
│   ├── model.py         # 模型管理
│   └── rag.py           # RAG检索
├── docs/                # 文档
└── scripts/             # 辅助脚本
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 📧 联系方式

如有问题或建议，请通过Issue联系。