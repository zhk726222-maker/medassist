import random
import datetime
from app.core.database import (
    SessionLocal, Patient, Diagnosis, Prescription,
    LabResult, Appointment, init_db
)

random.seed(42)

PATIENTS = [
    ("张伟", "男", 45), ("李娜", "女", 32), ("王芳", "女", 67),
    ("刘洋", "男", 55), ("陈静", "女", 28), ("赵磊", "男", 72),
    ("孙丽", "女", 41), ("周强", "男", 58), ("吴梅", "女", 35),
    ("郑浩", "男", 63),
]
BLOOD_TYPES = ["A", "B", "AB", "O"]
DISEASES = [
    ("哮喘", "J45", ["轻度", "中度", "重度"]),
    ("高血压", "I10", ["轻度", "中度", "重度"]),
    ("糖尿病", "E11", ["轻度", "中度"]),
    ("消化性溃疡", "K27", ["轻度", "中度"]),
    ("贫血", "D64", ["轻度", "中度"]),
    ("过敏性鼻炎", "J30", ["轻度", "中度"]),
    ("骨质疏松", "M81", ["轻度", "中度", "重度"]),
]
DOCTORS = ["王医生", "李医生", "张医生", "刘医生", "陈医生"]
DEPARTMENTS = ["内科", "外科", "儿科", "妇科", "骨科", "神经科"]
DRUGS = [
    ("布地奈德", "200μg", "每日两次", 30),
    ("二甲双胍", "500mg", "每日三次", 60),
    ("氨氯地平", "5mg", "每日一次", 30),
    ("奥美拉唑", "20mg", "每日两次", 14),
    ("碳酸钙D3", "600mg", "每日一次", 90),
    ("氯雷他定", "10mg", "每日一次", 14),
    ("阿司匹林", "100mg", "每日一次", 30),
]
LAB_TESTS = [
    ("空腹血糖", 3.9, 11.1, "mmol/L", "3.9-6.1"),
    ("血红蛋白", 60, 180, "g/L", "120-160"),
    ("血压收缩压", 90, 180, "mmHg", "90-140"),
    ("总胆固醇", 2.0, 7.0, "mmol/L", "2.8-5.2"),
    ("血肌酐", 40, 200, "μmol/L", "44-133"),
]

def seed():
    init_db()
    db = SessionLocal()

    # 清空旧数据
    for Model in [Appointment, LabResult, Prescription, Diagnosis, Patient]:
        db.query(Model).delete()
    db.commit()

    now = datetime.datetime.utcnow()

    # 创建患者
    patients = []
    for name, gender, age in PATIENTS:
        p = Patient(
            name=name, gender=gender, age=age,
            phone=f"138{random.randint(10000000,99999999)}",
            blood_type=random.choice(BLOOD_TYPES),
        )
        db.add(p)
        patients.append(p)
    db.commit()

    # 诊断记录
    for p in patients:
        for _ in range(random.randint(1, 3)):
            disease, icd, severities = random.choice(DISEASES)
            db.add(Diagnosis(
                patient_id=p.id,
                disease=disease,
                icd_code=icd,
                severity=random.choice(severities),
                doctor=random.choice(DOCTORS),
                diagnosed_at=now - datetime.timedelta(days=random.randint(1, 180)),
                notes=f"{p.name}患者{disease}，需定期复查",
            ))

    # 处方记录
    for p in patients:
        for _ in range(random.randint(1, 4)):
            drug, dosage, freq, dur = random.choice(DRUGS)
            db.add(Prescription(
                patient_id=p.id,
                drug_name=drug,
                dosage=dosage,
                frequency=freq,
                duration_days=dur,
                doctor=random.choice(DOCTORS),
                prescribed_at=now - datetime.timedelta(days=random.randint(1, 90)),
            ))

    # 检验结果
    for p in patients:
        for _ in range(random.randint(2, 5)):
            name, min_v, max_v, unit, ref = random.choice(LAB_TESTS)
            value = round(random.uniform(min_v, max_v), 1)
            ref_parts = ref.split("-")
            is_abnormal = 1 if (value < float(ref_parts[0]) or
                                value > float(ref_parts[1])) else 0
            db.add(LabResult(
                patient_id=p.id,
                test_name=name,
                value=value,
                unit=unit,
                reference_range=ref,
                is_abnormal=is_abnormal,
                tested_at=now - datetime.timedelta(days=random.randint(1, 60)),
            ))

    # 就诊预约
    for p in patients:
        for _ in range(random.randint(1, 3)):
            days_offset = random.randint(-30, 30)
            status = "completed" if days_offset < 0 else (
                "cancelled" if days_offset == 0 else "pending"
            )
            db.add(Appointment(
                patient_id=p.id,
                doctor=random.choice(DOCTORS),
                department=random.choice(DEPARTMENTS),
                scheduled_at=now + datetime.timedelta(days=days_offset),
                status=status,
            ))

    db.commit()
    print(f"患者: {db.query(Patient).count()}人")
    print(f"诊断记录: {db.query(Diagnosis).count()}条")
    print(f"处方记录: {db.query(Prescription).count()}条")
    print(f"检验结果: {db.query(LabResult).count()}条")
    print(f"预约记录: {db.query(Appointment).count()}条")
    db.close()

if __name__ == "__main__":
    seed()