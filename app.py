"""Foresight: the on-call copilot that remembers every outage (Streamlit UI)."""
import streamlit as st

from data.demo_alerts import DEMO_ALERTS
from src import agent, memory

st.set_page_config(page_title="Foresight | Incident memory", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1250px;}
.mem {border-left: 3px solid #2f6f6a; padding: .45rem .8rem; margin: .4rem 0;
      background: rgba(47,111,106,.08); border-radius: 0 6px 6px 0; font-size: .88rem;}
.nomem {border-left: 3px solid #9a9a9a; padding: .45rem .8rem; background: rgba(120,120,120,.08);
        border-radius: 0 6px 6px 0; font-size: .88rem;}
</style>
""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("result", None)
ss.setdefault("alert", "")
ss.setdefault("live_count", 1)
ss.setdefault("saved", None)

# ---------- sidebar ----------
with st.sidebar:
    st.header("Memory")
    use_memory = st.toggle("Hindsight memory ON", value=True,
                           help="Turn off to see the same alert answered with no history.")
    deep = st.toggle("Deep pattern analysis (reflect)", value=False,
                     help="Slower. Uses Hindsight reflect to reason across incidents.")
    st.caption(f"Bank: `{memory.BANK_ID}`  \nServer: `{memory.BASE_URL}`")
    if st.button("Set up bank and mission"):
        st.info(memory.setup_bank())
    st.divider()
    st.caption("Seed history first: `python -m scripts.seed`")

st.title("Foresight")
st.write("Paste an alert. The agent recalls what your team already learned about outages like it.")

# ---------- input ----------
choice = st.selectbox("Load a demo alert", ["(write your own)"] + list(DEMO_ALERTS))
default = DEMO_ALERTS.get(choice, ss.alert)
alert = st.text_area("Alert or log excerpt", value=default, height=130, key=f"alert_{choice}")

if st.button("Analyze incident", type="primary", disabled=not alert.strip()):
    ss.saved = None
    with st.spinner("Recalling past incidents and reasoning..."):
        try:
            ss.result = agent.analyze(alert, use_memory=use_memory, deep=deep)
            ss.alert = alert
        except Exception as e:
            ss.result = None
            st.error(f"Could not analyze: {e}")

# ---------- output ----------
res = ss.result
if res:
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Recommendation")
        st.caption(("Memory ON" if res.used_memory else "Memory OFF (no history)") + f" · {res.seconds:.1f}s")
        st.markdown(res.answer)
        if res.pattern:
            with st.expander("Pattern analysis from Hindsight reflect"):
                st.markdown(res.pattern)
    with right:
        st.subheader("Memory panel")
        if not res.used_memory:
            st.markdown('<div class="nomem">Memory is off. The agent has no access to past incidents.</div>',
                        unsafe_allow_html=True)
        elif not res.memories:
            st.markdown('<div class="nomem">Hindsight returned nothing relevant. The agent was told to say so rather than guess.</div>',
                        unsafe_allow_html=True)
        else:
            st.caption(f"{len(res.memories)} memories recalled by Hindsight")
            for m in res.memories[:8]:
                st.markdown(f'<div class="mem">{m.text}</div>', unsafe_allow_html=True)

    # ---------- feedback loop ----------
    st.divider()
    st.subheader("Teach the agent")
    st.caption("What you enter here is retained in Hindsight and used on the next similar alert.")
    with st.form("feedback"):
        outcome = st.radio("Did the suggestion help?", ["Yes, it worked", "Partly", "No, it was wrong"], horizontal=True)
        root = st.text_input("Actual root cause")
        notes = st.text_area("What fixed it, and what did NOT work?", height=90)
        if st.form_submit_button("Save to memory"):
            try:
                inc = agent.retain_feedback(ss.alert, res.answer, outcome, root, notes, ss.live_count)
                ss.live_count += 1
                ss.saved = inc
            except Exception as e:
                st.error(f"Could not save: {e}")
    if ss.saved:
        st.success(f"Saved as {ss.saved}. Run the same alert again to see the difference.")
