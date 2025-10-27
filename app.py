import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file_url):
    page_bg_img = f'''
    <style>
    /* Basic styling for the app */
    .stApp {{
        background-color: #f0f2f6; /* Light gray background */
    }}
    
    /* Style for the main content area */
    .main .block-container {{
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* Card-like container for inputs */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {{
        background-color: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }}

    /* Style for buttons */
    div[data-testid="stButton"] > button {{
        border-radius: 0.375rem;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    # Kidney background image (low opacity)
    st.markdown(
    f"""
    <style>
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Kidney_illustration.svg/1200px-Kidney_illustration.svg.png");
        background-size: contain;
        background-position: center;
        background-repeat: no-repeat;
        opacity: 0.05;
        z-index: -1;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Main App Function
def screening_app():
    """
    This function runs the main Streamlit application for the Kidney Transplant Referral Screener.
    """

    st.set_page_config(page_title="Kidney Transplant Screener", layout="centered")

    # Apply custom background and card styling
    set_png_as_page_bg(None)

    # --- Page Header ---
    st.title("Sanford Transplant Center, Fargo")
    st.header("Kidney Transplant Referral Screener")

    # --- Initialize Session State ---
    if 'screening_result' not in st.session_state:
        st.session_state.screening_result = None
    
    defaults = {
        'egfr': None, 'on_dialysis': False, 'has_uremia': False,
        'hgb_a1c': None, 'ejection_fraction': None,
        'home_o2': False, 'smoker': False, 'cancer': False,
        'infection': False, 'abuse': False, 'homeless': False,
        'no_support': False, 'noncompliance': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- Input Form ---
    with st.container():
        st.subheader("Patient Information")
        col1, col2 = st.columns(2)

        with col1:
            st.session_state.egfr = st.number_input("Lowest eGFR", value=st.session_state.egfr, placeholder="e.g., 18", format="%f", key="egfr_input")
            st.session_state.hgb_a1c = st.number_input("HgbA1c (%)", value=st.session_state.hgb_a1c, placeholder="e.g., 7.5 (Optional)", format="%f", key="hgba1c_input")
            st.session_state.ejection_fraction = st.number_input("Ejection Fraction on last ECHO (%)", value=st.session_state.ejection_fraction, placeholder="e.g., 55 (Optional)", format="%f", key="ef_input")
            st.session_state.on_dialysis = st.checkbox("Patient is on Dialysis", value=st.session_state.on_dialysis, key="dialysis_check")
            st.session_state.has_uremia = st.checkbox("Signs of Uremia (must be in MD note)", value=st.session_state.has_uremia, help="Required if Lowest eGFR is > 20 and <= 25", key="uremia_check")

        with col2:
            st.subheader("Current History")
            st.session_state.home_o2 = st.checkbox("Requires Home O2", value=st.session_state.home_o2, key="homeo2_check")
            st.session_state.smoker = st.checkbox("Current Active Smoker", value=st.session_state.smoker, key="smoker_check")
            st.session_state.cancer = st.checkbox("Active Cancer", value=st.session_state.cancer, key="cancer_check")
            st.session_state.infection = st.checkbox("Active Infectious Disease", value=st.session_state.infection, key="infection_check")
            st.session_state.abuse = st.checkbox("Current Drug/Alcohol Abuse", value=st.session_state.abuse, key="abuse_check")
            st.session_state.homeless = st.checkbox("Homeless", value=st.session_state.homeless, key="homeless_check")
            st.session_state.no_support = st.checkbox("No Social Support", value=st.session_state.no_support, key="support_check")
            st.session_state.noncompliance = st.checkbox("Missed Dialysis >50%", value=st.session_state.noncompliance, key="noncompliance_check")

        # --- Action Buttons ---
        st.write("") # Spacer
        col_btn_1, col_btn_2 = st.columns([1, 1])
        
        with col_btn_1:
             evaluate_button = st.button("Evaluate", type="primary", use_container_width=True)
        with col_btn_2:
            reset_button = st.button("Reset", use_container_width=True)


    # --- Logic ---
    if reset_button:
        for key, value in defaults.items():
            # Check if key exists before deleting to avoid error on first run
            if key in st.session_state:
                st.session_state[key] = value
        st.session_state.screening_result = None
        # Use st.rerun() to immediately clear inputs on the screen
        st.rerun()


    if evaluate_button:
        # --- Validation ---
        if st.session_state.egfr is None and not st.session_state.on_dialysis:
            st.error('Please enter a Lowest eGFR value or check if the patient is on dialysis.')
            st.session_state.screening_result = None
            return # Stop execution
        
        # HgbA1c and Ejection Fraction are optional, validation removed.

        # --- Screening Logic ---
        reasons_not_to_refer = []
        next_steps_not_to_refer = []

        hgb_a1c_val = float(st.session_state.hgb_a1c) if st.session_state.hgb_a1c is not None else None
        ef_val = float(st.session_state.ejection_fraction) if st.session_state.ejection_fraction is not None else None
        egfr_val = float(st.session_state.egfr) if st.session_state.egfr is not None else None

        # Step 1: Check for Absolute Contraindications
        if hgb_a1c_val is not None and hgb_a1c_val > 10:
            reasons_not_to_refer.append(f'HgbA1c is {hgb_a1c_val}%.')
            next_steps_not_to_refer.append(['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'])
        
        if ef_val is not None and ef_val < 15:
            reasons_not_to_refer.append(f'Ejection Fraction is {ef_val}%.')
            next_steps_not_to_refer.append(['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])
        
        if st.session_state.home_o2:
            reasons_not_to_refer.append('Patient requires home O2.')
            next_steps_not_to_refer.append(['Refer to Pulmonologist for optimization.'])
        
        if st.session_state.smoker:
            reasons_not_to_refer.append('Current active smoker.')
            next_steps_not_to_refer.append(['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
        
        if st.session_state.cancer:
            reasons_not_to_refer.append('Active cancer diagnosis.')
            next_steps_not_to_refer.append(['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
        
        if st.session_state.infection:
            reasons_not_to_refer.append('Active infectious disease.')
            next_steps_not_to_refer.append(['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'])
        
        if st.session_state.abuse:
            reasons_not_to_refer.append('Current drug or alcohol abuse.')
            next_steps_not_to_refer.append(['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
        
        if st.session_state.homeless:
            reasons_not_to_refer.append('Patient is homeless (high risk of infection).')
            next_steps_not_to_refer.append(['Address housing situation before referral can be considered.'])
        
        if st.session_state.no_support:
            reasons_not_to_refer.append('No social support system.')
            next_steps_not_to_refer.append(['Patient needs to establish a reliable social support system before referral.'])
        
        if st.session_state.noncompliance:
            reasons_not_to_refer.append('Missed Dialysis >50%.')
            next_steps_not_to_refer.append(['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'])

        # Step 1b: Aggregate Contraindications
        if len(reasons_not_to_refer) > 0:
            st.session_state.screening_result = {
                'decision': 'Do Not Refer',
                'reasons': reasons_not_to_refer,
                'next_steps': [step for sublist in next_steps_not_to_refer for step in sublist] # Flatten list
            }
        else:
            # Step 2: Check for Referral Qualifications (only if no contraindications)
            if st.session_state.on_dialysis:
                st.session_state.screening_result = {
                    'decision': 'Refer', 
                    'reason': 'Patient is currently on dialysis.', 
                    'next_steps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                }
            elif egfr_val is not None:
                if egfr_val <= 20:
                    st.session_state.screening_result = {
                        'decision': 'Refer', 
                        'reason': f'Lowest eGFR is {egfr_val}, which is <= 20.', 
                        'next_steps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                    }
                elif 20 < egfr_val <= 25 and st.session_state.has_uremia:
                    st.session_state.screening_result = {
                        'decision': 'Refer', 
                        'reason': 'Lowest eGFR is between 20-25 and have signs of uremia.', 
                        'next_steps': ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                    }
                else:
                    # Step 3: No criteria met
                    st.session_state.screening_result = {
                        'decision': 'Do Not Refer', 
                        'reason': 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', 
                        'next_steps': ['Continue to monitor patient as per standard CKD management protocols.']
                    }
            else:
                 # Should be caught by validation, but as a fallback
                 st.session_state.screening_result = {
                        'decision': 'Do Not Refer', 
                        'reason': 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', 
                        'next_steps': ['Continue to monitor patient as per standard CKD management protocols.']
                    }


    # --- Display Result ---
    if st.session_state.screening_result:
        result = st.session_state.screening_result
        decision_text = f"**Decision: {result['decision']} to Transplant**"
        
        if result['decision'] == 'Refer':
            with st.success(decision_text):
                if 'reason' in result:
                    st.write(f"**Reason:** {result['reason']}")
                
                if 'next_steps' in result and len(result['next_steps']) > 0:
                    st.write("**Next Steps:**")
                    for step in result['next_steps']:
                        st.write(f"- {step}")
        else:
            with st.error(decision_text):
                if 'reason' in result: # For single-reason "Do Not Refer" (e.g., criteria not met)
                    st.write(f"**Reason:** {result['reason']}")
                
                if 'reasons' in result: # For multiple contraindications
                    st.write("**Reasons:**")
                    for r in result['reasons']:
                        st.write(f"- {r}")

                if 'next_steps' in result and len(result['next_steps']) > 0:
                    st.write("**Next Steps:**")
                    for step in result['next_steps']:
                        st.write(f"- {step}")

    # --- Footer ---
    st.markdown("---")
    st.caption("Disclaimer: The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.")
    st.caption("© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.")


if __name__ == "__main__":
    screening_app()

