import streamlit as st

st.set_page_config(page_title="Haqdaar", page_icon="🪪", layout="centered")

PRESET_SCENARIOS = {
    "Low-income student": "I am a university student struggling to pay tuition, rent, and basic living costs while studying full-time.",
    "Senior citizen pension": "I am a retired senior with limited savings and I want to know what pension or support programs I may be eligible for.",
    "Small farmer": "I farm a small plot and need help understanding income support, grants, and application steps for my rural family.",
}

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "show_results" not in st.session_state:
    st.session_state.show_results = False

st.title("Haqdaar")
st.write("### Know your rights. Get what you're due.")
st.write("A demo civic-rights assistant that helps you outline potential benefits, next steps, and a letter draft based on your situation.")

st.info(
    "Haqdaar provides general, cited information — it is not legal or financial advice. Always verify with the relevant official body."
)

with st.form(key="input_form"):
    st.session_state.user_input = st.text_area(
        "Describe your situation, or paste an official document or notice…",
        value=st.session_state.user_input,
        height=220,
        key="description_area",
    )

    cols = st.columns(3)
    for idx, (label, text) in enumerate(PRESET_SCENARIOS.items()):
        if cols[idx].button(label):
            st.session_state.user_input = text
            st.session_state.show_results = False

    submit = st.form_submit_button("Find what I'm entitled to")
    if submit:
        st.session_state.show_results = True

if st.session_state.show_results and st.session_state.user_input.strip():
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
