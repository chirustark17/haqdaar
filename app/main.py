import streamlit as st

st.set_page_config(page_title="Haqdaar", page_icon="🪪", layout="centered")

PRESET_SCENARIOS = {
    "Low-income student": "I am a university student struggling to pay tuition, rent, and basic living costs while studying full-time.",
    "Senior citizen pension": "I am a retired senior with limited savings and I want to know what pension or support programs I may be eligible for.",
    "Small farmer": "I farm a small plot and need help understanding income support, grants, and application steps for my rural family.",
}

if "situation_text" not in st.session_state:
    st.session_state.situation_text = ""

if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("Haqdaar")
st.write("### Know your rights. Get what you're due.")
st.write("A demo civic-rights assistant that helps you outline potential benefits, next steps, and a letter draft based on your situation.")

st.info(
    "Haqdaar provides general, cited information — it is not legal or financial advice. Always verify with the relevant official body."
)

st.session_state.situation_text = st.text_area(
    "Describe your situation, or paste an official document or notice…",
    value=st.session_state.situation_text,
    height=220,
    key="situation_text",
)

st.write("**Example presets:**")
cols = st.columns(3)
for idx, (label, text) in enumerate(PRESET_SCENARIOS.items()):
    if cols[idx].button(label):
        st.session_state.situation_text = text
        st.session_state.submitted = False
        st.rerun()

if st.button("Find what I'm entitled to"):
    if st.session_state.situation_text.strip():
        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted and st.session_state.situation_text.strip():
    st.markdown("---")
    st.subheader("Explanation")
    st.write("Coming next phase: grounded, cited results.")

    st.subheader("Rights & benefits you may qualify for")
    st.write("Coming next phase: grounded, cited results.")

    st.subheader("Action plan")
    st.write("Coming next phase: grounded, cited results.")

    st.subheader("Drafted letter")
    st.write("Coming next phase: grounded, cited results.")

    with st.expander("Reasoning trace"):
        st.markdown("""
- [ ] Understand
- [ ] Classify
- [ ] Ground
- [ ] Reason
- [ ] Plan
- [ ] Act
- [ ] Safeguard
""")
else:
    st.write("Enter a scenario or choose a preset and click the button to see the placeholder results.")
