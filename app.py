import streamlit as st
from main import analyze_message, analyze_url, analyze_qr

st.set_page_config(
    page_title="Real-Time Scam Shield",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ Real-Time Scam Shield")
st.caption("UPI and Payment Fraud Detection System")

st.divider()

option = st.sidebar.selectbox(
    "Choose Detection Mode",
    ["Message Checker", "URL Checker", "QR Scanner"]
)


def show_result(result):
    score = result["score"]
    verdict = result["verdict"].upper()

    st.subheader("Analysis Result")

    st.metric("Risk Score", f"{score}/100")

    if verdict == "SCAM":
        st.error("🚨 SCAM DETECTED")
    elif verdict == "SUSPICIOUS":
        st.warning("⚠️ SUSPICIOUS")
    elif verdict == "SAFE":
        st.success("✅ SAFE")
    else:
        st.info("Result unavailable")

    st.write("**Detection reasons:**")

    if result["reasons"]:
        for reason in result["reasons"]:
            st.write(f"- {reason}")
    else:
        st.write("No suspicious patterns detected.")


if option == "Message Checker":
    st.header("Check a Message")

    message = st.text_area(
        "Paste your SMS or WhatsApp message:"
    )

    if st.button("Analyze Message"):
        if message.strip():
            with st.spinner("Analyzing message..."):
                result = analyze_message(message)
            show_result(result)
        else:
            st.warning("Please enter a message.")


elif option == "URL Checker":
    st.header("Check a URL")

    url = st.text_input("Enter website URL:")

    if st.button("Analyze URL"):
        if url.strip():
            with st.spinner("Checking URL..."):
                result = analyze_url(url)
            show_result(result)
        else:
            st.warning("Please enter a URL.")


elif option == "QR Scanner":
    st.header("Scan a QR Code")

    uploaded_file = st.file_uploader(
        "Upload a QR code image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        if st.button("Analyze QR Code"):
            import tempfile
            import os

            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                with st.spinner("Analyzing QR code..."):
                    result = analyze_qr(temp_path)

                show_result(result)

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)


st.divider()

st.caption(
    "Scam Shield | Educational prototype | "
    "Always verify payment requests independently."
)