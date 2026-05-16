import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

def merge_lora_weights(base_model_path: str, lora_path: str, output_path: str):
    print(f"Loading base model: {base_model_path}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    print(f"Loading LoRA adapter: {lora_path}")
    model = PeftModel.from_pretrained(base_model, lora_path)
    
    print("Merging LoRA weights...")
    model = model.merge_and_unload()
    
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Saving merged model to: {output_path}")
    model.save_pretrained(output_path, safe_serialization=True)
    tokenizer.save_pretrained(output_path)
    
    print("✅ LoRA weights merged successfully!")

if __name__ == "__main__":
    base_model = "D:\\Models\\Qwen3-4B"
    lora_path = "sft_output_final"
    output_path = "merged_model"
    
    merge_lora_weights(base_model, lora_path, output_path)