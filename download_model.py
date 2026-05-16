import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import snapshot_download

model_name = "Qwen/Qwen3-4B"
save_path = "D:\\Models\\Qwen3-4B"

print(f"Downloading {model_name} to {save_path}...")
snapshot_download(
    repo_id=model_name,
    local_dir=save_path,
    local_dir_use_symlinks=False,
    resume_download=True
)
print("Download completed!")
