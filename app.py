import datetime
import streamlit as st
import streamlit.components.v1 as components
from checkers.message import check_message
from checkers.url import check_url
from scoring import combine
from privacy import mask_text
from i18n import LANGS, reason, advice, label

try:
    from checkers.qr import decode_qr, analyse_qr   # Laptop C is still building this
except ImportError:
    decode_qr = analyse_qr = None

st.set_page_config(page_title="Real-Time Scam Shield", page_icon="🛡️")
COLORS = {"safe": "#1b8a3a", "suspicious": "#e0a100", "scam": "#c62828"}
SPEECH = {"en": "en-IN", "hi": "hi-IN", "pa": "pa-IN"}

SAMPLES = {
  "Fake KYC": "Dear customer your SBI account will be blocked today. Update KYC http://sbi-kyc.xyz",
  "Genuine OTP": "Your OTP for login is 482910. Do not share this with anyone.",
  "Collect trick": "Rs 500 collect request from Rahul. Approve and enter PIN to receive money",
  "Bank alert": "A/c XX1234 debited Rs 250.00 on 12-10. Avl bal Rs 3,400. -YourBank",
}

def verdict_from_score(s):
    return "safe" if s < 30 else "suspicious" if s < 60 else "scam"

def speak(text, lang):
    safe = text.replace("`", "").replace("\n", " ")
    components.html(f"""<button onclick="var u=new SpeechSynthesisUtterance(`{safe}`);
      u.lang='{SPEECH[lang]}'; speechSynthesis.cancel(); speechSynthesis.speak(u);"
      style="font-size:18px;padding:8px 16px">🔊</button>""", height=60)

def show_result(res, lang, masked):
    v = res.get("verdict") or verdict_from_score(res["score"])
    st.markdown(
        f"<div style='background:{COLORS[v]};color:white;padding:20px;border-radius:12px;"
        f"font-size:2em;font-weight:bold;text-align:center'>{label('verdict_'+v, lang)}"
        f" · {res['score']}/100</div>", unsafe_allow_html=True)
    lines = [reason(c, lang) for c in res["reasons"]][:4]
    for line in lines:
        st.write("• " + line)
    st.info(advice(v, lang))
    speak(" ".join(lines + [advice(v, lang)]), lang)
    st.link_button(label("report", lang), "https://cybercrime.gov.in")
    st.write(label("call_1930", lang))
    summary = (f"Verdict: {v.upper()} (score {res['score']})\nTime: {datetime.datetime.now():%Y-%m-%d %H:%M}\n"
               f"Message (masked): {masked}")
    st.code(summary, language=None)   # has a built-in copy icon

# ---------- sidebar ----------
lang = LANGS[st.sidebar.selectbox("Language / भाषा / ਭਾਸ਼ਾ", list(LANGS))]
if st.sidebar.checkbox(label("large_text", lang)):
    st.markdown("<style>html{font-size:22px}</style>", unsafe_allow_html=True)

st.title("🛡️ " + label("title", lang))
st.caption(label("privacy", lang))

tab_m, tab_l, tab_q = st.tabs([label("tab_message", lang), label("tab_link", lang), label("tab_qr", lang)])

with tab_m:
    cols = st.columns(len(SAMPLES))
    for col, (name, txt) in zip(cols, SAMPLES.items()):
        if col.button(name):
            st.session_state["msg"] = txt
    text = st.text_area(label("paste_here", lang), key="msg", height=150)
    if st.button(label("check", lang), key="check_msg") and text.strip():
        masked = mask_text(text[:5000])           # privacy first, limit huge pastes
        msg = check_message(masked)
        urls = [check_url(u) for u in msg["details"].get("links", [])]
        show_result(combine(msg, urls), lang, masked)

with tab_l:
    link = st.text_input("URL", key="link")
    if st.button(label("check", lang), key="check_link") and link.strip():
        res = check_url(link.strip())
        res["verdict"] = verdict_from_score(res["score"])
        show_result(res, lang, link.strip())

with tab_q:
    ctx_options = {"Paying a shop": "shop", "Receiving a refund": "refund",
                   "Receiving a prize / job payment": "prize", "Receiving money": "receive"}
    ctx = ctx_options[st.selectbox("What did the sender say this QR is for?", list(ctx_options))]
    img = st.file_uploader("QR image", type=["png", "jpg", "jpeg"])
    if img and decode_qr:
        data = decode_qr(img.getvalue())
        if data is None:
            st.warning("Could not read this QR. Try a clearer image.")
        else:
            res = analyse_qr(data, ctx)
            res["verdict"] = verdict_from_score(res["score"])
            d = res["details"]
            if d.get("pa"):
                st.warning(f"You are about to PAY ₹{d.get('am','?')} to {d.get('pn','?')} ({d['pa']})")
            show_result(res, lang, data)
    elif img:
        st.info("QR checker not connected yet.")

st.caption(label("disclaimer", lang))