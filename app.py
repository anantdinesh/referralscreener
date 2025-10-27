import streamlit as st

# --- App Config ---
st.set_page_config(
    page_title="Kidney Transplant Referral Screener | Sanford Fargo",
    page_icon="🩺",
    layout="centered",
)

# --- Helper Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f3f4f6;
        font-family: 'Segoe UI', sans-serif;
        color: #111827;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5em 1.5em;
    }
    .success-box {
        background-color: #ecfdf5;
        border-left: 5px solid #10b981;
        padding: 1em;
        border-radius: 12px;
    }
    .error-box {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 1em;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("Sanford Transplant Center, Fargo")
st.subheader("Kidney Transplant Referral Screener")
st.markdown("---")

# --- Patient Info Inputs ---
st.header("Patient Information"
