"""Haqdaar - Streamlit UI (Fluent-styled)."""

import sys
import html
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from agent.pipeline import run_pipeline
from agent.i18n import LANGUAGES, to_english, translate_result
from agent.report import build_report_text, build_report_pdf
from ui.styles import (
    inject_fluent_styles,
    hero_html,
    processing_html,
    message_bar_html,
    summary_html,
    rights_html,
    sources_html,
    trace_html,
    large_text_css,
    feature_cards_html,
    glance_html,
    footer_html,
)

st.set_page_config(page_title="Haqdaar", page_icon="🪪", layout="wide")
inject_fluent_styles()

# Reversible results-layout switch (A/B test). Set SHOW_LAYOUT_SWITCHER=False to hide for the final judged build.
SHOW_LAYOUT_SWITCHER = True
DEFAULT_RESULTS_LAYOUT = "understand_act"  # "centered" | "understand_act" | "reading_pane"
LAYOUT_LABELS = {
    "Centered (classic)": "centered",
    "A · Understand → Act": "understand_act",
    "B · Reading pane": "reading_pane",
}

PRESETS = {
    "Low-income student": "I am a final-year student from a low-income family and I'm struggling to pay my tuition and need support to continue my studies.",
    "Senior citizen pension": "I am 67 years old, retired with no regular income, and I want to know what pension support I can get.",
    "Small farmer": "I farm a small plot and need help with income support, grants, and application steps for my rural family.",
}

for _k, _v in {"situation_text": "", "result": None, "doc_error": "", "doc_notice": "", "result_nonce": 0, "lang_notice": "", "results_layout": "understand_act"}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def set_situation(text: str) -> None:
    st.session_state.situation_text = text
    st.session_state.result = None


def reset_all() -> None:
    st.session_state.situation_text = ""
    st.session_state.result = None
    st.session_state.doc_error = ""
    st.session_state.doc_notice = ""


MAX_DOC_CHARS = 6000


def use_uploaded_document() -> None:
    """Extract text from the uploaded PDF/TXT and load it into the situation box."""
    st.session_state.doc_error = ""
    st.session_state.doc_notice = ""
    f = st.session_state.get("uploaded_doc")
    if f is None:
        st.session_state.doc_error = "Please choose a PDF or TXT file first."
        return
    try:
        name = f.name.lower()
        if name.endswith(".pdf"):
            try:
                from pypdf import PdfReader
            except ImportError:
                st.session_state.doc_error = "PDF support isn't installed (pypdf missing). Run: pip install pypdf"
                return
            reader = PdfReader(f)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = f.getvalue().decode("utf-8", errors="ignore")
        text = text.strip()
        if not text:
            st.session_state.doc_error = (
                "No readable text found in this document. Scanned/image-only PDFs aren't supported in this demo - "
                "please paste the text instead."
            )
            return
        if len(text) > MAX_DOC_CHARS:
            text = text[:MAX_DOC_CHARS]
            st.session_state.doc_notice = f"Long document - using the first {MAX_DOC_CHARS} characters."
        st.session_state.situation_text = text
        st.session_state.result = None
        if not st.session_state.doc_notice:
            st.session_state.doc_notice = "Document text loaded into the situation box - review it, then press \"Find what I'm entitled to\"."
    except Exception as exc:
        st.session_state.doc_error = f"Couldn't read that file: {exc}"


# ---------- results rendering (presentation only; behavior unchanged) ----------
def _render_error(result):
    st.markdown(
        message_bar_html("Something went wrong while analysing your situation. Please try again.", "error"),
        unsafe_allow_html=True,
    )
    with st.expander("Technical detail"):
        st.code(result["error"])


def _render_ungrounded(result):
    st.markdown(
        message_bar_html(result.get("explanation", "No grounded information found."), "warning"),
        unsafe_allow_html=True,
    )


def render_glance(result):
    st.markdown(
        glance_html(
            len(result.get("rights", [])),
            len(result.get("action_plan", [])),
            len(result.get("sources", [])),
            str(st.session_state.get("response_language", "English")),
        ),
        unsafe_allow_html=True,
    )
    if st.session_state.lang_notice:
        st.markdown(message_bar_html(st.session_state.lang_notice, "warning"), unsafe_allow_html=True)


def render_explanation(result):
    st.markdown("<div class='hq-h2'>Explanation</div>", unsafe_allow_html=True)
    st.markdown(summary_html(result.get("explanation", "")), unsafe_allow_html=True)


def render_rights(result):
    st.markdown("<div class='hq-h2'>Rights &amp; benefits you may qualify for</div>", unsafe_allow_html=True)
    rights = result.get("rights", [])
    if rights:
        st.markdown(rights_html(rights), unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='hq-muted'>No specific entitlements identified from the available sources.</div>",
            unsafe_allow_html=True,
        )


def render_action_plan(result, nonce):
    st.markdown("<div class='hq-h2'>Action plan</div>", unsafe_allow_html=True)
    steps = result.get("action_plan", [])
    if steps:
        st.caption("Tick off each step as you complete it:")
        done = 0
        for i, step in enumerate(steps, 1):
            if st.checkbox(f"{i}. {step}", key=f"plan_{nonce}_{i}"):
                done += 1
        st.progress(done / len(steps))
        if done == len(steps):
            st.markdown(
                message_bar_html("All steps done — you're ready to send your letter below!", "info"),
                unsafe_allow_html=True,
            )
        else:
            st.caption(f"{done} of {len(steps)} steps completed")
    else:
        st.markdown("<div class='hq-muted'>No action steps available.</div>", unsafe_allow_html=True)


def render_letter(result, nonce):
    st.markdown("<div class='hq-h2'>Drafted letter</div>", unsafe_allow_html=True)
    letter = result.get("letter", "")
    if letter:
        st.caption("Personalise it (optional) - your details replace the placeholders live:")
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            user_name = st.text_input("Your name", key=f"name_{nonce}")
        with pcol2:
            user_contact = st.text_input("Your contact info", key=f"contact_{nonce}")
        final_letter = letter
        if user_name.strip():
            final_letter = final_letter.replace("[Your Name]", user_name.strip())
        if user_contact.strip():
            final_letter = final_letter.replace("[Your Contact Information]", user_contact.strip())
        st.text_area("You can copy or download this letter:", value=final_letter, height=240)

        lang = str(st.session_state.get("response_language", "English"))
        report_result = dict(result)
        report_result["letter"] = final_letter
        report_text = build_report_text(report_result)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("Download letter (.txt)", data=final_letter,
                               file_name="haqdaar_letter.txt", mime="text/plain",
                               use_container_width=True)
        with c2:
            if lang == "English":
                try:
                    pdf_bytes = build_report_pdf(report_result)
                    st.download_button("Download full report (PDF)", data=pdf_bytes,
                                       file_name="haqdaar_report.pdf", mime="application/pdf",
                                       use_container_width=True)
                except Exception:
                    st.download_button("Download full report (.txt)", data=report_text,
                                       file_name="haqdaar_report.txt", mime="text/plain",
                                       use_container_width=True)
            else:
                st.download_button("Download full report (.txt)", data=report_text,
                                   file_name="haqdaar_report.txt", mime="text/plain",
                                   use_container_width=True)
                st.caption("PDF export is available for English; other languages export as text.")

        mailto = "mailto:?subject=" + urllib.parse.quote("My Haqdaar letter") + "&body=" + urllib.parse.quote(final_letter)
        read_src = final_letter.replace("\\", " ").replace("`", "'")
        lang_codes = {"English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta"}
        lang_full = {"हिन्दी (Hindi)": "Hindi", "ಕನ್ನಡ (Kannada)": "Kannada", "தமிழ் (Tamil)": "Tamil"}.get(lang, "English")
        speak_code = lang_codes.get(lang_full, "en")
        import json as _json
        payload = _json.dumps(final_letter)
        st.components.v1.html(
            "<div class='hq-toolbar'>"
            f"<a class='hq-tool-btn' href=\"{mailto}\">\u2709 Email this letter</a>"
            "<button class='hq-tool-btn' onclick=\"navigator.clipboard.writeText(" + payload + ");this.innerText='\u2713 Copied';\">\u29C9 Copy letter</button>"
            "<button class='hq-tool-btn' onclick=\"var u=new SpeechSynthesisUtterance(" + payload + ");u.lang='" + speak_code + "';window.speechSynthesis.cancel();window.speechSynthesis.speak(u);\">\u25B6 Read aloud</button>"
            "<button class='hq-tool-btn' onclick=\"window.speechSynthesis.cancel();\">\u25A0 Stop</button>"
            "</div>"
            "<style>.hq-toolbar{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0;font-family:'Segoe UI',sans-serif;}"
            ".hq-tool-btn{display:inline-flex;align-items:center;gap:7px;background:#fff;border:1px solid #E1DFDD;border-radius:6px;padding:7px 13px;font-size:.84rem;font-weight:600;color:#242424;cursor:pointer;text-decoration:none;}"
            ".hq-tool-btn:hover{border-color:#0078D4;color:#0078D4;}</style>",
            height=56,
        )
    else:
        st.markdown("<div class='hq-muted'>No letter drafted.</div>", unsafe_allow_html=True)


def _render_sources_and_disclaimer(result):
    if result.get("sources"):
        st.markdown(sources_html(result["sources"]), unsafe_allow_html=True)
    if result.get("disclaimer"):
        st.markdown(f"<div class='hq-disclaimer'>{html.escape(result['disclaimer'])}</div>", unsafe_allow_html=True)


def _render_trace(result):
    with st.expander("Reasoning trace (how Haqdaar worked this out)"):
        st.markdown(trace_html(result.get("trace", [])), unsafe_allow_html=True)


def _render_grounded_centered(result, nonce):
    render_glance(result)
    render_explanation(result)
    render_rights(result)
    render_action_plan(result, nonce)
    render_letter(result, nonce)


def _render_grounded_understand_act(result, nonce):
    render_glance(result)
    col_l, col_r = st.columns([1.18, 0.82], gap="large")
    with col_l:
        render_explanation(result)
        render_rights(result)
    with col_r:
        render_action_plan(result, nonce)
    render_letter(result, nonce)


def _render_grounded_reading_pane(result, nonce):
    render_glance(result)
    main, aside = st.columns([0.64, 0.36], gap="large")
    with main:
        render_explanation(result)
        render_rights(result)
        render_letter(result, nonce)
    with aside:
        render_action_plan(result, nonce)


def _render_grounded_body(result, nonce, layout):
    if layout == "understand_act":
        _render_grounded_understand_act(result, nonce)
    elif layout == "reading_pane":
        _render_grounded_reading_pane(result, nonce)
    else:
        _render_grounded_centered(result, nonce)


def render_results(result, layout="centered"):
    nonce = st.session_state.result_nonce
    if "error" in result:
        _render_error(result)
        return
    st.markdown("<div class='hq-divider'></div>", unsafe_allow_html=True)
    if not result.get("grounded"):
        _render_ungrounded(result)
    else:
        _render_grounded_body(result, nonce, layout)
    _render_sources_and_disclaimer(result)
    _render_trace(result)


with st.sidebar:
    st.markdown("### About Haqdaar")
    st.markdown(
        "A grounded civic-rights co-pilot. Describe a situation (or paste an official notice) "
        "and Haqdaar explains it, finds benefits you may qualify for, plans your next steps, and "
        "drafts a ready-to-send letter — every claim cited to its source."
    )
    st.markdown("#### How it works")
    st.markdown(
        "1. **Understand** your situation\n"
        "2. **Classify** the domain\n"
        "3. **Ground** in cited rules (Foundry IQ)\n"
        "4. **Reason** about eligibility\n"
        "5. **Plan** the steps\n"
        "6. **Act** — draft the letter\n"
        "7. **Safeguard** — refuse if ungrounded"
    )
    st.button("Start over", on_click=reset_all, use_container_width=True)
    st.checkbox("Large text mode", key="large_text", help="Increase text size for easier reading")
    st.markdown(
        message_bar_html("Grounded by Microsoft Foundry IQ · agentic retrieval with citations.", "info"),
        unsafe_allow_html=True,
    )
    st.caption("Built with Azure AI Foundry · Foundry IQ · GitHub Copilot · Streamlit")
    st.markdown("[View source on GitHub](https://github.com/chirustark17/haqdaar)")
    if SHOW_LAYOUT_SWITCHER:
        st.markdown("#### Layout (A/B test)")
        _layout_keys = list(LAYOUT_LABELS.keys())
        _layout_vals = list(LAYOUT_LABELS.values())
        _cur = st.session_state.get("results_layout", DEFAULT_RESULTS_LAYOUT)
        _idx = _layout_vals.index(_cur) if _cur in _layout_vals else 0
        _picked = st.radio("Results layout", _layout_keys, index=_idx, label_visibility="collapsed")
        st.session_state.results_layout = LAYOUT_LABELS[_picked]

active_layout = (
    st.session_state.get("results_layout", DEFAULT_RESULTS_LAYOUT)
    if SHOW_LAYOUT_SWITCHER else DEFAULT_RESULTS_LAYOUT
)
if active_layout in ("understand_act", "reading_pane"):
    st.markdown("<style>.block-container{max-width:1180px;}</style>", unsafe_allow_html=True)

if st.session_state.get("large_text"):
    st.markdown(large_text_css(), unsafe_allow_html=True)

st.markdown(hero_html(), unsafe_allow_html=True)

st.markdown(
    message_bar_html(
        "Haqdaar provides general, cited information from a synthetic demo knowledge base — it is "
        "not legal or financial advice. Always verify with the relevant official body.",
        "warning",
    ),
    unsafe_allow_html=True,
)

if not st.session_state.result:
    st.markdown(feature_cards_html(), unsafe_allow_html=True)

st.selectbox("Response language", list(LANGUAGES.keys()), key="response_language")

tab_describe, tab_upload = st.tabs(["✍️ Describe your situation", "📄 Upload a document"])

with tab_describe:
    st.markdown("<div class='hq-section-label'>Try an example</div>", unsafe_allow_html=True)
    cols = st.columns(len(PRESETS))
    for col, (label, text) in zip(cols, PRESETS.items()):
        col.button(label, on_click=set_situation, args=(text,), use_container_width=True)

    st.text_area(
        "Describe your situation, or paste an official document or notice…",
        key="situation_text",
        height=160,
    )

with tab_upload:
    st.file_uploader(
        "Upload an official letter or notice (PDF or TXT - text-based, not scanned images)",
        type=["pdf", "txt"],
        key="uploaded_doc",
    )
    st.button("Use this document", on_click=use_uploaded_document)
    if st.session_state.doc_error:
        st.markdown(message_bar_html(st.session_state.doc_error, "error"), unsafe_allow_html=True)
    elif st.session_state.doc_notice:
        st.markdown(message_bar_html(st.session_state.doc_notice, "info"), unsafe_allow_html=True)
    st.caption("The extracted text lands in the Describe tab, where you can review or edit it before analysing.")

if st.button("Find what I'm entitled to", type="primary"):
    situation = st.session_state.situation_text.strip()
    if not situation:
        st.warning("Please describe your situation first.")
    else:
        progress = st.empty()
        progress.markdown(processing_html(), unsafe_allow_html=True)
        try:
            lang = LANGUAGES.get(st.session_state.get("response_language", "English"), "English")
            pipeline_input = to_english(situation, lang)
            result_data = run_pipeline(pipeline_input)
            translated = False
            if lang != "English" and isinstance(result_data, dict) and "error" not in result_data:
                result_data, translated = translate_result(result_data, lang)
            st.session_state.lang_notice = (
                "" if (lang == "English" or translated)
                else "Translation unavailable - showing results in English."
            )
            st.session_state.result = result_data
        except Exception as e:
            st.session_state.result = {"error": str(e)}
        finally:
            progress.empty()
        st.session_state.result_nonce += 1

result = st.session_state.result
if result:
    render_results(result, active_layout)

st.markdown(footer_html(), unsafe_allow_html=True)
