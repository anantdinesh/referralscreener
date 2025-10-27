import streamlit as st

# --- Initialize Session State ---
# This holds the output of the screening, much like React's `useState`
if 'screening_result' not in st.session_state:
    st.session_state.screening_result = None
if 'error' not in st.session_state:
    st.session_state.error = ""

# --- Logic Functions ---
# These functions modify the session state, triggered by button clicks.

def handle_screening():
    """
    Runs the screening logic based on values in st.session_state.
    Updates st.session_state.screening_result and st.session_state.error.
    """
    st.session_state.error = ""  # Clear previous errors
    st.session_state.screening_result = None # Clear previous results

    # --- Step 0: Validation ---
    # Get values from session_state (populated by widgets)
    egfr = st.session_state.get('egfr')
    on_dialysis = st.session_state.get('on_dialysis', False)

    if not egfr and not on_dialysis:
        st.session_state.error = 'Please enter a Lowest eGFR value or check if the patient is on dialysis.'
        return

    # Get optional values
    hgb_a1c = st.session_state.get('hgb_a1c')
    ef = st.session_state.get('ejection_fraction')

    # Arrays to collect all "Do Not Refer" reasons
    reasons_not_to_refer = []
    next_steps_not_to_refer = []

    # --- Step 1: Check for Absolute Contraindications ---
    if hgb_a1c is not None and hgb_a1c > 10:
        reasons_not_to_refer.append(f"HgbA1c is {hgb_a1c}%.")
        next_steps_not_to_refer.append(['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'])

    if ef is not None and ef < 15:
        reasons_not_to_refer.append(f"Ejection Fraction is {ef}%.")
        next_steps_not_to_refer.append(['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])

    # Check all contraindication checkboxes
    if st.session_state.get('homeO2', False):
        reasons_not_to_refer.append('Patient requires home O2.')
        next_steps_not_to_refer.append(['Refer to Pulmonologist for optimization.'])
    
    if st.session_state.get('smoker', False):
        reasons_not_to_refer.append('Current active smoker.')
        next_steps_not_to_refer.append(['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
    
    if st.session_state.get('cancer', False):
        reasons_not_to_refer.append('Active cancer diagnosis.')
        next_steps_not_to_refer.append(['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
    
    if st.session_state.get('infection', False):
        reasons_not_to_refer.append('Active infectious disease.')
        next_steps_not_to_refer.append(['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'])
    
    if st.session_state.get('abuse', False):
        reasons_not_to_refer.append('Current drug or alcohol abuse.')
        next_steps_not_to_refer.append(['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
    
    if st.session_state.get('homeless', False):
        reasons_not_to_refer.append('Patient is homeless (high risk of infection).')
        next_steps_not_to_refer.append(['Address housing situation before referral can be considered.'])
    
    if st.session_state.get('noSupport', False):
        reasons_not_to_refer.append('No social support system.')
        next_steps_not_to_refer.append(['Patient needs to establish a reliable social support system before referral.'])
    
    if st.session_state.get('noncompliance', False):
        reasons_not_to_refer.append('Missed Dialysis >50%.')
        next_steps_not_to_refer.append(['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'])

    # --- Step 1b: Aggregate Contraindications ---
    if reasons_not_to_refer:
        # Flatten the next_steps list
        flat_next_steps = [step for sublist in next_steps_not_to_refer for step in sublist]
        st.session_state.screening_result = {
            'decision': 'Do Not Refer',
            'reasons': reasons_not_to_refer,
            'nextSteps': flat_next_steps
        }
        return

    # --- Step 2: Check for Referral Qualifications ---
    # This part only runs if NO contraindications were found
    has_uremia = st.session_state.get('has_uremia', False)

    if on_dialysis:
        st.session_state.screening_result = {
            'decision': 'Refer',
            'reason': 'Patient is currently on dialysis.',
            'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
        }
        return

    if egfr is not None:
        if egfr <= 20:
            st.session_state.screening_result = {
                'decision': 'Refer',
                'reason': f'Lowest eGFR is {egfr}, which is <= 20.',
                'nextSteps': ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
            }
            return
        if 20 < egfr <= 25 and has_uremia:
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

def handle_reset():
    """
    Resets all input widgets and output states to their defaults.
    """
    # Reset all input widget states by setting their keys
    st.session_state.egfr = None
    st.session_state.on_dialysis = False
    st.session_state.has_uremia = False
    st.session_state.hgb_a1c = None
    st.session_state.ejection_fraction = None
    st.session_state.homeO2 = False
    st.session_state.smoker = False
    st.session_state.cancer = False
    st.session_state.infection = False
    st.session_state.abuse = False
    st.session_state.homeless = False
    st.session_state.noSupport = False
    st.session_state.noncompliance = False
    
    # Reset output states
    st.session_state.screening_result = None
    st.session_state.error = ""


def display_result():
    """
    Renders the ResultCard equivalent using st.success or st.error
    based on the content of st.session_state.screening_result.
    """
    result = st.session_state.screening_result
    if not result:
        return

    is_referral = result['decision'] == 'Refer'
    
    if is_referral:
        with st.success(f"**Decision: {result['decision']} to Transplant**", icon="✅"):
            if result.get('reason'):
                st.write(result['reason'])
            
            if result.get('nextSteps'):
                st.divider()
                st.markdown("**Next Steps:**")
                for step in result['nextSteps']:
                    st.markdown(f"- {step}")
    else:
        with st.error(f"**Decision: {result['decision']}**", icon="❌"):
            # Handle single reason (string) or multiple (array)
            if result.get('reason'):
                st.write(result['reason'])
            elif result.get('reasons'):
                st.markdown("**Reasons:**")
                for r in result['reasons']:
                    st.markdown(f"- {r}")

            if result.get('nextSteps'):
                st.divider()
                st.markdown("**Next Steps:**")
                for step in result['nextSteps']:
                    st.markdown(f"- {step}")

# --- Main App Layout ---

st.set_page_config(page_title="Kidney Transplant Screener", layout="centered")

# Header
st.title("Sanford Transplant Center, Fargo")
st.subheader("Kidney Transplant Referral Screener")

# Input Card
with st.container(border=True):
    st.subheader("Patient Information")

    # Display error if it exists
    if st.session_state.error:
        st.error(st.session_state.error)

    col1, col2 = st.columns(2)

    with col1:
        st.number_input(
            "Lowest eGFR", 
            key="egfr", 
            value=None, 
            placeholder="e.g., 18", 
            format="%f",
            step=1.0
        )
        st.number_input(
            "HgbA1c (%)", 
            key="hgb_a1c", 
            value=None, 
            placeholder="e.g., 7.5", 
            format="%.1f",
            step=0.1
        )
        st.number_input(
            "Ejection Fraction on last ECHO (%)", 
            key="ejection_fraction", 
            value=None, 
            placeholder="e.g., 55", 
            format="%f",
            step=1.0
        )
        st.checkbox("Patient is on Dialysis", key="on_dialysis")
        st.checkbox(
            "Signs of Uremia (must be in MD note)", 
            key="has_uremia", 
            help="Required if Lowest eGFR is > 20 and <= 25"
        )
    
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

    # Buttons
    # We use columns to right-align the buttons, similar to `justify-end`
    st.divider()
    _, btn_col1, btn_col2 = st.columns([2, 1, 1])
    
    with btn_col1:
        st.button(
            "Reset", 
            on_click=handle_reset, 
            use_container_width=True
        )
    with btn_col2:
        st.button(
            "Evaluate", 
            on_click=handle_screening, 
            type="primary", 
            use_container_width=True
        )

# Result Card
# This function will only display if st.session_state.screening_result is not None
display_result()

# Footer
st.divider()
st.caption(
    "**Disclaimer:** The information and results provided by this tool are for guidance only and "
    "are not a substitute for professional medical advice, diagnosis, or treatment. All referral "
    "decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient."
)
st.caption("© 2025 Anant Dinesh MD MS, Transplant Surgeon - Sanford Transplant Center, Fargo. All Rights Reserved.")
