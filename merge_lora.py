import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

MODEL_PATH = "data/models/Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "data/checkpoints/planner-lora-final"
MERGED_PATH = "data/models/planner-merged"

print("正在加载基座模型(float16,CPU)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, torch_dtype=torch.float16,
    device_map="cpu", trust_remote_code=True,
)
model = PeftModel.from_pretrained(model, LORA_PATH)
print("正在合并LoRA权重...")
model = model.merge_and_unload()
print(f"正在保存到 {MERGED_PATH}...")
model.save_pretrained(MERGED_PATH)
AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True).save_pretrained(MERGED_PATH)
print("合并完成!")