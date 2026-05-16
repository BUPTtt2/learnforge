import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ContentSafety:
    """内容安全检查器"""
    
    def __init__(self):
        # 敏感词列表（示例，实际项目中应该加载外部词库）
        self.sensitive_keywords = [
            '暴力', '血腥', '色情', '诈骗', '违法', '犯罪',
            '恐怖', '极端', '煽动', '分裂', '颠覆', '颠覆国家',
            '反动', '邪教', '迷信', '赌博', '毒品', '吸毒',
            '自杀', '自残', '侮辱', '诽谤', '辱骂', '威胁'
        ]
        
        # Prompt注入检测模式
        self.prompt_injection_patterns = [
            r'忽视[之\s的]*前.*指令',
            r'忽略[之\s的]*前.*提示',
            r'忘记[之\s的]*前.*要求',
            r'不要[遵守\管]*之前.*内容',
            r'你现在.*是.*而不是',
            r'请扮演.*而不是',
            r'假装.*忽略前面的',
            r'无视之前的[对话|指令|提示]',
            r'忘记你是一个.*助手',
            r'忽略以上.*说的话',
            r'你现在应该听我的',
            r'重新定义你的行为',
            r'你不再是一个.*而是'
        ]
        
        # 输出违规检测模式
        self.output_violation_patterns = [
            r'[如何\怎么\怎样]*.*[制作|制造|生产|获取|购买].*[毒品|武器|炸药|枪支]',
            r'[如何\怎么\怎样]*.*[攻击|入侵|渗透|破解].*[系统|网站|网络]',
            r'[如何\怎么\怎样]*.*[诈骗|欺骗|勒索|敲诈].*',
            r'[步骤|方法|教程].*[非法|违法|违规]'
        ]
    
    def check_input_safety(self, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        检查用户输入是否安全
        
        Args:
            text: 用户输入文本
            
        Returns:
            (is_safe, reason, details)
        """
        if not text:
            return True, "", {}
        
        details = {
            'sensitive_detected': [],
            'prompt_injection_detected': False
        }
        
        # 1. 检查敏感词
        text_lower = text.lower()
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                details['sensitive_detected'].append(keyword)
        
        if details['sensitive_detected']:
            logger.warning(f"[安全检查] 检测到敏感词: {details['sensitive_detected']}")
            return False, "检测到敏感内容", details
        
        # 2. 检查Prompt注入
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                details['prompt_injection_detected'] = True
                logger.warning(f"[安全检查] 检测到Prompt注入尝试: {text[:100]}...")
                return False, "检测到可疑内容", details
        
        return True, "", details
    
    def check_output_safety(self, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        检查模型输出是否安全
        
        Args:
            text: 模型输出文本
            
        Returns:
            (is_safe, reason, details)
        """
        if not text:
            return True, "", {}
        
        details = {
            'violation_detected': []
        }
        
        # 检查输出违规模式
        for pattern in self.output_violation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                details['violation_detected'].append(pattern)
        
        if details['violation_detected']:
            logger.warning(f"[安全检查] 检测到违规输出: {text[:100]}...")
            return False, "输出内容违规", details
        
        return True, "", details
    
    def sanitize_output(self, text: str) -> str:
        """
        输出内容清洗（可选的轻量级清洗）
        
        Args:
            text: 原始输出
            
        Returns:
            清洗后的输出
        """
        # 轻量清洗：仅过滤极端敏感词
        sanitized = text
        for keyword in self.sensitive_keywords:
            if keyword in sanitized:
                sanitized = sanitized.replace(keyword, '*' * len(keyword))
        return sanitized


# 单例模式
_content_safety = None

def get_content_safety() -> ContentSafety:
    """获取安全检查器单例"""
    global _content_safety
    if _content_safety is None:
        _content_safety = ContentSafety()
    return _content_safety
