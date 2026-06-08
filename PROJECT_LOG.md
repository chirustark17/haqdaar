# PROJECT_LOG — Haqdaar

**Purpose.** This is a running backup of context for the project. It records what was done in each phase so work can resume cleanly and so AI coding agents (GitHub Copilot, Claude Code, Codex) can read accurate context **without hallucinating**. Update this at the end of every working session and whenever something is added or changed.

**Entry format:** `[date] | Phase | What was done | Files touched | Next step`

---

## Locked decisions

- **Hackathon:** Microsoft Agents League — **Creative Apps** track (GitHub Copilot required + one Microsoft IQ layer required).
- **Project:** **Haqdaar** — a grounded civic-rights co-pilot that explains a situation/document, lists cited entitlements, plans the action, and drafts the letter.
- **IQ layer:** **Foundry IQ** (grounded, cited retrieval).
- **Tool chain:** GitHub Copilot (primary) → Claude Code → Codex (fallbacks). Repo and Copilot live on the personal GitHub account **"Chiru Stark"**; Azure is accessed via a GitHub Student Pack account ($200 Azure for Students credits).
- **Approach:** **MVP-first** — text input → cited rights → action plan → drafted letter. Stretch features added only after the MVP is complete and submittable.
- **Data:** **synthetic only** (no real data, PII, or confidential info).
- **Cost:** free except Azure, which is covered by the $200 student credits.

## The reasoning pipeline (7 steps)

Understand → Classify → Ground (Foundry IQ) → Reason → Plan → Act (draft) → Safeguard.
Each step is logged and shown in the UI as a reasoning trace.

## Planned file map

> This is the **intended** structure and may be refined as we build. Treat names here as the plan, not as confirmed files — this map is updated as files are actually created. Do not assume a file exists until it appears in a log entry's "Files touched".

```
haqdaar/
├─ app/                # Streamlit UI
│  └─ main.py
├─ agent/              # orchestration + the 7-step pipeline
│  ├─ pipeline.py
│  ├─ steps/
│  └─ prompts/
├─ grounding/          # Foundry IQ client + retrieval helpers
├─ knowledge/          # SYNTHETIC rule/scheme documents (knowledge-base source)
├─ data/               # SYNTHETIC demo profiles
├─ logs/               # run logs (gitignored)
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ README.md
└─ PROJECT_LOG.md
```

## Security checklist (carried through every phase)

- [ ] `.env` never committed; `.env.example` with placeholders committed instead
- [ ] `.gitignore` excludes `.env`, `__pycache__/`, `*.log`, `output/`, `.venv/`
- [ ] No real API keys or secrets printed anywhere
- [ ] Citation-gated answers; ungrounded-refusal behaviour
- [ ] Informational-only disclaimer present
- [ ] Synthetic data only; user inputs not stored

---

## Log

`2026-06-07 | Phase 0 — Planning & Setup | Locked the project (Haqdaar) and the Creative Apps track. Defined the 7-step reasoning architecture, feature set, Streamlit UI plan, tech stack, the Foundry IQ grounding approach, the synthetic-data plan, and the security/Responsible-AI guidelines. Created README.md and PROJECT_LOG.md. | README.md, PROJECT_LOG.md | Next: scaffold the repo — create the folder structure, .gitignore, .env.example, and requirements.txt, then initialise the Git repo and connect the GitHub remote under "Chiru Stark".`
`2026-06-07 | Phase 1 — Repo scaffold | Created public GitHub repo chirustark17/haqdaar. Added folder skeleton (app, agent/steps, agent/prompts, grounding, knowledge, data, logs), .gitignore, .env.example, requirements.txt (streamlit, python-dotenv). Initialised Git, committed, pushed to origin/main. | .gitignore, .env.example, requirements.txt, folder structure | Next: build the synthetic knowledge base + first Streamlit screen.`
`2026-06-07 | Phase 2 — First screen + synthetic KB | Built app/main.py (Streamlit input screen with example presets, disclaimer, placeholder results, reasoning-trace panel) and .streamlit/config.toml theme. Created synthetic KB: knowledge/SCHEME-001..003.md and knowledge/appeal-guide.md (fabricated, demo-only). Created .venv and installed streamlit + python-dotenv. No Azure/LLM yet. | app/main.py, .streamlit/config.toml, knowledge/*.md, PROJECT_LOG.md | Next: set up Azure AI Foundry + Foundry IQ, then wire grounded retrieval.`
`2026-06-07 | Phase 2 fix — Streamlit form bug | Fixed app/main.py crash (st.button inside st.form). Removed the form; presets and submit are now plain st.button calls synced via st.session_state. Screen renders without error. | app/main.py, PROJECT_LOG.md | Next: Azure AI Foundry + Foundry IQ setup, then wire grounded retrieval.`
`2026-06-07 | Phase 2 fix 2 — session-state binding | Fixed app/main.py crash (assigning a key-bound widget's return to st.session_state). Text area now bound by key only; presets use on_click callbacks; submit sets a non-widget flag. Screen renders without error. | app/main.py, PROJECT_LOG.md | Next: Azure AI Foundry + Foundry IQ setup, then wire grounded retrieval.`
`2026-06-07 | Phase 3 — Model connectivity | Added grounding/llm_client.py (Azure OpenAI client via openai SDK; get_client() + ask() + a connectivity test; api_version default 2024-10-21). Added openai to requirements.txt and installed it. Completed .env.example with placeholder names for the OpenAI vars. Verified gpt-4o-mini responds. | grounding/llm_client.py, requirements.txt, .env.example, PROJECT_LOG.md | Next: build the Foundry IQ knowledge base from knowledge/*.md, then wire grounded+cited retrieval.`
`2026-06-07 | Phase 3 done — Model connectivity working | grounding/llm_client.py uses the OpenAI v1 client (OpenAI(base_url, api_key)) against the Foundry endpoint (services.ai.azure.com/openai/v1) with key auth, plus a diagnostic printout (endpoint/deployment only, never the key). Connectivity test PASSED — gpt-4o-mini responds. | grounding/llm_client.py, .env.example, PROJECT_LOG.md | Next: build the Foundry IQ knowledge base from knowledge/*.md, then wire grounded+cited retrieval.`
`2026-06-07 | Phase 4a - Local grounding retriever | Added grounding/knowledge_base.py: load_documents() reads knowledge/*.md; retrieve(query, top_k) returns the most relevant synthetic docs by meaningful-term overlap, with source + matched terms for citations/trace. Dependency-free; provides the retrieve() interface Foundry IQ will later back. Verified on a sample query. | grounding/knowledge_base.py, PROJECT_LOG.md | Next: 4b - the 7-step agent pipeline (retrieve + LLM) producing explanation, cited rights, action plan, drafted letter.`
`2026-06-07 | Phase 4b - Reasoning pipeline | Added chat(system,user) to grounding/llm_client.py. Added agent/pipeline.py: run_pipeline(situation) runs the 7-step flow (Understand-Classify-Ground-Reason-Plan-Act-Safeguard) using retrieve() + the LLM, returning grounded CITED outputs (explanation, rights, action_plan, letter) plus a trace; refuses when no source matches. Verified on the small-farmer demo. | grounding/llm_client.py, agent/pipeline.py, PROJECT_LOG.md | Next: 4c - wire run_pipeline into the Streamlit UI.`
`2026-06-07 | Phase 4c - Pipeline wired into UI | Rewrote app/main.py to call run_pipeline() on submit (spinner + result cached in session_state) and render real grounded results: explanation, rights cards with source citations, numbered action plan, drafted letter with download button, grounded-sources caption, disclaimer, and the live reasoning-trace expander. Handles ungrounded/refusal and error cases. | app/main.py, PROJECT_LOG.md | Next: 4d - stand up Foundry IQ and swap the retrieve() backend.`
