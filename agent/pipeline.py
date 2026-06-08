"""Haqdaar reasoning pipeline (Phase 4b).

Turns a described situation into four grounded, cited outputs via a transparent
multi-step flow: Understand, Classify, Ground, Reason, Plan, Act, Safeguard.
Grounding uses the retrieve() interface (local now, Foundry IQ later).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from grounding.knowledge_base import retrieve
from grounding.llm_client import chat

DISCLAIMER = (
    "Haqdaar provides general, cited information based on a synthetic demo knowledge "
    "base - it is not legal or financial advice. Always verify with the relevant "
    "official body."
)


def _parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start : end + 1]
    return json.loads(t)


def run_pipeline(situation: str) -> dict:
    trace: list[str] = []
    situation = (situation or "").strip()
    if not situation:
        return {"grounded": False, "explanation": "Please describe your situation so I can help.",
                "rights": [], "action_plan": [], "letter": "", "sources": [],
                "trace": ["No input provided."], "disclaimer": DISCLAIMER}

    trace.append("1-2. Understand & classify the situation.")
    try:
        extract = _parse_json(chat(
            system=("You analyse a person's described situation for a civic-rights assistant. "
                    "Return ONLY a JSON object with keys: summary (one sentence), domain (short "
                    "label), keywords (array of 3-8 key terms for searching). JSON only."),
            user=situation))
        domain = str(extract.get("domain", "")).strip()
        keywords = [str(k) for k in extract.get("keywords", []) if str(k).strip()]
    except Exception:
        domain, keywords = "", []
    trace.append(f"   Domain: {domain or 'unknown'}; keywords: {', '.join(keywords) or '(none)'}")

    trace.append("3. Ground: retrieve relevant sources from the knowledge base.")
    docs = retrieve((" ".join(keywords) + " " + situation).strip(), top_k=4)
    relevant = [d for d in docs if d.get("score", 0) > 0]
    if relevant:
        trace.append("   Retrieved: " + "; ".join(f"{d['source']} (score {d['score']})" for d in relevant))
    else:
        trace.append("   No matching sources found.")
        trace.append("7. Safeguard: no grounded source - declining to guess.")
        return {"grounded": False,
                "explanation": ("I couldn't find anything in the available knowledge base that "
                                "clearly matches your situation, so I won't guess. Please add more "
                                "detail, or check directly with the relevant official body."),
                "rights": [], "action_plan": [], "letter": "", "sources": [],
                "trace": trace, "disclaimer": DISCLAIMER}

    context = "\n\n".join(f"[SOURCE: {d['source']}] {d['title']}\n{d['text']}" for d in relevant)

    trace.append("4-6. Reason over the sources, build an action plan, draft a letter.")
    system = (
        "You are Haqdaar, a civic-rights assistant. Use ONLY the SOURCES provided to decide what "
        "the person may be entitled to. Do not invent schemes, rules, or facts not in the SOURCES. "
        "Every entitlement and claim must cite its source filename in square brackets, e.g. "
        "[SCHEME-003.md]. If the SOURCES don't support something, leave it out.\n\n"
        "Return ONLY a JSON object with keys:\n"
        '  "explanation": 2-4 plain-language sentences on the situation and what it means,\n'
        '  "rights": array of {"name","why_eligible","citation"} for each scheme they may qualify for,\n'
        '  "action_plan": array of short step strings (what to do, documents needed),\n'
        '  "letter": a ready-to-send request/application letter as one string, grounded in the '
        "sources, using placeholders like [Your Name].\nJSON only, no commentary.")
    try:
        result = _parse_json(chat(system=system, user=f"PERSON'S SITUATION:\n{situation}\n\nSOURCES:\n{context}"))
    except Exception as e:
        trace.append(f"   Generation/parse issue: {e!r}")
        result = {}

    explanation = str(result.get("explanation", "")).strip()
    rights = result.get("rights", []) if isinstance(result.get("rights"), list) else []
    action_plan = result.get("action_plan", []) if isinstance(result.get("action_plan"), list) else []
    letter = str(result.get("letter", "")).strip()
    if not explanation:
        explanation = ("I found relevant sources for your situation (listed below), but couldn't "
                       "format a full answer this time. Please try rephrasing your situation.")

    trace.append("7. Safeguard: disclaimer attached; answers cite the sources above.")
    return {"grounded": True, "explanation": explanation, "rights": rights,
            "action_plan": action_plan, "letter": letter,
            "sources": [d["source"] for d in relevant], "trace": trace, "disclaimer": DISCLAIMER}


if __name__ == "__main__":
    demo = "I farm a small plot and need help with income support for my rural family."
    print(f"SITUATION: {demo}\n")
    out = run_pipeline(demo)
    print("GROUNDED:", out["grounded"])
    print("\nEXPLANATION:\n", out["explanation"])
    print("\nRIGHTS:")
    for r in out["rights"]:
        print(" -", r)
    print("\nACTION PLAN:")
    for s in out["action_plan"]:
        print(" -", s)
    print("\nLETTER:\n", out["letter"][:600])
    print("\nSOURCES:", out["sources"])
    print("\nTRACE:")
    for t in out["trace"]:
        print("  ", t)
