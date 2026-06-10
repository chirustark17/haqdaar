"""Presentation-level i18n for Haqdaar: translate user input to English for the
(unmodified) pipeline, and translate results back to the user's language.
Imports the existing LLM client; does NOT modify pipeline or grounding internals."""
import json

from grounding.llm_client import chat

LANGUAGES = {
    "English": "English",
    "हिन्दी (Hindi)": "Hindi",
    "ಕನ್ನಡ (Kannada)": "Kannada",
    "தமிழ் (Tamil)": "Tamil",
}


def to_english(text: str, source_language: str) -> str:
    """Translate user input to English for the pipeline. No-op for English."""
    if source_language == "English" or not text.strip():
        return text
    try:
        out = chat(
            "You are a precise translator. Translate the user's text to English. "
            "Return ONLY the English translation, nothing else.",
            text,
        )
        return out.strip() or text
    except Exception:
        return text


def translate_result(result: dict, target_language: str):
    """Translate user-facing result fields. Returns (result, translated_bool).
    Citations like [SCHEME-001.md], the placeholders [Your Name] and
    [Your Contact Information], file names, and numbers stay verbatim."""
    if target_language == "English" or not isinstance(result, dict) or "error" in result:
        return result, False
    keys = ("explanation", "rights", "action_plan", "letter", "disclaimer")
    payload = {k: result.get(k) for k in keys if result.get(k)}
    if not payload:
        return result, False
    system = (
        f"You are a precise translator. Translate every JSON string value into {target_language}. "
        "Keep all JSON keys and the structure EXACTLY the same. Do NOT translate or alter: "
        "citation strings in square brackets such as [SCHEME-001.md], the exact placeholders "
        "[Your Name] and [Your Contact Information], file names, reference numbers, or numbers. "
        "Return ONLY valid JSON with the same keys - no markdown fences, no commentary."
    )
    try:
        raw = chat(system, json.dumps(payload, ensure_ascii=False))
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        merged = dict(result)
        for k, v in data.items():
            if k in merged and isinstance(v, type(merged[k])):
                merged[k] = v
        return merged, True
    except Exception:
        return result, False
