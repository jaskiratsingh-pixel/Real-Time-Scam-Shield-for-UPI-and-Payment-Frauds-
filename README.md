# Real-Time-Scam-Shield-for-UPI-and-Payment-Frauds-
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install streamlit scikit-learn pandas opencv-python-headless pillow tldextract python-whois requests "qrcode[pil]" pytest joblib
python -c "import streamlit, sklearn, cv2, PIL, pandas, tldextract; print('ALL GOOD')"
