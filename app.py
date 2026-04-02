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
from agents.refresh_metadata import get_last_refresh, get_refresh_history

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
        st.subheader("✨ AI Transaction Parsing")
        uploaded_files = st.file_uploader(
            "Upload receipts, checkout screens, or bills (multiple allowed)...",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if uploaded_files:
            st.session_state.uploaded_images = [Image.open(f) for f in uploaded_files]

        if st.session_state.uploaded_images:
            cols = st.columns(min(len(st.session_state.uploaded_images), 3))
            for i, img in enumerate(st.session_state.uploaded_images):
                with cols[i % 3]:
                    st.image(img, use_container_width=True)

        st.markdown("<div style='margin-top:15px; font-weight:600;'>💬 Add context about your transaction (optional):</div>", unsafe_allow_html=True)
        user_context = st.text_area(
            "Describe the transaction (e.g., 'Uber ride to airport, HK$150')",
            value=st.session_state.user_context,
            height=80,
            key=f"context_{st.session_state.context_key}",
            label_visibility="collapsed"
        )
        st.session_state.user_context = user_context

        speech_to_text_button(reset_key=st.session_state.context_key)

        col_analyze, col_clear = st.columns(2)
        with col_analyze:
            analyze_disabled = not uploaded_files and not user_context.strip()
            if st.button("✨ Analyze with Gemini AI", use_container_width=True, disabled=analyze_disabled):
                images = []
                if uploaded_files:
                    for f in uploaded_files:
                        f.seek(0)
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
                st.session_state.uploaded_images = []
                st.session_state._last_speech = ""
                st.session_state.uploader_key += 1
                st.session_state.context_key += 1
                st.session_state.transaction_logged = False
                st.session_state.log_success = False
                st.rerun()

        if st.session_state.image_analyzed:
            st.markdown("##### Extracted Data")
            col_v, col_a = st.columns(2)
            col_v.metric("Vendor", st.session_state.extracted_vendor)
            col_a.metric("Amount", f"HK$ {st.session_state.extracted_amount:.2f}")
            st.metric("Mapped Category", st.session_state.extracted_category)

    with right_col:
        st.subheader("💳 Final Transaction Details")
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
                st.session_state.transaction_logged = False
                st.session_state.log_success = False

        if st.session_state.show_results and st.session_state.final_amount > 0:
            st.markdown("---")
            results = get_recommendations(
                st.session_state.final_category,
                st.session_state.final_amount
            )
            st.subheader("Card Recommendations")

            import base64
            import os
            def get_local_b64(path):
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
                return "https://www.cathaypacific.com/content/dam/focal-point/digital-library/hk/sc-cx-mastercard/sc-card-face-w.renditionimage.1600.1600.jpg"

            def get_card_vibe(card_name):
                if "SC Cathay" in card_name: return get_local_b64("assets/sc_cathay_cropped.png")
                if "EveryMile" in card_name: return "https://photos-hk.cdn-moneysmart.com/credit_cards/uploads/products/images/image_url_2023-03-03_hsbc-everymile-card_11zon.png"
                if "Red" in card_name: return "https://www.hsbc.com.hk/content/dam/hsbc/hk/images/mass/credit-cards/tile-16-9/9358-hsbc-red-credit-card-1280x828.jpg"
                if "Signature" in card_name: return "https://www.hsbc.com.hk/content/dam/hsbc/hk/images/mass/credit-cards/tile-16-9/9358-hsbc-visa-signature-card-1280x828.jpg"
                return get_local_b64("assets/sc_cathay_cropped.png")

            best = results[0]
            img_url = get_card_vibe(best['card'])
            
            # Log to Database removed from automatic flow
            # db_manager.log_transaction(st.session_state.extracted_vendor, st.session_state.final_category, st.session_state.final_amount, best['card'], best['miles'])

            best_html = f"""
<div class="hologram-container">
<div style="text-align: center;">
<span class="badge-winner">AI Optimal Recommendation</span>
</div>
<div class="card-img-wrapper">
<img src="{img_url}" class="card-img" alt="{best['card']}">
</div>
<div class="miles-glow">+{best['miles']} MILES</div>
<div style="text-align: center;">
<div class="rate-text">Effective Rate: HK${best['rate']} = 1 Mile</div>
<div class="notes-text" style="color: #00f2fe; margin-top: 5px;">🤖 {best['notes']}</div>
</div>
</div>
"""
            st.markdown(best_html, unsafe_allow_html=True)

            # --- PAY NOW ACTION ---
            if not st.session_state.transaction_logged:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💸 PAY NOW & LOG TRANSACTION", use_container_width=True, type="primary"):
                    db_manager.log_transaction(
                        st.session_state.extracted_vendor, 
                        st.session_state.final_category, 
                        st.session_state.final_amount, 
                        best['card'], 
                        best['miles']
                    )
                    st.session_state.transaction_logged = True
                    st.session_state.log_success = True
                    st.rerun()
            
            if st.session_state.log_success:
                st.success(f"Successfully logged {best['miles']} miles to your Dashboard ledger!")

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
<div style="color: #00f2fe; font-weight: 700; font-size: 1.2rem; text-shadow: 0 0 10px rgba(0,242,254,0.4);">+{res['miles']}</div>
<div style="font-size: 0.75rem; color: #94a3b8;">HK${res['rate']} = 1 Mile</div>
</div>
</div>
</div>
"""
                    st.markdown(other_html, unsafe_allow_html=True)

# --- ENGINE REFRESH PAGE ---
def render_engine_refresh():
    """Renders the agentic engine refresh page."""
    st.markdown("<div class='hologram-container'><h2 style='color:#00f2fe;'>🤖 Agentic Engine Refresh</h2><p style='color:#94a3b8;'>Deep Research Agent + Python Dev Agent pipeline powered by LangGraph</p></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### How It Works")
        st.markdown("""
        1. 🔬 **Deep Research Agent** scans bank websites for the latest earn rates, caps, promos & MCC codes
        2. 🧑‍💻 **Python Dev Agent** generates an updated `optimizer.py` based on verified findings
        3. 🌿 **Git Branch + PR** is created automatically for your review on GitHub
        4. ✅ **You merge** the PR on GitHub to apply the changes
        """)

    with col2:
        # Show last refresh info
        last_refresh = get_last_refresh()
        if last_refresh:
            refreshed_at = last_refresh.get("refreshed_at", "Unknown")
            status = last_refresh.get("status", "unknown")
            source = last_refresh.get("trigger_source", "unknown")
            status_emoji = {"pr_created": "📋", "merged": "✅", "rejected": "❌", "failed": "⚠️"}.get(status, "❓")
            st.markdown(f"""
            <div class='glass-panel' style='text-align:center;'>
                <p style='color:#94a3b8; margin-bottom:5px;'>Last Refresh</p>
                <p style='color:#e2e8f0; font-size:1.1rem;'>{refreshed_at[:10] if len(refreshed_at) > 10 else refreshed_at}</p>
                <p style='font-size:0.9rem;'>{status_emoji} {status.upper()} via {source}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='glass-panel' style='text-align:center;'><p style='color:#94a3b8;'>No refresh history found</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Refresh trigger button
    if st.button("🔬 Refresh Engine Now", type="primary", use_container_width=True):
        st.session_state["refresh_running"] = True

    if st.session_state.get("refresh_running", False):
        progress_container = st.empty()
        status_text = st.empty()
        result_container = st.container()

        with st.spinner("🔬 Running Agentic Pipeline... This takes 5-10 minutes."):
            from agents.runner import run_refresh_pipeline

            def streamlit_progress(step, detail):
                status_text.markdown(f"**{detail}**")

            result = run_refresh_pipeline(
                trigger_source="manual",
                progress_callback=streamlit_progress,
            )

        st.session_state["refresh_running"] = False
        st.session_state["last_refresh_result"] = result

    # Show results
    result = st.session_state.get("last_refresh_result")
    if result:
        if result["success"]:
            st.success("✅ Pipeline completed successfully!")

            if result.get("pr_url"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"🔗 **[View PR on GitHub]({result['pr_url']})**")
                with col_b:
                    if result.get("branch_name"):
                        st.markdown(f"🌿 Branch: `{result['branch_name']}`")

            if result.get("pr_note"):
                st.info(f"ℹ️ {result['pr_note']}")

            if result.get("patch_summary"):
                with st.expander("📝 Patch Summary", expanded=True):
                    st.markdown(result["patch_summary"])

            if result.get("research_report"):
                with st.expander("🔬 Full Deep Research Report"):
                    st.markdown(result["research_report"])
        else:
            st.error(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            if result.get("research_report"):
                with st.expander("🔬 Partial Research Report"):
                    st.markdown(result["research_report"])

    # Refresh history
    st.markdown("---")
    st.markdown("### 📜 Refresh History")
    history = get_refresh_history(10)
    if history:
        history_data = []
        for h in history:
            # Format the ISO timestamp to YYYY-MM-DD HH:MM
            raw_time = h.get("refreshed_at", "?")
            formatted_time = raw_time.replace("T", " ")[:16] if raw_time != "?" else "?"
            
            history_data.append({
                "Timestamp": formatted_time,
                "Source": h.get("trigger_source", "?"),
                "Status": h.get("status", "?"),
                "Summary": (h.get("patch_summary", "") or "")[:80],
                "PR": h.get("pr_url", ""),
            })
        st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)
    else:
        st.caption("No refresh history yet. Click the button above to start!")


# --- ROUTING LOGIC ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 10px 0;'><h2 style='color:#00f2fe; margin-bottom:0;'>Cathay Miles</h2><p style='color:#94a3b8; font-size:0.8rem;'>VAULT EDITION v4.0</p></div>", unsafe_allow_html=True)
    
    # DB Status Indicator
    if db_manager.USE_SUPABASE:
        st.markdown("<div style='background:rgba(0,242,254,0.1); border:1px solid rgba(0,242,254,0.3); border-radius:10px; padding:8px; text-align:center; margin-bottom:15px;'><span style='color:#00f2fe;'>●</span> <span style='font-size:0.85rem; color:#e2e8f0;'>CLOUD SYNC ACTIVE</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:10px; padding:8px; text-align:center; margin-bottom:15px;'><span style='color:#ef4444;'>●</span> <span style='font-size:0.85rem; color:#e2e8f0;'>LOCAL STORAGE ONLY</span></div>", unsafe_allow_html=True)

    page = st.radio("Navigation", ["💳 Optimizer Engine", "📊 Analytics Dashboard", "🤖 Engine Refresh"])
    st.markdown("---")
    st.info("💡 **Pro Tip:** Use the 'Pay Now' button to save transactions for long-term tracking.")

    # Engine Status Footer
    last = get_last_refresh()
    if last and last.get("refreshed_at"):
        r_date = last["refreshed_at"][:10]
        r_source = last.get("trigger_source", "unknown")
        st.markdown(f"<div style='text-align:center; padding:8px; margin-top:10px; background:rgba(0,242,254,0.05); border-radius:10px; border:1px solid rgba(0,242,254,0.15);'><span style='color:#94a3b8; font-size:0.75rem;'>🔄 Engine refreshed: {r_date}<br/>Source: {r_source}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding:8px; margin-top:10px;'><span style='color:#64748b; font-size:0.75rem;'>🔄 Engine: No refresh history</span></div>", unsafe_allow_html=True)

if page == "💳 Optimizer Engine":
    render_optimizer()
elif page == "📊 Analytics Dashboard":
    render_dashboard()
else:
    render_engine_refresh()
