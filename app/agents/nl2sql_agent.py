from app.core.config import client, DEFAULT_MODEL
from app.core.database import SessionLocal
from sqlalchemy import text

SCHEMA_DESCRIPTION = """
医疗数据库包含以下5张表:

1. patients(患者表)
   - id: 主键
   - name: 姓名
   - gender: 性别(男/女)
   - age: 年龄
   - phone: 电话
   - blood_type: 血型(A/B/AB/O)

2. diagnoses(诊断记录表)
   - id: 主键
   - patient_id: 外键,关联patients.id
   - disease: 疾病名称(如哮喘/高血压/糖尿病)
   - icd_code: ICD编码
   - severity: 严重程度(轻度/中度/重度)
   - doctor: 主治医生
   - diagnosed_at: 诊断时间
   - notes: 备注

3. prescriptions(处方记录表)
   - id: 主键
   - patient_id: 外键,关联patients.id
   - drug_name: 药品名称
   - dosage: 剂量(如500mg)
   - frequency: 用药频率(如每日两次)
   - duration_days: 用药天数
   - doctor: 开方医生
   - prescribed_at: 开方时间

4. lab_results(检验结果表)
   - id: 主键
   - patient_id: 外键,关联patients.id
   - test_name: 检验项目(如空腹血糖/血红蛋白)
   - value: 检验值(数字)
   - unit: 单位
   - reference_range: 参考范围(如3.9-6.1)
   - is_abnormal: 是否异常(0正常/1异常)
   - tested_at: 检验时间

5. appointments(就诊预约表)
   - id: 主键
   - patient_id: 外键,关联patients.id
   - doctor: 医生
   - department: 科室
   - scheduled_at: 预约时间
   - status: 状态(pending待就诊/completed已完成/cancelled已取消)
"""

SQL_PROMPT = """你是一个医疗数据库SQL生成助手,把用户的自然语言问题转换成SQLite查询语句。

数据库表结构:
{schema}

要求:
1. 只生成SELECT查询语句,禁止INSERT/UPDATE/DELETE/DROP等操作
2. 只返回SQL语句本身,不要任何解释,不要markdown代码块
3. 涉及多表时使用JOIN
4. 当前时间用 datetime('now') 表示
5. 中文字符串匹配用LIKE,如 WHERE disease LIKE '%哮喘%'

用户问题:{query}

SQL语句:"""

ANSWER_PROMPT = """你是一个医疗数据助手,请根据SQL查询结果用简洁自然的语言回答用户问题。

用户问题:{query}
查询结果:{results}

要求:如果查询结果为空,明确告知用户没有找到相关数据。回答要简洁专业。"""

def generate_sql(query: str) -> str:
    prompt = SQL_PROMPT.format(schema=SCHEMA_DESCRIPTION, query=query)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def is_safe_sql(sql: str) -> bool:
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return False
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP",
                 "ALTER", "TRUNCATE", "CREATE"]
    return not any(kw in sql_upper for kw in forbidden)

def execute_sql(sql: str) -> list[dict]:
    if not is_safe_sql(sql):
        raise ValueError(f"不安全的SQL已拦截: {sql}")
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]
    finally:
        db.close()

def nl2sql_answer(query: str) -> dict:
    sql = generate_sql(query)
    results = execute_sql(sql)
    prompt = ANSWER_PROMPT.format(query=query, results=results)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "answer": response.choices[0].message.content,
        "sql": sql,
        "raw_results": results,
    }

if __name__ == "__main__":
    tests = [
        "现在有哪些患者被诊断为哮喘",
        "张伟最近的处方是什么",
        "哪些患者有异常检验结果",
    ]
    for q in tests:
        print(f"\n{'='*50}")
        print(f"问题: {q}")
        result = nl2sql_answer(q)
        print(f"SQL: {result['sql']}")
        print(f"回答: {result['answer']}")