# MedAssist 一键启动脚本
Write-Host "===== MedAssist 医疗智能助手 =====" -ForegroundColor Cyan

# 检查虚拟环境
if ($env:CONDA_DEFAULT_ENV -ne "medassist") {
    Write-Host "正在激活虚拟环境..." -ForegroundColor Yellow
    conda activate medassist
} else {
    Write-Host "[OK] 虚拟环境: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
}

# 检查.env
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] 未找到.env文件,请配置ZHIPU_API_KEY" -ForegroundColor Red
    exit 1
} else {
    Write-Host "[OK] API密钥配置存在" -ForegroundColor Green
}

# 检查知识库
if (-not (Test-Path "data\chroma_db")) {
    Write-Host "[WARN] 未检测到向量数据库,请先运行: python -m app.tools.vectorstore" -ForegroundColor Yellow
} else {
    Write-Host "[OK] 知识库已就绪" -ForegroundColor Green
}

# 检查数据库
if (-not (Test-Path "data\medical.db")) {
    Write-Host "[WARN] 未检测到患者数据库,请先运行: python -m app.core.database && python -m app.tools.seed_database" -ForegroundColor Yellow
} else {
    Write-Host "[OK] 患者数据库已就绪" -ForegroundColor Green
}

Write-Host "`n正在启动 MedAssist 服务..." -ForegroundColor Cyan
uvicorn main:app --reload