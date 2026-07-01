import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from app.agents.rag_agent import rag_answer
from app.agents.nl2sql_agent import nl2sql_answer
from app.agents.tool_agent import tool_agent_answer

BASE_MODEL_PATH = "data/models/Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "data/checkpoints/planner-lora-final"
SYSTEM_PROMPT = "你是一个医疗助手的任务路由器。判断用户问题应该交给哪个子系统:RAG(医学知识问答)、SQL(患者数据查询)、TOOL(医疗计算工具)。只回答一个词。"

_tokenizer = None
_model = None

def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return
    print("正在加载Planner模型(基座+LoRA适配器)...")
    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)

    # 用4bit量化加载基座模型节省显存
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    # 叠加LoRA适配器，不合并，保持精度
    _model = PeftModel.from_pretrained(base_model, LORA_PATH)
    _model.eval()
    print("Planner模型加载完成")

def route(query: str) -> str:
    _load_model()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
    text = _tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = _tokenizer(text, return_tensors="pt").to(_model.device)
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=5,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            top_k=0,
            pad_token_id=_tokenizer.eos_token_id,
        )
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    decision = _tokenizer.decode(new_tokens, skip_special_tokens=True).strip().upper()
    if "TOOL" in decision:
        return "TOOL"
    if "SQL" in decision:
        return "SQL"
    return "RAG"

def planner_answer(query: str) -> dict:
    decision = route(query)
    if decision == "TOOL":
        result = tool_agent_answer(query)
        result["routed_to"] = "Tool Agent"
    elif decision == "SQL":
        result = nl2sql_answer(query)
        result["routed_to"] = "NL2SQL Agent"
    else:
        result = rag_answer(query)
        result["routed_to"] = "RAG Agent"
    return result

if __name__ == "__main__":
    tests = [
        "哮喘发作的症状有哪些",
        "张伟最近的处方是什么",
        "我身高165cm体重60kg,BMI正常吗",
        "高血压怎么预防",
        "李娜有哪些异常检验结果",
        "血糖7.5mmol/L正常吗",
    ]
    for q in tests:
        print(f"\n{'='*50}")
        print(f"问题: {q}")
        result = planner_answer(q)
        print(f"路由到: {result['routed_to']}")
        print(f"回答: {result['answer'][:80]}...")