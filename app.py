import streamlit as st

def display_result(decision, reasons, next_steps):
    """
    Helper function to display the result in a styled box.
    This version is updated to accept a list of reasons.
    """
    if decision == 'Refer':
        st.success(f"**Decision: {decision} to Transplant**")
    else:
        st.error(f"**Decision: {decision}**")

    # Check if 'reasons' is a list or a single string
    if isinstance(reasons, list):
        if len(reasons) > 0:
            st.markdown("**Reasons:**")
            st.markdown("\n".join([f"- {r}" for r in reasons]))
    else:
        # It's a single string
        st.write(f"**Reason:** {reasons}")

    if next_steps:
        st.markdown("**Next Steps:**")
        st.markdown("\n".join([f"- {step}" for step in next_steps]))

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
        hgbA1c = st.number_input("HgbA1c (%) if Diabetic", value=None, placeholder="e.g., 7.5 (Optional)", step=0.1)
        ejection_fraction = st.number_input("Ejection Fraction on last ECHO (%)", value=None, placeholder="e.g., 55 (Optional)", step=1.0)
        
        st.markdown("---")
        on_dialysis = st.checkbox("Patient is on Dialysis")
        has_uremia = st.checkbox(
            "Signs of Uremia (must be in MD note)", 
            help="Required if Lowest eGFR is > 20 and <= 25"
        )

    with col2:
        st.subheader("Current History")
        home_o2 = st.checkbox("Requires Home O2")
        smoker = st.checkbox("Current Active Smoker (>= 1 pack per day)")
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
        st.error('**Error:** Please enter a Lowest eGFR value or check if the patient is on dialysis.')
    
    else:
        # Arrays to collect all "Do Not Refer" reasons
        reasons_not_to_refer = []
        next_steps_not_to_refer = [] # This will be a list of lists

        # --- Step 1: Check for Absolute Contraindications ---
        # These checks will now collect reasons instead of returning immediately
        
        # Check numerical inputs (only if they are not empty)
        if hgbA1c is not None and hgbA1c > 10:
            reasons_not_to_refer.append(f"HgbA1c is {hgbA1c}%.")
            next_steps_not_to_refer.append(['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10'])
        
        if ejection_fraction is not None and ejection_fraction < 15:
            reasons_not_to_refer.append(f"Ejection Fraction is {ejection_fraction}%.")
            next_steps_not_to_refer.append(['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral'])
        
        # Check all boolean contraindications
        if home_o2:
            reasons_not_to_refer.append('Patient requires home O2.')
            next_steps_not_to_refer.append(['Refer to Pulmonologist for optimization.'])
        
        if smoker:
            reasons_not_to_refer.append('Current active smoker.')
            next_steps_not_to_refer.append(['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.'])
        
        if cancer:
            reasons_not_to_refer.append('Active cancer diagnosis.')
            next_steps_not_to_refer.append(['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.'])
        
        if infection:
            reasons_not_to_refer.append('Active infectious disease.')
            next_steps_not_to_refer.append(['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics'])
        
        if abuse:
            reasons_not_to_refer.append('Current drug or alcohol abuse.')
            next_steps_not_to_refer.append(['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.'])
        
        if homeless:
            reasons_not_to_refer.append('Patient is homeless (high risk of infection).')
            next_steps_not_to_refer.append(['Address housing situation before referral can be considered.'])
        
        if no_support:
            reasons_not_to_refer.append('No social support system.')
            next_steps_not_to_refer.append(['Patient needs to establish a reliable social support system before referral.'])
        
        if noncompliance:
            reasons_not_to_refer.append('Missed Dialysis >50%.')
            next_steps_not_to_refer.append(['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.'])
        

        # --- Step 1b: Aggregate Contraindications ---
        # If we found any contraindications, set that as the result and stop.
        if len(reasons_not_to_refer) > 0:
            # Flatten the list of next_steps lists
            flat_next_steps = [step for sublist in next_steps_not_to_refer for step in sublist]
            display_result('Do Not Refer', reasons_not_to_refer, flat_next_steps)
        
        else:
            # --- Step 2: Check for Referral Qualifications ---
            # This part only runs if NO contraindications were found
            
            if on_dialysis:
                display_result(
                    'Refer', 
                    'Patient is currently on dialysis.', 
                    ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                )
            
            elif egfr is not None:
                if egfr <= 20:
                    display_result(
                        'Refer', 
                        f'Lowest eGFR is {egfr}, which is <= 20.', 
                        ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                    )
                
                elif (egfr > 20 and egfr <= 25) and has_uremia:
                    display_result(
                        'Refer', 
                        'Lowest eGFR is between 20-25 and have signs of uremia.', 
                        ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.']
                    )
                
                else:
                    # --- Step 3: If no criteria met ---
                    display_result(
                        'Do Not Refer', 
                        'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', 
                        ['Continue to monitor patient as per standard CKD management protocols.']
                    )
            else:
                # This should be caught by validation, but serves as a fallback
                display_result(
                        'Do Not Refer', 
                        'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', 
                        ['Continue to monitor patient as per standard CKD management protocols.']
                    )


# --- Footer ---
st.markdown("---")
st.caption("""
**Disclaimer:** The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.

© 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.
""")
