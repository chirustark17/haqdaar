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


if __name__ == "__main__":
    try:
        build_all()
    except Exception as exc:
        print("Build FAILED:", repr(exc))
        raise
