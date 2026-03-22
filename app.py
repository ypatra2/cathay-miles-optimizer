import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import os

from optimizer import CATEGORIES, get_recommendations
from gemini_parser import parse_transaction_image

# Force reload of environment variables on each run to capture .env updates securely
load_dotenv(override=True)
api_key_status = os.getenv("GEMINI_API_KEY")

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
if 'is_partner_promo' not in st.session_state:
    st.session_state.is_partner_promo = False
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# Configure the page layout (Wide handles desktop split-screen perfectly, collapses safely on Mobile)
st.set_page_config(
    page_title="Cathay Miles Optimizer v2.0",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS for premium dark mode aesthetics
st.markdown("""
    <style>
    /* Global App Styling */
    .stApp {
        background: linear-gradient(180deg, #0a0c10 0%, #0f1115 100%);
    }
    
    /* Header styling */
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

    /* Cards Styling */
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
    
    /* Typography inside cards */
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

    /* Badges */
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

    /* Mobile adjustments: Adjust gaps and font sizes implicitly */
    @media (max-width: 600px) {
        .miles-highlight { font-size: 2.2rem; }
    }
    </style>
""", unsafe_allow_html=True)


st.title("Cathay Miles ✨ AI Optimizer")
st.markdown("<div class='subtitle'>Upload a screenshot of your transaction and instantly discover which credit card maximizes your Asia Miles!</div>", unsafe_allow_html=True)

if not api_key_status or api_key_status == "your_api_key_here":
    st.error("⚠️ The **GEMINI_API_KEY** is missing or default. Please populate the `.env` file in the project folder with your actual key to enable visual parsing.")
    st.info("You can still use the manual override below while the key is missing.")

# Split UI into two dynamic columns for Wide Desktop / Stacking Mobile layouts
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # --- AI Upload Section ---
    st.subheader("1. AI Screenshot Parsing")
    uploaded_file = st.file_uploader(
        "Upload a receipt, checkout screen, or bill...", 
        type=["png", "jpg", "jpeg"], 
        key=f"uploader_{st.session_state.uploader_key}"
    )

    # If user uploads imag