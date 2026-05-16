@echo off
REM LLaMA-Factory SFT 训练脚本
REM 使用 QLoRA 在 Qwen3-4B 上微调

cd /d D:\LLaMA-Factory

llamafactory-cli train D:\Appt\大三下\学习\multi_Agent_智能日程\learnforge\llama_factory_config.yaml

pause
