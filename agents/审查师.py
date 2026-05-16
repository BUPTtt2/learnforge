from typing import Dict, List, Any, Optional, Tuple
from utils.model_utils import hybrid_model_manager
from utils.logger import logger


class ReviewStrategy:
    """审查策略基类"""
    
    def __init__(self, min_quality_threshold: float, retry_threshold: float):
        self.min_quality_threshold = min_quality_threshold
        self.retry_threshold = retry_threshold
    
    def evaluate_chapter(self, score: float) -> bool:
        """评估单个章节是否需要重做"""
        return score < self.min_quality_threshold
    
    def decide_action(self, avg_score: float, problem_ratio: float) -> str:
        """决定整体操作"""
        if avg_score < self.min_quality_threshold:
            return "retry_all"
        elif problem_ratio >= self.retry_threshold:
            return "retry_all"
        elif problem_ratio > 0:
            return "rework_specific"
        else:
            return "approve"


class StrictReviewStrategy(ReviewStrategy):
    """严格审查策略"""
    
    def __init__(self):
        super().__init__(min_quality_threshold=0.5, retry_threshold=0.5)


class BalancedReviewStrategy(ReviewStrategy):
    """平衡审查策略（默认）"""
    
    def __init__(self):
        super().__init__(min_quality_threshold=0.3, retry_threshold=0.7)


class LenientReviewStrategy(ReviewStrategy):
    """宽松审查策略"""
    
    def __init__(self):
        super().__init__(min_quality_threshold=0.2, retry_threshold=0.9)


class ContentReviewer:
    def __init__(self, model=None, strategy: ReviewStrategy = None):
        self.model = model or hybrid_model_manager
        self.strategy = strategy or BalancedReviewStrategy()
        self.expected_chapters = []
    
    def set_strategy(self, strategy: ReviewStrategy):
        """切换审查策略"""
        self.strategy = strategy
        logger.info(f"[审查师] 策略已切换: {strategy.__class__.__name__}")
    
    def get_strategy_name(self):
        """获取当前策略名称"""
        return self.strategy.__class__.__name__.replace('ReviewStrategy', '')
    
    def pre_review_chapters(self, knowledge_point: str, chapters: List[str]) -> Dict[str, Any]:
        logger.info(f"[审查师] 预审查章节规划: {knowledge_point}")
        
        self.expected_chapters = chapters
        
        prompt = f"""请评估以下章节规划是否合理：

知识点：{knowledge_point}

规划的章节：
{chr(10).join([f"{i+1}. {chapter}" for i, chapter in enumerate(chapters)])}

请评估：
1. 完整性：是否覆盖了知识点的主要方面
2. 逻辑性：章节顺序是否合理
3. 深度：是否有足够的深度层次

输出格式（JSON）：
{{
    "score": 8,
    "is_acceptable": true,
    "reason": "章节规划合理",
    "suggestions": ["建议增加XX章节"]
}}"""
        
        try:
            result = self.model.generate(prompt, use_local=True)
            
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    review_data = json.loads(json_match.group())
                else:
                    review_data = {"score": 7, "is_acceptable": True, "reason": "解析失败，默认通过", "suggestions": []}
            except Exception as e:
                review_data = {"score": 7, "is_acceptable": True, "reason": f"解析错误: {e}", "suggestions": []}
            
            score = min(10, max(0, review_data.get("score", 7)))
            is_acceptable = review_data.get("is_acceptable", score >= 6)
            
            return {
                "score": score / 10,
                "is_acceptable": is_acceptable,
                "reason": review_data.get("reason", ""),
                "suggestions": review_data.get("suggestions", []),
                "expected_chapters": chapters
            }
        
        except Exception as e:
            logger.error(f"[审查师] 预审查失败: {e}")
            return {
                "score": 0.7,
                "is_acceptable": True,
                "reason": f"预审查失败，默认通过: {e}",
                "suggestions": [],
                "expected_chapters": chapters
            }
    
    def review_all_chapters(self, knowledge_point: str, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"[审查师] 开始审查: {knowledge_point}, 共 {len(chapters)} 个章节")
        
        review_results = []
        total_score = 0.0
        problem_chapters = []
        passed_chapters = []
        
        for chapter in chapters:
            result = self._review_single_chapter(chapter)
            review_results.append(result)
            total_score += result["score"]
            
            if self.strategy.evaluate_chapter(result["score"]):
                problem_chapters.append(chapter["chapter"])
            else:
                passed_chapters.append(chapter["chapter"])
        
        avg_score = total_score / len(chapters) if chapters else 0.0
        problem_ratio = len(problem_chapters) / len(chapters) if chapters else 0.0
        
        decision = self.strategy.decide_action(avg_score, problem_ratio)
        
        if decision == "retry_all":
            logger.warning(f"[审查师] {self.get_strategy_name()}策略：建议整体重试，平均分数: {avg_score:.2f}")
        elif decision == "rework_specific":
            logger.info(f"[审查师] 需要重做 {len(problem_chapters)} 个章节")
        else:
            logger.info(f"[审查师] 全部通过，平均分数: {avg_score:.2f}")
        
        return {
            "decision": decision,
            "average_score": avg_score,
            "total_chapters": len(chapters),
            "passed_count": len(passed_chapters),
            "problem_count": len(problem_chapters),
            "passed_chapters": passed_chapters,
            "problem_chapters": problem_chapters,
            "review_details": review_results,
            "summary": self._generate_summary(knowledge_point, review_results),
            "expected_chapters": self.expected_chapters,
            "strategy": self.get_strategy_name()
        }
    
    def _review_single_chapter(self, chapter: Dict[str, Any]) -> Dict[str, Any]:
        chapter_name = chapter["chapter"]
        content = chapter["content"]
        exercise = chapter["exercise"]
        
        explanation = content.get("explanation", "")
        exercise_data = exercise.get("exercise", {})
        
        expected_chapters_str = ""
        if self.expected_chapters:
            expected_chapters_str = f"\n预期章节：{', '.join(self.expected_chapters)}"
        
        prompt = f"""请审查以下学习内容的质量：

章节名称：{chapter_name}
{expected_chapters_str}

讲解内容：
{explanation[:500]}...

习题：
{exercise_data.get('question', '')}

请从以下维度评分（0-10分）：
1. 相关性：内容是否与章节主题相关
2. 准确性：信息是否正确无误
3. 完整性：是否覆盖核心知识点
4. 深度：是否有足够的深度
5. 清晰度：表达是否清晰易懂

请给出综合评分（0-10分），并说明是否需要重做，以及问题所在。

输出格式（JSON）：
{{
    "score": 8,
    "needs_rework": false,
    "reason": "内容质量良好",
    "suggestions": ["建议增加更多示例"]
}}"""

        try:
            result = self.model.generate(prompt, use_local=True)
            
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    review_data = json.loads(json_match.group())
                else:
                    review_data = {"score": 5, "needs_rework": False, "reason": "解析失败", "suggestions": []}
            except Exception as e:
                review_data = {"score": 5, "needs_rework": False, "reason": f"解析错误: {e}", "suggestions": []}
            
            score = min(10, max(0, review_data.get("score", 5)))
            
            return {
                "chapter": chapter_name,
                "score": score / 10,
                "needs_rework": self.strategy.evaluate_chapter(score / 10),
                "reason": review_data.get("reason", ""),
                "suggestions": review_data.get("suggestions", [])
            }
        
        except Exception as e:
            logger.error(f"[审查师] 审查章节失败: {chapter_name}", exception=e)
            return {
                "chapter": chapter_name,
                "score": 0.5,
                "needs_rework": False,
                "reason": f"审查失败: {e}",
                "suggestions": ["重新生成"]
            }
    
    def _generate_summary(self, knowledge_point: str, review_results: List[Dict]) -> str:
        summaries = []
        for result in review_results:
            if result["needs_rework"]:
                summaries.append(f"- {result['chapter']}: {result['reason']}")
        
        if summaries:
            return f"「{knowledge_point}」的学习内容审查结果：\n\n问题章节：\n" + "\n".join(summaries)
        else:
            return f"「{knowledge_point}」的学习内容全部通过审查！"
    
    def should_ask_user(self, review_result: Dict[str, Any]) -> bool:
        return review_result["decision"] == "retry_all"
    
    def get_retry_prompt(self, review_result: Dict[str, Any]) -> str:
        return f"""检测到学习内容存在质量问题：

🔍 审查结果：
- 平均质量分：{review_result['average_score']:.2f}
- 问题章节：{review_result['problem_count']}/{review_result['total_chapters']}
- {', '.join(review_result['problem_chapters'])}

📝 问题摘要：
{review_result['summary']}

是否需要重新生成？"""


reviewer = ContentReviewer()

def create_reviewer(strategy_name: str = "balanced") -> ContentReviewer:
    """工厂函数：创建指定策略的审查师"""
    strategy_map = {
        "strict": StrictReviewStrategy(),
        "balanced": BalancedReviewStrategy(),
        "lenient": LenientReviewStrategy()
    }
    return ContentReviewer(strategy=strategy_map.get(strategy_name, BalancedReviewStrategy()))