import json
import os

TRAINING_SAMPLES = [
    # RAG类 - 医学知识/症状/原理/用药科普
    {"query": "哮喘发作的症状有哪些", "label": "RAG"},
    {"query": "高血压的危险因素是什么", "label": "RAG"},
    {"query": "糖尿病怎么预防", "label": "RAG"},
    {"query": "贫血会有什么表现", "label": "RAG"},
    {"query": "骨质疏松怎么治疗", "label": "RAG"},
    {"query": "过敏反应的原理是什么", "label": "RAG"},
    {"query": "中风的早期症状有哪些", "label": "RAG"},
    {"query": "消化性溃疡怎么饮食调理", "label": "RAG"},
    {"query": "头痛的常见原因是什么", "label": "RAG"},
    {"query": "呼吸短促应该怎么处理", "label": "RAG"},
    {"query": "视力突然下降是什么原因", "label": "RAG"},
    {"query": "心悸是什么感觉怎么办", "label": "RAG"},
    {"query": "鼻塞流涕怎么缓解", "label": "RAG"},
    {"query": "尿频尿急是什么病", "label": "RAG"},
    {"query": "儿童腹泻怎么处理", "label": "RAG"},
    {"query": "血尿是什么原因引起的", "label": "RAG"},
    {"query": "记忆力下降和什么疾病有关", "label": "RAG"},
    {"query": "身体无力乏力是什么原因", "label": "RAG"},
    {"query": "模糊视力的常见原因", "label": "RAG"},
    {"query": "肠胃出血的症状是什么", "label": "RAG"},
    {"query": "哮喘患者能运动吗", "label": "RAG"},
    {"query": "高血压可以根治吗", "label": "RAG"},
    {"query": "糖尿病需要终身服药吗", "label": "RAG"},
    {"query": "贫血吃什么食物好", "label": "RAG"},
    {"query": "骨质疏松要补充什么营养", "label": "RAG"},

    # SQL类 - 查询患者数据/处方/检验/预约
    {"query": "张伟最近的处方是什么", "label": "SQL"},
    {"query": "哪些患者被诊断为糖尿病", "label": "SQL"},
    {"query": "李娜有哪些异常检验结果", "label": "SQL"},
    {"query": "今天有哪些就诊预约", "label": "SQL"},
    {"query": "王芳的诊断记录有哪些", "label": "SQL"},
    {"query": "刘洋用了什么药", "label": "SQL"},
    {"query": "哪些患者血糖检验异常", "label": "SQL"},
    {"query": "陈静最近一次就诊是什么时候", "label": "SQL"},
    {"query": "被诊断为重度哮喘的患者有谁", "label": "SQL"},
    {"query": "赵磊的血型是什么", "label": "SQL"},
    {"query": "本月有哪些处方记录", "label": "SQL"},
    {"query": "王医生开了哪些处方", "label": "SQL"},
    {"query": "有多少患者预约了内科", "label": "SQL"},
    {"query": "孙丽的检验结果正常吗", "label": "SQL"},
    {"query": "周强最近的诊断是什么", "label": "SQL"},
    {"query": "所有女性患者有哪些", "label": "SQL"},
    {"query": "60岁以上的患者有几位", "label": "SQL"},
    {"query": "吴梅用的什么药物治疗", "label": "SQL"},
    {"query": "郑浩的就诊记录", "label": "SQL"},
    {"query": "哪些预约已经取消了", "label": "SQL"},
    {"query": "最近开具布地奈德的患者是谁", "label": "SQL"},
    {"query": "有多少患者诊断为高血压", "label": "SQL"},
    {"query": "检验结果异常的患者名单", "label": "SQL"},
    {"query": "张医生负责哪些患者", "label": "SQL"},
    {"query": "待就诊的预约有哪些", "label": "SQL"},

    # TOOL类 - 计算/解读/查编码
    {"query": "我身高168cm体重65kg,BMI多少", "label": "TOOL"},
    {"query": "血糖8.5mmol/L正常吗", "label": "TOOL"},
    {"query": "糖尿病的ICD编码是多少", "label": "TOOL"},
    {"query": "25kg儿童用头孢每公斤30mg每日两次剂量多少", "label": "TOOL"},
    {"query": "血红蛋白85g/L是否偏低", "label": "TOOL"},
    {"query": "高血压ICD-10编码查询", "label": "TOOL"},
    {"query": "体重50kg身高155cm算胖吗", "label": "TOOL"},
    {"query": "总胆固醇6.5mmol/L超标了吗", "label": "TOOL"},
    {"query": "心肌梗死的疾病编码", "label": "TOOL"},
    {"query": "15kg小孩用阿莫西林每公斤25mg每日三次", "label": "TOOL"},
    {"query": "血压160mmHg正常范围是多少", "label": "TOOL"},
    {"query": "肺炎ICD编码", "label": "TOOL"},
    {"query": "我BMI是多少身高175体重90", "label": "TOOL"},
    {"query": "血肌酐150μmol/L超出正常值吗", "label": "TOOL"},
    {"query": "脑卒中的ICD-10是什么", "label": "TOOL"},
    {"query": "30kg儿童布洛芬每公斤10mg每日三次剂量", "label": "TOOL"},
    {"query": "白细胞11×10⁹/L偏高吗", "label": "TOOL"},
    {"query": "骨质疏松ICD编码查询", "label": "TOOL"},
    {"query": "身高160体重80kg体重正常吗", "label": "TOOL"},
    {"query": "空腹血糖5.8正常吗", "label": "TOOL"},
    {"query": "抑郁症的ICD编码", "label": "TOOL"},
    {"query": "10kg婴儿用药每公斤5mg每日两次", "label": "TOOL"},
    {"query": "血小板50×10⁹/L危险吗", "label": "TOOL"},
    {"query": "过敏性鼻炎疾病编码", "label": "TOOL"},
    {"query": "我体重70kg身高180cm是否超重", "label": "TOOL"},
]

def prepare_data():
    os.makedirs("data/training", exist_ok=True)
    output_path = "data/training/routing_train.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for sample in TRAINING_SAMPLES:
            conversation = {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个医疗助手的任务路由器。判断用户问题应该交给哪个子系统:RAG(医学知识问答)、SQL(患者数据查询)、TOOL(医疗计算工具)。只回答一个词。"
                    },
                    {"role": "user", "content": sample["query"]},
                    {"role": "assistant", "content": sample["label"]},
                ]
            }
            f.write(json.dumps(conversation, ensure_ascii=False) + "\n")

    from collections import Counter
    counts = Counter(s["label"] for s in TRAINING_SAMPLES)
    print(f"训练数据已生成: {output_path}")
    print(f"总样本数: {len(TRAINING_SAMPLES)}")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}条")

if __name__ == "__main__":
    prepare_data()