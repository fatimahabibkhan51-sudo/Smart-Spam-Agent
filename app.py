import streamlit as st
import PyPDF2
import joblib
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart_Spam AI Agent", layout="centered", page_icon="🛡️")

# --- MODEL LOADING ---
@st.cache_resource
def load_resources():
    try:
        model = joblib.load("spam_model.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
        return model, vectorizer
    except Exception as e:
        st.error(f"Model files nahi mili: {e}")
        return None, None

model, vectorizer = load_resources()

# --- SMART PREDICTION LOGIC ---
def predict_spam(text):
    if not text.strip():
        return None
        
    text_lower = text.lower()
    # 1. Keywords Check (For Instant Catch)
    spam_keywords = ["win", "prize", "cash", "lottery", "free", "$", "reward", "winner", "urgent", "claim", "congratulations"]
    if any(word in text_lower for word in spam_keywords):
        return 1  # Mark as Spam
    
    # 2. AI Model Prediction
    if model and vectorizer:
        vectorized_text = vectorizer.transform([text])
        prediction = model.predict(vectorized_text)
        return int(prediction[0])
    return 0

# --- UI DESIGN ---
st.title("🛡️ Smart_Spam AI Agent")

st.sidebar.header("Settings")
input_type = st.sidebar.radio("Input Method:", ["Text Message", "PDF Document", "Phone Number"])

# --- 1. TEXT MESSAGE ANALYZER ---
if input_type == "Text Message":
    user_input = st.text_area("Message yahan likhein:", placeholder="e.g. You won a cash prize of $1000!")
    if st.button("Check Spam"):
        if user_input.strip():
            result = predict_spam(user_input)
            if result == 1:
                st.error("🚨 Result: SPAM DETECTED!")
            else:
                st.success("✅ Result: SAFE MESSAGE")
        else:
            st.warning("Pehle kuch text toh likhein!")

# --- 2. PDF ANALYZER (Improved) ---
elif input_type == "PDF Document":
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_file:
        if st.button("Analyze PDF"):
            with st.spinner("PDF Scan ho raha hai..."):
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    pages_text = []
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            pages_text.append(extracted)
                    
                    full_text = " ".join(pages_text)

                    if full_text.strip():
                        result = predict_spam(full_text)
                        if result == 1:
                            st.error("🚨 Result: Potential Spam in PDF!")
                            with st.expander("Detected Text"):
                                st.write(full_text)
                        else:
                            st.success("✅ Result: PDF Content is Safe")
                    else:
                        st.error("❌ PDF read nahi ho pa raha. Shayad ye image-based ya scanned PDF hai.")
                        st.info("Tip: Aisa PDF try karein jisme text select ho sake.")
                except Exception as e:
                    st.error(f"PDF Error: {e}")

# --- 3. PHONE NUMBER ANALYZER ---
elif input_type == "Phone Number":
    num = st.text_input("Phone Number enter karein (e.g. +923001234567):")
    if st.button("Check Number"):
        # Normalize number (remove spaces/dashes)
        clean_num = re.sub(r'\D', '', num)
        
        # Simple Blocklist / Pattern Check
        spam_numbers = ["923001234567", "03001234567", "123456789"]
        
        if not num.strip():
            st.warning("Please enter a number.")
        elif clean_num in spam_numbers or len(clean_num) < 10:
            st.error("🚨 Result: Reported / Blacklisted Number!")
        else:
            st.success("✅ Result: Number is Safe")