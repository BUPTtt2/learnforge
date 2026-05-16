#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手动下载embedding模型 (safetensors格式)"""

import os
import ssl
import requests

ssl._create_default_https_context = ssl._create_unverified_context

# 模型文件列表 - 使用safetensors格式
files_to_download = [
    "model.safetensors",
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "modules.json",
    "config_sentence_transformers.json",
    "sentence_bert_config.json",
    "1_Pooling/config.json"
]

base_url = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/"
save_dir = "./models/all-MiniLM-L6-v2"

os.makedirs(save_dir, exist_ok=True)
os.makedirs(os.path.join(save_dir, "1_Pooling"), exist_ok=True)

# 删除旧的pytorch_model.bin
old_model = os.path.join(save_dir, "pytorch_model.bin")
if os.path.exists(old_model):
    os.remove(old_model)
    print(f"[REMOVE] Removed old pytorch_model.bin")

session = requests.Session()
session.verify = False  # 禁用SSL验证

for file_name in files_to_download:
    file_path = os.path.join(save_dir, file_name)
    if os.path.exists(file_path):
        print(f"[SKIP] {file_name} already exists")
        continue
    
    url = base_url + file_name
    print(f"[DOWNLOAD] {file_name}...")
    
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='')
        
        print(f"\n[OK] {file_name} downloaded")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to download {file_name}: {e}")

print("\n[DONE] Download completed")
