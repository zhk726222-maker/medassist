from app.core.config import client, DEFAULT_MODEL
from app.tools.hybrid_search import hybrid_search
from app.tools.reranker import rerank

RAG_PROMPT_TEMPLATE = """你是一个医疗知识助手,基于权威医学资料回答用户的健康咨询问题。

重要声明:
1. 本助手仅提供医学知识科普,不能替代专业医生的诊断和治疗建议
2. 如症状严重或持续,请及时就医
3. 回答必须基于下方参考资料,不得凭空编造医学信息
4. 如参考资料不足以回答问题,请明确说明并建议就医咨询

参考资料:
{context}

用户问题:{query}

请基于参考资料给出专业、准确、易懂的回答,并在末尾标注信息来源:"""

def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, start=1):
        source = c["source"].replace(".txt", "")
        parts.append(f"[资料{i} 来源:{source}]\n{c['text']}")
    return "\n\n".join(parts)

def rag_answer(query: str, top_k: int = 3) -> dict:
    """完整RAG流程:混合检索 -> Rerank -> 生成回答"""
    candidates = hybrid_search(query, top_k=10, candidate_k=10)
    top_chunks = rerank(query, candidates, top_k=top_k)
    context = build_context(top_chunks)
    prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": [
            {"source": c["source"], "id": c["id"]}
            for c in top_chunks
        ],
    }

if __name__ == "__main__":
    result = rag_answer("哮喘发作的时候应该怎么处理")
    print("回答:", result["answer"])
    print("\n来源:", result["sources"])