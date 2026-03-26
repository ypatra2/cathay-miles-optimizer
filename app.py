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
        background: linear-gradient(180deg, #0a0c10 0%, #0f1115 100%);
    }
    h1 {
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #00b2a9, #4db8ff);
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
    .best-card {
        background: linear-gradient(135deg, rgba(0, 178, 169, 0.1) 0%, rgba(0, 178, 169, 0.05) 100%);
        border: 1px solid rgba(0, 178, 169, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .best-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 178, 169, 0.2);
    }
    .other-card {
        background: rgba(28, 31, 38, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .miles-highlight {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00b2a9;
        line-height: 1;
        margin-bottom: 4px;
    }
    .rate-text {
        font-size: 0.9rem;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .notes-text {
        font-size: 0.85rem;
        color: #94a3b8;
        font-style: italic;
    }
    .badge-winner {
        background: #00b2a9;
        color: #0f1115;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .context-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
    @media (max-width: 600px) {
        .miles-highlight { font-size: 2.2rem; }
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
        key="context_input",
        label_visibility="collapsed"
    )
    st.session_state.user_context = user_context

    # Speech-to-text button (inserts directly into text area above via DOM)
    speech_to_text_button()

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
            st.session_state.uploader_key += 1
            st.rerun()

    # Display successful extraction stats
    if st.session_state.image_analyzed:
        st.markdown("##### Extracted Data")
        col_v, col_a = st.columns(2)
        col_v.metric("Vendor", st.session_state.extracted_vendor)
        col_a.metric("Amount", f"HK$ {st.session_state.extracted_amount:.2f}")
        st.metric("Mapped Category", st.session_state.extracted_category)


with right_col:
    # --- Manual Override Form ---
    st.subheader("2. Final Transaction Details")
    with st.form(key="transaction_form"):
        cat_search = st.session_state.extracted_category
        cat_idx = CATEGORIES.index(cat_search) if cat_search in CATEGORIES else 0
        form_category = st.selectbox("Spending Category (Can override AI)", CATEGORIES, index=cat_idx)

        default_amt = st.session_state.extracted_amount if st.session_state.extracted_amount > 0 else 100.0
        form_amount = st.number_input("Amount (HK$)", min_value=0.0, value=default_amt, step=10.0, format="%.2f")

        submit_calculation = st.form_submit_button("💳 Calculate Best Card", use_container_width=True)

        if submit_calculation:
            st.session_state.final_category = form_category
            st.session_state.final_amount = form_amount
            st.session_state.show_results = True

    # --- Execution & Results ---
    if st.session_state.show_results and st.session_state.final_amount > 0:
        st.markdown("---")
        results = get_recommendations(
            st.session_state.final_category,
            st.session_state.final_amount
        )

        st.subheader("Card Recommendations")

        # Render Best Card
        best = results[0]
        best_html = f"""
        <div class="best-card">
            <div class="card-title">
                🏆 {best['card']}
                <span class="badge-winner">Best Choice</span>
            </div>
            <div class="miles-highlight">+{best['miles']} Miles</div>
            <div class="rate-text">Effective Rate: HK${best['rate']} = 1 Mile</div>
            <div class="notes-text">💡 {best['notes']}</div>
        </div>
        """
        st.markdown(best_html, unsafe_allow_html=True)

        # Render alternative cards
        if len(results) > 1:
            st.markdown("#### Alternative Cards")
            for res in results[1:]:
                other_html = f"""
                <div class="other-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #e2e8f0; font-size: 1rem;">{res['card']}</div>
                            <div class="notes-text">{res['notes']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #4db8ff; font-weight: 700; font-size: 1.2rem;">+{res['miles']}</div>
                            <div style="font-size: 0.75rem; color: #64748b;">HK${res['rate']} = 1 Mile</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(other_html, unsafe_allow_html=True)
