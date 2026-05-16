import os
import hashlib
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from config import VOLCENGINE_API_KEY, VOLCENGINE_BASE_URL, DEEPSEEK_MODEL, MAX_CACHE_SIZE, API_CALL_DELAY

class ModelAPIError(Exception):
    pass

class RateLimitError(ModelAPIError):
    pass

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        print(f"[Retry] Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (attempt + 1)
                        print(f"[Retry] Error: {e}, waiting {wait_time}s...")
                        time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator

class ModelManager:
    def __init__(self):
        self.client = None
        self.models = {}
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.api_calls = 0
        self.failed_calls = 0
        self._init_models()
    
    def _init_models(self):
        try:
            from openai import OpenAI
            
            self.client = OpenAI(
                base_url=VOLCENGINE_BASE_URL,
                api_key=VOLCENGINE_API_KEY,
                timeout=60,
                max_retries=2
            )
            
            self.models['deepseek'] = DEEPSEEK_MODEL
            print(f"[Success] {DEEPSEEK_MODEL} model initialized successfully (VolcEngine API)")
        except Exception as e:
            print(f"[Warning] Model initialization failed: {e}")
            print("Using mock mode to continue running")
            self.models['deepseek'] = None
    
    def get_model(self, task_type: str = 'default'):
        return self.models.get('deepseek')
    
    def _generate_cache_key(self, task_type: str, prompt: str) -> str:
        content = f"{task_type}:{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @retry_on_error(max_retries=3, delay=0.5)
    def generate_content(self, task_type: str, prompt: str, use_cache: bool = True) -> Any:
        cache_key = self._generate_cache_key(task_type, prompt)
        
        if use_cache and cache_key in self.cache:
            self.cache_hits += 1
            print(f"[Cache Hit] {task_type} (Hits: {self.cache_hits}/{self.cache_hits + self.cache_misses})")
            return self.cache[cache_key]
        
        self.cache_misses += 1
        self.api_calls += 1
        
        model = self.get_model(task_type)
        if model is None or self.client is None:
            return self._generate_mock_response(prompt)
        
        try:
            result = self._call_model_with_retry(model, prompt)
            
            if use_cache and len(self.cache) < MAX_CACHE_SIZE:
                self.cache[cache_key] = result
            
            return result
            
        except RateLimitError:
            self.failed_calls += 1
            raise
        except Exception as e:
            self.failed_calls += 1
            print(f"[Error] API call failed: {e}")
            return self._generate_mock_response(prompt)
    
    @retry_on_error(max_retries=3, delay=1.0)
    def _call_model_with_retry(self, model: str, prompt: str) -> Any:
        try:
            print(f"[Model Call] Calling model: {model}")
            print(f"[Model Call] Prompt length: {len(prompt)} characters")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                stream=False
            )
            
            print(f"[Model Call] Response received")
            
            if response and response.choices:
                content = response.choices[0].message.content
                print(f"[Model Call] Content length: {len(content)} characters")
                return content
            print("[Model Call] No choices in response")
            return ""
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Model Call] Error: {error_msg}")
            if 'rate limit' in error_msg.lower() or '429' in error_msg:
                raise RateLimitError("API rate limit exceeded")
            raise
    
    def _generate_mock_response(self, prompt: str) -> Dict[str, Any]:
        if "复杂度" in prompt:
            return "简单"
        
        if "章节" in prompt or "拆分" in prompt:
            import re
            match = re.search(r'知识点[：:]\s*([^\n]+)', prompt)
            topic = match.group(1) if match else "这个知识点"
            chapters = [
                f"{topic}基础概念",
                f"{topic}核心原理",
                f"{topic}应用场景"
            ]
            return "\n".join(chapters)
        
        return {
            "explanation": f"这是关于知识点的专业讲解内容。",
            "exercise": {
                "question": "以下关于该知识点的说法正确的是？",
                "options": [
                    "A. 第一个正确说法",
                    "B. 第二个正确说法",
                    "C. 第三个正确说法",
                    "D. 以上都不对"
                ],
                "answer": "A",
                "explanation": "答案是A，因为..."
            }
        }
    
    def clear_cache(self):
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        print("[System] Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "api_calls": self.api_calls,
            "failed_calls": self.failed_calls,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{cache_hit_rate:.1%}",
            "cache_size": len(self.cache)
        }
    
    def log_stats(self):
        stats = self.get_stats()
        print("\n[Stats] Model Call Statistics:")
        print(f"  API Calls: {stats['api_calls']}")
        print(f"  Failed Calls: {stats['failed_calls']}")
        print(f"  Cache Hits: {stats['cache_hits']}")
        print(f"  Cache Misses: {stats['cache_misses']}")
        print(f"  Cache Hit Rate: {stats['cache_hit_rate']}")
        print(f"  Current Cache Size: {stats['cache_size']}")


model_manager = ModelManager()
