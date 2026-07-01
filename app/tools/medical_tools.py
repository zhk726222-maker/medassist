"""
医疗计算工具集
所有工具返回结构化字典,供Tool Agent调用
"""

def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """计算BMI并给出健康评估"""
    if weight_kg <= 0 or height_cm <= 0:
        return {"error": "体重和身高必须大于0"}
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        category = "偏瘦"
        advice = "建议适当增加营养摄入，加强体育锻炼"
    elif bmi < 24.0:
        category = "正常"
        advice = "保持良好的饮食和运动习惯"
    elif bmi < 28.0:
        category = "超重"
        advice = "建议控制饮食，增加有氧运动"
    else:
        category = "肥胖"
        advice = "建议在医生指导下进行体重管理"
    return {
        "tool": "calculate_bmi",
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "category": category,
        "advice": advice,
        "note": "BMI标准基于中国成人参考值(WHO亚洲标准)"
    }

def check_lab_result(test_name: str, value: float, unit: str) -> dict:
    """检验结果解读,判断是否在正常范围内"""
    reference_ranges = {
        "空腹血糖": (3.9, 6.1, "mmol/L", "偏低可能低血糖,偏高需警惕糖尿病"),
        "血红蛋白": (120, 160, "g/L", "偏低可能贫血,偏高需排除血液疾病"),
        "血压收缩压": (90, 140, "mmHg", "偏低可能低血压,偏高需警惕高血压"),
        "总胆固醇": (2.8, 5.2, "mmol/L", "偏高需注意心血管风险"),
        "血肌酐": (44, 133, "μmol/L", "偏高需警惕肾功能异常"),
        "白细胞计数": (4.0, 10.0, "×10⁹/L", "偏高可能感染或炎症,偏低需查原因"),
        "血小板": (100, 300, "×10⁹/L", "偏低需警惕出血风险"),
    }
    if test_name not in reference_ranges:
        return {
            "tool": "check_lab_result",
            "test_name": test_name,
            "note": f"暂不支持{test_name}的自动解读,请咨询医生"
        }
    low, high, std_unit, clinical_note = reference_ranges[test_name]
    if value < low:
        status = "偏低"
        is_abnormal = True
    elif value > high:
        status = "偏高"
        is_abnormal = True
    else:
        status = "正常"
        is_abnormal = False
    return {
        "tool": "check_lab_result",
        "test_name": test_name,
        "value": value,
        "unit": unit,
        "reference_range": f"{low}-{high} {std_unit}",
        "status": status,
        "is_abnormal": is_abnormal,
        "clinical_note": clinical_note if is_abnormal else "结果在正常范围内",
        "disclaimer": "本结果仅供参考,具体诊断请咨询医生"
    }

def calculate_drug_dose(
    drug_name: str,
    weight_kg: float,
    dose_per_kg: float,
    frequency_per_day: int
) -> dict:
    """根据体重计算儿童或体重敏感药物的每日剂量"""
    if weight_kg <= 0 or dose_per_kg <= 0 or frequency_per_day <= 0:
        return {"error": "所有参数必须大于0"}
    total_daily_dose = round(weight_kg * dose_per_kg, 1)
    single_dose = round(total_daily_dose / frequency_per_day, 1)
    return {
        "tool": "calculate_drug_dose",
        "drug_name": drug_name,
        "weight_kg": weight_kg,
        "dose_per_kg": dose_per_kg,
        "total_daily_dose_mg": total_daily_dose,
        "single_dose_mg": single_dose,
        "frequency_per_day": frequency_per_day,
        "disclaimer": "本计算仅供参考,实际用药请遵医嘱"
    }

def lookup_icd_code(disease_name: str) -> dict:
    """查询常见疾病的ICD-10编码"""
    ICD_DATABASE = {
        "哮喘": ("J45", "支气管哮喘"),
        "高血压": ("I10", "原发性高血压"),
        "糖尿病": ("E11", "2型糖尿病"),
        "心肌梗死": ("I21", "急性心肌梗死"),
        "脑卒中": ("I63", "脑梗死"),
        "肺炎": ("J18", "肺炎"),
        "消化性溃疡": ("K27", "消化性溃疡"),
        "贫血": ("D64", "其他贫血"),
        "骨质疏松": ("M81", "骨质疏松症"),
        "过敏性鼻炎": ("J30", "血管舒缩性及变应性鼻炎"),
        "抑郁症": ("F32", "抑郁发作"),
        "焦虑症": ("F41", "其他焦虑障碍"),
    }
    for key, (code, full_name) in ICD_DATABASE.items():
        if key in disease_name or disease_name in key:
            return {
                "tool": "lookup_icd_code",
                "query": disease_name,
                "icd_code": code,
                "full_name": full_name,
                "standard": "ICD-10"
            }
    return {
        "tool": "lookup_icd_code",
        "query": disease_name,
        "note": f"未找到'{disease_name}'的ICD编码,请查阅专业ICD手册或咨询医生"
    }