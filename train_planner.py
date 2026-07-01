"""
MedAssist Planner路由模型 QLoRA微调
基座模型: Qwen2.5-1.5B-Instruct
任务: 三分类路由(RAG/SQL/TOOL)
"""
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_PATH = "data/models/Qwen/Qwen2.5-1.5B-Instruct"
TRAIN_DATA_PATH = "data/training/routing_train.jsonl"
OUTPUT_DIR = "data/checkpoints/planner-lora"
LORA_SAVE_PATH = "data/checkpoints/planner-lora-final"

print("正在加载tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

print("正在加载基座模型(4bit量化)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("正在加载训练数据...")
dataset = load_dataset("json", data_files=TRAIN_DATA_PATH, split="train")

def format_conversation(example):
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}

dataset = dataset.map(format_conversation)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=50,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_steps=10,
    learning_rate=2e-4,
    bf16=True,
    fp16=False,
    logging_steps=5,
    save_strategy="epoch",
    save_total_limit=3,
    optim="paged_adamw_8bit",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=256,
)

print("\n===== 开始训练 =====")
print(f"显存使用(训练前): {torch.cuda.memory_allocated()/1024**2:.1f}MB")
trainer.train()
print("===== 训练完成 =====")

model.save_pretrained(LORA_SAVE_PATH)
tokenizer.save_pretrained(LORA_SAVE_PATH)
print(f"LoRA适配器已保存到: {LORA_SAVE_PATH}")