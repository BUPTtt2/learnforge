import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

base_model = "D:\\Models\\Qwen3-4B"
adapter_path = "D:\\Appt\\大三下\\学习\\multi_Agent_智能日程\\learnforge\\sft_output_final"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model)

print("Loading base model (4-bit)...")
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
base_model_instance = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=bnb_config, device_map="auto", trust_remote_code=True)

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(base_model_instance, adapter_path)
model.eval()

test_instruction = "请详细讲解 Agent 的规划能力，包括 ReAct、Plan-and-Solve 等多种方法的核心原理"

prompt = f"Instruction: {test_instruction}\nOutput:"

print("\n" + "="*50)
print("Test instruction:", test_instruction)
print("="*50)

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.7)
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\nGenerated output:")
print(result.replace(prompt, ""))
