from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from utils.embedding import embedding_manager

@dataclass
class RetrievalResult:
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalMetrics:
    query: str
    top_k: int
    results: List[RetrievalResult]

    avg_similarity: float = 0.0
    keyword_match_rate: float = 0.0
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    hit_rate: float = 0.0
    mrr: float = 0.0
    ndcg_at_k: Dict[int, float] = field(default_factory=dict)

@dataclass
class GenerationMetrics:
    query: str
    answer: str
    retrieved_contexts: List[str]

    answer_relevance: float = 0.0
    retrieval_match_rate: float = 0.0
    completeness: float = 0.0

    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    user_thumbs_up: Optional[bool] = None
    feedback_timestamp: Optional[datetime] = None

    combined_score: float = 0.0

@dataclass
class ComprehensiveMetrics:
    session_id: str
    timestamp: datetime
    query: str

    retrieval_metrics: Optional[RetrievalMetrics] = None
    generation_metrics: Optional[GenerationMetrics] = None

    overall_score: float = 0.0
    improvement_suggestions: List[str] = field(default_factory=list)

def _calculate_keyword_match(query: str, content: str) -> float:
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

class RetrievalEvaluator:
    """检索层评估器"""

    def __init__(self):
        self.embedding_manager = embedding_manager

    def evaluate(self, query: str, results: List[Dict],
                 relevant_docs: Optional[List[str]] = None,
                 k_values: List[int] = None) -> RetrievalMetrics:
        """评估检索结果"""
        if k_values is None:
            k_values = [3, 5, 10]

        retrieval_results = [
            RetrievalResult(
                id=r.get('id', ''),
                content=r.get('content', ''),
                score=r.get('score', 0.0),
                metadata=r.get('metadata', {})
            )
            for r in results
        ]

        metrics = RetrievalMetrics(
            query=query,
            top_k=len(results),
            results=retrieval_results
        )

        metrics.avg_similarity = self._calculate_avg_similarity(retrieval_results)

        metrics.keyword_match_rate = self._calculate_keyword_match_rate(
            query, retrieval_results
        )

        if relevant_docs is not None and len(relevant_docs) > 0:
            metrics.recall_at_k = self._calculate_recall_at_k(
                retrieval_results, relevant_docs, k_values
            )
            metrics.hit_rate = self._calculate_hit_rate(
                retrieval_results, relevant_docs
            )
            metrics.mrr = self._calculate_mrr(
                retrieval_results, relevant_docs
            )
            metrics.ndcg_at_k = self._calculate_ndcg_at_k(
                retrieval_results, relevant_docs, k_values
            )

        return metrics

    def _calculate_avg_similarity(self, results: List[RetrievalResult]) -> float:
        """计算平均相似度"""
        if not results:
            return 0.0
        return sum(r.score for r in results) / len(results)

    def _calculate_keyword_match_rate(self, query: str,
                                     results: List[RetrievalResult]) -> float:
        """计算关键词匹配率（支持中英文）"""
        if not results or not query:
            return 0.0

        total_matches = 0
        for result in results:
            score = _calculate_keyword_match(query, result.content)
            total_matches += score

        return total_matches / len(results)

    def _calculate_recall_at_k(self, results: List[RetrievalResult],
                              relevant_docs: List[str],
                              k_values: List[int]) -> Dict[int, float]:
        """计算Recall@K"""
        relevant_set = set(relevant_docs)
        recall_scores = {}

        for k in k_values:
            if k > len(results):
                continue
            top_k_results = results[:k]
            top_k_contents = set(r.content for r in top_k_results)
            recall = len(top_k_contents & relevant_set) / len(relevant_set) if relevant_set else 0
            recall_scores[k] = recall

        return recall_scores

    def _calculate_hit_rate(self, results: List[RetrievalResult],
                           relevant_docs: List[str]) -> float:
        """计算Hit Rate"""
        if not relevant_docs:
            return 0.0

        result_contents = set(r.content for r in results)
        relevant_set = set(relevant_docs)

        return 1.0 if result_contents & relevant_set else 0.0

    def _calculate_mrr(self, results: List[RetrievalResult],
                       relevant_docs: List[str]) -> float:
        """计算Mean Reciprocal Rank"""
        if not relevant_docs:
            return 0.0

        relevant_set = set(relevant_docs)

        for i, result in enumerate(results, 1):
            if result.content in relevant_set:
                return 1.0 / i

        return 0.0

    def _calculate_ndcg_at_k(self, results: List[RetrievalResult],
                             relevant_docs: List[str],
                             k_values: List[int]) -> Dict[int, float]:
        """计算NDCG@K"""
        relevant_set = set(relevant_docs)
        ndcg_scores = {}

        for k in k_values:
            if k > len(results):
                continue

            dcg = 0.0
            for i, result in enumerate(results[:k], 1):
                rel = 1.0 if result.content in relevant_set else 0.0
                dcg += (2 ** rel - 1) / np.log2(i + 1)

            ideal_k = min(k, len(relevant_docs))
            if ideal_k == 0:
                ndcg_scores[k] = 0.0
                continue

            idcg = sum((2 ** 1 - 1) / np.log2(i + 1) for i in range(1, ideal_k + 1))
            ndcg = dcg / idcg if idcg > 0 else 0
            ndcg_scores[k] = ndcg

        return ndcg_scores

class GenerationEvaluator:
    """生成层评估器"""

    def __init__(self):
        self.embedding_manager = embedding_manager
        self.feedback_history: List[Dict] = []
        self.alpha = 0.8
        self.beta = 0.2

    def evaluate(self, query: str, answer: str,
                retrieved_contexts: List[str],
                feedback: Optional[Dict] = None) -> GenerationMetrics:
        """评估生成结果"""
        metrics = GenerationMetrics(
            query=query,
            answer=answer,
            retrieved_contexts=retrieved_contexts
        )

        metrics.answer_relevance = self._calculate_answer_relevance(query, answer)

        metrics.retrieval_match_rate = self._calculate_retrieval_match_rate(
            answer, retrieved_contexts
        )

        metrics.completeness = self._calculate_completeness(
            query, answer, retrieved_contexts
        )

        if feedback:
            metrics.user_rating = feedback.get('rating')
            metrics.user_feedback = feedback.get('feedback')
            metrics.user_thumbs_up = feedback.get('thumbs_up')
            metrics.feedback_timestamp = feedback.get('timestamp', datetime.now())

            self._update_feedback_history(metrics)

        metrics.combined_score = self._calculate_combined_score(metrics)

        return metrics

    def _calculate_answer_relevance(self, query: str, answer: str) -> float:
        """计算答案与问题的相关性"""
        if not query or not answer:
            return 0.0

        query_emb = self.embedding_manager.embed_query(query)
        answer_emb = self.embedding_manager.embed_query(answer)

        if not query_emb or not answer_emb:
            return 0.0

        similarity = self.embedding_manager.calculate_similarity(query_emb, answer_emb)
        return similarity

    def _calculate_retrieval_match_rate(self, answer: str,
                                       retrieved_contexts: List[str]) -> float:
        """计算答案对检索内容的引用率"""
        if not answer or not retrieved_contexts:
            return 0.0

        answer_lower = answer.lower()
        answer_words = set(answer_lower.split())

        if len(answer_words) == 0:
            return 0.0

        total_overlap_ratio = 0.0

        for context in retrieved_contexts:
            score = _calculate_keyword_match(context, answer)
            total_overlap_ratio += score

        return total_overlap_ratio / len(retrieved_contexts) if retrieved_contexts else 0.0

    def _calculate_completeness(self, query: str, answer: str,
                               retrieved_contexts: List[str]) -> float:
        """计算答案完整程度"""
        if not query or not answer:
            return 0.0

        query_keywords = set(query.lower().split())
        answer_keywords = set(answer.lower().split())

        if not query_keywords:
            return 0.0

        keyword_coverage = len(query_keywords & answer_keywords) / len(query_keywords)

        retrieval_hint_coverage = 0.0
        if retrieved_contexts:
            all_retrieval_text = ' '.join(retrieved_contexts).lower()
            retrieval_words = set(all_retrieval_text.split())

            answer_in_retrieval = answer_keywords & retrieval_words
            retrieval_hint_coverage = len(answer_in_retrieval) / len(answer_keywords) if answer_keywords else 0

        completeness = (keyword_coverage * 0.6 + retrieval_hint_coverage * 0.4)

        return min(1.0, completeness)

    def _calculate_combined_score(self, metrics: GenerationMetrics) -> float:
        """计算综合分数（质量分 + 反馈分）"""
        base_score = (
            metrics.answer_relevance * 0.4 +
            metrics.retrieval_match_rate * 0.3 +
            metrics.completeness * 0.3
        )

        feedback_score = 0.0
        if metrics.user_rating is not None:
            feedback_score = (metrics.user_rating - 1) / 4.0

        if metrics.user_thumbs_up is not None:
            feedback_score = 1.0 if metrics.user_thumbs_up else 0.0

        self._adjust_weights()

        combined = self.alpha * base_score + self.beta * feedback_score

        return combined

    def _update_feedback_history(self, metrics: GenerationMetrics):
        """更新反馈历史"""
        self.feedback_history.append({
            'query': metrics.query,
            'answer': metrics.answer,
            'rating': metrics.user_rating,
            'thumbs_up': metrics.user_thumbs_up,
            'timestamp': metrics.feedback_timestamp or datetime.now()
        })

        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]

    def _adjust_weights(self):
        """根据反馈历史动态调整权重"""
        if len(self.feedback_history) < 5:
            return

        recent_feedback = self.feedback_history[-20:]

        positive_count = sum(
            1 for f in recent_feedback
            if f.get('thumbs_up') is True or (f.get('rating', 0) >= 4)
        )

        positive_ratio = positive_count / len(recent_feedback)

        if positive_ratio > 0.7:
            self.beta = min(0.5, self.beta + 0.05)
        elif positive_ratio < 0.4:
            self.beta = max(0.2, self.beta - 0.05)

        self.alpha = 1.0 - self.beta

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """获取反馈统计信息"""
        if not self.feedback_history:
            return {
                'total_feedbacks': 0,
                'positive_ratio': 0.0,
                'avg_rating': 0.0,
                'current_alpha': self.alpha,
                'current_beta': self.beta
            }

        positive_count = sum(
            1 for f in self.feedback_history
            if f.get('thumbs_up') is True or (f.get('rating', 0) >= 4)
        )

        ratings = [f['rating'] for f in self.feedback_history if f.get('rating')]

        return {
            'total_feedbacks': len(self.feedback_history),
            'positive_ratio': positive_count / len(self.feedback_history),
            'avg_rating': sum(ratings) / len(ratings) if ratings else 0.0,
            'current_alpha': self.alpha,
            'current_beta': self.beta
        }

class RAGEvaluator:
    """RAG系统综合评估器"""

    def __init__(self):
        self.retrieval_evaluator = RetrievalEvaluator()
        self.generation_evaluator = GenerationEvaluator()
        self.session_metrics: Dict[str, List[ComprehensiveMetrics]] = {}

    def evaluate_interaction(self, session_id: str, query: str,
                           retrieval_results: List[Dict],
                           answer: str,
                           retrieved_contexts: List[str],
                           relevant_docs: Optional[List[str]] = None,
                           feedback: Optional[Dict] = None) -> ComprehensiveMetrics:
        """评估一次完整的交互"""
        timestamp = datetime.now()

        retrieval_metrics = self.retrieval_evaluator.evaluate(
            query, retrieval_results, relevant_docs
        )

        generation_metrics = self.generation_evaluator.evaluate(
            query, answer, retrieved_contexts, feedback
        )

        overall_score = self._calculate_overall_score(
            retrieval_metrics, generation_metrics
        )

        metrics = ComprehensiveMetrics(
            session_id=session_id,
            timestamp=timestamp,
            query=query,
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
            overall_score=overall_score
        )

        metrics.improvement_suggestions = self._generate_improvement_suggestions(
            retrieval_metrics, generation_metrics
        )

        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = []

        self.session_metrics[session_id].append(metrics)

        return metrics

    def _calculate_overall_score(self, retrieval: RetrievalMetrics,
                                generation: GenerationMetrics) -> float:
        """计算综合得分"""
        retrieval_score = (
            retrieval.avg_similarity * 0.5 +
            retrieval.keyword_match_rate * 0.3 +
            retrieval.hit_rate * 0.2
        )

        generation_score = generation.combined_score

        return retrieval_score * 0.4 + generation_score * 0.6

    def _generate_improvement_suggestions(self, retrieval: RetrievalMetrics,
                                        generation: GenerationMetrics) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if retrieval.avg_similarity < 0.5:
            suggestions.append("检索相似度偏低，考虑优化Embedding模型或调整检索参数")

        if retrieval.keyword_match_rate < 0.3:
            suggestions.append("关键词匹配率低，建议扩展同义词库或使用混合检索")

        if generation.answer_relevance < 0.5:
            suggestions.append("答案相关性不足，可能需要改进Prompt模板")

        if generation.retrieval_match_rate < 0.4:
            suggestions.append("答案对检索内容的引用率低，生成时可更多结合检索上下文")

        if generation.completeness < 0.5:
            suggestions.append("答案完整度不足，建议增加答案长度或分点论述")

        if not suggestions:
            suggestions.append("整体表现良好，继续保持！")

        return suggestions

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话评估摘要"""
        if session_id not in self.session_metrics:
            return {}

        metrics_list = self.session_metrics[session_id]

        avg_overall = sum(m.overall_score for m in metrics_list) / len(metrics_list)

        retrieval_scores = [
            m.retrieval_metrics.avg_similarity
            for m in metrics_list if m.retrieval_metrics
        ]
        avg_retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0

        generation_scores = [
            m.generation_metrics.combined_score
            for m in metrics_list if m.generation_metrics
        ]
        avg_generation = sum(generation_scores) / len(generation_scores) if generation_scores else 0

        return {
            'session_id': session_id,
            'total_interactions': len(metrics_list),
            'avg_overall_score': avg_overall,
            'avg_retrieval_score': avg_retrieval,
            'avg_generation_score': avg_generation,
            'feedback_stats': self.generation_evaluator.get_feedback_statistics()
        }

retrieval_evaluator = RetrievalEvaluator()
generation_evaluator = GenerationEvaluator()
rag_evaluator = RAGEvaluator()
