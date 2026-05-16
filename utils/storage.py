import json
import os
from datetime import datetime

class LearningStorage:
    def __init__(self, storage_dir="learning_data"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.session_file = os.path.join(storage_dir, "current_session.json")
        self.sessions_dir = os.path.join(storage_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.history_file = os.path.join(storage_dir, "history.json")
        self.progress_file = os.path.join(storage_dir, "progress.json")

    def save_session(self, session_data, answer_results=None):
        """保存会话数据

        Args:
            session_data: 会话数据字典
            answer_results: 答题结果（可选）
        """
        if isinstance(session_data, dict) and 'session_id' in session_data:
            session_id = session_data.get('session_id')
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            print(f"[Storage] Session {session_id} saved")
        else:
            if isinstance(session_data, dict) and 'learning_result' in session_data:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                print(f"[Storage] Session saved to {self.session_file}")
            else:
                learning_result = session_data
                answer_results = answer_results or {}
                old_session_data = {
                    "timestamp": datetime.now().isoformat(),
                    "learning_result": learning_result,
                    "answer_results": answer_results
                }
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(old_session_data, f, ensure_ascii=False, indent=2)
                print(f"[Storage] Session saved to {self.session_file}")

    def get_session(self, session_id):
        """获取指定会话

        Args:
            session_id: 会话 ID

        Returns:
            会话数据字典
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def load_session(self, session_id=None):
        if session_id:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_to_history(self, learning_result):
        history = self.load_history()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "knowledge_point": learning_result.get("knowledge_point"),
            "learning_mode": learning_result.get("learning_mode"),
            "learning_goal": learning_result.get("learning_goal"),
            "chapters": learning_result.get("chapters"),
            "type": learning_result.get("type")
        })
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"[Storage] Added to history: {learning_result.get('knowledge_point')}")

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_progress(self, chapter, mastery_level):
        progress = self.load_progress()
        progress[chapter] = {
            "mastery_level": mastery_level,
            "last_practiced": datetime.now().isoformat()
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_learning_summary(self):
        history = self.load_history()
        progress = self.load_progress()
        return {
            "total_topics": len(history),
            "recent_topics": history[-5:] if len(history) > 0 else [],
            "progress": progress
        }

storage = LearningStorage()
