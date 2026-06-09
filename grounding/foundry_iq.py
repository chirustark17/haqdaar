"""Foundry IQ (Azure AI Search agentic retrieval) integration for Haqdaar.
Key-based, no managed identity, no blob, no embeddings (keyword + semantic ranker).

Phase 4d progress:
  - get_index_client()/get_search_client()/check_connection(): connectivity
  - build_index() + push_documents(): create index, load synthetic knowledge/*.md (this step)
  - [next] create_knowledge_source(), create_knowledge_base(), retrieve()
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
)

load_dotenv()

SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_ADMIN_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY")

INDEX_NAME = "haqdaar-index"
SEMANTIC_CONFIG = "haqdaar-semantic"
KNOWLEDGE_DIR = "knowledge"
KS_NAME = "haqdaar-ks"
KB_NAME = "haqdaar-kb"


def get_index_client() -> SearchIndexClient:
    if not SEARCH_ENDPOINT or not SEARCH_ADMIN_KEY:
        raise RuntimeError("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_ADMIN_KEY in .env")
    return SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_ADMIN_KEY))


def get_search_client() -> SearchClient:
    if not SEARCH_ENDPOINT or not SEARCH_ADMIN_KEY:
        raise RuntimeError("Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_ADMIN_KEY in .env")
    return SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_ADMIN_KEY),
    )


def check_connection() -> None:
    stats = get_index_client().get_service_statistics()
    print("Connected to Azure AI Search (Foundry IQ).")
    print("Service statistics:", stats)


def build_index() -> None:
    """Create/update a keyword + semantic index (no vectors -> no embedding model)."""
    index = SearchIndex(
        name=INDEX_NAME,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="source", type=SearchFieldDataType.String, filterable=True),
        ],
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIG,
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                    ),
                )
            ]
        ),
    )
    get_index_client().create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' created/updated (semantic config '{SEMANTIC_CONFIG}').")


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-=]", "_", value)


def _chunk_markdown(text: str):
    """Split markdown into (heading, body) chunks at lines starting with '#'.
    Whole file becomes one chunk if it has no headings."""
    chunks, heading, body = [], None, []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            if body:
                chunks.append((heading, "\n".join(body).strip()))
            heading = line.lstrip("# ").strip()
            body = [line]
        else:
            body.append(line)
    if body:
        chunks.append((heading, "\n".join(body).strip()))
    return [(h, b) for (h, b) in chunks if b]


def build_documents():
    md_files = sorted(Path(KNOWLEDGE_DIR).glob("*.md"))
    if not md_files:
        raise RuntimeError(f"No .md files found in {KNOWLEDGE_DIR}/")
    docs = []
    for fp in md_files:
        text = fp.read_text(encoding="utf-8")
        chunks = _chunk_markdown(text) or [(fp.stem, text.strip())]
        for i, (heading, body) in enumerate(chunks):
            docs.append({
                "id": f"{_safe_id(fp.stem)}-{i}",
                "title": heading or fp.stem,
                "content": body,
                "source": fp.name,
            })
    return docs


def push_documents() -> None:
    docs = build_documents()
    result = get_search_client().upload_documents(documents=docs)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(docs)} document chunks to '{INDEX_NAME}'.")
    for d in docs:
        print(f"  {d['id']} (source={d['source']}, title={d['title']!r}, {len(d['content'])} chars)")


def build_search_layer() -> None:
    build_index()
    push_documents()


def create_knowledge_source() -> None:
    """Wrap haqdaar-index as a SearchIndexKnowledgeSource (keyword + semantic)."""
    from azure.search.documents.indexes.models import (
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    ks = SearchIndexKnowledgeSource(
        name=KS_NAME,
        description="Synthetic civic-rights schemes + appeal guide for Haqdaar.",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=INDEX_NAME,
            semantic_configuration_name=SEMANTIC_CONFIG,
            search_fields=["title", "content"],
            source_data_fields=["title", "content", "source"],
        ),
    )
    get_index_client().create_or_update_knowledge_source(ks)
    print(f"Knowledge source '{KS_NAME}' created/updated (index '{INDEX_NAME}').")


def create_knowledge_base() -> None:
    """Create a KnowledgeBase over the knowledge source. No LLM model -> extractive
    retrieval; the Haqdaar pipeline does its own reasoning over grounded chunks."""
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
    )

    kb = KnowledgeBase(
        name=KB_NAME,
        knowledge_sources=[KnowledgeSourceReference(name=KS_NAME)],
    )
    get_index_client().create_or_update_knowledge_base(kb)
    print(f"Knowledge base '{KB_NAME}' created/updated (source '{KS_NAME}').")


def build_all() -> None:
    build_index()
    push_documents()
    create_knowledge_source()
    create_knowledge_base()


def _foundry_retrieve(query: str, top_k: int = 5):
    """Query the Foundry IQ knowledge base; return grounded chunks as
    {source, title, text, score, matched}. Raises on failure (caller handles fallback)."""
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalSemanticIntent,
        SearchIndexKnowledgeSourceParams,
    )

    client = KnowledgeBaseRetrievalClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_ADMIN_KEY),
        knowledge_base_name=KB_NAME,
    )
    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search=query)],
        knowledge_source_params=[
            SearchIndexKnowledgeSourceParams(
                knowledge_source_name=KS_NAME,
                include_references=True,
                include_reference_source_data=True,
            )
        ],
        include_activity=False,
    )
    resp = client.retrieve(request)

    results = []
    for ref in (getattr(resp, "references", None) or [])[:top_k]:
        sd = getattr(ref, "source_data", None) or {}
        get = sd.get if hasattr(sd, "get") else (lambda *_: None)
        source = get("source")
        if not source:
            doc_key = getattr(ref, "doc_key", None) or ""
            stem = re.sub(r"-\d+$", "", doc_key)
            source = f"{stem}.md" if stem else "Foundry IQ"
        results.append({
            "source": source,
            "title": get("title") or "",
            "text": get("content") or "",
            "score": getattr(ref, "reranker_score", None),
            "matched": True,
        })
    return results


def retrieve(query: str, top_k: int = 5):
    """Grounded retrieval via Foundry IQ, with automatic fallback to the local
    retriever so the app never breaks."""
    try:
        results = _foundry_retrieve(query, top_k)
        if results:
            return results
        print("[foundry_iq] No Foundry IQ results; falling back to local retriever.")
    except Exception as exc:
        print(f"[foundry_iq] Foundry IQ retrieve failed ({exc!r}); falling back to local retriever.")
    from grounding.knowledge_base import retrieve as local_retrieve
    return local_retrieve(query, top_k)


def test_retrieve() -> None:
    """Standalone smoke test against the knowledge base (3 demo-style queries)."""
    queries = [
        "I am a final-year student needing financial help for my fees",
        "My elderly mother needs monthly income support",
        "I run a small farm and lost income this season",
    ]
    for q in queries:
        print("=" * 60)
        print("QUERY:", q)
        results = retrieve(q, top_k=3)
        if not results:
            print("  (no results)")
        for r in results:
            print(f"  score={r['score']} source={r['source']} title={r['title']!r}")
            print(f"     text[:160]={r['text'][:160]!r}")


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    try:
        if cmd == "test":
            test_retrieve()
        else:
            build_all()
    except Exception as exc:
        print(f"{cmd} FAILED:", repr(exc))
        raise
