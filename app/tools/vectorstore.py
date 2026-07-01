import os
import posthog
posthog.capture = lambda *args, **kwargs: None

import chromadb
from chromadb.config import Settings
from app.core.config import client, EMBEDDING_MODEL
from app.tools.chunker import chunk_all_docs

chroma_client = chromadb.PersistentClient(
    path="data/chroma_db",
    settings=Settings(anonymized_telemetry=False),
)

collection = chroma_client.get_or_create_collection(
    name="medical_knowledge",
    metadata={"hnsw:space": "cosine"},
)

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding

def build_index():
    chunks = chunk_all_docs()
    print(f"\n准备写入 {len(chunks)} 个chunk...")
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["text"])
        collection.add(
            ids=[chunk["id"]],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[{"source": chunk["source"]}],
        )
        if (i + 1) % 10 == 0:
            print(f"已写入 {i+1}/{len(chunks)}")
    print(f"\n入库完成,共 {collection.count()} 条记录")

def search(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
        })
    return hits

if __name__ == "__main__":
    build_index()
    print("\n--- 测试检索 ---")
    results = search("哮喘的症状有哪些", top_k=3)
    for i, r in enumerate(results):
        print(f"\n结果{i+1} (来源:{r['source']}, 距离:{r['distance']:.4f})")
        print(r["text"][:150])