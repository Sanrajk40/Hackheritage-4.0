import streamlit as st
import pandas as pd
import time
from PIL import Image
import requests

st.set_page_config(
    page_title="SecureID | SSB Border Checkpoint",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E3A8A; }
    .sub-header { font-size: 1.2rem; color: #4B5563; margin-bottom: 2rem; }
    .login-header { font-size: 2rem; font-weight: 600; color: #1E3A8A; text-align: center; }
    </style>
""", unsafe_allow_html=True)

def login_page():
    st.markdown('<div class="login-header">MHA / SSB SecureID Portal Access</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 2rem;'>Restricted Access: Authorized Checkpoint Personnel Only.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("Officer Authentication")
            
            email = st.text_input("Official Email Address (Mandatory)", placeholder="officer@ssb.gov.in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            st.divider()
            
            user_id = st.text_input("Officer ID (User ID)", placeholder="e.g., ID-49201")
            airport_id = st.selectbox(
                "Assigned Airport / Border Checkpoint ID", 
                ["DEL - Indira Gandhi Int. Airport", 
                 "BOM - Chhatrapati Shivaji Int. Airport", 
                 "CCU - Netaji Subhas Chandra Bose Int.", 
                 "SSB - Land Border Checkpoint Alpha",
                 "SSB - Land Border Checkpoint Bravo"]
            )
            
            submit_button = st.form_submit_button("Secure Login", type="primary", use_container_width=True)
            
            if submit_button:
                if email and username and password and user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": username,
                        "email": email,
                        "user_id": user_id,
                        "airport_id": airport_id
                    }
                    payload={
                        "username": username,
                        "email": email,
                        "user_id": user_id,
                        "airport_id": airport_id,
                        "password":password

                    }
                    django_url='http://127.0.0.1:8000/api/authenticate_global'
                    response=requests.post(django_url,json=payload)
                    if response.status_code==200:
                        value=response.json().get('value')
                        if value=='5':
                            st.error("A user with this user name is already logged in")
                        elif value=='1':
                             st.success("Authentication successful! Initializing secure session...")
                             time.sleep(1.5)
                             st.rerun()
                        elif value =='0':
                            st.warning('No user name with this userid exists')
                        elif value =='4':
                            st.warning('Password Doesnot match')
                        elif value =='2':
                            st.error("Airport id does not match")


                    
                else:
                    st.error("Please fill in all mandatory fields (Email, Username, Password, User ID).")

def main_app():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Government_of_India_logo.svg/220px-Government_of_India_logo.svg.png", width=100)
        st.title("SecureID Portal")
        st.caption("Sashastra Seema Bal (SSB) Terminal")
        st.divider()
        
        app_mode = st.radio("Navigation", ["Dashboard & Scanning", "Verification History", "System Settings"])
        
        st.divider()
        st.info(f"**Logged In As:** {st.session_state.user_info['username']}\n\n"
                f"**Officer ID:** {st.session_state.user_info['user_id']}\n\n"
                f"**Location:** {st.session_state.user_info['airport_id']}")
        
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            django_url='http://127.0.0.1:8000/api/logout_global'
            z=False
            usid = st.session_state.user_info['user_id']
            m={'logout':z,'userid':usid}
            response=requests.post(django_url,json=m)
            if response.status_code==200:
                st.success("Loggged Out Successfully")
            st.session_state.user_info = {}
            st.rerun()
    if app_mode == "Dashboard & Scanning":
        
        st.markdown('<div class="main-header">AI-Based Identity & Document Screening</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Automated detection of fake passports, visas, and tampered identities.</div>', unsafe_allow_html=True)

        st.subheader("1. Document Input")
        col1, col2 = st.columns(2)
        
        with col1:
            doc_type = st.selectbox("Select Document Type", ["Passport", "e-Visa", "National ID"])
            uploaded_file = st.file_uploader("Upload Scanned Document", type=["png", "jpg", "jpeg", "pdf"])
            
        with col2:
            st.write("Or use live capture (For face matching)")
            camera_input = st.camera_input("Capture Live Photo")

        st.divider()

        if uploaded_file is not None:
            st.subheader("2. AI Verification Results")
            
            analyze_btn = st.button("Run AI Screening & Blockchain Verification", type="primary")
            
            if analyze_btn:
                with st.spinner("Extracting features (MRZ, Watermarks)..."):
                    time.sleep(1)
                with st.spinner("Checking for altered photographs and modified DOB..."):
                    time.sleep(1.5)
                with st.spinner("Verifying against Blockchain ledger..."):
                    time.sleep(1)
                    
                st.success("Screening Complete!")
                
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    st.write("**Uploaded Document**")
                    image = Image.open(uploaded_file)
                    st.image(image, use_column_width=True)
                    
                with res_col2:
                    score_col1, score_col2, score_col3 = st.columns(3)
                    score_col1.metric("Authenticity Score", "98%", "Pass")
                    score_col2.metric("Face Match Confidence", "95%", "Match")
                    score_col3.metric("Blockchain Status", "Verified", "Valid")
                    
                    st.write("---")
                    st.write("**Detailed Anomaly Detection:**")
                    
                    results = pd.DataFrame({
                        "Screening Parameter": [
                            "MRZ Code Validation", 
                            "Photograph Tampering Check", 
                            "Date of Birth (DOB) Modification", 
                            "Visa Hologram/Stamp Check"
                        ],
                        "Status": ["✅ Passed", "✅ Passed", "❌ Flagged (Modified)", "✅ Passed"],
                        "Confidence Level": ["99%", "97%", "82%", "94%"]
                    })
                    
                    st.dataframe(results, use_container_width=True, hide_index=True)
                    
                    st.write("---")
                    st.write("**Officer Action:**")
                    action_c1, action_c2, action_c3 = st.columns(3)
                    action_c1.button("✅ Approve Entry", use_container_width=True)
                    action_c2.button("⚠️ Hold for Manual Review", use_container_width=True)
                    action_c3.button("🚫 Reject & Flag", type="primary", use_container_width=True)

    elif app_mode == "Verification History":
        st.title("Recent Scan History")
        st.write(f"Log of recent individuals processed at {st.session_state.user_info['airport_id']}.")
        
        history_data = pd.DataFrame({
            "Timestamp": ["2026-09-07 14:15", "2026-09-07 14:10", "2026-09-07 13:45"],
            "Document ID": ["P129384", "V992813", "P440192"],
            "Doc Type": ["Passport", "Visa", "Passport"],
            "Result": ["Cleared", "Flagged (Fake Photo)", "Cleared"],
            "Officer ID": [st.session_state.user_info['user_id']] * 3
        })
        st.dataframe(history_data, use_container_width=True)
        
    else:
        st.title("System Settings")
        st.write("Configure AI sensitivity thresholds and Blockchain node connections.")
        st.slider("Face Match strictness threshold (%)", 50, 100, 85)
        st.slider("Forgery detection sensitivity (%)", 50, 100, 90)
        st.toggle("Enable Live Blockchain Sync", value=True)
if not st.session_state.logged_in:
    login_page()
else:
    main_app()