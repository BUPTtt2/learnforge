import sys
import os
import time
import logging
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 后台生成任务状态
background_tasks = {}

# 健康检查
@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'LearnForge API is running', 'version': '1.0.0'})

# 测试章节状态 API
@app.route('/api/learning/chapter_status', methods=['POST'])
def get_chapter_status():
    try:
        data = request.json
        session_id = data.get('session_id')
        part_id = data.get('part_id')
        return jsonify({
            'chapters': [],
            'completed_count': 0,
            'total_count': 5,
            'progress': 20,
            'background_task': {}
        })
    except Exception as e:
        logger.error(f"Error in get_chapter_status: {e}")
        return jsonify({'error': 'Failed to get chapter status'}), 500

# 测试生成下一章节 API
@app.route('/api/learning/generate_next', methods=['POST'])
def generate_next_chapter():
    try:
        data = request.json
        session_id = data.get('session_id')
        part_id = data.get('part_id')
        return jsonify({
            'chapter': {
                'id': 'chapter_2',
                'title': '第二章 测试',
                'content': {'explanation': '测试内容'}
            },
            'status': 'completed'
        })
    except Exception as e:
        logger.error(f"Error in generate_next_chapter: {e}")
        return jsonify({'error': 'Failed to generate next chapter'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)