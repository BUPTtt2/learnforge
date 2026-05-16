from flask import Blueprint, request, jsonify
from agents.planning_agent import planning_agent
from agents.generation_agent import generation_agent
from utils.storage import storage
import time

# 创建蓝图
new_architecture_bp = Blueprint('new_architecture', __name__)

@new_architecture_bp.route('/api/learning/plan', methods=['POST'])
def plan_learning():
    try:
        data = request.json
        knowledge_point = data.get('knowledge_point')
        learning_goal = data.get('learning_goal')
        scene = data.get('scene', 'language')

        if not knowledge_point:
            return jsonify({'error': 'knowledge_point is required'}), 400

        # 使用规划 Agent 进行 Part 拆分
        result = planning_agent.split_into_parts(knowledge_point, learning_goal, scene)
        
        # 保存规划结果
        session_id = f"session_{hash(knowledge_point + learning_goal)}_{int(time.time())}"
        storage.save_session({
            'session_id': session_id,
            'knowledge_point': knowledge_point,
            'learning_goal': learning_goal,
            'scene': scene,
            'parts': result.get('parts', []),
            'suggested_order': result.get('suggested_order', []),
            'total_estimated_time': result.get('total_estimated_time', ''),
            'created_at': time.time(),
            'updated_at': time.time()
        })

        return jsonify({
            'session_id': session_id,
            'parts': result.get('parts', []),
            'suggested_order': result.get('suggested_order', []),
            'total_estimated_time': result.get('total_estimated_time', '')
        })

    except Exception as e:
        print(f"Error in plan_learning: {e}")
        return jsonify({'error': str(e)}), 500

@new_architecture_bp.route('/api/learning/start', methods=['POST'])
def start_learning_new():
    try:
        data = request.json
        session_id = data.get('session_id')
        part_id = data.get('part_id')
        learning_mode = data.get('learning_mode', 'simple')

        if not session_id or not part_id:
            return jsonify({'error': 'session_id and part_id are required'}), 400

        # 获取会话信息
        session = storage.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # 查找指定 Part
        part = None
        for p in session.get('parts', []):
            if p.get('id') == part_id:
                part = p
                break

        if not part:
            return jsonify({'error': 'Part not found'}), 404

        # 规划章节
        chapters = planning_agent.plan_chapters(part, session.get('learning_goal', ''))
        
        # 为 Part 添加章节信息
        part['chapters'] = []
        for chapter in chapters:
            part['chapters'].append({
                'id': chapter['id'],
                'title': chapter['title'],
                'description': chapter.get('description', ''),
                'status': 'pending',
                'content': None
            })

        # 生成第一章节
        first_chapter = part['chapters'][0]
        first_chapter['status'] = 'generating'
        
        # 保存会话状态
        storage.save_session(session)
        
        # 生成第一章节内容
        chapter_content = generation_agent.generate_chapter_content(
            first_chapter,
            part,
            session.get('learning_goal', ''),
            learning_mode
        )
        
        # 更新章节状态
        first_chapter['status'] = 'completed'
        first_chapter['content'] = chapter_content
        
        # 保存会话状态
        storage.save_session(session)

        return jsonify({
            'chapter': {
                'id': first_chapter['id'],
                'title': first_chapter['title'],
                'content': chapter_content
            },
            'part': part,
            'status': 'completed'
        })

    except Exception as e:
        print(f"Error in start_learning_new: {e}")
        return jsonify({'error': str(e)}), 500

@new_architecture_bp.route('/api/learning/generate_next', methods=['POST'])
def generate_next_chapter():
    try:
        data = request.json
        session_id = data.get('session_id')
        part_id = data.get('part_id')
        learning_mode = data.get('learning_mode', 'simple')

        if not session_id or not part_id:
            return jsonify({'error': 'session_id and part_id are required'}), 400

        # 获取会话信息
        session = storage.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # 查找指定 Part
        part = None
        for p in session.get('parts', []):
            if p.get('id') == part_id:
                part = p
                break

        if not part:
            return jsonify({'error': 'Part not found'}), 404

        # 查找下一个待生成的章节
        next_chapter = None
        chapters = part.get('chapters', [])
        
        for chapter in chapters:
            if chapter.get('status') == 'pending':
                next_chapter = chapter
                break

        if not next_chapter:
            return jsonify({'error': 'No more chapters to generate'}), 400

        # 更新章节状态
        next_chapter['status'] = 'generating'
        storage.save_session(session)
        
        # 生成章节内容
        chapter_content = generation_agent.generate_chapter_content(
            next_chapter,
            part,
            session.get('learning_goal', ''),
            learning_mode
        )
        
        # 更新章节状态
        next_chapter['status'] = 'completed'
        next_chapter['content'] = chapter_content
        storage.save_session(session)

        return jsonify({
            'chapter': {
                'id': next_chapter['id'],
                'title': next_chapter['title'],
                'content': chapter_content
            },
            'status': 'completed'
        })

    except Exception as e:
        print(f"Error in generate_next_chapter: {e}")
        return jsonify({'error': str(e)}), 500

@new_architecture_bp.route('/api/learning/status', methods=['GET'])
def get_learning_status():
    try:
        session_id = request.args.get('session_id')

        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        # 获取会话信息
        session = storage.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'session': session,
            'current_chapter': None  # 可以根据状态计算当前章节
        })

    except Exception as e:
        print(f"Error in get_learning_status: {e}")
        return jsonify({'error': str(e)}), 500