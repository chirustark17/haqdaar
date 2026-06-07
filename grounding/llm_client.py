"""LLM client for Haqdaar — talks to the Azure OpenAI (Foundry) deployment.

Reads configuration from environment variables (.env). No secrets are hardcoded.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


def get_client() -> AzureOpenAI:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError(
            "Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. Check your .env file."
        )
    return AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=API_VERSION)


def ask(prompt: str) -> str:
    """Send a single user prompt to the deployed model and return its reply."""
    deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT")
    if not deployment:
        raise RuntimeError("Missing AZURE_AI_MODEL_DEPLOYMENT in .env.")
    client = get_client()
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    try:
        reply = ask("In one sentence, what is a government welfare scheme?")
        print("Connection OK. Model replied:\n")
        print(reply)
    except Exception as e:
        print("Connection failed:")
        print(repr(e))
