"""Local knowledge retriever for Haqdaar (Phase 4a).

Reads the synthetic Markdown documents in the `knowledge/` folder and returns the
most relevant ones for a query. A simple, dependency-free lexical retriever so we can
build and demo the full pipeline now; later we swap this backend for Foundry IQ
behind the same `retrieve()` interface.
"""

from __future__ import annotations

import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "i", "a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "on",
    "my", "is", "are", "need", "help", "get", "this", "that", "it", "be", "have",
    "do", "at", "as", "from", "by", "me", "we", "you", "your", "can", "about",
}


def _content_terms(text: str) -> set[str]:
    return {t for t in _WORD.findall(text.lower()) if len(t) > 2 and t not in _STOPWORDS}


def load_documents() -> list[dict]:
    """Load every .md file in knowledge/ as a document."""
    docs = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        heading = next((ln for ln in text.splitlines() if ln.lstrip().startswith("#")), "")
        title = heading.lstrip("# ").strip() or path.stem
        docs.append({"source": path.name, "title": title, "text": text})
    return docs


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Return up to top_k documents most relevant to the query.

    Each result: {"source", "title", "text", "score", "matched"}. Scored by how many
    distinct meaningful query terms appear in the document. Simple but effective for the
    small synthetic KB; later replaced by Foundry IQ agentic retrieval behind this
    same signature.
    """
    docs = load_documents()
    q_terms = _content_terms(query)
    results = []
    for doc in docs:
        doc_terms = _content_terms(doc["text"])
        matched = sorted(q_terms & doc_terms)
        results.append({**doc, "score": len(matched), "matched": matched})
    results.sort(key=lambda d: d["score"], reverse=True)
    matched_docs = [r for r in results if r["score"] > 0]
    chosen = (matched_docs or results)[:top_k]
    return chosen


if __name__ == "__main__":
    sample = "I farm a small plot and need help with income support for my rural family."
    print(f"Query: {sample}\n")
    for r in retrieve(sample):
        print(f"[score {r['score']}] {r['source']} - {r['title']}  (matched: {', '.join(r['matched'])})")
