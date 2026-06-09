"""Haqdaar - Streamlit UI (Fluent-styled)."""

import sys
import html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from agent.pipeline import run_pipeline
from ui.styles import (
    inject_fluent_styles,
    hero_html,
    processing_html,
    message_bar_html,
    summary_html,
    rights_html,
    steps_html,
    sources_html,
    trace_html,
)

st.set_page_config(page_title="Haqdaar", page_icon="🪪", layout="wide")
inject_fluent_styles()

PRESETS = {
    "Low-income student": "I am a final-year student from a low-income family and I'm struggling to pay my tuition and need support to continue my studies.",
    "Senior citizen pension": "I am 67 years old, retired with no regular income, and I want to know what pension support I can get.",
    "Small farmer": "I farm a small plot and need help with income support, grants, and application steps for my rural family.",
}

for _k, _v in {"situation_text": "", "result": None}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def set_situation(text: str) -> None:
    st.session_state.situation_text = text
    st.session_state.result = None


def reset_all() -> None:
    st.session_state.situation_text = ""
    st.session_state.result = None


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
    st.markdown(
        message_bar_html("Grounded by Microsoft Foundry IQ · agentic retrieval with citations.", "info"),
        unsafe_allow_html=True,
    )
    st.caption("Built with Azure AI Foundry · Foundry IQ · GitHub Copilot · Streamlit")

st.markdown(hero_html(), unsafe_allow_html=True)

st.markdown(
    message_bar_html(
        "Haqdaar provides general, cited information from a synthetic demo knowledge base — it is "
        "not legal or financial advice. Always verify with the relevant official body.",
        "warning",
    ),
    unsafe_allow_html=True,
)

st.markdown("<div class='hq-section-label'>Try an example</div>", unsafe_allow_html=True)
cols = st.columns(len(PRESETS))
for col, (label, text) in zip(cols, PRESETS.items()):
    col.button(label, on_click=set_situation, args=(text,), use_container_width=True)

st.text_area(
    "Describe your situation, or paste an official document or notice…",
    key="situation_text",
    height=160,
)

if st.button("Find what I'm entitled to", type="primary"):
    situation = st.session_state.situation_text.strip()
    if not situation:
        st.warning("Please describe your situation first.")
    else:
        progress = st.empty()
        progress.markdown(processing_html(), unsafe_allow_html=True)
        try:
            st.session_state.result = run_pipeline(situation)
        except Exception as e:
            st.session_state.result = {"error": str(e)}
        finally:
            progress.empty()

result = st.session_state.result
if result:
    if "error" in result:
        st.markdown(
            message_bar_html("Something went wrong while analysing your situation. Please try again.", "error"),
            unsafe_allow_html=True,
        )
        with st.expander("Technical detail"):
            st.code(result["error"])
    else:
        st.markdown("<div class='hq-divider'></div>", unsafe_allow_html=True)
        if not result.get("grounded"):
            st.markdown(
                message_bar_html(result.get("explanation", "No grounded information found."), "warning"),
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='hq-h2'>Explanation</div>", unsafe_allow_html=True)
            st.markdown(summary_html(result.get("explanation", "")), unsafe_allow_html=True)

            st.markdown("<div class='hq-h2'>Rights &amp; benefits you may qualify for</div>", unsafe_allow_html=True)
            rights = result.get("rights", [])
            if rights:
                st.markdown(rights_html(rights), unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div class='hq-muted'>No specific entitlements identified from the available sources.</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<div class='hq-h2'>Action plan</div>", unsafe_allow_html=True)
            steps = result.get("action_plan", [])
            if steps:
                st.markdown(steps_html(steps), unsafe_allow_html=True)
            else:
                st.markdown("<div class='hq-muted'>No action steps available.</div>", unsafe_allow_html=True)

            st.markdown("<div class='hq-h2'>Drafted letter</div>", unsafe_allow_html=True)
            letter = result.get("letter", "")
            if letter:
                st.text_area("You can copy or download this letter:", value=letter, height=240)
                st.download_button("Download letter", data=letter, file_name="haqdaar_letter.txt", mime="text/plain")
            else:
                st.markdown("<div class='hq-muted'>No letter drafted.</div>", unsafe_allow_html=True)

        if result.get("sources"):
            st.markdown(sources_html(result["sources"]), unsafe_allow_html=True)
        if result.get("disclaimer"):
            st.markdown(f"<div class='hq-disclaimer'>{html.escape(result['disclaimer'])}</div>", unsafe_allow_html=True)

        with st.expander("Reasoning trace (how Haqdaar worked this out)"):
            st.markdown(trace_html(result.get("trace", [])), unsafe_allow_html=True)
