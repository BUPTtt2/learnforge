"""
SFT 微调脚本 - 使用 QLoRA 在本地微调 Qwen 模型
适用于 Ollama 兼容的 Qwen3-4B 模型
"""

import json
import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kv_storage
from datasets import Dataset
import bitsandbytes as bnb

# 配置
MODEL_NAME = "qwen2.5-4b"  # Ollama 模型名称
OUTPUT_DIR = "./sft_output"
DATA_PATH = "./sft_data/merged_sft_data.json"
MICRO_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
EPOCHS = 3
LEARNING_RATE = 2e-4
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

def load_data(data_path):
    """加载并格式化数据"""
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 转换为对话格式
    formatted_data = []
    for item in raw_data:
        formatted_item = {
            "instruction": item["instruction"],
            "input": item.get("input", ""),
            "output": item["output"]
        }
        formatted_data.append(formatted_item)

    return formatted_data

def format_sample(sample):
    """格式化单个样本为指令微调格式"""
    instruction = sample["instruction"]
    input_text = sample.get("input", "")
    output = sample["output"]

    if input_text:
        text = f"指令: {instruction}\n输入: {input_text}\n\n回答: {output}"
    else:
        text = f"指令: {instruction}\n\n回答: {output}"

    return {"text": text}

def tokenize(sample, tokenizer, max_length=512):
    """tokenize 样本"""
    text = sample["text"]
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors=None
    )
    encoding["labels"] = encoding["input_ids"].copy()
    return encoding

def print_trainable_parameters(model):
    """打印可训练参数信息"""
    trainable_params = 0
    all_params = 0
    for _, param in model.named_parameters():
        all_params += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(f"\n📊 可训练参数: {trainable_params:,} / {all_params:,} ({100 * trainable_params / all_params:.2f}%)")

def main():
    print("=" * 60)
    print("🚀 SFT 微调开始")
    print("=" * 60)

    # 1. 加载数据
    print("\n📂 加载数据...")
    data = load_data(DATA_PATH)
    print(f"✅ 数据加载完成: {len(data)} 条")

    # 2. 格式化数据
    print("\n🔄 格式化数据...")
    formatted_data = [format_sample(sample) for sample in data]
    dataset = Dataset.from_list(formatted_data)
    print(f"✅ 数据格式化完成")

    # 3. 加载 tokenizer
    print(f"\n🔄 加载 Tokenizer: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    print(f"✅ Tokenizer 加载完成")
    print(f"   Vocab size: {tokenizer.vocab_size:,}")

    # 4. Tokenize 数据
    print("\n🔄 Tokenizing 数据...")
    dataset = dataset.map(
        lambda sample: tokenize(sample, tokenizer),
        batched=False,
        remove_columns=["text"]
    )
    print(f"✅ Tokenization 完成")

    # 5. 加载模型 (QLoRA 配置)
    print(f"\n🔄 加载模型: {MODEL_NAME}...")
    print(f"   使用 4-bit 量化 (QLoRA)...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
        quantization_config=bnb.QLoftConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    )

    # 准备 KV 存储
    model = prepare_model_for_kv_storage(model)

    # 6. 配置 LoRA
    print("\n🔄 配置 LoRA...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    print_trainable_parameters(model)

    # 7. 训练参数
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=MICRO_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        fp16=False,
        bf16=True,
        logging_steps=10,
        save_steps=50,
        warmup_steps=10,
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        report_to="none",
        save_total_limit=2,
    )

    # 8. 数据整理器
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # 因果语言模型不使用 MLM
    )

    # 9. 创建 Trainer
    print("\n🔄 创建 Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    # 10. 开始训练
    print("\n" + "=" * 60)
    print("🔥 开始训练...")
    print("=" * 60)
    trainer.train()

    # 11. 保存模型
    print(f"\n💾 保存模型到: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("✅ SFT 微调完成!")
    print("=" * 60)
    print(f"\n📁 模型保存在: {OUTPUT_DIR}")
    print(f"\n🚀 可以使用以下命令加载模型:")
    print(f"   ollama create sft-qwen -f {OUTPUT_DIR}/Modelfile")

if __name__ == "__main__":
    main()
