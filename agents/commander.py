import json
import os
import time
from typing import Dict, List, Any, Optional
from utils.logger import logger
from utils.storage import storage
from .讲解师 import explainer
from .审查师 import reviewer, ContentReviewer
from memory.memory_manager import memory_manager


class Commander:
    def __init__(self, reviewer_instance: ContentReviewer = None):
        self.state_file = "commander_state.json"
        self.current_knowledge_point = ""
        self.current_mode = ""
        self.chapters = []
        self.results = {}
        self.max_retries = 2
        self.reviewer = reviewer_instance or reviewer
        self.memory = memory_manager  # 使用统一记忆管理器
        self.load_state()
    
    def set_reviewer(self, reviewer_instance: ContentReviewer):
        """切换审查师"""
        self.reviewer = reviewer_instance
        logger.info(f"[Commander] 审查师已切换")
    
    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.current_knowledge_point = state.get('knowledge_point', "")
                    self.current_mode = state.get('mode', "")
                    self.chapters = state.get('chapters', [])
                    self.results = state.get('results', {})
                logger.info("Commander state loaded")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    def save_state(self):
        try:
            state = {
                'knowledge_point': self.current_knowledge_point,
                'mode': self.current_mode,
                'chapters': self.chapters,
                'results': self.results
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.debug("Commander state saved")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def analyze_complexity(self, knowledge_point: str) -> Dict[str, Any]:
        logger.info(f"[Commander] Analyzing complexity: {knowledge_point}")
        prompt = f"""请评估以下知识点的学习复杂度（简单/中等/复杂）：
知识点：{knowledge_point}

请输出JSON格式：
{{
    "complexity": "简单",
    "reason": "理由",
    "estimated_chapters": 3
}}"""
        
        from utils.model_utils import hybrid_model_manager
        try:
            result = hybrid_model_manager.generate(prompt, use_local=True)
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
        
        return {"complexity": "简单", "reason": "默认简单", "estimated_chapters": 4}
    
    def plan_chapters(self, knowledge_point: str, mode: str = "simple") -> List[str]:
        logger.info(f"[Commander] Planning chapters for: {knowledge_point}")
        complexity = self.analyze_complexity(knowledge_point)
        score = complexity.get('complexity', '简单')
        
        if score == "复杂":
            chapters = [
                f"{knowledge_point}基础概念",
                f"{knowledge_point}核心原理",
                f"{knowledge_point}实现方法",
                f"{knowledge_point}应用场景",
                f"{knowledge_point}进阶技巧"
            ]
        else:
            chapters = [
                f"{knowledge_point}基础概念",
                f"{knowledge_point}核心原理",
                f"{knowledge_point}应用实践",
                f"{knowledge_point}实战练习"
            ]
        
        pre_review = self.reviewer.pre_review_chapters(knowledge_point, chapters)
        logger.info(f"[Commander] 预审查结果: 分数={pre_review['score']}, 通过={pre_review['is_acceptable']}")
        
        if pre_review['is_acceptable']:
            return chapters
        return chapters
    
    def _process_single_chapter(self, chapter: str, learning_mode: str, knowledge_point: str) -> Dict[str, Any]:
        logger.info(f"[Commander] Processing chapter: {chapter}")
        try:
            chapter_content = explainer.generate_explanation(
                chapter, 
                mode=learning_mode
            )
            chapter_exercise = chapter_content.get("exercise", {})
            
            return {
                "chapter": chapter,
                "content": chapter_content,
                "exercise": {"exercise": chapter_exercise},
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Failed to process chapter: {chapter}", exception=e)
            return {
                "chapter": chapter,
                "content": {"explanation": f"生成失败: {str(e)}", "exercise": None},
                "exercise": {"exercise": None},
                "status": "failed"
            }
    
    def _process_chapters_parallel(self, chapters: List[str], learning_mode: str) -> List[Dict[str, Any]]:
        results = []
        
        for chapter in chapters:
            result = self._process_single_chapter(chapter, learning_mode, self.current_knowledge_point)
            results.append(result)
        
        return results
    
    def process_learning_request(self, knowledge_point: str, learning_mode: str = "simple", learning_goal: str = "") -> Dict[str, Any]:
        logger.info(f"Processing learning request: {knowledge_point} mode={learning_mode}, goal={learning_goal}")
        
        # 使用统一记忆管理器查询长期记忆（知识图谱）
        try:
            node = self.memory.get_long_term(knowledge_point)
            
            if node:
                mastery_level = node.get('properties', {}).get('mastery_level', 0.0)
                logger.info(f"[长期记忆] 知识点 '{knowledge_point}' 掌握度: {mastery_level}")
                
                # 根据掌握度调整学习模式
                if mastery_level > 0.7:
                    learning_mode = "deep"
                    logger.info(f"[长期记忆] 掌握度较高，自动切换为深度模式")
                elif mastery_level < 0.3:
                    learning_mode = "simple"
                    logger.info(f"[长期记忆] 掌握度较低，自动切换为简单模式")
            else:
                # 知识点不存在，添加到长期记忆
                self.memory.add_long_term(knowledge_point, {
                    "status": "学习中",
                    "mastery_level": 0.0,
                    "learning_mode": learning_mode,
                    "history": [{"action": "开始学习", "timestamp": time.time()}]
                })
                logger.info(f"[长期记忆] 新增知识点: {knowledge_point}")
        except Exception as e:
            logger.warning(f"[长期记忆] 查询失败: {e}")
        
        # 记录到短期记忆
        self.memory.add_short_term("learning_goal", learning_goal, knowledge_point)
        
        self.current_knowledge_point = knowledge_point
        self.current_mode = learning_mode
        
        all_chapters = self.plan_chapters(knowledge_point, learning_mode)
        self.chapters = all_chapters
        
        retry_count = 0
        max_retries = 2
        chapter_results = []
        
        while retry_count <= max_retries:
            if not chapter_results:
                chapters_to_process = all_chapters
            else:
                chapters_to_process = [r['chapter'] for r in chapter_results if r['status'] == 'failed']
            
            logger.info(f"Processing {len(chapters_to_process)} chapters")
            
            current_results = self._process_chapters_parallel(chapters_to_process, learning_mode)
            
            if not chapter_results:
                chapter_results = current_results
            else:
                for new_result in current_results:
                    for i, existing in enumerate(chapter_results):
                        if existing['chapter'] == new_result['chapter']:
                            chapter_results[i] = new_result
                            break
            
            successful = [r for r in chapter_results if r['status'] == 'success']
            failed = [r for r in chapter_results if r['status'] == 'failed']
            
            if not failed:
                review_result = self.reviewer.review_all_chapters(knowledge_point, chapter_results)
                
                if review_result['decision'] == 'approve':
                    # 新增：学习完成，更新知识图谱掌握度
                    self._update_knowledge_graph(knowledge_point, 0.3)  # 学习后掌握度+0.3
                    self.save_state()
                    return {
                        "type": "success",
                        "knowledge_point": knowledge_point,
                        "chapters": chapter_results,
                        "learning_mode": learning_mode,
                        "quality_score": review_result['average_score']
                    }
                elif review_result['decision'] == 'rework_specific':
                    for i, r in enumerate(chapter_results):
                        if r['chapter'] in review_result['problem_chapters']:
                            chapter_results[i]['status'] = 'failed'
                    logger.info(f"[Commander] 标记需要重做的章节: {review_result['problem_chapters']}")
                    self.save_state()
                elif review_result['decision'] == 'retry_all':
                    # 新增：学习完成，更新知识图谱掌握度
                    self._update_knowledge_graph(knowledge_point, 0.2)  # 部分完成，掌握度+0.2
                    logger.warning(f"[Commander] 内容质量不足，但仍返回已生成内容")
                    return {
                        "type": "success",
                        "knowledge_point": knowledge_point,
                        "chapters": chapter_results,
                        "learning_mode": learning_mode,
                        "quality_score": review_result['average_score'],
                        "message": "内容已生成，部分章节质量有待提升",
                        "review_result": review_result
                    }
            else:
                logger.error(f"[Commander] {len(failed)}/{len(chapter_results)} 章节生成失败")
            
            retry_count += 1
        
        return {
            "type": "partial",
            "knowledge_point": knowledge_point,
            "chapters": chapter_results,
            "message": "重试次数已用尽，返回已生成内容"
        }
    
    def submit_answer(self, chapter: str, user_answer: str, correct_answer: str = "") -> Dict[str, Any]:
        return {
            "status": "success",
            "chapter": chapter,
            "user_answer": user_answer,
            "correct": user_answer == correct_answer if correct_answer else True
        }
    
    def get_progress(self) -> Dict[str, Any]:
        return {
            "knowledge_point": self.current_knowledge_point,
            "chapters": self.chapters,
            "completed": len(self.results)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "knowledge_point": self.current_knowledge_point,
            "chapters": self.chapters,
            "mode": self.current_mode
        }
    
    def _update_knowledge_graph(self, knowledge_point: str, increment: float) -> None:
        """更新长期记忆中的掌握度"""
        try:
            current_level = self.memory.get_mastery(knowledge_point)
            new_level = min(1.0, current_level + increment)
            
            # 使用记忆管理器更新掌握度
            self.memory.update_mastery(knowledge_point, new_level)
            
            # 更新状态
            status = "已掌握" if new_level >= 0.8 else ("学习中" if new_level > 0 else "未学")
            self.memory.update_long_term(knowledge_point, {
                "status": status,
                "history": [{"action": "学习完成", "timestamp": time.time(), "increment": increment}]
            })
            
            logger.info(f"[长期记忆] 知识点 '{knowledge_point}' 掌握度更新: {current_level:.2f} → {new_level:.2f}")
        except Exception as e:
            logger.warning(f"[长期记忆] 更新失败: {e}")


commander = Commander()