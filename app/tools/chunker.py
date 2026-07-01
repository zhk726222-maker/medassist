import os
import re
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

def clean_long_tokens(text: str, max_word_len: int = 50) -> str:
    """过滤超长无空格片段(如base64编码),防止tokenizer崩溃"""
    words = text.split()
    cleaned = []
    for w in words:
        if len(w) > max_word_len:
            cleaned.append(w[:max_word_len] + "...[截断]")
        else:
            cleaned.append(w)
    return " ".join(cleaned)

def split_text(text: str) -> list[str]:
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end - CHUNK_OVERLAP
    return chunks

def chunk_all_docs(raw_dir: str = "data/raw") -> list[dict]:
    all_chunks = []
    for filename in sorted(os.listdir(raw_dir)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        text = clean_long_tokens(text)
        chunks = split_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{filename}_{i}",
                "text": chunk,
                "source": filename,
            })
        print(f"{filename}: 切出 {len(chunks)} 个chunk")
    return all_chunks