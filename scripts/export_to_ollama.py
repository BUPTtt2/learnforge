import os
import subprocess
import json

def create_modelfile(model_name: str, merged_model_path: str, output_dir: str = "ollama_model"):
    os.makedirs(output_dir, exist_ok=True)
    
    modelfile_content = f"""FROM {merged_model_path}

PARAMETER temperature 0.7
PARAMETER max_ctx_size 4096
PARAMETER num_ctx 4096
PARAMETER num_threads 4

SYSTEM """你是一个专业的AI助手，擅长解答关于AI Agent、Transformer架构、MLOps等领域的技术问题。请用中文回答，提供详细、准确且专业的解答。"""

TEMPLATE """
{{- if .System }}
<|im_start|>system
{{ .System }}
<|im_end|>
{{- end }}
<|im_start|>user
{{ .Prompt }}
<|im_end|>
<|im_start|>assistant
"""
"""
    
    modelfile_path = os.path.join(output_dir, "Modelfile")
    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    print(f"✅ Modelfile created at: {modelfile_path}")
    return modelfile_path

def export_to_ollama(model_name: str, modelfile_path: str):
    print(f"Exporting model '{model_name}' to Ollama format...")
    
    command = f"ollama create {model_name} -f {modelfile_path}"
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Ollama model created successfully!")
        print(f"Output: {result.stdout}")
        
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Ollama model: {e.stderr}")
        return False

def verify_ollama_model(model_name: str):
    print(f"Verifying Ollama model '{model_name}'...")
    
    command = f"ollama list"
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"✅ Model '{model_name}' is available in Ollama")
            return True
        else:
            print(f"❌ Model '{model_name}' not found in Ollama")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to list Ollama models: {e.stderr}")
        return False

if __name__ == "__main__":
    model_name = "qwen3-4b-sft"
    merged_model_path = "merged_model"
    output_dir = "ollama_model"
    
    modelfile_path = create_modelfile(model_name, merged_model_path, output_dir)
    
    if export_to_ollama(model_name, modelfile_path):
        verify_ollama_model(model_name)
        print(f"\n🎉 模型已成功导出为 Ollama 格式！")
        print(f"使用方式: ollama run {model_name}")
    else:
        print("\n❌ 导出失败，请检查错误信息")