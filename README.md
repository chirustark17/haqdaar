# Haqdaar

**Know your rights. Get what you're due.**

> A grounded civic-rights co-pilot. You describe a confusing situation — or paste/upload a confusing official document (a rejection letter, notice, bill, or form) — and Haqdaar gives you a plain-language explanation, a **cited** list of the benefits and rights you actually qualify for, a step-by-step action plan, and a ready-to-send **drafted letter**. Every claim is backed by a citation to the source rule, powered by **Microsoft Foundry IQ**.

**Hackathon:** Microsoft Agents League (AI Skills Fest 2026)
**Track:** Creative Apps (built with GitHub Copilot)
**Microsoft IQ layer:** Foundry IQ (grounded, permission-aware retrieval with citations)
**Status:** Active development — MVP in progress.

---

## The problem

The benefits, schemes, and protections people are entitled to are buried in dense, jargon-filled rules spread across many sources. The people who need them most — first-time applicants, low-literacy users, the elderly, anyone facing an unfamiliar official process — often can't *discover* what they qualify for or *decode* the documents they receive. Generic chatbots make this worse: they confidently *hallucinate* eligibility and procedures, which is actively harmful when someone acts on a wrong answer.

Haqdaar takes a different approach. It grounds every answer in the actual rule with a visible citation, proactively surfaces entitlements the user didn't know to ask about, and doesn't stop at information — it drafts the document the user needs to send.

## What Haqdaar does

Given a described situation (or a pasted/uploaded official document), Haqdaar produces four things:

1. **Plain-language explanation** — what the situation or document actually means, in clear words.
2. **Cited rights & benefits** — the schemes, rights, or options the user qualifies for, each with a citation to the source rule.
3. **Step-by-step action plan** — what to do, which office/body, which documents to bring, and any deadlines.
4. **A ready-to-send drafted letter** — an application, appeal, or formal request, grounded in the cited rules and ready to copy or download.

## Why it's different

- **It acts, not just answers** — it drafts the actual document, not just a reply.
- **It discovers entitlements** the user didn't know existed.
- **Every claim is citation-backed** — no ungrounded guesses.
- **Built for accessibility** — plain-language and large-text modes (multilingual/voice planned).

## The reasoning loop (multi-step and visible)

Haqdaar runs a transparent, seven-step pipeline. Each step is logged and surfaced in the UI as a **reasoning trace** the user (and a judge) can watch:

1. **Understand** — parse the described situation (and, as a stretch feature, OCR an uploaded document).
2. **Classify** — identify the domain and what is at stake.
3. **Ground** — retrieve the exact applicable rules via Foundry IQ, with citations.
4. **Reason** — check eligibility/validity for *this specific* person.
5. **Plan** — produce the step-by-step action plan.
6. **Act** — draft the required letter/application, grounded and cited.
7. **Safeguard** — if no grounded source is found, say so instead of guessing; attach an informational disclaimer.

## Architecture

- **UI (Streamlit)** — input area → a live reasoning-trace panel → results: plain-language explanation, cited rights cards (each with a source chip), the action plan, and the drafted letter (copy/download). Accessibility: plain-language and large-text modes, plus demo example presets.
- **Agent orchestration (Python)** — a transparent implementation of the seven-step pipeline; every step is logged.
- **Grounding (Microsoft Foundry IQ)** — a knowledge base built from a synthetic corpus of rule/scheme documents; agentic retrieval returns grounded answers *with citations*. This is the trust backbone and the required IQ integration.
- **Model (Azure-hosted)** — a small/cost-efficient model (subject to regional availability) handles the reasoning and letter-drafting steps.
- **Local NLP (Hugging Face)** — a lightweight local model (e.g., DistilBERT) handles the classification step to conserve Azure credits.
- **Safety layer** — citation enforcement, ungrounded-refusal, informational framing, input sanitization, and graceful error handling.

## Tech stack

| Layer | Choice |
| --- | --- |
| Language | Python |
| UI | Streamlit |
| Optional API layer | Flask |
| Local NLP | Hugging Face Transformers (DistilBERT / T5) |
| Grounding / retrieval | Microsoft Foundry IQ (knowledge base + agentic retrieval with citations, backed by Azure AI Search) |
| LLM | Azure-hosted model via Foundry |
| OCR (stretch) | Tesseract |
| Dev environment | VS Code + GitHub Copilot |
| Version control | Git / GitHub |

## Microsoft IQ integration — Foundry IQ

Haqdaar uses **Foundry IQ** as its grounded knowledge layer. A knowledge base is built from a synthetic corpus of rule and scheme documents. When the agent answers, it uses agentic retrieval against that knowledge base, and answers come back **grounded with citations** to the source documents. This is what powers the cited rights cards and the grounded drafted letters, and it is what keeps the system from hallucinating eligibility or procedure.

## GitHub Copilot

This project is built using AI-assisted development with **GitHub Copilot** in VS Code — Copilot Chat for problem-solving, debugging, and code explanation, and inline suggestions to accelerate implementation. Specific examples of where Copilot helped will be documented here before submission.

## Data — synthetic only

> All knowledge documents and demo profiles in this project are **synthetic and for demonstration only**. No real personal data, PII, customer records, or confidential information is used anywhere. Identifiers are deliberately fabricated (for example, `SCHEME-001`, `USER-DEMO-01`).

- `knowledge/` — synthetic rule/scheme documents that form the knowledge base.
- `data/` — synthetic demo profiles used to showcase the flow.

## Security & Responsible AI

- Secrets live in a `.env` file and are **never committed**; a `.env.example` with placeholder values is committed instead.
- `.gitignore` excludes `.env`, `__pycache__/`, `*.log`, `output/`, and `.venv/`.
- **Citation-gated answers:** no claim is shown without a grounded source.
- **Ungrounded-refusal:** when no grounded source is found, the agent says so rather than guessing.
- **Informational only:** Haqdaar is not legal or financial advice; users are told to verify with the relevant official body.
- **Data protection:** user inputs are not stored.
- **Transparency:** users are always told they are interacting with an AI assistant.

## Getting started (intended setup)

> These are the intended steps; full, click-by-click guidance (including Azure/Foundry connection and secret handling) is provided during setup.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
#    Copy .env.example to .env and fill in your Azure / Foundry values
cp .env.example .env

# 4. Run the app
streamlit run app/main.py
```

## Roadmap

- **MVP:** text-situation input → cited rights → action plan → drafted letter.
- **Stretch:** document upload + OCR; multilingual and voice; expose the engine as an MCP server for GitHub Copilot; an evaluation/observability harness.

## What I learned

_To be completed at submission — a short reflection on building with Foundry IQ, grounding, and Copilot._

## License

To be decided (MIT recommended for an open hackathon submission).
