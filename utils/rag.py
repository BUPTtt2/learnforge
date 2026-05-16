import chromadb
from typing import List, Dict, Any, Optional
from utils.embedding import embedding_manager
from utils.tavily_client import tavily_search
import os

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        print("[Warning] langchain text splitter not available, using simple text splitting")

class RAGSystem:
    """检索增强生成（RAG）系统 - 支持智能文档切分和搜索过滤"""

    def __init__(self):
        self.collection_name = "learnforge_knowledge"
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag_db")
        os.makedirs(self.db_path, exist_ok=True)

        self.text_splitter = None
        if LANGCHAIN_AVAILABLE:
            self._init_text_splitter()

        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "LearnForge knowledge base"}
            )
            print(f"[Success] RAG system initialized with collection: {self.collection_name}")
        except Exception as e:
            print(f"[Error] RAG system initialization failed: {e}")
            self.client = None
            self.collection = None

    def _init_text_splitter(self):
        """初始化langchain文本分割器"""
        try:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";"]
            )
            print("[Success] LangChain text splitter initialized")
        except Exception as e:
            print(f"[Error] Failed to initialize text splitter: {e}")
            self.text_splitter = None

    def split_document(self, content: str) -> List[str]:
        """使用langchain分割文档"""
        if self.text_splitter is not None:
            try:
                return self.text_splitter.split_text(content)
            except Exception as e:
                print(f"[Error] LangChain splitting failed: {e}")
        return self._simple_split(content)

    def _simple_split(self, content: str, max_chunk_size: int = 512) -> List[str]:
        """简单的文本分割方法"""
        chunks = []
        paragraphs = content.split("\n\n")
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(paragraph) > max_chunk_size:
                    for i in range(0, len(paragraph), max_chunk_size):
                        chunks.append(paragraph[i:i + max_chunk_size])
                    current_chunk = ""
                else:
                    current_chunk = paragraph + "\n\n"
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks if chunks else [content]

    def add_document(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """添加文档到知识库，自动分割长文档"""
        if not self.collection:
            return False
        try:
            chunks = self.split_document(content)
            if len(chunks) == 1:
                embedding = embedding_manager.embed_query(content)
                if not embedding:
                    return False
                doc_id = f"doc_{hash(content)}_{len(self.collection.get()['ids'])}"
                self.collection.add(
                    documents=[content],
                    embeddings=[embedding],
                    metadatas=[metadata or {}],
                    ids=[doc_id]
                )
            else:
                for i, chunk in enumerate(chunks):
                    embedding = embedding_manager.embed_query(chunk)
                    if not embedding:
                        continue
                    doc_id = f"doc_{hash(chunk)}_{i}_{len(self.collection.get()['ids'])}"
                    chunk_metadata = (metadata or {}).copy()
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    chunk_metadata["is_chunk"] = True
                    self.collection.add(
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[chunk_metadata],
                        ids=[doc_id]
                    )
            print(f"[RAG] Added document with {len(chunks)} chunks")
            return True
        except Exception as e:
            print(f"[Error] Failed to add document: {e}")
            return False

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None) -> bool:
        """批量添加文档"""
        if not self.collection or not documents:
            return False
        try:
            all_chunks = []
            all_metadatas = []
            for i, doc in enumerate(documents):
                chunks = self.split_document(doc)
                metadata = (metadatas or [{}] * len(documents))[i] if metadatas else {}
                for j, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = j
                    chunk_metadata["total_chunks"] = len(chunks)
                    chunk_metadata["original_doc_index"] = i
                    all_metadatas.append(chunk_metadata)
            if not all_chunks:
                return False
            embeddings = embedding_manager.embed_texts(all_chunks)
            if not all(embeddings):
                return False
            ids = [f"doc_{hash(chunk)}_{i}" for i, chunk in enumerate(all_chunks)]
            self.collection.add(
                documents=all_chunks,
                embeddings=embeddings,
                metadatas=all_metadatas,
                ids=ids
            )
            print(f"[RAG] Added {len(documents)} documents with {len(all_chunks)} total chunks")
            return True
        except Exception as e:
            print(f"[Error] Failed to add documents: {e}")
            return False

    def search_local(self, query: str, k: int = 3, min_score: float = 0.0) -> List[Dict]:
        """在本地知识库中搜索（结合向量检索和关键词匹配）"""
        if not self.collection:
            return []

        try:
            query_embedding = embedding_manager.embed_query(query)
            if not query_embedding:
                return self._keyword_search(query, k)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k * 3,
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                content = results["documents"][0][i]

                vector_score = 1.0 / (1.0 + distance) if distance >= 0 else 0

                keyword_score = self._calculate_keyword_match(query, content)

                final_score = (vector_score * 0.4) + (keyword_score * 0.6)

                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": content,
                    "metadata": results["metadatas"][0][i],
                    "score": final_score,
                    "vector_score": vector_score,
                    "keyword_score": keyword_score
                })

            formatted_results.sort(key=lambda x: x["score"], reverse=True)

            return formatted_results[:k]

        except Exception as e:
            print(f"[Error] Local search failed: {e}")
            return self._keyword_search(query, k)

    def _keyword_search(self, query: str, k: int = 3) -> List[Dict]:
        """基于关键词匹配的搜索（备用方法）"""
        if not self.collection:
            return []

        try:
            all_data = self.collection.get(include=["documents", "metadatas"])

            results = []
            for i, doc_id in enumerate(all_data["ids"]):
                content = all_data["documents"][i]
                metadata = all_data["metadatas"][i]

                score = self._calculate_keyword_match(query, content)

                if score > 0:
                    results.append({
                        "id": doc_id,
                        "content": content,
                        "metadata": metadata,
                        "score": score,
                        "vector_score": 0,
                        "keyword_score": score
                    })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:k]

        except Exception as e:
            print(f"[Error] Keyword search failed: {e}")
            return []

    def _calculate_keyword_match(self, query: str, content: str) -> float:
        """计算关键词匹配分数（支持中英文）"""
        query_lower = query.lower()
        content_lower = content.lower()

        query_tokens = query_lower.split()

        if len(query_tokens) == 1 and not query_tokens[0].isascii():
            chinese_chars = set(query_tokens[0])
            content_chars = set(content_lower)
            if len(chinese_chars) == 0:
                return 0.0
            char_matches = len(chinese_chars & content_chars)
            return char_matches / len(chinese_chars)
        else:
            if not query_tokens:
                return 0.0
            matches = sum(1 for token in query_tokens if token in content_lower)
            return matches / len(query_tokens)

    def search_external(self, query: str, search_depth: str = "basic") -> Dict:
        """使用外部搜索引擎搜索"""
        return tavily_search.search_and_summarize(query, search_depth=search_depth)

    def _filter_search_results(self, results: List[Dict], query: str, min_score: float = 0.0) -> List[Dict]:
        """使用LLM过滤搜索结果"""
        if not results:
            return []
        return results

    def _evaluate_retrieval_quality(self, local_results: List[Dict]) -> Dict:
        """评估本地检索结果质量"""
        if not local_results:
            return {
                "quality_score": 0.0,
                "avg_vector_score": 0.0,
                "avg_keyword_score": 0.0,
                "has_relevant": False
            }

        avg_score = sum(r["score"] for r in local_results) / len(local_results)
        avg_vector_score = sum(r.get("vector_score", 0) for r in local_results) / len(local_results)
        avg_keyword_score = sum(r.get("keyword_score", 0) for r in local_results) / len(local_results)

        quality_score = (avg_score * 0.5 + avg_vector_score * 0.3 + avg_keyword_score * 0.2)

        has_relevant = False
        for r in local_results:
            if r.get("vector_score", 0) >= 0.5:
                has_relevant = True
                break

        return {
            "quality_score": quality_score,
            "avg_vector_score": avg_vector_score,
            "avg_keyword_score": avg_keyword_score,
            "has_relevant": has_relevant
        }

    def hybrid_search(self, query: str, local_k: int = 3, use_external: bool = True,
                      min_score: float = 0.3, auto_add_to_knowledge: bool = True,
                      quality_threshold: float = 0.5,
                      vector_threshold: float = 0.3) -> Dict:
        """混合搜索（本地 + 外部）- 智能决策是否联网"""
        results = {
            "local": [],
            "external": {},
            "query": query,
            "external_triggered": False,
            "retrieval_quality": 0.0,
            "decision_reason": ""
        }

        local_results = self.search_local(query, k=local_k, min_score=min_score)
        local_results = self._filter_search_results(local_results, query, min_score=min_score)
        results["local"] = local_results

        quality_info = self._evaluate_retrieval_quality(local_results)
        results["retrieval_quality"] = quality_info["quality_score"]

        need_external = False
        reason = ""

        if use_external:
            if not local_results:
                need_external = True
                reason = "本地无检索结果"
            elif quality_info["quality_score"] < quality_threshold:
                need_external = True
                reason = f"综合质量 {quality_info['quality_score']:.2f} < 阈值 {quality_threshold}"
            elif quality_info["avg_vector_score"] < vector_threshold:
                need_external = True
                reason = f"向量相似度 {quality_info['avg_vector_score']:.2f} < 阈值 {vector_threshold}"
            elif not quality_info["has_relevant"]:
                need_external = True
                reason = "无高相关结果（向量相似度<0.5）"

        if need_external:
            print(f"[RAG] 触发外部搜索: {reason}")
            external = self.search_external(query)
            results["external"] = external
            results["external_triggered"] = True
            results["decision_reason"] = reason
            if auto_add_to_knowledge and external.get("success") and external.get("results"):
                self._add_external_results_to_knowledge(external.get("results", []), query)
        else:
            print(f"[RAG] 无需外部搜索: 综合质量 {quality_info['quality_score']:.2f}, 向量相似度 {quality_info['avg_vector_score']:.2f}")
            results["decision_reason"] = "本地检索质量达标"

        return results

    def _add_external_results_to_knowledge(self, search_results: List[Dict], query: str):
        """将外部搜索结果添加到知识库"""
        try:
            for result in search_results[:3]:
                content = result.get("content", "")
                if content and len(content) > 50:
                    metadata = {
                        "source": "tavily_search",
                        "query": query,
                        "url": result.get("url", ""),
                        "timestamp": str(hash(content))
                    }
                    self.add_document(content, metadata)
            print(f"[RAG] Added {min(3, len(search_results))} external search results to knowledge base")
        except Exception as e:
            print(f"[Error] Failed to add external results to knowledge: {e}")

    def generate_context(self, query: str, max_chars: int = 1000) -> str:
        """为生成任务构建上下文"""
        search_results = self.hybrid_search(query, local_k=3, use_external=True)
        context_parts = []
        if search_results.get("local"):
            context_parts.append("# 本地知识")
            for result in search_results["local"]:
                context_parts.append(f"[相关度: {result['score']:.2f}] {result['content']}")
        if search_results.get("external", {}).get("success"):
            external = search_results["external"]
            if external.get("summary"):
                context_parts.append("# 外部搜索")
                context_parts.append(external["summary"])
        context = "\n\n".join(context_parts)
        if len(context) > max_chars:
            context = context[:max_chars] + "..."
        return context

    def clear_collection(self) -> bool:
        """清空知识库"""
        if not self.collection:
            return False
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "LearnForge knowledge base"}
            )
            return True
        except Exception as e:
            print(f"[Error] Failed to clear collection: {e}")
            return False

    def get_collection_stats(self) -> Dict:
        """获取知识库统计信息"""
        if not self.collection:
            return {"document_count": 0, "chunk_count": 0}
        try:
            all_data = self.collection.get()
            count = len(all_data['ids'])
            chunk_count = sum(1 for m in all_data.get('metadatas', []) if m.get('is_chunk', False))
            return {
                "document_count": count,
                "chunk_count": chunk_count
            }
        except Exception as e:
            print(f"[Error] Failed to get collection stats: {e}")
            return {"document_count": 0, "chunk_count": 0}

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索接口（供API调用）"""
        results = self.hybrid_search(query, local_k=top_k, use_external=False)
        return results.get("local", [])

    def query(self, query: str, top_k: int = 5) -> List[Dict]:
        """查询接口（别名，供讲解师调用）"""
        return self.search(query, top_k)

    def get_stats(self) -> Dict:
        """获取统计信息接口（供API调用）"""
        return self.get_collection_stats()

rag_system = RAGSystem()
