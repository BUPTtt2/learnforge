#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试SSL修复方案"""

import os
import ssl
import sys

# 设置环境变量
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL'] = '1'

# 配置SSL上下文
ssl._create_default_https_context = ssl._create_unverified_context

# 尝试修改httpx的默认SSL配置
try:
    import httpx
    httpx_client = httpx.Client(verify=False)
    print("[OK] Created httpx client with verify=False")
except Exception as e:
    print(f"[Error] httpx config failed: {e}")

# 尝试设置全局httpx配置
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
    print("[OK] Patched httpx Client classes")
except Exception as e:
    print(f"[Error] httpx patching failed: {e}")

# 现在尝试加载模型
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("[SUCCESS] Model loaded successfully!")
    print(f"Model name: {model.get_sentence_embedding_dimension()} dimensions")
except Exception as e:
    print(f"[Error] Failed to load model: {e}")
    print("[Info] Will use fallback embedding method")
