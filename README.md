# Haqdaar

**Know your rights. Get what you're due.**

> A grounded civic-rights co-pilot. You describe a confusing situation — or paste/upload a confusing official document (a rejection letter, notice, bill, or form) — and Haqdaar gives you a plain-language explanation, a **cited** list of the benefits and rights you actually qualify for, a step-by-step action plan, and a ready-to-send **drafted letter**. Every claim is backed by a citation to the source rule, powered by **Microsoft Foundry IQ**.

**Hackathon:** Microsoft Agents League (AI Skills Fest 2026)  
**Track:** Creative Apps (built with GitHub Copilot)  
**Microsoft IQ layer:** Foundry IQ (grounded, agentic retrieval with citations via Azure AI Search)  
**Status:** Complete — submitted June 14 2026.

---

## The problem

The benefits, schemes, and protections people are entitled to are buried in dense, jargon-filled rules spread across many sources. The people who need them most — first-time applicants, low-literacy users, the elderly, anyone facing an unfamiliar official process — often can't *discover* what they qualify for or *decode* the documents they receive. Generic chatbots make this worse: they confidently hallucinate eligibility and procedures, which is actively harmful when someone acts on a wrong answer.

Haqdaar takes a different approach. It grounds every answer in the actual rule with a visible citation, proactively surfaces entitlements the user didn't know to ask about, and doesn't stop at information — it drafts the document the user needs to send.

---

## What Haqdaar does

Given a described situation (or a pasted/uploaded official document), Haqdaar produces four things:

1. **Plain-language explanation** — what the situation or document actually means, in clear words.
2. **Cited rights & benefits** — the schemes, rights, or options the user qualifies for, each with a citation to the source rule.
3. **Step-by-step action plan** — what to do, which office/body, which documents to bring, and any deadlines.
4. **A ready-to-send drafted letter** — an application, appeal, or formal request, grounded in the cited rules and ready to personalise, copy, or download.

---

## Why it's different

- **Grounded, not guessed** — every right or benefit cited traces back to a source document retrieved by Foundry IQ. If nothing matches, Haqdaar says so rather than inventing an answer.
- **Action-complete** — most civic-tech tools stop at information. Haqdaar goes all the way to a sendable letter.
- **Built for accessibility** — multilingual support (English, Hindi, Kannada, Tamil); large-text mode; read-aloud for the drafted letter.
- **Transparent reasoning** — the 7-step reasoning trace is visible after every result so users can see exactly how the answer was reached.

---

## The reasoning loop (multi-step and visible)

Every query runs through a 7-step reasoning pipeline. The steps are shown to the user during processing (as an estimated stepper) and the full trace appears after results:

1. **Understand** — parse and clarify the situation.
2. **Classify** — identify the domain (education, pension, agriculture, health, housing, etc.).
3. **Ground** — retrieve the exact applicable rules via Foundry IQ, with citations.
4. **Reason** — assess eligibility against the retrieved rules.
5. **Plan** — build a concrete, ordered action plan.
6. **Act** — draft the ready-to-send letter.
7. **Safeguard** — verify every claim is cited; refuse to answer if nothing is grounded.

The pipeline is implemented in `agent/pipeline.py` using `gpt-4o-mini` on Microsoft Azure AI Foundry (Korea Central).

---

## Architecture

```
User input (text / uploaded PDF or TXT)
        |
        v
  agent/i18n.py          -- translate non-English input to English for retrieval
        |
        v
  agent/pipeline.py      -- 7-step reasoning (run_pipeline); calls grounding + LLM
        |
    +---+----------------------------------+
    |                                      |
grounding/foundry_iq.py        grounding/knowledge_base.py
Microsoft Foundry IQ           Local retriever (automatic fallback)
(Azure AI Search,              if Foundry IQ is unavailable
 agentic retrieval,
 semantic ranking,
 citation from source_data)
    |
    +--------------------------------------+
                                           v
                             grounding/llm_client.py
                             OpenAI v1 client ->
                             gpt-4o-mini on Foundry
                             (Korea Central)
        |
        v
  agent/i18n.py          -- translate result back to selected language
        |
        v
  agent/report.py        -- build_report_pdf (Microsoft-standard styled PDF)
                           build_report_text (all languages, plain text)
        |
        v
  app/main.py            -- Streamlit UI (Fluent-styled, Layout A: two-column results)
  ui/styles.py           -- CSS / HTML helpers
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Fluent-inspired theme: Microsoft Blue #0078D4, Segoe UI) |
| LLM | gpt-4o-mini on Microsoft Azure AI Foundry (Korea Central) |
| Grounding / retrieval | Microsoft Foundry IQ -- SearchIndexKnowledgeSource, KnowledgeBaseRetrievalClient, KnowledgeRetrievalSemanticIntent; backed by Azure AI Search Free tier (haqdaar-search, Korea Central) |
| PDF generation | fpdf2 (core fonts, Latin-1; Microsoft-standard styled output) |
| Document parsing | pypdf (text-based PDFs; scanned/image PDFs flagged gracefully) |
| Multilingual | agent/i18n.py -- English, Hindi, Kannada, Tamil |
| Dev environment | VS Code + GitHub Copilot |
| Deployment | Local / Streamlit (Azure-ready) |

---

## Microsoft IQ integration -- Foundry IQ

Haqdaar uses **Foundry IQ** as its grounded knowledge layer (`grounding/foundry_iq.py`).

**How it works:**

- A knowledge base (`haqdaar-kb`) is built on Azure AI Search (`haqdaar-search`, Korea Central, Free tier) from a synthetic corpus of rule and scheme documents (`knowledge/*.md`).
- At query time, `KnowledgeBaseRetrievalClient` issues a `KnowledgeRetrievalSemanticIntent` request -- this is agentic retrieval with semantic ranking.
- Citations are extracted from `response.references[].source_data` (reranker score + doc key).
- A local retriever (`grounding/knowledge_base.py`) serves as an automatic fallback if Foundry IQ is unavailable, so the app never hard-fails.

**Key learnings from wiring this up:**

- `azure-search-documents==12.0.0` does not include the `file` knowledge source type documented in some preview docs -- the correct class is `SearchIndexKnowledgeSource` (discovered via SDK introspection, not docs).
- Omitting the embedding model on the search index avoided managed identity requirements incompatible with an Azure for Students subscription.
- East US 2 was blocked on the restricted subscription; Korea Central worked for both Foundry and AI Search.

---

## GitHub Copilot

This project was built using **GitHub Copilot** in VS Code as the primary development tool -- as required by the Creative Apps track.

Copilot was used throughout:

- **Scaffolding** -- generating the initial project structure, `requirements.txt`, `.gitignore`, and boilerplate.
- **Pipeline implementation** -- Copilot Chat helped design and refine the 7-step `run_pipeline` function, the grounding retrieval loop, and the result schema.
- **Foundry IQ integration** -- debugging the SDK class hierarchy (especially the `SearchIndexKnowledgeSource` pivot), the `KnowledgeBaseRetrievalClient` wiring, and the `include_reference_source_data` parameter.
- **UI** -- generating the Streamlit layout, the Fluent-inspired CSS, the two-column results layout, and the interactive checklist + progress bar.
- **Bug fixes** -- diagnosing and fixing the sandboxed-iframe clipboard issue (copy letter), the stToolbar sidebar-reopen bug (Streamlit 1.58 DOM inspection), and the f-string backslash restriction on Python 3.10.
- **PDF styling** -- the fpdf2 styled report with the Microsoft-standard header band, section rules, and repeating footer.
- **Multilingual** -- the `agent/i18n.py` translate-in / translate-out wrapper.

All Copilot usage is genuine and traceable in the commit history.

---

## Data -- synthetic only

All knowledge base documents (`knowledge/*.md`, `data/sample_notice.*`) are **entirely synthetic** -- written for demo purposes only. They contain no real personal data (PII), no real government documents, and no real case records. The app is not connected to any live government database. Every result is clearly marked as informational and not legal or financial advice.

---

## Known limitations and honest caveats

- **Synthetic knowledge base** -- schemes and rules are illustrative, not live-updated official data. Do not use for real legal or financial decisions.
- **Read-aloud (regional languages)** -- Hindi/Kannada/Tamil speech depends on voices installed on the listener's operating system. English speech works on all modern browsers. Windows typically includes a Hindi voice; Kannada and Tamil voices may be absent without manual installation.
- **Scanned / image PDFs** -- pypdf can only extract text from text-based PDFs. Scanned documents are flagged with a clear error and the user is asked to paste the text instead.
- **Multilingual output** -- translation is done via the LLM (gpt-4o-mini); quality varies by language and domain. Citation strings and filenames are preserved verbatim through translation.

---

## Security and Responsible AI

- All secrets (Azure endpoint, API key, model deployment name) are stored in `.env` -- never committed. A `.env.example` with placeholder values is provided.
- `.gitignore` excludes `.env`, `__pycache__`, `*.log`, `output/`.
- The Safeguard step in the pipeline explicitly refuses to answer if no grounded sources are found -- it does not fabricate.
- All data is synthetic; no PII is processed or stored.

---

## How to run

**Prerequisites:** Python 3.10+, a `.env` file with your Azure / Foundry credentials (see `.env.example`).

```bash
# 1. Clone
git clone https://github.com/chirustark17/haqdaar.git
cd haqdaar

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up credentials
cp .env.example .env
# Edit .env -- fill in AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY,
# AZURE_OPENAI_DEPLOYMENT, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY

# 5. Run
streamlit run app/main.py
```

**First run:** the local retriever fallback works immediately. Foundry IQ requires the Azure AI Search index (`haqdaar-index`) to be populated -- run `python grounding/foundry_iq.py` once to build it.

---

## What I learned

**Foundry IQ and grounding:** The most important thing I learned is that grounding is not just an API call -- it is a design discipline. Getting citations right required understanding how `source_data` is structured in the response, how the semantic ranker re-scores documents, and why the fallback architecture matters. When Foundry IQ was unavailable during development, a hard failure would have blocked all progress; the local fallback made the app continuously demoable.

**SDK introspection over docs:** Preview SDKs drift from their documentation. The `file` knowledge source type documented in some Foundry previews does not exist in `azure-search-documents==12.0.0`. Finding the real class (`SearchIndexKnowledgeSource`) required reading the SDK source directly -- a habit I will carry into every future Azure integration.

**Region policy on student subscriptions:** East US 2 was blocked; Korea Central worked. This kind of silent regional restriction is invisible until you hit it, and it cost several hours. The lesson: always check region availability before scaffolding resources, especially on restricted subscriptions.

**Isolation as discipline:** Keeping `agent/pipeline.py` and `grounding/foundry_iq.py` locked throughout the UI build phase prevented every UI change from risking a regression in the grounding layer. The boundary between presentation and pipeline was enforced deliberately, not accidentally.

**GitHub Copilot as a pair programmer:** Copilot's biggest value was not code generation -- it was the speed of iteration on debugging. When the sidebar reopen button had a zero-size rect because it lived inside a hidden toolbar, Copilot Chat helped me read the DOM output and reason to the root cause in minutes rather than hours.

**Encoding in agent-driven workflows:** When coding agents write non-ASCII characters with the wrong encoding assumption, the resulting mojibake compiles and passes syntax checks but corrupts the UI. The fix -- routing all non-ASCII insertions through escape sequences in a pure-ASCII apply script -- is a pattern I now use by default.

---

## License

MIT -- see `LICENSE`.

---

*Haqdaar - Microsoft Agents League 2026 - Creative Apps track - Grounded by Foundry IQ on Azure AI Search - Built with GitHub Copilot and VS Code - Synthetic demo knowledge base - informational only, not legal or financial advice.*
