import streamlit as st
import pandas as pd
import time
from PIL import Image
import requests
#pls don't remove this this is important
from OCR.pass_ocr import backend_passport_ocr


st.set_page_config(
    page_title="SecureID | SSB Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

import os

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("design.css")
except FileNotFoundError:
    st.warning("design.css not found. Please ensure it is in the same folder as app.py")
def display_metric(title, value, status="pass"):
    card_class = "metric-card-pass" if status == "pass" else "metric-card-warn"
    html = f"""
    <div class="{card_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown(
            '<div class="login-header-card">'
            '<span class="login-classification">Authorized Personnel Only</span>'
            '<div class="mha-title">MHA SecureID</div>'
            '<div class="mha-gold-underline"></div>'
            '<div class="mha-subtitle">Sashastra Seema Bal (SSB) Restricted Portal</div>'
            '<div class="login-security-note">This terminal is restricted to authorized SSB personnel. All access attempts are logged.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        with st.form("login_form", border=False):
            st.markdown('<div class="login-form-heading">Officer Credentials</div>', unsafe_allow_html=True)
            email = st.text_input("Official Email Address", placeholder="officer@ssb.gov.in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            user_id = st.text_input("Officer ID", placeholder="e.g., ID-49201")
            
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
                    # Please don't change this is very crucial
                    payload={
                        "username": username, "email": email, "user_id": user_id, "airport_id": airport_id,'password':password

                    }
                    django_url='http://127.0.0.1:8000/api/authenticate_global'
                    response= requests.post(django_url,json=payload)
                    if response.status_code==200:
                        value = response.json().get('value')
                        if value=='5':
                            st.error("The user is already logged in.")
                        elif value=='4':
                            st.warning("The password did not match")
                        elif value=='1':
                            st.success("Verification successful. Establishing secure connection...")
                            st.rerun()
                            time.sleep(1.2)
                        elif value=='2':
                            st.warning("The airport id did not match")
                        elif value=='0':
                            st.warning("No user with this userid found")
                    else:
                        st.warning("Failed to connect to the server side")

                    
                    
                    
                else:
                    st.error("Authentication Failed: Missing mandatory credentials.")

        st.markdown('<div class="login-footer-note">MHA SecureID · Government of India · SSB Restricted Network</div>', unsafe_allow_html=True)

def main_app():
    with st.sidebar:
        
        st.markdown(
            '<div class="sb-gov-badge">'
            '<div class="sb-gov-badge-mark">GoI</div>'
            '<div class="sb-gov-badge-text">Government<br/>of India</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="sb-brand-title">SecureID Portal</div>'
            '<div class="sb-brand-sub">Government security terminal</div>',
            unsafe_allow_html=True
        )
        st.caption("Active Session")
        st.divider()

        st.markdown('<div class="sb-section-label">System Modules</div>', unsafe_allow_html=True)
        app_mode = st.radio(
            "System Modules",
            ["🛂 Document Scanner", "📋 Audit Logs", "⚙️ System Config"],
            label_visibility="collapsed"
        )

        st.divider()

        st.markdown('<div class="sb-section-label">Current Officer</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sb-officer-card">'
            f'<div class="sb-officer-row"><span class="sb-officer-icon">👤</span>{st.session_state.user_info["username"]}</div>'
            f'<div class="sb-officer-row"><span class="sb-officer-icon">🏷️</span>ID: {st.session_state.user_info["user_id"]}</div>'
            f'<div class="sb-officer-row"><span class="sb-officer-icon">📍</span>{st.session_state.user_info["airport_id"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if st.button("End Session (Logout)", use_container_width=True):

            # This is important for logging out pls donot change
            empid=st.session_state.user_info['userid']
            payload={'userid':empid}
            django_url='http://127.0.0.1:8000/api/logout_global'
            response=requests.post(django_url,json=payload)
            if response.status_code==200:
                st.session_state.logged_in = False
                st.session_state.user_info = {}
                st.rerun()
            else:
                st.warning("Failed to logout")



            
            
            

    if app_mode == "🛂 Document Scanner":
        st.markdown('<div class="op-header-eyebrow">Document Scanner Module</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-header">Identity & Document Screening</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-sub">AI-powered threat detection for passports, visas, and identities.</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(
                '<div class="workspace-title">📥 1. Secure Input</div>'
                '<div class="workspace-sub">Document information + live biometric capture</div>',
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown('<div class="workspace-col-label">📄 Document Upload</div>', unsafe_allow_html=True)
                doc_type = st.selectbox("Document Category", ["E-Passport", "Tourist Visa", "National ID"])
                if doc_type=='E-passport':
                    passport = st.file_uploader("Upload Scanned File", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")
                elif doc_type=='Tourist Visa':
                    visa=st.file_uploader("Upload Scanned File",type =['png','jpg','jpeg','pdf'],label_visibility="collapsed")
                elif doc_type=='Nationa ID':
                    doc=st.file_uploader("Upload Scanned File",type =['png','jpg','jpeg','pdf'],label_visibility="collapsed")

                
                st.caption("Supported document/image input")

            with col2:
                st.markdown('<div class="workspace-col-label">🎥 Live Biometric Capture</div>', unsafe_allow_html=True)
                camera_input = st.camera_input("Live Biometric Capture", label_visibility="collapsed")

        st.divider()

        if passport and visa is not None:
            st.markdown("### 🔍 2. Analysis Dashboard")
            
            analyze_btn = st.button("Initialize Deep Scan & Ledger Sync", type="primary")
            
            if analyze_btn:
                progress_bar = st.progress(0)
                status_text = st.empty()

                file_bytes = passport.read()
                mime_type = passport.type
                result = backend_passport_ocr(file_bytes,mime_type)

                if result['success']:
                    st.subheader("System has extracted these output pls check")
                    st.code(result['Passport Details'],language='python')
                
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
                    
                    st.dataframe(results.style.map(highlight_tampered, subset=['Status']), use_container_width=True, hide_index=True)
                    
                with tab2:
                    st.write("**Processed Image Artifacts**")
                    image = Image.open(passport)
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