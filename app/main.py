"""Haqdaar - Streamlit UI (Phase 4c)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from agent.pipeline import run_pipeline

st.set_page_config(page_title="Haqdaar", page_icon="🪪", layout="centered")

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


st.title("Haqdaar")
st.subheader("Know your rights. Get what you're due.")
st.caption(
    "A demo civic-rights assistant that explains your situation, finds the benefits you "
    "may qualify for, plans your next steps, and drafts a letter - every claim cited to its source."
)
st.info(
    "Haqdaar provides general, cited information based on a synthetic demo knowledge base - "
    "it is not legal or financial advice. Always verify with the relevant official body."
)

st.write("**Try an example:**")
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
        with st.spinner("Analysing your situation and checking the knowledge base…"):
            try:
                st.session_state.result = run_pipeline(situation)
            except Exception as e:
                st.session_state.result = {"error": str(e)}

result = st.session_state.result
if result:
    if "error" in result:
        st.error("Something went wrong while analysing your situation. Please try again.")
        with st.expander("Technical detail"):
            st.code(result["error"])
    else:
        st.divider()
        if not result.get("grounded"):
            st.warning(result.get("explanation", "No grounded information found."))
        else:
            st.markdown("### Explanation")
            st.write(result.get("explanation", ""))

            st.markdown("### Rights & benefits you may qualify for")
            rights = result.get("rights", [])
            if rights:
                for r in rights:
                    with st.container(border=True):
                        st.markdown(f"**{r.get('name', 'Benefit')}**")
                        if r.get("why_eligible"):
                            st.write(r["why_eligible"])
                        if r.get("citation"):
                            st.caption(f"Source: {r['citation']}")
            else:
                st.write("No specific entitlements identified from the available sources.")

            st.markdown("### Action plan")
            steps = result.get("action_plan", [])
            if steps:
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. {step}")
            else:
                st.write("No action steps available.")

            st.markdown("### Drafted letter")
            letter = result.get("letter", "")
            if letter:
                st.text_area("You can copy or download this letter:", value=letter, height=240)
                st.download_button("Download letter", data=letter, file_name="haqdaar_letter.txt", mime="text/plain")
            else:
                st.write("No letter drafted.")

        if result.get("sources"):
            st.caption("Grounded in sources: " + ", ".join(result["sources"]))
        st.caption(result.get("disclaimer", ""))

        with st.expander("Reasoning trace (how Haqdaar worked this out)"):
            for line in result.get("trace", []):
                st.text(line)
