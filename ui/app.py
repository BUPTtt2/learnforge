import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.commander import commander
from utils.tools import format_learning_content
from utils.cache import cache_manager
from utils.performance import performance_monitor

st.set_page_config(
    page_title="📚 LearnForge - 智能学习助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.5rem;
        font-weight: 600;
    }
    .highlight-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📚 LearnForge</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">基于多智能体的个性化学习助手 | 智能拆解 · 专业讲解 · 即时练习</p>', unsafe_allow_html=True)

if 'current_result' not in st.session_state:
    st.session_state.current_result = None
    st.session_state.current_chapter = 0
    st.session_state.learning_mode = "simple"
    st.session_state.show_stats = False

with st.sidebar:
    st.markdown("## ⚙️ 学习设置")
    
    mode = st.radio(
        "🎯 学习模式",
        ["simple", "deep"],
        index=0 if st.session_state.learning_mode == "simple" else 1,
        format_func=lambda x: "📖 简单了解" if x == "simple" else "🧠 弄清楚",
        help="简单了解：通俗易懂，多用类比\n弄清楚：严谨专业，包含推导"
    )
    st.session_state.learning_mode = mode
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 统计", use_container_width=True):
            st.session_state.show_stats = not st.session_state.show_stats
    
    with col2:
        if st.button("🗑️ 清空缓存", use_container_width=True):
            cache_manager.clear()
            st.success("缓存已清空！")
    
    if st.button("📈 性能报告", use_container_width=True):
        performance_monitor.print_report()
    
    st.markdown("---")
    st.markdown("### 📚 学习进度")
    progress = commander.get_learning_progress()
    
    if progress and "knowledge_stats" in progress:
        kg_stats = progress["knowledge_stats"]
        st.progress(kg_stats.get("progress_rate", 0), 
                   text=f"完成度：{kg_stats.get('progress_rate', 0):.1%}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总知识点", kg_stats.get("total", 0))
        with col2:
            st.metric("已学习", kg_stats.get("learned", 0))
        
        if "learning_stats" in progress:
            ls_stats = progress["learning_stats"]
            st.metric("总请求数", ls_stats.get("total_requests", 0))

if st.session_state.show_stats:
    with st.expander("📊 详细统计信息", expanded=True):
        progress = commander.get_learning_progress()
        
        if progress:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📚 知识统计")
                st.json(progress.get("knowledge_stats", {}))
            
            with col2:
                st.markdown("### 🤖 模型统计")
                st.json(progress.get("model_stats", {}))
            
            with col3:
                st.markdown("### 💾 缓存统计")
                st.json(progress.get("cache_stats", {}))

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    knowledge_input = st.text_input(
        "🎓 请输入想学习的内容",
        placeholder="例如：梯度消失、正态分布、条件概率、机器学习...",
        help="输入你想要学习的知识点，系统会自动分析复杂度并生成学习内容"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    start_learning = st.button("🚀 开始学习", type="primary", use_container_width=True)

if start_learning and knowledge_input:
    with st.spinner("🔍 正在分析知识点复杂度..."):
        result = commander.process_learning_request(
            knowledge_input,
            st.session_state.learning_mode
        )
        
        st.session_state.current_result = result
        st.session_state.current_chapter = 0
        
        st.success(f"""
        ### ✅ 分析完成
        
        **类型**：{'📗 复杂知识点（按章节学习）' if result['type'] == 'complex' else '📕 简单知识点'}
        
        **章节数**：{len(result['chapters'])}
        
        **学习模式**：{'🧠 深度理解' if result['learning_mode'] == 'deep' else '📖 简单了解'}
        
        **预计时间**：{len(result['chapters']) * 15}分钟左右
        """)
        
        if result['type'] == 'complex':
            with st.expander("📋 章节列表", expanded=True):
                for i, chapter in enumerate(result['chapters'], 1):
                    st.write(f"{i}. **{chapter}**")

if st.session_state.current_result:
    result = st.session_state.current_result
    
    if st.session_state.current_chapter < len(result['results']):
        current_idx = st.session_state.current_chapter
        chapter_result = result['results'][current_idx]
        
        st.markdown("---")
        
        cols = st.columns([1, 1, 1, 1])
        for i, chapter in enumerate(result['chapters']):
            with cols[i % 4]:
                if i == current_idx:
                    st.markdown(f"**📖 第{i+1}章**")
                    st.markdown(f"_{chapter[:10]}..._")
                else:
                    st.markdown(f"第{i+1}章")
                    st.markdown(f"_{chapter[:10]}..._")
        
        st.markdown(f"## 📖 第{current_idx + 1}章：{chapter_result['chapter']}")
        
        with st.container():
            st.markdown("### 📚 讲解内容")
            
            explanation = chapter_result['content'].get('explanation', '')
            if explanation:
                st.info(explanation)
            else:
                st.warning("暂无讲解内容")
        
        st.markdown("### 📝 习题练习")
        
        exercise = chapter_result['content'].get('exercise', {})
        
        if exercise and exercise.get('question'):
            st.write(f"**{exercise.get('question', '')}**")
            
            options = exercise.get('options', [])
            if options:
                selected_option = st.radio(
                    "请选择答案",
                    options,
                    index=None,
                    key=f"exercise_{current_idx}_{id(exercise)}"
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    submit = st.button("✅ 提交答案", type="primary", use_container_width=True)
                    
                    if submit and selected_option:
                        user_answer = selected_option[0]
                        correct_answer = exercise.get('answer', 'A')
                        
                        answer_result = commander.check_answer(
                            chapter_result['chapter'],
                            user_answer,
                            correct_answer
                        )
                        
                with col2:
                    if current_idx + 1 < len(result['results']):
                        next_chapter = st.button("▶️ 下一章", use_container_width=True)
                    else:
                        next_chapter = st.button("🏁 完成学习", use_container_width=True)
                
                with col3:
                    review = st.button("🔄 重新学习", use_container_width=True)
                
                if 'answer_result' in locals():
                    if answer_result['is_correct']:
                        st.success(f"🎉 {answer_result['feedback']}")
                    else:
                        st.error(f"❌ {answer_result['feedback']}")
                    
                    st.info(f"💡 解析：{exercise.get('explanation', '')}")
                    st.markdown(f"**掌握度**：{answer_result['new_mastery_level']:.1%}")
                
                if 'next_chapter' in locals() and next_chapter:
                    if current_idx + 1 < len(result['results']):
                        st.session_state.current_chapter += 1
                        st.rerun()
                    else:
                        st.balloons()
                        st.success("🎊 恭喜！你已完成所有章节的学习！")
                
                if 'review' in locals() and review:
                    st.session_state.current_chapter = 0
                    st.rerun()
        else:
            st.warning("暂无习题")
    else:
        st.balloons()
        st.markdown("## 🎊 恭喜！")
        st.success("你已经完成了所有章节的学习！")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 重新开始", use_container_width=True):
                st.session_state.current_result = None
                st.session_state.current_chapter = 0
                st.rerun()
        
        with col2:
            if st.button("📊 查看学习报告", use_container_width=True):
                st.session_state.show_stats = True
                st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>Built with ❤️ by LearnForge Team | © 2026</p>
    <p>基于 GLM5.1 大模型 | 多智能体协作 | RAG增强系统</p>
</div>
""", unsafe_allow_html=True)
