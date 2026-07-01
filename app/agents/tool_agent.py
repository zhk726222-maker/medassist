import json
from app.core.config import client, DEFAULT_MODEL
from app.tools.medical_tools import (
    calculate_bmi,
    check_lab_result,
    calculate_drug_dose,
    lookup_icd_code,
)

TOOL_REGISTRY = {
    "calculate_bmi": calculate_bmi,
    "check_lab_result": check_lab_result,
    "calculate_drug_dose": calculate_drug_dose,
    "lookup_icd_code": lookup_icd_code,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculate_bmi",
            "description": "根据体重和身高计算BMI体质指数,并给出健康评估和建议",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "体重(公斤)"},
                    "height_cm": {"type": "number", "description": "身高(厘米)"},
                },
                "required": ["weight_kg", "height_cm"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_lab_result",
            "description": "解读检验结果,判断是否在正常范围内,支持血糖/血红蛋白/血压/胆固醇等常见指标",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "检验项目名称,如空腹血糖"},
                    "value": {"type": "number", "description": "检验值"},
                    "unit": {"type": "string", "description": "单位,如mmol/L"},
                },
                "required": ["test_name", "value", "unit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_drug_dose",
            "description": "根据体重计算药物剂量,适用于儿童或体重敏感药物的剂量计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "药品名称"},
                    "weight_kg": {"type": "number", "description": "患者体重(公斤)"},
                    "dose_per_kg": {"type": "number", "description": "每公斤体重的剂量(mg/kg)"},
                    "frequency_per_day": {"type": "integer", "description": "每日用药次数"},
                },
                "required": ["drug_name", "weight_kg", "dose_per_kg", "frequency_per_day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_icd_code",
            "description": "查询疾病的ICD-10国际疾病分类编码",
            "parameters": {
                "type": "object",
                "properties": {
                    "disease_name": {"type": "string", "description": "疾病名称,如哮喘/高血压"},
                },
                "required": ["disease_name"],
            },
        },
    },
]

def tool_agent_answer(query: str) -> dict:
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=TOOLS_SCHEMA,
    )
    message = response.choices[0].message

    if not message.tool_calls:
        return {"answer": message.content, "tool_called": None}

    tool_call = message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    tool_result = TOOL_REGISTRY[tool_name](**tool_args)

    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }],
    })
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(tool_result, ensure_ascii=False),
    })

    final_response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
    )
    return {
        "answer": final_response.choices[0].message.content,
        "tool_called": tool_name,
        "tool_args": tool_args,
        "tool_result": tool_result,
    }

if __name__ == "__main__":
    tests = [
        "我身高170cm体重75kg,BMI正常吗",
        "空腹血糖7.2mmol/L正常吗",
        "哮喘的ICD编码是多少",
        "20kg的儿童用阿莫西林每公斤25mg每日三次剂量是多少",
    ]
    for q in tests:
        print(f"\n{'='*50}")
        print(f"问题: {q}")
        result = tool_agent_answer(q)
        print(f"调用工具: {result['tool_called']}")
        print(f"回答: {result['answer']}")