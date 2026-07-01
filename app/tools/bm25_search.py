import re
from rank_bm25 import BM25Okapi
from app.tools.chunker import chunk_all_docs

def tokenize(text: str) -> list[str]:
    """分词:拆分驼峰命名,转小写,提取字母数字和中文字符"""
    # 拆分驼峰
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # 提取中文词(单字)和英文/数字词
    tokens = re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", text.lower())
    return tokens

_chunks = None
_bm25 = None

def _build_index():
    global _chunks, _bm25
    if _bm25 is not None:
        return
    _chunks = chunk_all_docs()
    corpus_tokens = [tokenize(c["text"]) for c in _chunks]
    _bm25 = BM25Okapi(corpus_tokens)

def search_bm25(query: str, top_k: int = 5) -> list[dict]:
    _build_index()
    query_tokens = tokenize(query)
    scores = _bm25.get_scores(query_tokens)
    ranked_idx = sorted(range(len(scores)),
                        key=lambda i: scores[i], reverse=True)[:top_k]
    return [
        {
            "id": _chunks[idx]["id"],
            "text": _chunks[idx]["text"],
            "source": _chunks[idx]["source"],
            "score": scores[idx],
        }
        for idx in ranked_idx
    ]

if __name__ == "__main__":
    results = search_bm25("哮喘的症状", top_k=3)
    for i, r in enumerate(results):
        print(f"\n结果{i+1} (来源:{r['source']}, 分数:{r['score']:.4f})")
        print(r["text"][:150])