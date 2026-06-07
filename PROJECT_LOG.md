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
