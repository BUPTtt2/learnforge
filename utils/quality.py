from typing import Dict, List, Any, Optional
import re

class ContentQualityController:
    def __init__(self):
        self.quality_checks = {
            "min_length": 50,
            "max_length": 2000,
            "required_sections": ["定义", "原理", "应用"],
            "forbidden_patterns": [
                r"抱歉.*无法",
                r"我不能",
                r"我不确定",
                r"这个问题.*不清楚"
            ]
        }
        
        self.exercise_criteria = {
            "min_options": 4,
            "max_options": 4,
            "require_answer": True,
            "require_explanation": True,
            "valid_options": ["A", "B", "C", "D"]
        }
    
    def validate_explanation(self, explanation: str, mode: str = "simple") -> Dict[str, Any]:
        issues = []
        warnings = []
        score = 100
        
        if len(explanation) < self.quality_checks["min_length"]:
            issues.append(f"讲解内容过短（{len(explanation)}字符）")
            score -= 30
        
        if len(explanation) > self.quality_checks["max_length"]:
            warnings.append(f"讲解内容过长（{len(explanation)}字符），可能过于冗长")
            score -= 10
        
        for pattern in self.quality_checks["forbidden_patterns"]:
            if re.search(pattern, explanation):
                issues.append("内容包含不确定或模糊的表达")
                score -= 40
                break
        
        has_definition = any(kw in explanation for kw in ["定义", "概念", "是什么"])
        has原理 = any(kw in explanation for kw in ["原理", "原理是", "基于", "通过"])
        has应用 = any(kw in explanation for kw in ["应用", "用于", "可以用来", "在...中"])
        
        if mode == "deep":
            if not has_definition:
                warnings.append("缺少精确定义")
                score -= 15
            if not has原理:
                warnings.append("缺少核心原理")
                score -= 15
        else:
            if not has_definition and not has原理:
                warnings.append("缺少核心概念解释")
                score -= 20
        
        if not has应用:
            warnings.append("缺少应用场景说明")
            score -= 10
        
        is_valid = len(issues) == 0 and score >= 60
        
        return {
            "is_valid": is_valid,
            "score": max(0, score),
            "issues": issues,
            "warnings": warnings,
            "metrics": {
                "length": len(explanation),
                "has_definition": has_definition,
                "has原理": has原理,
                "has应用": has应用
            }
        }
    
    def validate_exercise(self, exercise: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        warnings = []
        score = 100
        
        if not exercise.get("question"):
            issues.append("缺少题目内容")
            score -= 50
        
        options = exercise.get("options", [])
        if len(options) < self.exercise_criteria["min_options"]:
            issues.append(f"选项数量不足（{len(options)}个）")
            score -= 30
        elif len(options) > self.exercise_criteria["max_options"]:
            warnings.append(f"选项数量过多（{len(options)}个）")
            score -= 10
        
        correct_answer = exercise.get("answer", "").strip().upper()
        if not correct_answer:
            issues.append("缺少正确答案")
            score -= 40
        elif correct_answer not in self.exercise_criteria["valid_options"]:
            warnings.append(f"答案格式可能不正确（{correct_answer}）")
            score -= 10
        
        explanation = exercise.get("explanation", "")
        if not explanation:
            issues.append("缺少答案解析")
            score -= 30
        elif len(explanation) < 20:
            warnings.append("答案解析过于简短")
            score -= 10
        
        is_valid = len(issues) == 0 and score >= 60
        
        return {
            "is_valid": is_valid,
            "score": max(0, score),
            "issues": issues,
            "warnings": warnings,
            "metrics": {
                "has_question": bool(exercise.get("question")),
                "options_count": len(options),
                "has_answer": bool(correct_answer),
                "has_explanation": bool(explanation),
                "explanation_length": len(explanation)
            }
        }
    
    def validate_learning_content(self, content: Dict[str, Any], mode: str = "simple") -> Dict[str, Any]:
        explanation = content.get("explanation", "")
        exercise = content.get("exercise", {})
        
        explanation_validation = self.validate_explanation(explanation, mode)
        exercise_validation = self.validate_exercise(exercise)
        
        overall_score = (explanation_validation["score"] * 0.6 + exercise_validation["score"] * 0.4)
        
        all_issues = explanation_validation["issues"] + exercise_validation["issues"]
        all_warnings = explanation_validation["warnings"] + exercise_validation["warnings"]
        
        is_valid = explanation_validation["is_valid"] and exercise_validation["is_valid"] and overall_score >= 60
        
        return {
            "is_valid": is_valid,
            "overall_score": max(0, overall_score),
            "explanation_validation": explanation_validation,
            "exercise_validation": exercise_validation,
            "all_issues": all_issues,
            "all_warnings": all_warnings
        }
    
    def improve_content(self, content: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        improved = content.copy()
        
        if not validation["explanation_validation"]["is_valid"]:
            issues = validation["explanation_validation"]["issues"]
            
            if "讲解内容过短" in str(issues):
                improved["explanation"] = self._expand_explanation(
                    improved.get("explanation", ""),
                    content.get("knowledge_point", "")
                )
            
            if "内容包含不确定或模糊的表达" in str(issues):
                improved["explanation"] = self._remove_uncertainty(improved.get("explanation", ""))
        
        if not validation["exercise_validation"]["is_valid"]:
            issues = validation["exercise_validation"]["issues"]
            
            if "缺少答案解析" in str(issues):
                improved["exercise"]["explanation"] = self._generate_simple_explanation(
                    improved.get("exercise", {}).get("question", ""),
                    improved.get("exercise", {}).get("answer", "")
                )
        
        return improved
    
    def _expand_explanation(self, explanation: str, knowledge_point: str) -> str:
        if len(explanation) < 100:
            expanded = f"{explanation}\n\n这个概念在{knowledge_point}中非常重要，理解它有助于掌握后续相关知识。"
            return expanded
        return explanation
    
    def _remove_uncertainty(self, explanation: str) -> str:
        uncertain_phrases = ["可能", "也许", "大概", "应该", "似乎"]
        
        for phrase in uncertain_phrases:
            explanation = explanation.replace(phrase, "")
        
        explanation = explanation.replace("不确定", "明确").replace("不清楚", "清晰")
        
        return explanation
    
    def _generate_simple_explanation(self, question: str, answer: str) -> str:
        return f"这道题考察了对知识点的理解。选择{answer}是正确的，因为它是基于核心概念的正确理解。"
    
    def get_quality_report(self, content: Dict[str, Any], mode: str = "simple") -> str:
        validation = self.validate_learning_content(content, mode)
        
        lines = []
        lines.append("\n📋 内容质量报告")
        lines.append("="*50)
        lines.append(f"总体评分：{validation['overall_score']:.0f}/100")
        lines.append(f"状态：{'✅ 通过' if validation['is_valid'] else '❌ 需要改进'}")
        
        if validation['all_issues']:
            lines.append("\n⚠️ 问题：")
            for issue in validation['all_issues']:
                lines.append(f"  - {issue}")
        
        if validation['all_warnings']:
            lines.append("\n💡 建议：")
            for warning in validation['all_warnings']:
                lines.append(f"  - {warning}")
        
        return "\n".join(lines)


quality_controller = ContentQualityController()
