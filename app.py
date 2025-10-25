import streamlit as st

# --- Page and State Setup ---

# Configure the page to be wide, matching the React app's layout
st.set_page_config(layout="wide")

st.title("Sanford Transplant Center, Fargo")
st.header("Kidney Transplant Referral Screener")

def initialize_state():
    """Sets or resets all session state variables to their defaults."""
    # Patient info inputs
    st.session_state.egfr = None
    st.session_state.onDialysis = False
    st.session_state.hasUremia = False
    st.session_state.hgbA1c = None
    st.session_state.ejectionFraction = None

    # Contraindications inputs
    st.session_state.homeO2 = False
    st.session_state.smoker = False
    st.session_state.cancer = False
    st.session_state.infection = False
    st.session_state.abuse = False
    st.session_state.homeless = False
    st.session_state.noSupport = False
    st.session_state.noncompliance = False
    
    # App state
    st.session_state.screeningResult = None
    st.session_state.error = ""

def set_result(decision, reason, next_steps=None):
    """Helper function to set the screening result in session state."""
    st.session_state.screeningResult = {
        "decision": decision,
        "reason": reason,
        "nextSteps": next_steps or []
    }

# Initialize state if it's the first run
if 'screeningResult' not in st.session_state:
    initialize_state()

# --- Form UI ---

# Use st.container with a border to replicate the "Card" component
with st.container(border=True):
    st.subheader("Patient Information")

    # Display an error message if one exists (from validation)
    if st.session_state.error:
        st.error(st.session_state.error)

    # Create a two-column layout like the React app
    col1, col2 = st.columns(2)

    with col1:
        # Use st.number_input for numeric fields, binding them to session_state
        # Setting value=None allows the placeholder to show
        st.number_input(
            "Lowest eGFR",
            value=st.session_state.egfr,
            placeholder="e.g., 18",
            format="%.1f", # Allows decimal input
            key="egfr"
        )
        st.number_input(
            "HgbA1c (%)",
            value=st.session_state.hgbA1c,
            placeholder="e.g., 7.5",
            format="%.1f",
            key="hgbA1c"
        )
        st.number_input(
            "Ejection Fraction on last ECHO (%)",
            value=st.session_state.ejectionFraction,
            placeholder="e.g., 55",
            format="%.1f",
            key="ejectionFraction"
        )
        
        # Checkboxes bound to session_state
        st.checkbox(
            "Patient is on Dialysis",
            value=st.session_state.onDialysis,
            key="onDialysis"
        )
        st.checkbox(
            "Signs of Uremia (must be in MD note)",
            value=st.session_state.hasUremia,
            key="hasUremia",
            help="Required if Lowest eGFR is > 20 and <= 25"
        )

    with col2:
        st.markdown("#### Current History (Contraindications)")
        
        # Checkboxes for all contraindications
        st.checkbox("Requires Home O2", value=st.session_state.homeO2, key="homeO2")
        st.checkbox("Current Active Smoker", value=st.session_state.smoker, key="smoker")
        st.checkbox("Active Cancer", value=st.session_state.cancer, key="cancer")
        st.checkbox("Active Infectious Disease", value=st.session_state.infection, key="infection")
        st.checkbox("Current Drug/Alcohol Abuse", value=st.session_state.abuse, key="abuse")
        st.checkbox("Homeless", value=st.session_state.homeless, key="homeless")
        st.checkbox("No Social Support", value=st.session_state.noSupport, key="noSupport")
        st.checkbox("Missed Dialysis >50%", value=st.session_state.noncompliance, key="noncompliance")

    st.divider()

    # --- Form Buttons and Logic ---
    
    # Create columns to right-align the buttons, similar to "flex justify-end"
    b_col_spacer, b_col_reset, b_col_eval = st.columns([0.6, 0.2, 0.2])

    with b_col_reset:
        # Reset Button: Calls the initialize_state function
        if st.button("Reset", use_container_width=True):
            initialize_state()
            # The script will automatically rerun, clearing the UI

    with b_col_eval:
        # Evaluate Button: Triggers the main screening logic
        if st.button("Evaluate", type="primary", use_container_width=True):
            
            # Reset error and result states on every evaluation attempt
            st.session_state.error = ""
            st.session_state.screeningResult = None

            # --- Step 0: Validation ---
            # Check for `None` instead of `''`
            if st.session_state.egfr is None and not st.session_state.onDialysis:
                st.session_state.error = 'Please enter a Lowest eGFR value or check if the patient is on dialysis.'
            elif st.session_state.hgbA1c is None or st.session_state.ejectionFraction is None:
                st.session_state.error = 'Please enter values for both HgbA1c and Ejection Fraction.'
            
            # --- If Validation Passes, Run Logic ---
            if not st.session_state.error:
                # Use values directly from session_state
                hgbA1cValue = st.session_state.hgbA1c
                efValue = st.session_state.ejectionFraction

                # --- Step 1: Check for Absolute Contraindications ---
                if hgbA1cValue > 10:
                    set_result('Do Not Refer', f'HgbA1c is {hgbA1cValue}%.', ['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'])
                elif efValue < 15:
                    set_result('Do Not Refer', f'Ejection Fraction is {efValue}%.', ['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])
                elif st.session_state.homeO2:
                    set_result('Do Not Refer', 'Patient requires home O2.', ['Refer to Pulmonologist for optimization.'])
                elif st.session_state.smoker:
                    set_result('Do Not Refer', 'Current active smoker.', ['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
                elif st.session_state.cancer:
                    set_result('Do Not Refer', 'Active cancer diagnosis.', ['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
                elif st.session_state.infection:
                    set_result('Do Not Refer', 'Active infectious disease.', ['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'])
                elif st.session_state.abuse:
                    set_result('Do Not Refer', 'Current drug or alcohol abuse.', ['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
                elif st.session_state.homeless:
                    set_result('Do Not Refer', 'Patient is homeless (high risk of infection).', ['Address housing situation before referral can be considered.'])
                elif st.session_state.noSupport:
                    set_result('Do Not Refer', 'No social support system.', ['Patient needs to establish a reliable social support system before referral.'])
                elif st.session_state.noncompliance:
                    set_result('Do Not Refer', 'Missed Dialysis >50%.', ['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'])
                
                # --- Step 2: Check for Referral Qualifications ---
                # This block runs only if no contraindications were found
                if not st.session_state.screeningResult:
                    egfrValue = st.session_state.egfr # This is safe because of the validation check

                    if st.session_state.onDialysis:
                        set_result('Refer', 'Patient is currently on dialysis.', ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
                    # Check if egfrValue is not None before numeric comparison
                    elif egfrValue is not None:
                        if egfrValue <= 20:
                            set_result('Refer', f'Lowest eGFR is {egfrValue}, which is <= 20.', ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
                        elif 20 < egfrValue <= 25 and st.session_state.hasUremia:
                            set_result('Refer', 'Lowest eGFR is between 20-25 and have signs of uremia.', ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'])
                        else:
                            # --- Step 3: If no criteria met ---
                            set_result('Do Not Refer', 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', ['Continue to monitor patient as per standard CKD management protocols.'])
                    else:
                        # Fallback if egfr is None and not on dialysis (should be caught by validation, but good to have)
                         set_result('Do Not Refer', 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', ['Continue to monitor patient as per standard CKD management protocols.'])


# --- Result Display ---

# This section is outside the form container, similar to the React app
# It will display the result *after* the button is pressed and the state is set
if st.session_state.screeningResult:
    result = st.session_state.screeningResult
    decision = result['decision']
    reason = result['reason']
    next_steps = result.get('nextSteps', [])

    if decision == 'Refer':
        # st.success provides the green-themed "ResultCard"
        with st.success(f"**Decision: {decision} to Transplant**", icon="✅"):
            st.markdown(f"**Reason:** {reason}")
            if next_steps:
                st.divider()
                st.markdown("**Next Steps:**")
                for step in next_steps:
                    st.markdown(f"- {step}")
    else:
        # st.error provides the red-themed "ResultCard"
        with st.error(f"**Decision: {decision} to Transplant**", icon="🚫"):
            st.markdown(f"**Reason:** {reason}")
            if next_steps:
                st.divider()
                st.markdown("**Next Steps:**")
                for step in next_steps:
                    st.markdown(f"- {step}")

# --- Footer ---

st.divider()
# st.caption is the Streamlit-native way to add centered, small-font footer text
st.caption("Disclaimer: The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.")
st.caption("© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.")
