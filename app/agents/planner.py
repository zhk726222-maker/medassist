from app.core.config import client, DEFAULT_MODEL
from app.agents.rag_agent import rag_answer
from app.agents.nl2sql_agent import nl2sql_answer
from app.agents.tool_agent import tool_agent_answer

ROUTING_PROMPT = """你是一个医疗助手的任务路由器,判断用户问题应该交给哪个子系统处理。

三个子系统:
1. RAG - 回答医学知识类问题:疾病介绍、症状原理、治疗方法、用药知识、健康科普
   例如:"哮喘怎么治疗""高血压有什么症状""阿司匹林的副作用"
2. SQL - 查询患者数据:处方记录、诊断历史、检验结果、就诊预约
   例如:"张伟的处方是什么""哪些患者有异常检验结果""今天有哪些预约"
3. TOOL - 执行医疗计算:BMI计算、检验值解读、药物剂量计算、ICD编码查询
   例如:"我身高170体重75BMI多少""血糖7.2正常吗""哮喘的ICD编码"

用户问题:{query}

只回答一个词:RAG 或 SQL 或 TOOL,不要任何解释。"""

def route(query: str) -> str:
    prompt = ROUTING_PROMPT.format(query=query)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    decision = response.choices[0].message.content.strip().upper()
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
        "王芳最近的诊断记录是什么",
        "我身高165cm体重60kg,BMI正常吗",
        "高血压怎么用药治疗",
        "李娜有哪些异常检验结果",
        "血红蛋白90g/L正常吗",
    ]
    for q in tests:
        print(f"\n{'='*50}")
        print(f"问题: {q}")
        result = planner_answer(q)
        print(f"路由到: {result['routed_to']}")
        print(f"回答: {result['answer'][:100]}...")