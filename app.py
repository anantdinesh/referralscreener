import streamlit as st

def show_result_card(result):
    """Displays the screening result in a formatted box."""
    if not result:
        return

    is_referral = result['decision'] == 'Refer'
    
    # Build the message content
    message_content = [
        f"**Reason:** {result['reason']}",
    ]
    
    if result.get('nextSteps'):
        message_content.append("**Next Steps:**")
        steps = "\n".join([f"- {step}" for step in result['nextSteps']])
        message_content.append(steps)
        
    final_message = "\n\n".join(message_content)

    if is_referral:
        st.success(f"**Decision: {result['decision']} to Transplant**\n\n{final_message}", icon="✅")
    else:
        st.error(f"**Decision: {result['decision']} to Transplant**\n\n{final_message}", icon="❌")

def reset_form():
    """Clears all input fields and results from the session state."""
    keys = [
        'egfr', 'hgbA1c', 'ejectionFraction', 'onDialysis', 'hasUremia',
        'homeO2', 'smoker', 'cancer', 'infection', 'abuse', 'homeless', 
        'noSupport', 'noncompliance', 'screeningResult'
    ]
    for key in keys:
        if 'Result' in key:
            st.session_state[key] = None
        elif key in ['onDialysis', 'hasUremia', 'homeO2', 'smoker', 'cancer', 'infection', 'abuse', 'homeless', 'noSupport', 'noncompliance']:
            st.session_state[key] = False
        else:
            st.session_state[key] = None # For number inputs

def run_screening(error_placeholder):
    """Runs the full screening logic based on session state."""
    error_placeholder.empty()
    st.session_state.screeningResult = None # Clear previous result

    # --- Get values from session state ---
    egfrValue = st.session_state.egfr
    hgbA1cValue = st.session_state.hgbA1c
    efValue = st.session_state.ejectionFraction
    onDialysis = st.session_state.onDialysis
    hasUremia = st.session_state.hasUremia
    
    contraindications = {
        'homeO2': st.session_state.homeO2,
        'smoker': st.session_state.smoker,
        'cancer': st.session_state.cancer,
        'infection': st.session_state.infection,
        'abuse': st.session_state.abuse,
        'homeless': st.session_state.homeless,
        'noSupport': st.session_state.noSupport,
        'noncompliance': st.session_state.noncompliance,
    }

    # --- Step 0: Validation ---
    if (egfrValue is None) and not onDialysis:
        error_placeholder.error('Please enter a Lowest eGFR value or check if the patient is on dialysis.')
        return
    
    if hgbA1cValue is None or efValue is None:
        error_placeholder.error('Please enter values for both HgbA1c and Ejection Fraction.')
        return

    # --- Step 1: Check for Absolute Contraindications ---
    if hgbA1cValue > 10:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': f'HgbA1c is {hgbA1cValue}%.', 'nextSteps': ['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'] })
      return
    
    if efValue < 15:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': f'Ejection Fraction is {efValue}%.', 'nextSteps': ['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'] })
      return
    
    if contraindications['homeO2']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Patient requires home O2.', 'nextSteps': ['Refer to Pulmonologist for optimization.'] })
      return
    
    if contraindications['smoker']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Current active smoker.', 'nextSteps': ['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'] })
      return
    
    if contraindications['cancer']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Active cancer diagnosis.', 'nextSteps': ['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'] })
      return
    
    if contraindications['infection']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Active infectious disease.', 'nextSteps': ['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'] })
      return
    
    if contraindications['abuse']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Current drug or alcohol abuse.', 'nextSteps': ['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'] })
      return
    
    if contraindications['homeless']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Patient is homeless (high risk of infection).', 'nextSteps': ['Address housing situation before referral can be considered.'] })
      return
    
    if contraindications['noSupport']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'No social support system.', 'nextSteps': ['Patient needs to establish a reliable social support system before referral.'] })
      return
    
    if contraindications['noncompliance']:
      st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Missed Dialysis >50%.', 'nextSteps': ['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'] })
      return
    
    # --- Step 2: Check for Referral Qualifications ---
    if onDialysis:
        st.session_state.screeningResult = ({ 'decision': 'Refer', 'reason': 'Patient is currently on dialysis.', 'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] })
        return

    if egfrValue is not None:
        if egfrValue <= 20:
            st.session_state.screeningResult = ({ 'decision': 'Refer', 'reason': f'Lowest eGFR is {egfrValue}, which is <= 20.', 'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] })
            return
        
        if 20 < egfrValue <= 25 and hasUremia:
            st.session_state.screeningResult = ({ 'decision': 'Refer', 'reason': 'Lowest eGFR is between 20-25 and have signs of uremia.', 'nextSteps': ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] })
            return

    # --- Step 3: If no criteria met ---
    st.session_state.screeningResult = ({ 'decision': 'Do Not Refer', 'reason': 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', 'nextSteps': ['Continue to monitor patient as per standard CKD management protocols.'] })

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Kidney Transplant Screener", layout="centered")

    # Add the background image with opacity
    st.markdown(
        f"""
        <style>
        .stApp {{
            position: relative;
        }}
        /* This pseudo-element adds the background image */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Kidney_illustration.svg/1200px-Kidney_illustration.svg.png");
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.05; /* React opacity-5 */
            z-index: -1; /* Place it behind the content */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state for the result
    if 'screeningResult' not in st.session_state:
        st.session_state.screeningResult = None

    # --- Header ---
    st.title("Sanford Transplant Center, Fargo")
    st.header("Kidney Transplant Referral Screener")

    # --- Main Form Card ---
    with st.container(border=True):
        st.subheader("Patient Information")
        
        # Placeholder for validation errors
        error_placeholder = st.empty()

        col1, col2 = st.columns(2)

        with col1:
            st.number_input("Lowest eGFR", key='egfr', value=None, placeholder="e.g., 18", format="%f", help="Patient's lowest recorded eGFR.")
            st.number_input("HgbA1c (%)", key='hgbA1c', value=None, placeholder="e.g., 7.5", format="%.1f")
            st.number_input("Ejection Fraction on last ECHO (%)", key='ejectionFraction', value=None, placeholder="e.g., 55", format="%f")
            st.checkbox("Patient is on Dialysis", key='onDialysis')
            st.checkbox("Signs of Uremia (must be in MD note)", key='hasUremia', help="Required if Lowest eGFR is > 20 and <= 25")

        with col2:
            st.subheader("Current History")
            st.checkbox("Requires Home O2", key='homeO2')
            st.checkbox("Current Active Smoker", key='smoker')
            st.checkbox("Active Cancer", key='cancer')
            st.checkbox("Active Infectious Disease", key='infection')
            st.checkbox("Current Drug/Alcohol Abuse", key='abuse')
            st.checkbox("Homeless", key='homeless')
            st.checkbox("No Social Support", key='noSupport')
            st.checkbox("Missed Dialysis >50%", key='noncompliance')

        # --- Action Buttons ---
        eval_col, reset_col = st.columns([3, 1]) # Give 'Evaluate' more space
        
        with eval_col:
            evaluate_button = st.button("Evaluate", type="primary", use_container_width=True)
            
        with reset_col:
            if st.button("Reset", use_container_width=True):
                reset_form()
                st.rerun()

    # --- Result Display ---
    result_container = st.container()

    if evaluate_button:
        run_screening(error_placeholder)

    if st.session_state.screeningResult:
        with result_container:
            show_result_card(st.session_state.screeningResult)

    # --- Footer ---
    st.caption("---")
    st.caption("**Disclaimer:** The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.")
    st.caption("© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.")

if __name__ == "__main__":
    main()

