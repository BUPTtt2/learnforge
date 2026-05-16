#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试搜索功能"""

from utils.rag import rag_system
from utils.embedding import embedding_manager

print("=" * 60)
print("调试搜索功能")
print("=" * 60)

# 1. 检查embedding维度
print("\n[1] 检查embedding维度...")
query = "西班牙语学习"
query_embedding = embedding_manager.embed_query(query)
print("查询embedding维度:", len(query_embedding))
print("查询embedding前5个值:", query_embedding[:5])

# 2. 直接从collection获取数据
print("\n[2] 检查collection数据...")
if rag_system.collection:
    all_data = rag_system.collection.get(include=['documents', 'embeddings', 'metadatas'])
    print("collection中的文档数:", len(all_data['ids']))
    if all_data['embeddings']:
        print("第一个文档的embedding维度:", len(all_data['embeddings'][0]))
        print("第一个文档的embedding前5个值:", all_data['embeddings'][0][:5])
        print("\n第一个文档内容:", all_data['documents'][0][:100])
        
        # 3. 手动计算相似度
        print("\n[3] 手动计算相似度...")
        import numpy as np
        
        scores = []
        for i, doc_embedding in enumerate(all_data['embeddings']):
            # 计算余弦相似度
            dot = np.dot(query_embedding, doc_embedding)
            norm1 = np.linalg.norm(query_embedding)
            norm2 = np.linalg.norm(doc_embedding)
            similarity = dot / (norm1 * norm2) if (norm1 * norm2) > 0 else 0
            scores.append((similarity, all_data['documents'][i][:80], i))
        
        scores.sort(reverse=True, key=lambda x: x[0])
        print("Top 5 相似度:")
        for s, doc, idx in scores[:5]:
            print(f"  [{s:.4f}] {doc}...")

print("\n" + "=" * 60)
print("调试完成")
print("=" * 60)
