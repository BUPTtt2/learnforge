from typing import List, Any, Optional
import numpy as np
import os
import ssl
import gc
import sys

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL'] = '1'

ssl._create_default_https_context = ssl._create_unverified_context

try:
    import httpx
    from httpx import AsyncClient, Client
    
    original_async_client_init = AsyncClient.__init__
    original_client_init = Client.__init__
    
    def patched_async_client_init(self, *args, **kwargs):
        kwargs.setdefault('verify', False)
        original_async_client_init(self, *args, **kwargs)
    
    def patched_client_init(self, *args, **kwargs):
        kwargs.setdefault('verify', False)
        original_client_init(self, *args, **kwargs)
    
    AsyncClient.__init__ = patched_async_client_init
    Client.__init__ = patched_client_init
    print("[OK] Patched httpx Client classes for SSL bypass")
except Exception as e:
    print(f"[Warning] httpx patching failed: {e}")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[Warning] sentence-transformers not installed, using fallback method")

class EmbeddingManager:
    """嵌入模型管理器 - 支持sentence-transformers和显存优化"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_model()
        else:
            print("[Info] Using embedding fallback method (sentence-transformers not available)")

    def _load_model(self):
        """加载sentence-transformers模型，支持显存优化"""
        try:
            print(f"[Info] Loading embedding model: {self.model_name}")
            
            # 首先尝试本地模型路径
            local_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", self.model_name)
            
            if os.path.exists(local_model_path):
                print(f"[Info] Loading model from local path: {local_model_path}")
                self.model = SentenceTransformer(local_model_path, device='cpu')
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"[Success] Loaded model from local path (dimension: {self.dimension})")
                return
            
            # 如果本地没有，尝试从HuggingFace下载
            print("[Info] Local model not found, trying HuggingFace...")
            self.model = SentenceTransformer(self.model_name, device='cpu')
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"[Success] Embedding model '{self.model_name}' loaded successfully (dimension: {self.dimension})")

        except Exception as e:
            print(f"[Error] Failed to load embedding model: {e}")
            print("[Info] Falling back to simple embedding method")
            self.model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        为文本列表生成嵌入向量

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not texts:
            return []

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return embeddings.tolist()
            except Exception as e:
                print(f"[Error] Sentence transformer encoding failed: {e}")
                return self._fallback_embed_texts(texts)
        else:
            return self._fallback_embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        """
        为单个查询生成嵌入向量

        Args:
            query: 查询文本

        Returns:
            List[float]: 嵌入向量
        """
        if not query:
            return [0.0] * self.dimension

        if self.model is not None:
            try:
                embedding = self.model.encode(query, convert_to_numpy=True, show_progress_bar=False)
                return embedding.tolist()
            except Exception as e:
                print(f"[Error] Sentence transformer encoding failed: {e}")
                return self._fallback_embed_query(query)
        else:
            return self._fallback_embed_query(query)

    def _fallback_embed_texts(self, texts: List[str]) -> List[List[float]]:
        """回退方法：为文本列表生成简单嵌入向量"""
        return [self._fallback_embed_query(text) for text in texts]

    def _fallback_embed_query(self, query: str) -> List[float]:
        """回退方法：为查询生成简单嵌入向量（基于词频和字符特征）"""
        if not query:
            return [0.0] * self.dimension
        
        query_lower = query.lower()
        vector = []
        
        # 提取特征
        features = []
        
        # 字符级特征
        char_counts = {}
        for char in query_lower:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # 基于ASCII值的特征
        ascii_sum = sum(ord(c) for c in query_lower)
        ascii_avg = ascii_sum / len(query_lower) if query_lower else 0
        
        # 长度特征
        len_norm = len(query_lower) / 1000.0
        
        # 构建向量
        for i in range(self.dimension):
            if i == 0:
                vector.append(len_norm)
            elif i == 1:
                vector.append(ascii_avg / 256.0)
            else:
                # 使用字符哈希
                char_pos = (i - 2) % len(query_lower)
                char = query_lower[char_pos]
                char_val = (ord(char) + i * 37) % 256
                vector.append(char_val / 256.0)
        
        return vector

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        计算两个嵌入向量的余弦相似度

        Args:
            embedding1: 第一个嵌入向量
            embedding2: 第二个嵌入向量

        Returns:
            float: 相似度分数 (0-1)
        """
        if not embedding1 or not embedding2:
            return 0.0

        try:
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(max(0, similarity))
        except Exception as e:
            print(f"[Error] Similarity calculation failed: {e}")
            return 0.0

    def unload_model(self):
        """卸载模型以释放显存"""
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            print("[Info] Embedding model unloaded to free memory")

    def reload_model(self):
        """重新加载模型"""
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.model is None:
            self._load_model()

embedding_manager = EmbeddingManager()