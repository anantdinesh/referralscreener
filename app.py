import streamlit as st

# --- State Management ---
# We use st.session_state to store all input values and results,
# mimicking React's state.

def initialize_state():
    """Initializes session state for all form inputs and results."""
    # Define all default values in one place
    defaults = {
        "egfr": None,
        "onDialysis": False,
        "hasUremia": False,
        "hgbA1c": None,
        "ejectionFraction": None,
        "homeO2": False,
        "smoker": False,
        "cancer": False,
        "infection": False,
        "abuse": False,
        "homeless": False,
        "noSupport": False,
        "noncompliance": False,
        "screening_result": None,
        "error_message": None
    }
    # Loop and set keys in session_state if they don't already exist
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_form():
    """Resets all session state keys to their default values."""
    # Define all default values
    defaults = {
        "egfr": None,
        "onDialysis": False,
        "hasUremia": False,
        "hgbA1c": None,
        "ejectionFraction": None,
        "homeO2": False,
        "smoker": False,
        "cancer": False,
        "infection": False,
        "abuse": False,
        "homeless": False,
        "noSupport": False,
        "noncompliance": False,
        "screening_result": None,
        "error_message": None
    }
    # Overwrite all keys with default values
    for key, value in defaults.items():
        st.session_state[key] = value

# --- Core Logic ---

def evaluate_screening():
    """
    Runs the screening logic based on values in st.session_state.
    Results are saved back into st.session_state.
    """
    # Clear previous results and errors
    st.session_state.screening_result = None
    st.session_state.error_message = None

    # --- Step 0: Validation ---
    # st.number_input returns None if empty, which is what we want to check.
    if st.session_state.egfr is None and not st.session_state.onDialysis:
        st.session_state.error_message = 'Please enter a Lowest eGFR value or check if the patient is on dialysis.'
        return

    # Get values from session state
    hgbA1c_value = st.session_state.hgbA1c
    ef_value = st.session_state.ejectionFraction

    reasons_not_to_refer = []
    next_steps_not_to_refer = []

    # --- Step 1: Check for Absolute Contraindications ---
    if hgbA1c_value is not None and hgbA1c_value > 10:
        reasons_not_to_refer.append(f"HgbA1c is {hgbA1c_value}%.")
        next_steps_not_to_refer.extend(['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'])
    
    if ef_value is not None and ef_value < 15:
        reasons_not_to_refer.append(f"Ejection Fraction is {ef_value}%.")
        next_steps_not_to_refer.extend(['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])
    
    if st.session_state.homeO2:
        reasons_not_to_refer.append('Patient requires home O2.')
        next_steps_not_to_refer.extend(['Refer to Pulmonologist for optimization.'])
    
    if st.session_state.smoker:
        reasons_not_to_refer.append('Current active smoker.')
        next_steps_not_to_refer.extend(['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
    
    if st.session_state.cancer:
        reasons_not_to_refer.append('Active cancer diagnosis.')
        next_steps_not_to_refer.extend(['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
    
    if st.session_state.infection:
        reasons_not_to_refer.append('Active infectious disease.')
        next_steps_not_to_refer.extend(['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'])
    
    if st.session_state.abuse:
        reasons_not_to_refer.append('Current drug or alcohol abuse.')
        next_steps_not_to_refer.extend(['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
    
    if st.session_state.homeless:
        reasons_not_to_refer.append('Patient is homeless (high risk of infection).')
        next_steps_not_to_refer.extend(['Address housing situation before referral can be considered.'])
    
    if st.session_state.noSupport:
        reasons_not_to_refer.append('No social support system.')
        next_steps_not_to_refer.extend(['Patient needs to establish a reliable social support system before referral.'])
    
    if st.session_state.noncompliance:
        reasons_not_to_refer.append('Missed Dialysis >50%.')
        next_steps_not_to_refer.extend(['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'])

    # --- Step 1b: Aggregate Contraindications ---
    if reasons_not_to_refer:
        st.session_state.screening_result = {
            'decision': 'Do Not Refer',
            'reasons': reasons_not_to_refer,
            'nextSteps': next_steps_not_to_refer
        }
        return

    # --- Step 2: Check for Referral Qualifications ---
    egfr_value = st.session_state.egfr

    if st.session_state.onDialysis:
        st.session_state.screening_result = {
            'decision': 'Refer',
            'reason': 'Patient is currently on dialysis.',
            'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
        }
        return

    if egfr_value is not None:
        if egfr_value <= 20:
            st.session_state.screening_result = {
                'decision': 'Refer',
                'reason': f'Lowest eGFR is {egfr_value}, which is <= 20.',
                'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
            }
            return
        
        if 20 < egfr_value <= 25 and st.session_state.hasUremia:
            st.session_state.screening_result = {
                'decision': 'Refer',
                'reason': 'Lowest eGFR is between 20-25 and have signs of uremia.',
                'nextSteps': ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
            }
            return

    # --- Step 3: If no criteria met ---
    st.session_state.screening_result = {
        'decision': 'Do Not Refer',
        'reason': 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.',
        'nextSteps': ['Continue to monitor patient as per standard CKD management protocols.']
    }

# --- UI Display Functions ---

def display_result():
    """
    Renders the result from session_state using st.success or st.error,
    matching the style of the React ResultCard.
    """
    result = st.session_state.screening_result
    if not result:
        return

    if result['decision'] == 'Refer':
        # Use st.success for the green "Refer" card
        with st.success(""):
            # The icon parameter is not used inside 'with' block,
            # so we use markdown for the header.
            st.markdown(f"### <span style='font-size: 1.25em;'>✅ Refer to Transplant</span>", unsafe_allow_html=True)
            
            # Display Reason(s)
            if result.get('reason'):
                st.markdown(f"**Reason:** {result['reason']}")
            if result.get('reasons'):
                st.markdown("**Reasons:**")
                for r in result['reasons']:
                    st.markdown(f"- {r}")

            # Display Next Steps
            if result.get('nextSteps'):
                st.markdown("---")  # Horizontal line divider
                st.markdown("**Next Steps:**")
                for step in result['nextSteps']:
                    st.markdown(f"- {step}")
    
    elif result['decision'] == 'Do Not Refer':
        # Use st.error for the red "DoNot Refer" card
        with st.error(""):
            st.markdown(f"### <span style='font-size: 1.25em;'>❌ Do Not Refer</span>", unsafe_allow_html=True)
            
            # Display Reason(s)
            if result.get('reason'):
                st.markdown(f"**Reason:** {result['reason']}")
            if result.get('reasons'):
                st.markdown("**Reasons:**")
                for r in result['reasons']:
                    st.markdown(f"- {r}")

            # Display Next Steps
            if result.get('nextSteps'):
                st.markdown("---")  # Horizontal line divider
                st.markdown("**Next Steps:**")
                for step in result['nextSteps']:
                    st.markdown(f"- {step}")

# --- Main Application ---

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="Kidney Transplant Screener",
    page_icon=" kidneys:",
    layout="centered"
)

# Initialize the session state
initialize_state()

# --- Header ---
st.title("Sanford Transplant Center, Fargo")
st.header("Kidney Transplant Referral Screener")

# We use st.container with a border to mimic the "Card" layout
with st.container(border=True):
    st.subheader("Patient Information")

    # Display error message if it exists in session state
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    # Create the form
    with st.form(key="screener_form"):
        col1, col2 = st.columns(2)

        # --- Left Column ---
        with col1:
            st.number_input(
                "Lowest eGFR",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                placeholder="e.g., 18",
                key="egfr"  # Link to session state
            )
            st.number_input(
                "HgbA1c (%)",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                placeholder="e.g., 7.5 (Optional)",
                key="hgbA1c"
            )
            st.number_input(
                "Ejection Fraction on last ECHO (%)",
                min_value=0.0,
                step=0.1,
                format="%.1f",
                placeholder="e.g., 55 (Optional)",
                key="ejectionFraction"
            )
            st.checkbox("Patient is on Dialysis", key="onDialysis")
            st.checkbox(
                "Signs of Uremia (must be in MD note)",
                key="hasUremia",
                help="Required if Lowest eGFR is > 20 and <= 25"
            )

        # --- Right Column ---
        with col2:
            st.markdown("**Current History**")
            st.checkbox("Requires Home O2", key="homeO2")
            st.checkbox("Current Active Smoker", key="smoker")
            st.checkbox("Active Cancer", key="cancer")
            st.checkbox("Active Infectious Disease", key="infection")
            st.checkbox("Current Drug/Alcohol Abuse", key="abuse")
            st.checkbox("Homeless", key="homeless")
            st.checkbox("No Social Support", key="noSupport")
            st.checkbox("Missed Dialysis >50%", key="noncompliance")

        # --- Form Buttons ---
        btn_col_1, btn_col_2, _ = st.columns([1, 1, 3])
        submit_button = btn_col_1.form_submit_button("Evaluate", type="primary")
        reset_button = btn_col_2.form_submit_button("Reset")

# --- Button Logic ---
# Handle button presses *after* the form is defined
if reset_button:
    reset_form()
    st.rerun()  # Rerun the script to show the cleared form

if submit_button:
    evaluate_screening()

# --- Display Results ---
# This function will check session_state and display if a result exists
display_result()


# --- Footer ---
st.caption("---") # Visual separator
st.caption(
    "**Disclaimer:** The information and results provided by this tool are for "
    "guidance only and are not a substitute for professional medical advice, "
    "diagnosis, or treatment. All referral decisions must be made by "
    "qualified medical personnel based on a comprehensive evaluation of the patient."
)
st.caption(
    "© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. "
    "All Rights Reserved."
)
