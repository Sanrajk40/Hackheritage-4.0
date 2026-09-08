import streamlit as st
import pandas as pd
import time
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SecureID | SSB Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# --- ADVANCED CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fallback Light Blue Background */
    [data-testid="stAppViewContainer"] {
        background-color: #E0F2FE;
    }
    
    /* Yellow Border for Sidebar */
    [data-testid="stSidebar"] {
        border-right: 4px solid #EAB308 !important;
    }

    /* Login Card Styling with Yellow Border */
    .login-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        border: 4px solid #EAB308; /* THICK YELLOW BORDER */
        margin-top: 5vh;
    }
    .mha-title { font-size: 2.2rem; font-weight: 800; color: #0284C7; text-align: center; letter-spacing: -0.5px;}
    .mha-subtitle { text-align: center; color: #475569; font-weight: 600; margin-bottom: 30px; }
    
    /* Main Dashboard Headers */
    .dashboard-header { font-size: 2rem; font-weight: 800; color: #0F172A; }
    .dashboard-sub { font-size: 1.1rem; color: #475569; margin-bottom: 20px; }
    
    /* Custom Metric Cards with Yellow Borders */
    .metric-card-pass, .metric-card-warn {
        background-color: #ffffff;
        border: 3px solid #EAB308; /* YELLOW BORDER */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .metric-title { font-size: 0.9rem; color: #475569; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #0284C7; margin-top: 5px;}
    
    /* Button Styling */
    div.stButton > button[kind="primary"] {
        background-color: #0284C7; /* Blue button */
        color: white;
        border: 2px solid #EAB308; /* Yellow border on button */
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0369A1;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION FOR METRICS ---
def display_metric(title, value, status="pass"):
    card_class = "metric-card-pass" if status == "pass" else "metric-card-warn"
    html = f"""
    <div class="{card_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
#               LOGIN MODULE
# ==========================================
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="mha-title">MHA SecureID</div>', unsafe_allow_html=True)
        st.markdown('<div class="mha-subtitle">Sashastra Seema Bal (SSB) Restricted Portal</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Official Email Address", placeholder="officer@ssb.gov.in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            user_id = st.text_input("Officer ID", placeholder="e.g., ID-49201")
            
            # --- EXPANDED AIRPORT & BORDER LIST ---
            airport_id = st.selectbox(
                "Assigned Border / Airport Checkpoint", 
                [
                    "DEL - Indira Gandhi Int. Airport, New Delhi", 
                    "BOM - Chhatrapati Shivaji Maharaj Int. Airport, Mumbai", 
                    "BLR - Kempegowda Int. Airport, Bengaluru",
                    "HYD - Rajiv Gandhi Int. Airport, Hyderabad",
                    "MAA - Chennai Int. Airport, Chennai",
                    "CCU - Netaji Subhas Chandra Bose Int. Airport, Kolkata",
                    "COK - Cochin Int. Airport, Kochi",
                    "AMD - Sardar Vallabhbhai Patel Int. Airport, Ahmedabad",
                    "SSB - Sunauli Land Border (Indo-Nepal)",
                    "SSB - Raxaul Land Border (Indo-Nepal)",
                    "SSB - Jaigaon Land Border (Indo-Bhutan)",
                    "ICP - Moreh (Indo-Myanmar)",
                    "ICP - Attari (Indo-Pak)"
                ]
            )
            
            submit_button = st.form_submit_button("Authenticate Secure Session", type="primary", use_container_width=True)
            
            if submit_button:
                if email and username and password and user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": username, "email": email, "user_id": user_id, "airport_id": airport_id
                    }
                    st.success("Verification successful. Establishing secure connection...")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("Authentication Failed: Missing mandatory credentials.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
#             MAIN APPLICATION
# ==========================================
def main_app():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_of_India_logo.svg/220px-Government_of_India_logo.svg.png", width=90)
        st.markdown("### SecureID Portal")
        st.caption("Active Session")
        st.divider()
        
        app_mode = st.radio("System Modules", ["🛂 Document Scanner", "📋 Audit Logs", "⚙️ System Config"])
        
        st.divider()
        st.info(f"👤 **{st.session_state.user_info['username']}**\n\n"
                f"🏷️ **ID:** {st.session_state.user_info['user_id']}\n\n"
                f"📍 **Post:** {st.session_state.user_info['airport_id']}")
        
        if st.button("End Session (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()

    if app_mode == "🛂 Document Scanner":
        st.markdown('<div class="dashboard-header">Identity & Document Screening</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-sub">AI-powered threat detection for passports, visas, and identities.</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown("### 📥 1. Secure Input")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                doc_type = st.selectbox("Document Category", ["E-Passport", "Tourist Visa", "National ID"])
                uploaded_file = st.file_uploader("Upload Scanned File", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")
                
            with col2:
                camera_input = st.camera_input("Live Biometric Capture")

        st.divider()

        if uploaded_file is not None:
            st.markdown("### 🔍 2. Analysis Dashboard")
            
            analyze_btn = st.button("Initialize Deep Scan & Ledger Sync", type="primary")
            
            if analyze_btn:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Scanning MRZ & Micro-printing...")
                progress_bar.progress(25)
                time.sleep(0.8)
                
                status_text.text("Running Facial Forgery Detection Models...")
                progress_bar.progress(60)
                time.sleep(1)
                
                status_text.text("Validating Date of Birth modifications...")
                progress_bar.progress(85)
                time.sleep(0.8)
                
                status_text.text("Querying Blockchain Ledger...")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                status_text.empty()
                progress_bar.empty()
                
                tab1, tab2, tab3 = st.tabs(["📊 AI Analysis", "👁️ Visual Inspection", "⛓️ Blockchain Audit"])
                
                with tab1:
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        display_metric("Authenticity Score", "98.4%", "pass")
                    with m_col2:
                        display_metric("Biometric Match", "95.1%", "pass")
                    with m_col3:
                        display_metric("DOB Integrity", "Flagged", "warn")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### Detailed Screening Matrix")
                    
                    results = pd.DataFrame({
                        "Security Parameter": ["MRZ Verification", "Photograph Integrity", "Date of Birth (DOB)", "Visa Hologram"],
                        "Status": ["Verified", "Verified", "Tampered", "Verified"],
                        "Confidence Level": ["99.9%", "97.2%", "82.1%", "96.5%"]
                    })
                    
                    def highlight_tampered(val):
                        color = '#fee2e2' if val == 'Tampered' else ''
                        return f'background-color: {color}; color: #991b1b' if val == 'Tampered' else ''
                    
                    st.dataframe(results.style.applymap(highlight_tampered, subset=['Status']), use_container_width=True, hide_index=True)
                    
                with tab2:
                    st.write("**Processed Image Artifacts**")
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Document (Enhancement Filters Applied)", width=400)
                    
                with tab3:
                    st.code('''
{
    "ledger_id": "blk_0x99482A...",
    "timestamp": "2026-09-09T14:22:10Z",
    "status": "VALID",
    "issuer": "Govt of India"
}
                    ''', language="json")
                
                st.divider()
                st.markdown("### ⚡ Command Actions")
                action_c1, action_c2, action_c3 = st.columns(3)
                action_c1.button("✅ Approve Clearance", use_container_width=True)
                action_c2.button("⚠️ Detain for Interrogation", use_container_width=True)
                with action_c3.expander("🚫 Reject & Trigger Alert"):
                    st.error("Are you sure you want to flag this individual?")
                    st.button("Confirm Rejection", type="primary", use_container_width=True)

    elif app_mode == "📋 Audit Logs":
        st.markdown('<div class="dashboard-header">Terminal Audit Logs</div>', unsafe_allow_html=True)
        st.write("Chronological ledger of security clearances.")
        st.dataframe(pd.DataFrame({
            "Time": ["14:15", "14:10", "13:45"],
            "Target ID": ["P129384", "V992813", "P440192"],
            "Alerts": ["None", "Fake Photo", "None"],
            "Officer": [st.session_state.user_info['user_id']] * 3
        }), use_container_width=True)
        
    else:
        st.markdown('<div class="dashboard-header">System Configuration</div>', unsafe_allow_html=True)
        st.markdown("Adjust AI threshold weights for the checkpoint.")
        st.slider("Facial Recognition Confidence Threshold (%)", 70, 100, 85)
        st.slider("Tamper Detection Strictness (%)", 70, 100, 95)
        st.toggle("Secure Blockchain Ledger Sync", value=True)

if not st.session_state.logged_in:
    login_page()
else:
    main_app()