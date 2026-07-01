"""
MedAssist 医疗智能助手 - Streamlit前端
运行方式: streamlit run app_ui.py
"""
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="MedAssist 医疗智能助手",
    page_icon="🏥",
    layout="wide",
)

# 侧边栏
with st.sidebar:
    st.title("🏥 MedAssist")
    st.caption("基于Multi-Agent架构的医疗智能助手")

    st.divider()
    st.subheader("📋 支持三类问题")

    st.markdown("**🔍 医学知识 (RAG)**")
    st.markdown("""
    - 哮喘发作的症状有哪些
    - 高血压怎么预防
    - 贫血吃什么好
    """)

    st.markdown("**📊 患者数据 (SQL)**")
    st.markdown("""
    - 张伟最近的处方是什么
    - 哪些患者有异常检验结果
    - 今天有哪些就诊预约
    """)

    st.markdown("**🧮 医疗计算 (Tool)**")
    st.markdown("""
    - 我身高170cm体重75kg,BMI正常吗
    - 血糖7.2mmol/L正常吗
    - 哮喘的ICD编码是多少
    """)

    st.divider()
    # 系统状态检查
    try:
        resp = requests.get(f"{API_BASE}/", timeout=3)
        if resp.status_code == 200:
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端服务异常")
    except Exception:
        st.error("❌ 无法连接后端\n请先运行 uvicorn main:app")

    st.divider()
    st.caption("⚠️ 本系统仅供医学知识科普\n不能替代专业医生诊断")

# 主界面
st.title("🏥 MedAssist 医疗智能助手")
st.caption("RAG知识问答 · NL2SQL数据查询 · 医疗计算工具 · QLoRA微调Planner路由")

# 对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("routed_to"):
            agent_icons = {
                "RAG Agent": "🔍",
                "NL2SQL Agent": "📊",
                "Tool Agent": "🧮",
            }
            icon = agent_icons.get(msg["routed_to"], "🤖")
            st.caption(f"{icon} {msg['routed_to']}")
        if msg.get("sql"):
            with st.expander("📝 查看执行的SQL"):
                st.code(msg["sql"], language="sql")
        if msg.get("tool_called"):
            with st.expander("🔧 查看工具调用详情"):
                st.json({
                    "工具": msg["tool_called"],
                    "参数": msg.get("tool_args", {}),
                })

# 输入框
if query := st.chat_input("请输入您的医疗咨询问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # 调用后端
    with st.chat_message("assistant"):
        with st.spinner("正在分析您的问题..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/chat",
                    json={"query": query},
                    timeout=120,
                )
                result = resp.json()
                answer = result.get("answer", "抱歉,未能获取回答")
                routed_to = result.get("routed_to", "")

                st.markdown(answer)

                agent_icons = {
                    "RAG Agent": "🔍",
                    "NL2SQL Agent": "📊",
                    "Tool Agent": "🧮",
                }
                icon = agent_icons.get(routed_to, "🤖")
                if routed_to:
                    st.caption(f"{icon} {routed_to}")

                if result.get("sql"):
                    with st.expander("📝 查看执行的SQL"):
                        st.code(result["sql"], language="sql")

                if result.get("tool_called"):
                    with st.expander("🔧 查看工具调用详情"):
                        st.json({
                            "工具": result["tool_called"],
                            "参数": result.get("tool_args", {}),
                        })

                msg_data = {
                    "role": "assistant",
                    "content": answer,
                    "routed_to": routed_to,
                    "sql": result.get("sql"),
                    "tool_called": result.get("tool_called"),
                    "tool_args": result.get("tool_args"),
                }
                st.session_state.messages.append(msg_data)

            except requests.exceptions.Timeout:
                st.error("请求超时,请稍后重试")
            except Exception as e:
                st.error(f"请求失败: {str(e)}")