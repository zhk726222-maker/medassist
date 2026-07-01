"""
MedAssist MCP Server
运行方式: python -m app.api.mcp_server
作为独立进程运行,通过stdio与MCP客户端通信
"""
from fastmcp import FastMCP
from app.tools.medical_tools import (
    calculate_bmi,
    check_lab_result,
    calculate_drug_dose,
    lookup_icd_code,
)

mcp = FastMCP("MedAssist Tools")

@mcp.tool()
def bmi_calculator(weight_kg: float, height_cm: float) -> dict:
    """计算BMI体质指数并给出健康评估建议"""
    return calculate_bmi(weight_kg, height_cm)

@mcp.tool()
def lab_result_checker(test_name: str, value: float, unit: str) -> dict:
    """解读检验结果是否在正常范围内"""
    return check_lab_result(test_name, value, unit)

@mcp.tool()
def drug_dose_calculator(
    drug_name: str,
    weight_kg: float,
    dose_per_kg: float,
    frequency_per_day: int
) -> dict:
    """根据体重计算药物剂量"""
    return calculate_drug_dose(drug_name, weight_kg, dose_per_kg, frequency_per_day)

@mcp.tool()
def icd_code_lookup(disease_name: str) -> dict:
    """查询疾病的ICD-10编码"""
    return lookup_icd_code(disease_name)

if __name__ == "__main__":
    mcp.run()