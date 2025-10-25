import streamlit as st

def display_result(decision, reason, next_steps):
    """Helper function to display the result in a styled box."""
    if decision == 'Refer':
        st.success(f"**Decision: {decision} to Transplant**")
        st.write(f"**Reason:** {reason}")
    else:
        st.error(f"**Decision: {decision}**")
        st.write(f"**Reason:** {reason}")

    if next_steps:
        st.markdown("**Next Steps:**")
        for step in next_steps:
            st.markdown(f"- {step}")

# --- Page Configuration ---
st.set_page_config(page_title="Kidney Transplant Screener", layout="wide")

# --- Header ---
st.title("Sanford Transplant Center, Fargo")
st.header("Kidney Transplant Referral Screener")

st.markdown("---")

# --- Input Form ---
# Using a form bundles all inputs; the app only reruns when "Evaluate" is clicked.
with st.form(key="screener_form"):
    
    # We use columns to create the two-column layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Patient Information")
        # Use None as default for number_input to check if it's filled
        egfr = st.number_input("Lowest eGFR", value=None, placeholder="e.g., 18", step=1.0)
        hgbA1c = st.number_input("HgbA1c (%)", value=None, placeholder="e.g., 7.5", step=0.1)
        ejection_fraction = st.number_input("Ejection Fraction on last ECHO (%)", value=None, placeholder="e.g., 55", step=1.0)
        
        st.markdown("---")
        on_dialysis = st.checkbox("Patient is on Dialysis")
        has_uremia = st.checkbox("Signs of Uremia (must be in MD note)", help="Required if lowest eGFR is 20-25")

    with col2:
        st.subheader("Other Contraindications")
        home_o2 = st.checkbox("Requires Home O2")
        smoker = st.checkbox("Current Active Smoker")
        cancer = st.checkbox("Active Cancer")
        infection = st.checkbox("Active Infectious Disease")
        abuse = st.checkbox("Current Drug/Alcohol Abuse")
        homeless = st.checkbox("Homeless")
        no_support = st.checkbox("No Social Support")
        noncompliance = st.checkbox("Missed Dialysis >50%")

    # --- Buttons ---
    submitted = st.form_submit_button("Evaluate")
    
# --- Logic (runs after "Evaluate" is clicked) ---
if submitted:
    # This is the translated logic from your React app's `handleScreening` function
    
    # --- Step 0: Validation ---
    if egfr is None and not on_dialysis:
        st.error('**Error:** Please enter an eGFR value or check if the patient is on dialysis.')
    elif hgbA1c is None or ejection_fraction is None:
        st.error('**Error:** Please enter values for both HgbA1c and Ejection Fraction.')
    
    # --- Step 1: Check Contraindications ---
    elif hgbA1c > 10:
        display_result('Do Not Refer', f'HgbA1c is {hgbA1c}%.', ['Work with Primary Medical Doctor/Endocrinologist, transplant referral after HbA1C<10'])
    elif ejection_fraction < 15:
        display_result('Do Not Refer', f'Ejection Fraction is {ejection_fraction}%.', ['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])
    elif home_o2:
        display_result('Do Not Refer', 'Patient requires home O2.', ['Refer to Pulmonologist for optimization.'])
    elif smoker:
        display_result('Do Not Refer', 'Current active smoker.', ['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
    elif cancer:
        display_result('Do Not Refer', 'Active cancer diagnosis.', ['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
    elif infection:
        display_result('Do Not Refer', 'Active infectious disease.', ['Consult Infectious Disease, refer after resolution of active infection and completion of course of antibiotics'])
    elif abuse:
        display_result('Do Not Refer', 'Current drug or alcohol abuse.', ['Enter CD Eval as First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
    elif homeless:
        display_result('Do Not Refer', 'Patient is homeless (high risk of infection).', ['Address housing situation before referral can be considered.'])
    elif no_support:
        display_result('Do Not Refer', 'No social support system.', ['Patient needs to establish a reliable social support system before referral.'])
    elif noncompliance:
        display_result('Do Not Refer', 'Missed Dialysis >50%', ['Patient must demonstrate a 6 months period of compliance before re-referral.'])
    
    # --- Step 2: Check Referral Qualifications ---
    elif on_dialysis:
        display_result('Refer', 'Patient is currently on dialysis.', ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
    
    elif egfr is not None:
        if egfr <= 20:
            display_result('Refer', f'Lowest eGFR is {egfr}, which is <= 20.', ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
        elif 21 <= egfr <= 25 and has_uremia:
            display_result('Refer', 'Lowest eGFR is between 20-25 and have signs of uremia.', ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
        else:
            # --- Step 3: If no criteria met ---
            display_result('Do Not Refer', 'Patient does not meet the eGFR or dialysis criteria for referral at this time.', ['Continue to monitor patient as per standard CKD management protocols.'])
    
    else:
        # This case should be caught by validation, but it's good to have a fallback.
        st.info("Please fill out the form to get an evaluation.")


# --- Footer ---
st.markdown("---")
st.caption("""
**Disclaimer:** The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.

© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.
""")
