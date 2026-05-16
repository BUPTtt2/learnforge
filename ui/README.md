# LearnForge React UI 启动说明

## 项目结构

```
ui/
├── react/              # React前端
│   ├── src/
│   │   ├── pages/      # 页面组件
│   │   ├── components/  # 通用组件
│   │   ├── context/    # 全局状态
│   │   ├── services/   # API服务
│   │   └── ...
│   ├── package.json
│   └── ...
├── api.py              # Flask后端API
└── app.py             # Streamlit备用UI
```

## 启动步骤

### 1. 安装依赖

#### 前端依赖
```bash
cd ui/react
npm install
```

#### 后端依赖
```bash
pip install flask flask-cors
```

### 2. 启动后端API

```bash
cd ui
python api.py
```

后端将在 http://localhost:5000 启动

### 3. 启动前端

在另一个终端中：

```bash
cd ui/react
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 访问应用

打开浏览器访问 http://localhost:3000

## 功能说明

### 页面结构

1. **首页** - 输入学习内容、选择学习模式、设置学习目标
2. **知识讲解页** - 分章节展示详细讲解内容，支持展开/折叠
3. **习题练习页** - 进行各章节的习题练习
4. **学习完成页** - 查看学习总结和答题统计

### 学习模式

- **简单了解**：通俗易懂，多用类比
- **弄清楚**：严谨专业，包含推导，强调深度理解

### 主要特性

- 知识讲解分章节展示
- 习题练习支持多种题型
- 学习进度跟踪
- 答题结果统计

## 技术栈

- **前端**：React 18 + Vite + TailwindCSS + React Router
- **后端**：Flask + Python
- **模型**：Qwen3.4b (Ollama本地运行)

## 注意事项

1. 确保Ollama已启动并加载了qwen3:4b模型
2. 确保后端API正常运行
3. 前端开发服务器会自动代理API请求到后端

## 故障排除

### 问题1：API请求失败
- 检查后端API是否正常运行
- 检查端口5000是否被占用

### 问题2：模型调用失败
- 检查Ollama是否已启动
- 检查模型是否已加载：`ollama list`

### 问题3：前端无法访问
- 检查前端开发服务器是否在3000端口运行
- 检查浏览器控制台是否有错误信息
