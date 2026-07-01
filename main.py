from fastapi import FastAPI
from pydantic import BaseModel
from app.agents.planner import planner_answer

app = FastAPI(title="MedAssist - 医疗智能助手")

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "MedAssist 医疗智能助手已启动",
        "agents": ["RAG Agent", "NL2SQL Agent", "Tool Agent"],
    }

@app.post("/chat")
def chat(request: ChatRequest):
    result = planner_answer(request.query)
    return result