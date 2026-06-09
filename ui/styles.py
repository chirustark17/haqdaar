"""Fluent-inspired styling + HTML render helpers for the Haqdaar UI (presentation only).
Does NOT touch the pipeline, grounding, or any Azure/Foundry connectivity."""
import html
import streamlit as st

_CSS = """
<style>
:root{
  --hq-blue:#0078D4; --hq-blue-hover:#106EBE;
  --hq-ink:#242424; --hq-ink2:#424242; --hq-muted:#616161;
  --hq-line:#E1DFDD; --hq-surface:#FFFFFF; --hq-bg:#FAF9F8;
  --hq-radius:8px;
  --hq-shadow:0 1.6px 3.6px rgba(0,0,0,.10),0 .3px .9px rgba(0,0,0,.07);
  --hq-shadow-hover:0 3.2px 7.2px rgba(0,0,0,.13),0 .6px 1.8px rgba(0,0,0,.09);
  --hq-font:"Segoe UI","Segoe UI Web (West European)",-apple-system,BlinkMacSystemFont,Roboto,"Helvetica Neue",Arial,sans-serif;
}
/* Font: text elements only — never icon spans (prevents icon-ligature leak) */
.stApp,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *,
h1,h2,h3,h4,h5,h6,
.stButton button, .stDownloadButton button,
.stTextArea textarea, .stTextInput input, textarea, input, select,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[class^="hq-"], [class*=" hq-"]{font-family:var(--hq-font)!important;}

.stApp{background:var(--hq-bg);}
.block-container{max-width:880px;padding-top:2.4rem;padding-bottom:3rem;margin:0 auto;}
#MainMenu,footer{visibility:hidden;}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none;}
[data-testid="stHeader"]{background:transparent;}

.stButton>button{border-radius:6px!important;font-weight:600!important;border:1px solid var(--hq-line)!important;color:var(--hq-ink)!important;background:var(--hq-surface)!important;box-shadow:var(--hq-shadow)!important;transition:all .15s ease!important;}
.stButton>button:hover{box-shadow:var(--hq-shadow-hover)!important;transform:translateY(-1px);border-color:#C8C6C4!important;}
.stButton>button[kind="primary"]{background:var(--hq-blue)!important;border-color:var(--hq-blue)!important;color:#fff!important;}
.stButton>button[kind="primary"]:hover{background:var(--hq-blue-hover)!important;border-color:var(--hq-blue-hover)!important;}
.stDownloadButton>button{border-radius:6px!important;font-weight:600!important;border:1px solid var(--hq-blue)!important;color:var(--hq-blue)!important;background:var(--hq-surface)!important;}
.stDownloadButton>button:hover{background:#EFF6FC!important;}
.stTextArea textarea,.stTextInput input{border-radius:6px!important;border:1px solid var(--hq-line)!important;color:var(--hq-ink)!important;}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:var(--hq-blue)!important;box-shadow:0 0 0 1px var(--hq-blue)!important;}

/* Foundry-style hero */
.hq-hero{position:relative;overflow:hidden;border-radius:12px;padding:26px 28px;margin:0 0 16px;color:#fff;background:linear-gradient(125deg,#0a2a66 0%,#0078D4 48%,#5b2e9e 100%);box-shadow:0 6px 20px rgba(11,42,102,.28);}
.hq-hero::after{content:"";position:absolute;right:-60px;top:-70px;width:230px;height:230px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.18),rgba(255,255,255,0) 70%);}
.hq-hero-kicker{font-size:.74rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.82);margin-bottom:8px;position:relative;}
.hq-hero-title{font-size:2.1rem;font-weight:700;letter-spacing:-.02em;line-height:1.05;margin:0;position:relative;}
.hq-hero-tagline{font-size:1.05rem;font-weight:600;color:rgba(255,255,255,.96);margin:4px 0 0;position:relative;}
.hq-hero-sub{font-size:.92rem;color:rgba(255,255,255,.86);line-height:1.5;margin:10px 0 0;max-width:64ch;position:relative;}
.hq-hero-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;position:relative;}
.hq-hero-chip{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.30);color:#fff;border-radius:16px;padding:5px 12px;font-size:.78rem;font-weight:600;}
.hq-hero-chip::before{content:"";width:7px;height:7px;border-radius:50%;background:#7ee0c0;display:inline-block;}

/* Processing animation */
.hq-proc{background:var(--hq-surface);border:1px solid var(--hq-line);border-radius:var(--hq-radius);box-shadow:var(--hq-shadow);padding:18px 20px;margin:8px 0 4px;}
.hq-proc-head{display:flex;align-items:center;gap:10px;font-weight:700;color:var(--hq-ink);font-size:1rem;margin-bottom:14px;}
.hq-proc-spin{width:16px;height:16px;border:2.5px solid #C7E0F4;border-top-color:#0078D4;border-radius:50%;animation:hqspin .8s linear infinite;}
@keyframes hqspin{to{transform:rotate(360deg);}}
.hq-proc-steps{display:flex;flex-direction:column;gap:8px;}
.hq-proc-step{display:flex;align-items:center;gap:11px;font-size:.92rem;color:var(--hq-muted);border-left:3px solid transparent;padding-left:10px;border-radius:2px;animation:hqstep 4.9s ease-in-out infinite;}
.hq-proc-step .hq-proc-label{font-weight:600;color:var(--hq-ink2);}
.hq-proc-dot{flex:0 0 24px;height:24px;width:24px;border-radius:50%;background:#EFF6FC;border:2px solid #C7E0F4;color:#0078D4;font-size:.78rem;font-weight:700;display:flex;align-items:center;justify-content:center;}
@keyframes hqstep{0%,100%{opacity:.5;border-left-color:transparent;background:transparent;}45%,65%{opacity:1;border-left-color:#0078D4;background:#F3F9FD;}}
.hq-proc-step:nth-child(1){animation-delay:0s;}
.hq-proc-step:nth-child(2){animation-delay:.7s;}
.hq-proc-step:nth-child(3){animation-delay:1.4s;}
.hq-proc-step:nth-child(4){animation-delay:2.1s;}
.hq-proc-step:nth-child(5){animation-delay:2.8s;}
.hq-proc-step:nth-child(6){animation-delay:3.5s;}
.hq-proc-step:nth-child(7){animation-delay:4.2s;}

.hq-section-label{font-size:.82rem;font-weight:600;color:var(--hq-muted);text-transform:uppercase;letter-spacing:.04em;margin:14px 0 6px;}
.hq-h2{font-size:1.22rem;font-weight:700;color:var(--hq-ink);margin:20px 0 8px;letter-spacing:-.01em;}
.hq-divider{height:1px;background:var(--hq-line);margin:18px 0;}
.hq-muted{color:var(--hq-muted);font-size:.92rem;}
.hq-msgbar{border-radius:6px;padding:11px 14px 11px 13px;font-size:.9rem;margin:0 0 12px;border:1px solid var(--hq-line);border-left-width:4px;line-height:1.5;}
.hq-msg-info{background:#EFF6FC;border-color:#C7E0F4;border-left-color:#0078D4;color:#10456b;}
.hq-msg-warning{background:#FFF4CE;border-color:#F2E0A0;border-left-color:#D9A400;color:#5e4905;}
.hq-msg-error{background:#FDE7E9;border-color:#F1B9BE;border-left-color:#D13438;color:#7a1d24;}
.hq-summary,.hq-card{animation:hqfade .35s ease both;}
@keyframes hqfade{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:none;}}
.hq-summary{background:var(--hq-surface);border:1px solid var(--hq-line);border-left:4px solid var(--hq-blue);border-radius:var(--hq-radius);box-shadow:var(--hq-shadow);padding:14px 16px;color:var(--hq-ink2);font-size:.96rem;line-height:1.55;margin-bottom:6px;}
.hq-card{background:var(--hq-surface);border:1px solid var(--hq-line);border-radius:var(--hq-radius);box-shadow:var(--hq-shadow);padding:14px 16px;margin-bottom:12px;transition:box-shadow .15s ease,transform .15s ease;}
.hq-card:hover{box-shadow:var(--hq-shadow-hover);transform:translateY(-1px);}
.hq-card-title{font-weight:700;font-size:1.03rem;color:var(--hq-ink);margin:0 0 5px;}
.hq-card-body{color:var(--hq-ink2);font-size:.93rem;line-height:1.5;margin:0 0 10px;}
.hq-chip{display:inline-flex;align-items:center;gap:6px;background:#F3F2F1;color:var(--hq-muted);border:1px solid var(--hq-line);border-radius:12px;padding:3px 10px;font-size:.76rem;font-weight:500;}
.hq-steps{display:flex;flex-direction:column;gap:2px;}
.hq-step{display:flex;gap:12px;padding:7px 0;align-items:flex-start;}
.hq-step-num{flex:0 0 26px;height:26px;width:26px;border-radius:50%;background:var(--hq-blue);color:#fff;font-weight:600;font-size:.84rem;display:flex;align-items:center;justify-content:center;}
.hq-step-text{color:var(--hq-ink2);font-size:.94rem;line-height:1.5;padding-top:2px;}
.hq-sources{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:14px 0 4px;}
.hq-sources-label{font-size:.8rem;color:var(--hq-muted);font-weight:600;margin-right:2px;}
.hq-source-chip{display:inline-flex;align-items:center;background:#EFF6FC;color:#005A9E;border:1px solid #C7E0F4;border-radius:10px;padding:2px 9px;font-size:.76rem;font-weight:500;}
.hq-disclaimer{font-size:.8rem;color:var(--hq-muted);margin-top:8px;line-height:1.45;}
.hq-trace{display:flex;flex-direction:column;gap:2px;}
.hq-trace-row{display:flex;gap:10px;padding:6px 0;border-bottom:1px dashed #EDEBE9;align-items:baseline;}
.hq-trace-row:last-child{border-bottom:none;}
.hq-trace-step{flex:0 0 auto;font-weight:600;color:var(--hq-blue);font-size:.84rem;min-width:96px;}
.hq-trace-detail{color:var(--hq-ink2);font-size:.88rem;line-height:1.45;}
</style>
"""


def inject_fluent_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero_html() -> str:
    return (
        "<div class='hq-hero'>"
        "<div class='hq-hero-kicker'>Microsoft Agents League · Creative Apps</div>"
        "<div class='hq-hero-title'>Haqdaar</div>"
        "<div class='hq-hero-tagline'>Know your rights. Get what you&#39;re due.</div>"
        "<div class='hq-hero-sub'>A grounded civic-rights co-pilot: describe your situation or paste an official notice, and Haqdaar explains it, finds the benefits you may qualify for, plans your next steps, and drafts a ready-to-send letter — every claim cited.</div>"
        "<div class='hq-hero-chips'>"
        "<span class='hq-hero-chip'>Grounded by Foundry IQ</span>"
        "<span class='hq-hero-chip'>Cited answers</span>"
        "<span class='hq-hero-chip'>Action plan &amp; letter</span>"
        "</div></div>"
    )


def processing_html() -> str:
    steps = [
        ("Understand", "Reading your situation"),
        ("Classify", "Identifying the domain"),
        ("Ground", "Retrieving cited rules via Foundry IQ"),
        ("Reason", "Checking your eligibility"),
        ("Plan", "Building your action plan"),
        ("Act", "Drafting your letter"),
        ("Safeguard", "Verifying every claim is cited"),
    ]
    rows = []
    for i, (name, desc) in enumerate(steps, 1):
        rows.append(
            f"<div class='hq-proc-step'><div class='hq-proc-dot'>{i}</div>"
            f"<div><span class='hq-proc-label'>{name}</span> — {html.escape(desc)}</div></div>"
        )
    return (
        "<div class='hq-proc'><div class='hq-proc-head'>"
        "<div class='hq-proc-spin'></div>Haqdaar is reasoning through your case…</div>"
        f"<div class='hq-proc-steps'>{''.join(rows)}</div></div>"
    )


def message_bar_html(text: str, kind: str = "info") -> str:
    cls = {"info": "hq-msg-info", "warning": "hq-msg-warning", "error": "hq-msg-error"}.get(kind, "hq-msg-info")
    return f"<div class='hq-msgbar {cls}'>{html.escape(text)}</div>"


def summary_html(text: str) -> str:
    return f"<div class='hq-summary'>{html.escape(text)}</div>"


def rights_html(rights) -> str:
    cards = []
    for r in rights:
        name = html.escape(str(r.get("name", "Benefit")))
        why = r.get("why_eligible")
        cit = r.get("citation")
        body = f"<div class='hq-card-body'>{html.escape(str(why))}</div>" if why else ""
        chip = f"<span class='hq-chip'>{html.escape(str(cit))}</span>" if cit else ""
        cards.append(f"<div class='hq-card'><div class='hq-card-title'>{name}</div>{body}{chip}</div>")
    return "".join(cards)


def steps_html(steps) -> str:
    rows = [
        f"<div class='hq-step'><div class='hq-step-num'>{i}</div><div class='hq-step-text'>{html.escape(str(s))}</div></div>"
        for i, s in enumerate(steps, 1)
    ]
    return f"<div class='hq-steps'>{''.join(rows)}</div>"


def sources_html(sources) -> str:
    chips = "".join(f"<span class='hq-source-chip'>{html.escape(str(s))}</span>" for s in sources)
    return f"<div class='hq-sources'><span class='hq-sources-label'>Grounded in sources</span>{chips}</div>"


def trace_html(lines) -> str:
    rows = []
    for line in lines:
        line = str(line)
        if ":" in line:
            head, _, rest = line.partition(":")
            rows.append(
                f"<div class='hq-trace-row'><span class='hq-trace-step'>{html.escape(head.strip())}</span>"
                f"<span class='hq-trace-detail'>{html.escape(rest.strip())}</span></div>"
            )
        else:
            rows.append(f"<div class='hq-trace-row'><span class='hq-trace-detail'>{html.escape(line)}</span></div>")
    return f"<div class='hq-trace'>{''.join(rows)}</div>"
