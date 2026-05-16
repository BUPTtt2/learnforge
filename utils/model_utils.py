import time
import threading
import requests
import json
from typing import Optional, Any

class TimeoutException(Exception):
    pass

def timeout_decorator(timeout: int = 3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            exception = None
            
            def target():
                nonlocal result, exception
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout=timeout)
            
            if thread.is_alive():
                raise TimeoutException(f"Request timed out after {timeout} seconds")
            
            if exception:
                raise exception
            
            return result
        return wrapper
    return decorator

class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434/v1"
        self.available = self._check_connection()
    
    def _check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                models = response.json()
                model_ids = [m['id'] for m in models.get('data', [])]
                if 'qwen3:4b' in model_ids or 'qwen2.5:7b' in model_ids:
                    print("[OllamaClient] Connected to Ollama")
                    return True
            return False
        except Exception as e:
            print(f"[OllamaClient] Not available: {e}")
            return False
    
    def generate(self, prompt: str, model_name: str = "qwen3:4b", max_tokens: int = 300, temperature: float = 0.7):
        if not self.available:
            raise ValueError("Ollama not available")
        
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(
                f"{self.base_url}/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('text', '')
            else:
                raise ValueError(f"Ollama API error: {response.status_code}")
        except Exception as e:
            print(f"[OllamaClient] Generation error: {e}")
            raise

class HybridModelManager:
    def __init__(self):
        from .model import model_manager
        self.ollama_client = OllamaClient()
        self.remote_model = model_manager
        self.default_timeout = 3
    
    def generate_local(self, prompt: str, **kwargs) -> str:
        if self.ollama_client.available:
            try:
                model_name = kwargs.get('model_name', 'qwen3:4b')
                max_tokens = kwargs.get('max_new_tokens', kwargs.get('max_tokens', 300))
                temperature = kwargs.get('temperature', 0.7)
                return self.ollama_client.generate(prompt, model_name, max_tokens, temperature)
            except Exception as e:
                print(f"[HybridModel] Ollama error: {e}")
                raise
        raise ValueError("No local model available")
    
    @timeout_decorator(timeout=3)
    def generate_remote_with_timeout(self, prompt: str, task_type: str = 'default') -> str:
        return self.remote_model.generate_content(task_type, prompt, use_cache=False)
    
    def generate_remote_safe(self, prompt: str, task_type: str = 'default') -> Optional[str]:
        try:
            return self.generate_remote_with_timeout(prompt, task_type)
        except TimeoutException:
            print(f"[HybridModel] Remote API timeout after {self.default_timeout}s, falling back")
            return None
        except Exception as e:
            print(f"[HybridModel] Remote API error: {e}")
            return None
    
    def generate(self, prompt: str, use_local: bool = True, fallback_to_remote: bool = True, **kwargs) -> str:
        """
        生成响应，支持自动降级
        
        Args:
            prompt: 输入提示
            use_local: 是否优先使用本地模型
            fallback_to_remote: 本地失败时是否降级到远程API
            **kwargs: 其他参数（model_name, max_tokens, temperature等）
        
        Returns:
            生成的文本响应
        """
        if use_local:
            try:
                return self.generate_local(prompt, **kwargs)
            except Exception as e:
                print(f"[HybridModel] Local model failed: {e}")
                if fallback_to_remote:
                    print("[HybridModel] Falling back to remote API")
                    remote_result = self.generate_remote_safe(prompt)
                    if remote_result:
                        return remote_result
                    print("[HybridModel] Remote API also failed")
                    return f"Model generation failed: {str(e)}"
                raise
        
        result = self.generate_remote_safe(prompt)
        if result is None and fallback_to_remote:
            print("[HybridModel] Remote failed, trying local")
            try:
                return self.generate_local(prompt, **kwargs)
            except Exception as e:
                return f"Both local and remote failed: {str(e)}"
        
        return result or "Failed to generate response"

hybrid_model_manager = HybridModelManager()