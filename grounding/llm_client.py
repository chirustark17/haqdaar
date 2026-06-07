"""LLM client for Haqdaar — talks to the Foundry model deployment via the OpenAI v1 client.

Reads configuration from environment variables (.env). No secrets are hardcoded.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client() -> OpenAI:
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not base_url or not api_key:
        raise RuntimeError(
            "Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. Check your .env file."
        )
    return OpenAI(base_url=base_url, api_key=api_key)


def ask(prompt: str) -> str:
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
    print("--- Haqdaar connectivity check ---")
    print("base_url  :", os.getenv("AZURE_OPENAI_ENDPOINT", "(NOT SET)"))
    print("deployment:", os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "(NOT SET)"))
    print("api_key set:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
    print("----------------------------------")
    try:
        reply = ask("In one sentence, what is a government welfare scheme?")
        print("Connection OK. Model replied:\n")
        print(reply)
    except Exception as e:
        print("Connection failed:")
        print(repr(e))
