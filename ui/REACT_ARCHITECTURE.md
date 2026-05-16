# LearnForge React UI 架构规划

## 设计目标

1. **知识讲解和习题分页/分块**：清晰分离，提供专注的学习体验
2. **单页应用**：使用React Router实现页面导航
3. **组件化设计**：易于维护和扩展
4. **响应式布局**：适配不同屏幕尺寸

## 页面结构

### 1. 首页 / 学习设置页
- 学习内容输入
- 学习模式选择（简单了解 / 弄清楚）
- 学习目标输入
- 开始学习按钮

### 2. 知识讲解页
- 章节导航（侧边栏或顶部标签）
- 详细讲解内容（Markdown渲染）
- 核心概念、技术实现、实战经验、生态关联、面试要点等板块
- 展开/折叠功能
- 下一章按钮

### 3. 习题练习页
- 章节导航
- 习题列表
- 选择题：单选/多选
- 简答题：文本输入
- 实践题：代码输入
- 综合题：综合分析
- 提交答案
- 查看答案和解析

### 4. 学习完成页
- 学习总结
- 掌握度统计
- 重新学习按钮
- 返回首页按钮

## 技术栈

- **框架**：React 18
- **构建工具**：Vite
- **路由**：React Router v6
- **样式**：TailwindCSS
- **HTTP客户端**：Axios
- **Markdown渲染**：react-markdown
- **状态管理**：React Context + useReducer

## 目录结构

```
ui/
├── react/                    # React前端
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/       # 通用组件
│   │   │   ├── Header.jsx
│   │   │   ├── ChapterNav.jsx
│   │   │   ├── ContentCard.jsx
│   │   │   ├── ExerciseCard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/           # 页面组件
│   │   │   ├── Home.jsx     # 首页/学习设置
│   │   │   ├── Learning.jsx # 知识讲解
│   │   │   ├── Practice.jsx # 习题练习
│   │   │   └── Complete.jsx # 学习完成
│   │   ├── services/        # API服务
│   │   │   └── api.js
│   │   ├── context/         # 全局状态
│   │   │   └── LearningContext.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── app.py                    # Streamlit备用
└── __init__.py
```

## API接口设计

### 1. 开始学习
- **POST** `/api/learning/start`
- **请求体**：
```json
{
  "knowledge_point": "RAG",
  "learning_mode": "deep",
  "learning_goal": "面试Agent"
}
```
- **响应**：
```json
{
  "type": "complex",
  "knowledge_point": "RAG",
  "learning_mode": "deep",
  "learning_goal": "面试Agent",
  "chapters": ["核心概念与基础原理", "技术实现与方法", ...],
  "results": [
    {
      "chapter": "核心概念与基础原理",
      "content": {
        "explanation": "...",
        "exercises": [...]
      }
    }
  ]
}
```

### 2. 提交答案
- **POST** `/api/learning/answer`
- **请求体**：
```json
{
  "chapter": "核心概念与基础原理",
  "user_answer": "A",
  "correct_answer": "A"
}
```
- **响应**：
```json
{
  "is_correct": true,
  "feedback": "正确！",
  "new_mastery_level": 0.8
}
```

### 3. 获取学习进度
- **GET** `/api/learning/progress`
- **响应**：
```json
{
  "total": 10,
  "learned": 5,
  "average_mastery": 0.65,
  "progress_rate": 0.5
}
```

## 组件设计

### Header组件
- Logo和标题
- 导航菜单
- 用户信息（可选）

### ChapterNav组件
- 章节列表
- 当前章节高亮
- 章节完成状态标记
- 点击切换章节

### ContentCard组件
- 标题
- 内容区域（支持Markdown）
- 展开/折叠按钮
- 关键词高亮

### ExerciseCard组件
- 题目类型标签
- 题目内容
- 选项列表（选择题）
- 文本输入框（简答题）
- 提交按钮
- 答案解析（提交后显示）

### LoadingSpinner组件
- 加载动画
- 提示文字

## 状态管理

使用React Context管理全局状态：

```javascript
// LearningContext
{
  // 当前学习状态
  learningResult: null,  // 学习结果
  currentChapter: 0,     // 当前章节索引
  learningMode: 'simple', // 学习模式
  learningGoal: '',      // 学习目标

  // 操作方法
  startLearning: (knowledge, mode, goal) => {},
  nextChapter: () => {},
  prevChapter: () => {},
  submitAnswer: (chapter, answer) => {},
  resetLearning: () => {}
}
```

## 待实施任务

1. [ ] 创建React项目结构
2. [ ] 配置Vite和TailwindCSS
3. [ ] 实现API服务层
4. [ ] 实现全局状态管理
5. [ ] 开发首页/学习设置页
6. [ ] 开发知识讲解页
7. [ ] 开发习题练习页
8. [ ] 开发学习完成页
9. [ ] 添加路由配置
10. [ ] 测试完整流程

## 备注

- 后端API需要添加Flask/FastAPI端点
- 或者使用Python的SimpleHTTPServer提供API服务
- 考虑使用WebSocket实现实时通信（可选）
