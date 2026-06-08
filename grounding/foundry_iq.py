"""Foundry IQ (Azure AI Search agentic retrieval) integration for Haqdaar.
Step 1: key-based connectivity check. Later steps add: file knowledge source,
knowledge base (GA 2026-04-01 API), and a retrieve() that the pipeline calls.
"""
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

load_dotenv()

SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_ADMIN_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY")


def get_index_client() -> SearchIndexClient:
    if not SEARCH_ENDPOINT or not SEARCH_ADMIN_KEY:
        raise RuntimeError(
            "Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_ADMIN_KEY in .env"
        )
    return SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_ADMIN_KEY),
    )


def check_connection() -> None:
    client = get_index_client()
    stats = client.get_service_statistics()
    print("Connected to Azure AI Search (Foundry IQ).")
    print("Service statistics:", stats)


if __name__ == "__main__":
    try:
        check_connection()
    except Exception as exc:
        print("Connection FAILED:", repr(exc))
        raise
