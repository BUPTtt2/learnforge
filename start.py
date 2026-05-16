#!/usr/bin/env python3
import sys
import os
import subprocess
import time

# 确保使用最新代码
sys.dont_write_bytecode = True

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 清理缓存
cache_dirs = []
for root, dirs, files in os.walk(project_root):
    if '__pycache__' in dirs:
        cache_dirs.append(os.path.join(root, '__pycache__'))
        
for cache_dir in cache_dirs:
    try:
        import shutil
        shutil.rmtree(cache_dir)
        print(f"[Cleanup] Removed cache: {cache_dir}")
    except:
        pass

# 导入并清理内存缓存
from utils.cache import cache_manager
cache_manager.clear()
print("[Cleanup] Memory cache cleared")

# 启动API
from ui.api import app

if __name__ == '__main__':
    print("[Startup] Starting LearnForge API Server...")
    print(f"[Startup] Using Python: {sys.executable}")
    print(f"[Startup] Project root: {project_root}")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
