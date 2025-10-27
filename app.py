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
st.header("Patient Information")

col1, col2 = st.columns(2)

with col1:
    egfr = st.number_input("Lowest eGFR", min_value=0.0, step=0.1, format="%.1f")
    hgba1c = st.number_input("HgbA1c (%)", min_value=0.0, step=0.1, format="%.1f")
    ef = st.number_input("Ejection Fraction on last ECHO (%)", min_value=0.0, step=0.1, format="%.1f")
    on_dialysis = st.checkbox("Patient is on Dialysis")
    has_uremia = st.checkbox("Signs of Uremia (must be in MD note)",
                             help="Required if Lowest eGFR is > 20 and <= 25")

with col2:
    st.subheader("Current History")
    contraindications = {
        "homeO2": st.checkbox("Requires Home O2"),
        "smoker": st.checkbox("Current Active Smoker"),
        "cancer": st.checkbox("Active Cancer"),
        "infection": st.checkbox("Active Infectious Disease"),
        "abuse": st.checkbox("Current Drug/Alcohol Abuse"),
        "homeless": st.checkbox("Homeless"),
        "noSupport": st.checkbox("No Social Support"),
        "noncompliance": st.checkbox("Missed Dialysis >50%"),
    }

# --- Button Controls ---
evaluate = st.button("Evaluate", type="primary")
reset = st.button("Reset Form")

if reset:
    st.experimental_rerun()

# --- Screening Logic ---
if evaluate:
    error = ""
    result = {}

    if not egfr and not on_dialysis:
        error = "Please enter a Lowest eGFR value or check if the patient is on dialysis."

    if error:
        st.markdown(f"<div class='error-box'>{error}</div>", unsafe_allow_html=True)
    else:
        reasons_not_to_refer = []
        next_steps_not_to_refer = []

        # --- Absolute Contraindications ---
        if hgba1c > 10:
            reasons_not_to_refer.append(f"HgbA1c is {hgba1c}%.")
            next_steps_not_to_refer.append(
                "Work with PMD/Endocrinologist; refer after HgbA1c < 10."
            )
        if ef < 15:
            reasons_not_to_refer.append(f"Ejection Fraction is {ef}%.")
            next_steps_not_to_refer.append(
                "Consult Cardiology for optimization before transplant referral."
            )

        if contraindications["homeO2"]:
            reasons_not_to_refer.append("Patient requires home O2.")
            next_steps_not_to_refer.append("Refer to Pulmonologist for optimization.")
        if contraindications["smoker"]:
            reasons_not_to_refer.append("Current active smoker.")
            next_steps_not_to_refer.extend([
                "Refer to Tobacco Cessation.",
                "Can be re-referred after abstaining for 6 months."
            ])
        if contraindications["cancer"]:
            reasons_not_to_refer.append("Active cancer diagnosis.")
            next_steps_not_to_refer.append(
                "Referral reconsidered after treatment and oncologist clearance."
            )
        if contraindications["infection"]:
            reasons_not_to_refer.append("Active infectious disease.")
            next_steps_not_to_refer.append(
                "Refer after resolution of infection and completion of antibiotics."
            )
        if contraindications["abuse"]:
            reasons_not_to_refer.append("Current drug or alcohol abuse.")
            next_steps_not_to_refer.extend([
                "Enter CD Eval for First Step (651-925-0057).",
                "Re-refer when treatment complete and documented."
            ])
        if contraindications["homeless"]:
            reasons_not_to_refer.append("Patient is homeless (high infecti_
