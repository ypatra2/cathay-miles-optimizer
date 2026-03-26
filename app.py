import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import os

from optimizer import CATEGORIES, get_recommendations
from gemini_parser import parse_transaction
from speech_input import speech_to_text_button

# Force reload of environment variables on each run to capture .env updates securely
load_dotenv(override=True)
api_key_status = os.getenv("GEMINI_API_KEY")
# Also check Streamlit secrets (for cloud deployment)
try:
    cloud_key = st.secrets.get("GEMINI_API_KEY", None)
    if cloud_key:
        api_key_status = cloud_key
except Exception:
    pass

# Initialize Session State Variables to prevent unnecessary API calls
if 'extracted_vendor' not in st.session_state:
    st.session_state.extracted_vendor = "Unknown (Manual Input)"
if 'extracted_amount' not in st.session_state:
    st.session_state.extracted_amount = 0.0
if 'extracted_category' not in st.session_state:
    st.session_state.extracted_category = "Shopping (In-Store General)"
if 'image_analyzed' not in st.session_state:
    st.session_state.image_analyzed = False
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'final_amount' not in st.session_state:
    st.session_state.final_amount = 0.0
if 'final_category' not in st.session_state:
    st.session_state.final_category = "Shopping (In-Store General)"
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'user_context' not in st.session_state:
    st.session_state.user_context = ""
if 'context_key' not in st.session_state:
    st.session_state.context_key = 0

# Configure the page layout
st.set_page_config(
    page_title="Cathay Miles Optimizer v3.2",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS for premium dark mode aesthetics
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #050914 0%, #0a1120 100%);
    }
    h1 {
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    /* Holographic Display Container */
    .hologram-container {
        border: 2px solid rgba(0, 242, 254, 0.4);
        padding: 30px;
        border-radius: 20px;
        background: rgba(0, 242, 254, 0.05);
        box-shadow: 0 0 40px rgba(0, 242, 254, 0.15), inset 0 0 20px rgba(0, 242, 254, 0.1);
        position: relative;
        margin-bottom: 30px;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    .hologram-container::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: conic-gradient(transparent, rgba(0, 242, 254, 0.15), transparent 30%);
        animation: rotate 6s linear infinite;
        opacity: 0.5;
        pointer-events: none;
        z-index: -1;
    }
    @keyframes rotate { 100% { transform: rotate(1turn); } }
    
    /* CSS Credit Cards */
    .cc-visual {
        width: 100%; max-width: 340px; height: 200px;
        border-radius: 16px;
        padding: 24px;
        display: flex; flex-direction: column; justify-content: space-between;
        position: relative;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        margin: 0 auto 20px auto;
        color: white;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .cc-visual::after {
        content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 40%);
        pointer-events: none;
    }
    .chip {
        width: 45px; height: 35px; border-radius: 6px;
        background: linear-gradient(135deg, #eccc68, #ffa502);
        box-shadow: inset 0 0 5px rgba(0,0,0,0.5);
        position: relative;
    }
    .chip::after {
        content: ''; position: absolute; top: 10px; bottom: 10px; left: 0; right: 0;
        border-top: 1px solid rgba(0,0,0,0.2); border-bottom: 1px solid rgba(0,0,0,0.2);
    }
    .cc-logo { font-size: 26px; font-weight: 900; font-style: italic; text-align: right; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .cc-mc { 
        width: 50px; height: 30px; position: relative; margin-left: auto;
    }
    .cc-mc::before, .cc-mc::after {
        content: ''; position: absolute; width: 30px; height: 30px; border-radius: 50%; opacity: 0.9;
    }
    .cc-mc::before { background: #ff5f00; left: 0; }
    .cc-mc::after { background: #eb001b; right: 20px; }
    
    /* Card specific backgrounds matching the AI ad vibe */
    .bg-sc { background: linear-gradient(135deg, #bfa85c 0%, #006b5f 100%); }
    .bg-em { background: linear-gradient(135deg, #111 0%, #2b323c 100%); border: 1px solid #00f2fe; }
    .bg-red { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
    .bg-sig { background: linear-gradient(135deg, #d4af37 0%, #f1c40f 100%); color: #111; }
    
    .miles-glow {
        text-align: center; font-size: 3.5rem; font-weight: 900;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 40px #00f2fe;
        margin: 10px 0; line-height: 1;
    }
    
    /* Alternative Cards */
    .other-card {
        background: rgba(10, 17, 32, 0.8);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .other-card:hover {
        border-color: rgba(0, 242, 254, 0.6);
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
    }
    .rate-text {
        font-size: 0.9rem; color: #cbd5e1;
        background: rgba(255, 255, 255, 0.1);
        padding: 4px 10px; border-radius: 4px;
        display: inline-block; margin-bottom: 8px;
    }
    .notes-text { font-size: 0.85rem; color: #94a3b8; font-style: italic; }
    .badge-winner {
        background: #00f2fe; color: #0a1120;
        font-size: 0.8rem; font-weight: 800;
        padding: 6px 12px; border-radius: 20px;
        text-transform: uppercase; letter-spacing: 1px;
        box-shadow: 0 0 10px #00f2fe;
        display: inline-block; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Cathay Miles ✨ AI Optimizer")
st.markdown("<div class='subtitle'>Upload screenshots, type or speak your transaction details, and discover which card maximizes your Asia Miles!</div>", unsafe_allow_html=True)

if not api_key_status or api_key_status == "your_api_key_here":
    st.error("⚠️ The **GEMINI_API_KEY** is missing or default. Please populate the `.env` file or Streamlit secrets.")
    st.info("You can still use the manual override below while the key is missing.")

# Split UI into two dynamic columns
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # --- AI Upload Section ---
    st.subheader("1. AI Transaction Parsing")

    # Multi-image uploader
    uploaded_files = st.file_uploader(
        "Upload receipts, checkout screens, or bills (multiple allowed)...",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

    # Show image previews in a grid
    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 3))
        for i, f in enumerate(uploaded_files):
            with cols[i % 3]:
                img = Image.open(f)
                st.image(img, caption=f.name, use_container_width=True)

    # Text context input
    st.markdown("<div class='context-label'>💬 Add context about your transaction (optional):</div>", unsafe_allow_html=True)

    # Text area for typed/dictated context
    user_context = st.text_area(
        "Describe the transaction (e.g., 'Uber ride to airport, HK$150')",
        value=st.session_state.user_context,
        height=80,
        key=f"context_{st.session_state.context_key}",
        label_visibility="collapsed"
    )
    st.session_state.user_context = user_context

    # Speech-to-text button (inserts directly into text area above via DOM)
    speech_to_text_button(reset_key=st.session_state.context_key)

    # Action buttons
    col_analyze, col_clear = st.columns(2)
    with col_analyze:
        analyze_disabled = not uploaded_files and not user_context.strip()
        if st.button("✨ Analyze with Gemini AI", use_container_width=True, disabled=analyze_disabled):
            # Collect all images
            images = []
            if uploaded_files:
                for f in uploaded_files:
                    f.seek(0)  # Reset file position for re-read
                    images.append(Image.open(f))

            with st.spinner(f"Analyzing {len(images)} image(s) + context with Gemini..."):
                extraction = parse_transaction(images, user_context)

            if "error" in extraction:
                st.error(f"Analysis Failed: {extraction['error']}")
            else:
                st.success("✅ Extraction Complete!")
                st.session_state.extracted_vendor = extraction.get("vendor", "Unknown")
                st.session_state.extracted_amount = float(extraction.get("amount", 0.0))
                st.session_state.extracted_category = extraction.get("category", "Shopping (In-Store General)")
                st.session_state.image_analyzed = True

    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.image_analyzed = False
            st.session_state.show_results = False
            st.session_state.extracted_amount = 0.0
            st.session_state.extracted_category = "Shopping (In-Store General)"
            st.session_state.extracted_vendor = "Unknown (Manual Input)"
            st.session_state.user_context = ""
            st.session_state._last_speech = ""
            st.session_state.uploade