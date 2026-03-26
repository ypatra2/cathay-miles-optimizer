import streamlit as st
from PIL import Image
import dotenv
import os
import db_manager
import pandas as pd
import numpy as np
if not hasattr(np, 'bool8'):
    np.bool8 = np.bool_
import plotly.express as px

# Init DB
db_manager.init_db()

from optimizer import CATEGORIES, get_recommendations
from gemini_parser import parse_transaction
from speech_input import speech_to_text_button

# --- 1. SETUP & CONFIG ---
st.set_page_config(
    page_title="Cathay Miles Optimizer v4.0",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

dotenv.load_dotenv(override=True)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
api_key_status = os.getenv("GEMINI_API_KEY")
try:
    if not api_key_status and st.secrets.get("GEMINI_API_KEY"):
        api_key_status = "Loaded from Secrets"
except:
    pass

# No manual class instantiation needed for top-level functions

# --- 2. CSS STYLING ---
futuristic_css = """
<style>
/* Base Theme overrides for futuristic look */
body { background-color: #060b13; color: #e2e8f0; font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 10% 20%, #060b13 0%, #0a1120 100%); }

/* Glassmorphism Containers */
.hologram-container, .glass-panel {
    background: rgba(10, 17, 32, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 0 30px rgba(0, 242, 254, 0.1), inset 0 0 20px rgba(0, 242, 254, 0.05);
    position: relative;
    overflow: hidden;
    margin-bottom: 25px;
}
.hologram-container::before {
    content: ''; position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(transparent, rgba(0, 242, 254, 0.15), transparent 30%);
    animation: rotate 6s linear infinite;
    opacity: 0.5; pointer-events: none; z-index: -1;
}
@keyframes rotate { 100% { transform: rotate(1turn); } }

/* CSS Image Cards */
.card-img-wrapper { text-align: center; margin: 25px auto; padding: 5px; }
.card-img {
    max-width: 100%; max-height: 220px; border-radius: 14px;
    box-shadow: 0 15px 30px rgba(0,0,0,0.7), 0 0 25px rgba(0, 242, 254, 0.4);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
}
.card-img:hover {
    transform: scale(1.04) translateY(-8px);
    box-shadow: 0 25px 45px rgba(0,0,0,0.9), 0 0 40px rgba(0, 242, 254, 0.7);
}

.miles-glow {
    text-align: center; font-size: 3.5rem; font-weight: 900;
    color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 40px #00f2fe;
    margin: 10px 0; line-height: 1;
}

/* Alternative Cards */
.other-card {
    background: rgba(10, 17, 32, 0.8);
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 12px; padding: 16px; margin-bottom: 12px;
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
"""
st.markdown(futuristic_css, unsafe_allow_html=True)


# --- 3. SESSION STATE ---
if 'parsed_transactions' not in st.session_state:
    st.session_state.parsed_transactions = []
if 'image_analyzed' not in st.session_state:
    st.session_state.image_analyzed = False
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'extracted_amount' not in st.session_state:
    st.session_state.extracted_amount = 0.0
if 'extracted_category' not in st.session_state:
    st.session_state.extracted_category = "Shopping (In-Store General)"
if 'extracted_vendor' not in st.session_state:
    st.session_state.extracted_vendor = "Unknown (Manual Input)"
if 'final_category' not in st.session_state:
    st.session_state.final_category = ""
if 'final_amount' not in st.session_state:
    st.session_state.final_amount = 0.0
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'user_context' not in st.session_state:
    st.session_state.user_context = ""
if 'context_key' not in st.session_state:
    st.session_state.context_key = 0
if 'transaction_logged' not in st.session_state:
    st.session_state.transaction_logged = False
if 'log_success' not in st.session_state:
    st.session_state.log_success = False
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'show_delete_confirm' not in st.session_state:
    st.session_state.show_delete_confirm = False

def render_dashboard():
    st.title("📊 Analytics & Budget Dashboard")
    
    df = db_manager.fetch_all_transactions()
    if df.empty:
        st.info("No transactions logged yet. Use the Optimizer Engine to calculate miles!")
        return

    # KPIs
    total_miles = df['miles_earned'].sum()
    total_spend = df['amount'].sum()
    avg_rate = total_spend / total_miles if total_miles > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>Total Miles</h3><h2 style='color:#00f2fe'>{total_miles:,}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>Total Spend</h3><h2>HK${total_spend:,.2f}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>Effective Rate</h3><h2>HK${avg_rate:.2f}/mi</h2></div>", unsafe_allow_html=True)

    # Charts
    st.markdown("### Spending Patterns")
    c1, c2 = st.columns(2)
    with c1:
        cat_df = df.groupby('category')['amount'].sum().reset_index()
        fig_donut = px.pie(cat_df, values='amount', names='category', hole=0.5, template="plotly_dark")
        fig_donut.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        card_df = df.groupby('recommended_card')['amount'].sum().reset_index()
        fig_bar = px.bar(card_df, x='recommended_card', y='amount', color_discrete_sequence=['#00f2fe'], template="plotly_dark")
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Amount (HK$)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("### Miles Velocity (Trend)")
    time_df = df.sort_values('timestamp')
    time_df['cumulative_miles'] = time_df['miles_earned'].cumsum()
    fig_line = px.line(time_df, x='timestamp', y='cumulative_miles', markers=True, template="plotly_dark")
    fig_line.update_traces(line_color="#00f2fe", fill='tozeroy', fillcolor='rgba(0,242,254,0.1)')
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("### Transaction Ledger")
    
    # Manage Transactions (Deletion)
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Review or edit your transaction history below.</p>", unsafe_allow_html=True)
    
    for _, row in df.iterrows():
        with st.expander(f"🗓️ {row['timestamp'].strftime('%Y-%m-%d %H:%M')} | {row['vendor']} | HK${row['amount']:,.2f}"):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Miles Earned:** {row['miles_earned']}")
                st.write(f"**Card Used:** {row['recommended_card']}")
            with c2:
                if st.button("🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                    db_manager.delete_transaction(row['id'])
                    st.toast(f"Transaction with {row['vendor']} deleted.")
                    st.rerun()

    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    if not st.session_state.show_delete_confirm:
        if st.button("🚨 NUKE ENTIRE DATABASE", type="secondary", use_container_width=True):
            st.session_state.show_delete_confirm = True
            st.rerun()
    else:
        st.warning("ARE YOU ABSOLUTELY SURE? This will permanently delete ALL transaction history.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("🔥 YES, DELETE EVERYTHING", type="primary", use_container_width=True):
                db_manager.delete_all_transactions()
                st.session_state.show_delete_confirm = False
                st.success("Database purged.")
                st.rerun()
        with col_no:
            if st.button("❌ CANCEL", use_container_width=True):
                st.session_state.show_delete_confirm = False
                st.rerun()


def render_optimizer():
    st.title("Cathay Miles ✨ AI Optimizer")
    st.markdown("<div class='subtitle' style='color:#94a3b8; margin-bottom:20px;'>Upload screenshots, type or speak your transaction details, and discover which card maximizes your Asia Miles!</div>", unsafe_allow_html=True)

    if not api_key_status or api_key_status == "your_api_key_here":
        st.error("⚠️ The **GEMINI_API_KEY** is missing or default. Please populate the `.env` file or Streamlit secrets.")
        st.info("You can still use the manual override below while the key is missing.")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("1. AI Transaction Parsing")
        uploaded_files = st.file_uploader(
            "Upload receipts, checkout screens, or bills (multiple allowed)...",
            type=["png", "jpg", "jpeg"],
           