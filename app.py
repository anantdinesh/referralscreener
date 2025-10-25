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
        st.checkbox("Active
