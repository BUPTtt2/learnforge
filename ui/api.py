import sys
import os
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.commander import commander
from utils.cache import cache_manager
from utils.storage import storage
from utils.rag import rag_system
from utils.evaluation import rag_evaluator, generation_evaluator
from utils.tavily_client import tavily_search
from utils.memory_monitor import memory_monitor
from utils.request_queue import request_queue
from config_loader import config
from utils.safety import get_content_safety

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'learnforge.log'), encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)

import sys
for handler in logging.root.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.stream = sys.stdout
        handler.flush = lambda: sys.stdout.flush()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip):
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip):
        if client_ip not in self.requests:
            return self.max_requests
        
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        valid_requests = [r for r in self.requests[client_ip] if r > cutoff]
        return max(0, self.max_requests - len(valid_requests))


rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


def validate_input(data, required_fields, max_length=500):
    if not isinstance(data, dict):
        return False, 'Invalid data format'
    for field in required_fields:
        if field not in data:
            return False, f'Missing required field: {field}'
        if not data[field] or not str(data[field]).strip():
            return False, f'Field cannot be empty: {field}'
    for key, value in data.items():
        if isinstance(value, str) and len(value) > max_length:
            return False, f'Field exceeds maximum length: {key}'
    return True, ''


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


@app.before_request
def check_rate_limit():
    if request.endpoint in ['start_learning', 'submit_answer', 'rag_search', 'rag_hybrid_search']:
        client_ip = get_client_ip()
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"[限流] Client {client_ip} 请求过于频繁")
            return jsonify({
                'error': 'Too many requests. Please try again later.',
                'retry_after': 60
            }), 429


@app.route('/api/learning/start', methods=['POST'])
def start_learning():
    try:
        data = request.json
        valid, error = validate_input(data, ['knowledge_point'], max_length=200)
        if not valid:
            return jsonify({'error': error}), 400

        knowledge_point = data.get('knowledge_point')
        learning_mode = data.get('learning_mode', 'simple')
        learning_goal = data.get('learning_goal', '')
        use_cache = data.get('use_cache', True)
        use_semantic_cache = data.get('use_semantic_cache', True)
        semantic_threshold = data.get('semantic_threshold', 0.8)

        memory_status = memory_monitor.get_memory_status()
        if not memory_monitor.is_available():
            logger.warning(f"[内存警告] CPU: {memory_status['cpu_memory']:.1%}, GPU: {memory_status['gpu_memory']:.1%}")
            logger.info(f"[内存警告] 继续处理请求...")

        logger.info(f"[学习开始] 知识点: {knowledge_point}, 模式: {learning_mode}, 目标: {learning_goal}")

        # ============================================
        # 输入安全检查
        # ============================================
        safety = get_content_safety()
        is_safe, reason, details = safety.check_input_safety(knowledge_point)
        if learning_goal:
            is_safe_goal, reason_goal, details_goal = safety.check_input_safety(learning_goal)
            if not is_safe_goal:
                is_safe = False
                reason = reason_goal
                details = details_goal
                
        if not is_safe:
            logger.warning(f"[安全拦截] 学习输入不安全: {reason}")
            return jsonify({
                'success': False,
                'error': reason,
                'details': details
            }), 400

        # ============================================
        # 缓存集成：先检查缓存（精确匹配优先）
        # ============================================
        cache_key = f"learning:{hashlib.md5((knowledge_point + ':' + learning_mode).encode('utf-8')).hexdigest()}"
        cached_result = None
        
        if use_cache:
            # 1. 先查精确匹配
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"[缓存] 精确命中，直接返回")
                return jsonify({
                    **cached_result,
                    'cached': True,
                    'cache_type': 'exact'
                })
            
            # 2. 精确匹配没有，尝试语义缓存
            if use_semantic_cache:
                cached_result = cache_manager.get_semantic_cache(
                    knowledge_point, 
                    learning_mode, 
                    threshold=semantic_threshold
                )
                if cached_result is not None:
                    logger.info(f"[语义缓存] 模糊命中，直接返回")
                    return jsonify({
                        **cached_result,
                        'cached': True,
                        'cache_type': 'semantic'
                    })

        # ============================================
        # 缓存未命中：走原流程
        # ============================================
        result = commander.process_learning_request(knowledge_point, learning_mode, learning_goal)

        # ============================================
        # 输出安全检查（检查章节内容）
        # ============================================
        chapters = result.get('chapters', [])
        for chapter in chapters:
            chapter_content = chapter.get('content', '')
            is_safe, reason, details = safety.check_output_safety(chapter_content)
            if not is_safe:
                logger.warning(f"[安全拦截] 章节内容不安全: {reason}")
                # 可选：清洗或拦截
                chapter['content'] = safety.sanitize_output(chapter['content'])
        
        storage.save_to_history(result)

        # ============================================
        # 缓存集成：写入缓存（缓存24小时）
        # ============================================
        if use_cache and result.get('status') == 'success':
            cache_manager.set(cache_key, result, ttl=86400)
            logger.info(f"[缓存] 已写入学习内容缓存: {cache_key}")
        
        logger.info(f"[学习完成] 知识点: {knowledge_point}, 章节数: {len(result.get('chapters', []))}")
        return jsonify({
            **result,
            'cached': False
        })

    except Exception as e:
        logger.error(f"[学习错误] {str(e)}")
        return jsonify({'error': 'Failed to start learning'}), 500


@app.route('/api/learning/answer', methods=['POST'])
def submit_answer():
    try:
        data = request.json
        valid, error = validate_input(data, ['chapter', 'user_answer'], max_length=1000)
        if not valid:
            return jsonify({'error': error}), 400

        chapter = data.get('chapter')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer', '')

        if correct_answer and len(correct_answer) > 1000:
            return jsonify({'error': 'correct_answer exceeds maximum length'}), 400

        result = commander.submit_answer(chapter, user_answer, correct_answer)
        return jsonify(result)

    except Exception as e:
        logger.error(f"[答题错误] {str(e)}")
        return jsonify({'error': 'Failed to submit answer'}), 500


@app.route('/api/learning/progress', methods=['GET'])
def get_progress():
    try:
        progress = commander.get_progress()
        return jsonify(progress)
    except Exception as e:
        logger.error(f"[进度错误] {str(e)}")
        return jsonify({'error': 'Failed to get progress'}), 500

@app.route('/api/learning/mastery', methods=['GET'])
def get_mastery():
    try:
        from memory.knowledge_graph import knowledge_graph
        
        knowledge_point = request.args.get('knowledge_point')
        
        if knowledge_point:
            # 查询单个知识点的掌握度
            node = knowledge_graph.get_node(knowledge_point)
            if node:
                return jsonify({
                    'success': True,
                    'knowledge_point': knowledge_point,
                    'mastery_level': node.get('properties', {}).get('mastery_level', 0.0),
                    'status': node.get('properties', {}).get('status', '未学'),
                    'learning_mode': node.get('properties', {}).get('learning_mode', '')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '知识点不存在'
                })
        else:
            # 返回所有知识点的掌握度
            all_nodes = knowledge_graph.search_nodes('', limit=100)
            mastery_data = []
            for node in all_nodes:
                props = node.get('properties', {})
                mastery_data.append({
                    'name': node.get('name', ''),
                    'mastery_level': props.get('mastery_level', 0.0),
                    'status': props.get('status', '未学'),
                    'type': node.get('type', '')
                })
            
            return jsonify({
                'success': True,
                'data': mastery_data,
                'total': len(mastery_data)
            })
    except Exception as e:
        logger.error(f"[掌握度错误] {str(e)}")
        return jsonify({'error': 'Failed to get mastery'}), 500


@app.route('/api/learning/cache/clear', methods=['POST'])
def clear_cache():
    try:
        cache_manager.clear()
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"[缓存错误] {str(e)}")
        return jsonify({'error': 'Failed to clear cache'}), 500

@app.route('/api/learning/cache/stats', methods=['GET'])
def get_cache_stats():
    try:
        stats = cache_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"[缓存统计错误] {str(e)}")
        return jsonify({'error': 'Failed to get cache stats'}), 500

# 记忆管理接口
@app.route('/api/memory/short', methods=['GET'])
def get_short_term_memory():
    try:
        from memory.memory_manager import memory_manager
        conversation_id = request.args.get('conversation_id')
        
        if conversation_id:
            context = memory_manager.get_short_term("chat_context", conversation_id)
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'context': context
            })
        else:
            stats = memory_manager.get_stats()
            return jsonify({
                'success': True,
                'short_term': stats['short_term'],
                'active_conversations': len(memory_manager.short_term["chat_context"])
            })
    except Exception as e:
        logger.error(f"[短期记忆错误] {str(e)}")
        return jsonify({'error': 'Failed to get short-term memory'}), 500

@app.route('/api/memory/long', methods=['GET'])
def get_long_term_memory():
    try:
        from memory.memory_manager import memory_manager
        
        knowledge_point = request.args.get('knowledge_point')
        
        if knowledge_point:
            node = memory_manager.get_long_term(knowledge_point)
            if node:
                return jsonify({
                    'success': True,
                    'knowledge_point': knowledge_point,
                    'data': node
                })
            else:
                return jsonify({'success': False, 'message': '知识点不存在'})
        else:
            stats = memory_manager.get_stats()
            return jsonify({
                'success': True,
                'long_term': stats['long_term']
            })
    except Exception as e:
        logger.error(f"[长期记忆错误] {str(e)}")
        return jsonify({'error': 'Failed to get long-term memory'}), 500

@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    try:
        from memory.memory_manager import memory_manager
        stats = memory_manager.get_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"[记忆统计错误] {str(e)}")
        return jsonify({'error': 'Failed to get memory stats'}), 500

@app.route('/api/memory/clear/short', methods=['POST'])
def clear_short_term_memory():
    try:
        from memory.memory_manager import memory_manager
        conversation_id = request.json.get('conversation_id')
        
        if conversation_id:
            memory_manager.clear_short_term(conversation_id)
            return jsonify({'success': True, 'message': f'会话 {conversation_id} 短期记忆已清除'})
        else:
            memory_manager.clear_short_term()
            return jsonify({'success': True, 'message': '所有短期记忆已清除'})
    except Exception as e:
        logger.error(f"[清除短期记忆错误] {str(e)}")
        return jsonify({'error': 'Failed to clear short-term memory'}), 500


@app.route('/api/learning/history', methods=['GET'])
def get_history():
    try:
        history = storage.load_history()
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"[历史错误] {str(e)}")
        return jsonify({'error': 'Failed to get history'}), 500


@app.route('/api/learning/summary', methods=['GET'])
def get_summary():
    try:
        summary = commander.get_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"[总结错误] {str(e)}")
        return jsonify({'error': 'Failed to get summary'}), 500


@app.route('/api/rag/search', methods=['POST'])
def rag_search():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data.get('query')
        top_k = data.get('top_k', 5)
        session_id = data.get('session_id', 'default')
        enable_evaluation = data.get('enable_evaluation', True)

        results = rag_system.search(query, top_k=top_k)

        if enable_evaluation:
            evaluation = rag_evaluator.evaluate_interaction(
                session_id=session_id,
                query=query,
                retrieval_results=results,
                answer="",
                retrieved_contexts=[r.get('content', '') for r in results]
            )

            return jsonify({
                'results': results,
                'evaluation': {
                    'retrieval_quality': evaluation.retrieval_metrics.avg_similarity if evaluation.retrieval_metrics else 0,
                    'keyword_match_rate': evaluation.retrieval_metrics.keyword_match_rate if evaluation.retrieval_metrics else 0,
                    'hit_rate': evaluation.retrieval_metrics.hit_rate if evaluation.retrieval_metrics else 0,
                    'overall_score': evaluation.overall_score
                }
            })

        return jsonify({'results': results})
    except Exception as e:
        logger.error(f"[RAG搜索错误] {str(e)}")
        return jsonify({'error': 'Failed to search'}), 500


@app.route('/api/rag/hybrid', methods=['POST'])
def rag_hybrid_search():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data.get('query')
        top_k = data.get('top_k', 3)
        session_id = data.get('session_id', 'default')

        result = rag_system.hybrid_search(
            query=query,
            local_k=top_k,
            use_external=True,
            auto_add_to_knowledge=True
        )

        return jsonify({
            'query': query,
            'local_results': result.get('local', []),
            'external_triggered': result.get('external_triggered', False),
            'retrieval_quality': result.get('retrieval_quality', 0),
            'decision_reason': result.get('decision_reason', ''),
            'external_success': result.get('external', {}).get('success', False),
            'external_results_count': len(result.get('external', {}).get('results', []))
        })
    except Exception as e:
        logger.error(f"[混合搜索错误] {str(e)}")
        return jsonify({'error': 'Failed to hybrid search'}), 500


@app.route('/api/rag/add', methods=['POST'])
def rag_add_document():
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400

        content = data.get('content')
        rag_system.add_document(content)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"[RAG添加错误] {str(e)}")
        return jsonify({'error': 'Failed to add document'}), 500


@app.route('/api/rag/stats', methods=['GET'])
def rag_stats():
    try:
        stats = rag_system.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"[RAG统计错误] {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500


@app.route('/api/rag/clear', methods=['POST'])
def rag_clear():
    try:
        success = rag_system.clear_collection()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"[RAG清除错误] {str(e)}")
        return jsonify({'error': 'Failed to clear collection'}), 500


@app.route('/api/evaluation/session/<session_id>', methods=['GET'])
def get_session_evaluation(session_id):
    try:
        summary = rag_evaluator.get_session_summary(session_id)
        if not summary:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(summary)
    except Exception as e:
        logger.error(f"[评估错误] {str(e)}")
        return jsonify({'error': 'Failed to get evaluation'}), 500


@app.route('/api/evaluation/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        if not data or 'session_id' not in data or 'rating' not in data:
            return jsonify({'error': 'session_id and rating are required'}), 400

        session_id = data.get('session_id')
        rating = data.get('rating')
        thumbs_up = data.get('thumbs_up')
        feedback_text = data.get('feedback', '')

        gen_metrics = generation_evaluator.evaluate(
            query=data.get('query', ''),
            answer=data.get('answer', ''),
            retrieved_contexts=data.get('contexts', []),
            feedback={
                'rating': rating,
                'thumbs_up': thumbs_up,
                'feedback': feedback_text
            }
        )

        return jsonify({
            'success': True,
            'combined_score': gen_metrics.combined_score,
            'feedback_stats': generation_evaluator.get_feedback_statistics()
        })
    except Exception as e:
        logger.error(f"[反馈错误] {str(e)}")
        return jsonify({'error': 'Failed to submit feedback'}), 500


@app.route('/api/evaluation/stats', methods=['GET'])
def get_evaluation_stats():
    try:
        return jsonify({
            'feedback_stats': generation_evaluator.get_feedback_statistics(),
            'sessions': list(rag_evaluator.session_metrics.keys())
        })
    except Exception as e:
        logger.error(f"[评估统计错误] {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500


@app.route('/api/search/history', methods=['GET'])
def get_search_history():
    try:
        limit = request.args.get('limit', 20, type=int)
        history = tavily_search.get_search_history(limit=limit)
        return jsonify({
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        logger.error(f"[搜索历史错误] {str(e)}")
        return jsonify({'error': 'Failed to get search history'}), 500


@app.route('/api/search/stats', methods=['GET'])
def get_search_stats():
    try:
        stats = tavily_search.get_search_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"[搜索统计错误] {str(e)}")
        return jsonify({'error': 'Failed to get search stats'}), 500


@app.route('/api/search/clear', methods=['POST'])
def clear_search_history():
    try:
        tavily_search.clear_history()
        return jsonify({'success': True, 'message': 'Search history cleared'})
    except Exception as e:
        logger.error(f"[清除搜索历史错误] {str(e)}")
        return jsonify({'error': 'Failed to clear history'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        message = data.get('message')
        history = data.get('history', [])
        conversation_id = data.get('conversation_id')
        session_id = data.get('session_id', 'default')
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)
        use_tools = data.get('use_tools', True)
        use_cache = data.get('use_cache', True)

        logger.info(f"[对话] 用户消息: {message[:50]}...")

        # ============================================
        # 输入安全检查
        # ============================================
        safety = get_content_safety()
        is_safe, reason, details = safety.check_input_safety(message)
        if not is_safe:
            logger.warning(f"[安全拦截] 输入不安全: {reason}")
            return jsonify({
                'success': False,
                'error': reason,
                'details': details
            }), 400

        from utils.chat_history import chat_history_manager
        
        if not conversation_id:
            topic = message[:50] if len(message) > 50 else message
            conversation_id = chat_history_manager.create_conversation(session_id, topic)
            logger.info(f"[对话] 创建新对话: {conversation_id}")
        
        chat_history_manager.add_message(conversation_id, 'user', message)

        # ============================================
        # 缓存集成：先检查缓存
        # ============================================
        cache_key = f"chat:{hashlib.md5(message.encode('utf-8')).hexdigest()}"
        cached_response = None
        
        if use_cache:
            cached_response = cache_manager.get(cache_key)
            if cached_response is not None:
                logger.info(f"[缓存] 命中缓存，直接返回")
                chat_history_manager.add_message(conversation_id, 'assistant', cached_response['response'])
                
                return jsonify({
                    'success': True,
                    'response': cached_response['response'],
                    'conversation_id': conversation_id,
                    'duration': time.time() - start_time,
                    'tool_results': cached_response.get('tool_results', []),
                    'cached': True
                })

        # ============================================
        # 缓存未命中：走原流程
        # ============================================
        history_prompt = ""
        if history:
            for item in history:
                role = item.get('role', 'user')
                content = item.get('content', '')
                if role == 'user':
                    history_prompt += f"用户: {content}\n"
                else:
                    history_prompt += f"助手: {content}\n"

        context_info = ""
        
        # 新增：从 RAG 检索相关的对话历史
        try:
            from utils.rag import rag_system
            rag_results = rag_system.search(message, top_k=2)
            if rag_results:
                related_chats = []
                for r in rag_results:
                    if r.get('metadata', {}).get('type') == 'chat':
                        related_chats.append(r['content'])
                if related_chats:
                    context_info = "\n".join([f"相关对话: {chat}" for chat in related_chats])
                    logger.info(f"[RAG] 检索到 {len(related_chats)} 条相关对话")
        except Exception as e:
            logger.warning(f"[RAG] 检索对话历史失败: {e}")
        
        if use_tools:
            from utils.tools import tool_manager
            
            tools_prompt = f"""你可以使用以下工具来帮助回答问题：

{tool_manager.get_tools_prompt()}

使用工具的格式：<tool_call>工具名(参数=值)</tool_call>

请根据问题判断是否需要使用工具：
1. 如果是数学计算问题，使用 calculator 工具
2. 如果是技术知识查询，先使用 rag_search 工具
3. 如果需要最新信息，使用 web_search 工具
4. 如果是长文本，需要摘要，使用 summarize 工具

如果你决定使用工具，请直接输出工具调用，不需要其他文字。
如果你决定直接回答，请直接给出答案，不需要使用工具。
"""
        else:
            tools_prompt = ""

        prompt = f"""你是一个智能学习助手，擅长帮助用户学习编程和技术知识。

{tools_prompt}

{context_info}

历史对话:
{history_prompt}

用户问: {message}

请给出详细、清晰、有帮助的回答。
"""

        from utils.model_utils import hybrid_model_manager
        response = hybrid_model_manager.generate(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature
        )

        tool_results = []
        final_response = response.strip()
        
        if use_tools:
            tool_calls = tool_manager.parse_tool_calls(final_response)
            if tool_calls:
                final_response = ""
                for tool_call in tool_calls:
                    tool_name = tool_call['tool']
                    params = tool_call['params']
                    
                    result = tool_manager.call_tool(tool_name, **params)
                    tool_results.append(result)
                    
                    if result.get('success', False):
                        if tool_name == 'calculator':
                            final_response += f"计算结果：{result['expression']} = {result['result']}\n\n"
                        elif tool_name == 'rag_search':
                            final_response += "从知识库中找到以下相关信息：\n"
                            for r in result.get('results', []):
                                final_response += f"- {r.get('title', '')}: {r.get('content', '')}\n\n"
                        elif tool_name == 'web_search':
                            final_response += "网络搜索结果：\n"
                            for r in result.get('results', []):
                                final_response += f"- [{r.get('title', '')}]({r.get('url', '')}): {r.get('content', '')}\n\n"
                        elif tool_name == 'summarize':
                            final_response += f"摘要（原长{result['original_length']}字）：\n{result['summary']}\n\n"
                    else:
                        final_response += f"工具调用失败 ({tool_name}): {result.get('error', '未知错误')}\n"

        # ============================================
        # 输出安全检查
        # ============================================
        is_output_safe, output_reason, output_details = safety.check_output_safety(final_response)
        if not is_output_safe:
            logger.warning(f"[安全拦截] 输出不安全: {output_reason}")
            # 可选：可以选择清洗后返回，或直接拦截
            final_response = safety.sanitize_output(final_response)
            # 或拦截返回：
            # return jsonify({'success': False, 'error': output_reason, 'details': output_details}), 400

        chat_history_manager.add_message(conversation_id, 'assistant', final_response)

        # ============================================
        # 缓存集成：写入缓存
        # ============================================
        if use_cache:
            cache_data = {
                'response': final_response,
                'tool_results': tool_results,
                'message': message
            }
            cache_manager.set(cache_key, cache_data, ttl=3600)  # 1小时过期
            logger.info(f"[缓存] 已写入缓存: {cache_key}")

        duration = time.time() - start_time
        logger.info(f"[对话完成] 耗时: {duration:.2f}秒")
        
        return jsonify({
            'success': True,
            'response': final_response,
            'conversation_id': conversation_id,
            'duration': duration,
            'tool_results': tool_results,
            'cached': False
        })

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[对话错误] {str(e)}, 耗时: {duration:.2f}秒")
        return jsonify({'error': 'Failed to generate response'}), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        session_id = request.args.get('session_id', 'default')
        limit = request.args.get('limit', 20, type=int)
        
        from utils.chat_history import chat_history_manager
        conversations = chat_history_manager.get_conversations_by_session(session_id, limit)
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'count': len(conversations)
        })
    except Exception as e:
        logger.error(f"[对话历史错误] {str(e)}")
        return jsonify({'error': 'Failed to get chat history'}), 500


@app.route('/api/chat/conversation/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        from utils.chat_history import chat_history_manager
        conversation = chat_history_manager.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation
        })
    except Exception as e:
        logger.error(f"[获取对话错误] {str(e)}")
        return jsonify({'error': 'Failed to get conversation'}), 500


@app.route('/api/chat/conversation/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    try:
        from utils.chat_history import chat_history_manager
        success = chat_history_manager.delete_conversation(conversation_id)
        
        if not success:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({'success': True, 'message': 'Conversation deleted'})
    except Exception as e:
        logger.error(f"[删除对话错误] {str(e)}")
        return jsonify({'error': 'Failed to delete conversation'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f'[服务器错误] {str(e)}')
    return jsonify({'error': 'Internal server error', 'code': 500}), 500


@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({'error': str(e), 'code': 400}), 400


@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': str(e), 'code': 404}), 404


@app.errorhandler(413)
def handle_request_too_large(e):
    logger.error(f'[请求过大] {str(e)}')
    return jsonify({'error': 'Request too large', 'code': 413}), 413


@app.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({'error': 'Too many requests', 'code': 429}), 429


if __name__ == '__main__':
    logger.info("Starting LearnForge API Server...")
    logger.info(f"API will be available at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=False)
