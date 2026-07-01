# MedAssist 医疗智能助手

基于 Multi-Agent 架构的医疗知识问答系统，面向患者数据查询、医学知识科普和医疗计算三类场景，支持自动路由分发。

> ⚠️ 本系统仅供医学知识科普，不能替代专业医生的诊断和治疗建议。

## 系统架构

用户提问统一进入 **Planner**（QLoRA微调路由模型），自动判断意图后分发给三个子Agent：

| 子Agent | 适用场景 | 核心技术 |
|---------|---------|---------|
| RAG Agent | 医学知识问答（症状/原理/治疗） | 混合检索 + BGE Rerank + GLM-5.2生成 |
| NL2SQL Agent | 患者数据查询（处方/诊断/检验） | Schema-aware SQL生成 + 安全校验 |
| Tool Agent | 医疗计算（BMI/检验解读/ICD编码） | Function Calling + 本地工具函数 |

## 核心能力

- **混合检索**：向量检索（语义）+ BM25（关键词）+ RRF融合，中文医疗文档检索
- **Rerank精排**：本地部署 BGE-reranker-v2-m3，对候选结果做二次精确排序
- **防幻觉生成**：基于检索结果的受限生成，资料不足时明确告知而非编造
- **安全SQL校验**：白名单+黑名单双重拦截，只允许SELECT查询
- **MCP工具服务**：4个医疗计算工具按FastMCP协议标准封装
- **本地Planner**：QLoRA微调Qwen2.5-1.5B，路由延迟~50ms，替代API调用

## 技术栈

| 模块 | 技术选型 |
|------|---------|
| 大模型 | 智谱 GLM-5.2（生成）、embedding-3（向量化） |
| 向量检索 | ChromaDB（余弦相似度） |
| 关键词检索 | BM25Okapi（rank-bm25），中文单字分词 |
| 检索融合 | RRF（Reciprocal Rank Fusion，自实现） |
| Rerank | BAAI/bge-reranker-v2-m3（本地CPU推理） |
| 数据库 | SQLite + SQLAlchemy ORM（5张医疗数据表） |
| 工具调用 | Function Calling（GLM-5.2原生支持） |
| MCP协议 | FastMCP（4个医疗计算工具标准化封装） |
| 模型微调 | QLoRA（peft + bitsandbytes），基座Qwen2.5-1.5B |
| 后端服务 | FastAPI + uvicorn |
| 前端 | Streamlit |

## 知识库

- 来源：默沙东诊疗手册中文版（msdmanuals.cn）
- 规模：20篇医学文档，368个文本块（chunk）
- 覆盖：哮喘、中风、骨质疏松、过敏反应、贫血、头痛、心悸、呼吸短促等常见病症

## 数据库设计

5张表覆盖完整医疗场景：

| 表名 | 说明 | 关联 |
|------|------|------|
| patients | 患者基本信息（姓名/年龄/血型） | 主表 |
| diagnoses | 诊断记录（疾病/严重程度/医生） | → patients |
| prescriptions | 处方记录（药品/剂量/用药频率） | → patients |
| lab_results | 检验结果（项目/数值/是否异常） | → patients |
| appointments | 就诊预约（科室/医生/预约状态） | → patients |

## 快速开始

```powershell
# 1. 创建虚拟环境
conda create -n medassist python=3.11 -y
conda activate medassist

# 2. 安装依赖
pip install -r requirements.txt
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# 3. 配置API密钥
# 新建 .env 文件,写入: ZHIPU_API_KEY=你的密钥

# 4. 构建知识库
python -m app.tools.fetch_docs
python -m app.tools.vectorstore

# 5. 初始化数据库
python -m app.core.database
python -m app.tools.seed_database

# 6. 启动服务
uvicorn main:app --reload

# 7. 启动前端(新终端)
streamlit run app_ui.py
```

## 接口示例

```json
POST /chat
{"query": "哮喘发作的症状有哪些"}        → RAG Agent
{"query": "张伟最近的处方是什么"}         → NL2SQL Agent  
{"query": "我身高170体重75，BMI正常吗"}   → Tool Agent
```

## MCP工具服务

GET  /mcp/tools/list   查看可用工具列表
POST /mcp/tools/call   调用指定工具
支持工具：`bmi_calculator` · `lab_result_checker` · `drug_dose_calculator` · `icd_code_lookup`

## 效果数据

### Planner路由准确率

| 方案 | 准确率 | 路由延迟 |
|------|--------|---------|
| 基座模型(未微调) | 待测 | ~50ms |
| **QLoRA微调后** | **6/6 (100%)** | **~50ms** |
| API路由(GLM-5.2) | 6/6 (100%) | 800-2000ms |

训练参数：81条样本，50 epochs，loss从5.5收敛至0.21

## 已知局限

- 知识库规模偏小（368个chunk），部分疾病覆盖不完整
- Planner微调样本量75条，边界问题偶发误判
- Tool Agent工具为模拟计算，未接入真实医疗数据库
- 不支持多轮对话记忆（每次独立处理）

## 踩过的坑

- `fastmcp`的`mount`方法在1.0版本已移除，改为stdio独立运行模式
- ChromaDB遥测需在导入前用monkeypatch屏蔽（`posthog.capture = lambda...`）
- BGE-reranker需设置`return_token_type_ids=False`避免CUDA越界访问
- autoawq会强制降级torch版本，本项目不使用AWQ量化
- BM25中文分词需用正则提取单字（`[\u4e00-\u9fff]`）而非英文词法分词
- LoRA合并(`merge_and_unload`)会导致路由精度下降，改用LoRA适配器叠加4bit基座模型推理，避免精度损失
- Qwen2.5的`generation_config.json`预设了`temperature/top_p/top_k`采样参数，贪婪解码时需显式覆盖这些参数