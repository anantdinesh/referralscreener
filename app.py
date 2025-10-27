import React, { useState } from 'react';

// --- Helper Components ---
const Card = ({ children, className }) => (
  <div className={`bg-white rounded-2xl shadow-lg p-6 sm:p-8 ${className}`}>
    {children}
  </div>
);

const Checkbox = ({ id, label, checked, onChange, helpText }) => (
  <div className="flex items-start">
    <div className="flex items-center h-5">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
      />
    </div>
    <div className="ml-3 text-sm">
      <label htmlFor={id} className="font-medium text-gray-700">{label}</label>
      {helpText && <p className="text-gray-500">{helpText}</p>}
    </div>
  </div>
);

const ResultCard = ({ result }) => {
    if (!result) return null;

    const isReferral = result.decision === 'Refer';
    const bgColor = isReferral ? 'bg-green-50' : 'bg-red-50';
    const textColor = isReferral ? 'text-green-800' : 'text-red-800';
    const ringColor = isReferral ? 'ring-green-600/20' : 'ring-red-600/20';
    const icon = isReferral ? (
        <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    ) : (
        <svg className="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    );

    return (
        <Card className={`${bgColor} ring-1 ${ringColor}`}>
            <div className="flex items-start gap-4">
                <div>{icon}</div>
                <div className="flex-1">
                    <h3 className={`text-2xl font-bold ${textColor}`}>{result.decision} to Transplant</h3>
                    
                    {/* Display Reason(s) */}
                    <div className="mt-2">
                        {result.reason && (
                            <>
                                <h4 className="font-semibold text-gray-800">Reason:</h4>
                                <p className={`mt-1 text-md ${textColor}`}>{result.reason}</p>
                            </>
                        )}
                        {result.reasons && result.reasons.length > 0 && (
                            <>
                                <h4 className="font-semibold text-gray-800">Reasons:</h4>
                                <ul className={`list-disc list-inside mt-1 text-md ${textColor} space-y-1`}>
                                    {result.reasons.map((r, i) => <li key={i}>{r}</li>)}
                                </ul>
                            </>
                        )}
                    </div>
                </div>
            </div>
            {result.nextSteps && result.nextSteps.length > 0 && (
                 <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-800">Next Steps:</h4>
                    <ul className="list-disc list-inside mt-2 text-gray-700 space-y-1">
                       {result.nextSteps.map((step, index) => <li key={index}>{step}</li>)}
                    </ul>
                 </div>
            )}
        </Card>
    );
};

const InputField = ({ id, label, value, onChange, placeholder, type = "number", required = false }) => (
    <div>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700">{label}</label>
        <input
            type={type}
            id={id}
            value={value}
            onChange={onChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder={placeholder}
            required={required}
        />
    </div>
);


export default function App() {
  const [egfr, setEgfr] =useState('');
  const [onDialysis, setOnDialysis] = useState(false);
  const [hasUremia, setHasUremia] = useState(false);
  const [hgbA1c, setHgbA1c] = useState('');
  const [ejectionFraction, setEjectionFraction] = useState('');

  const [contraindications, setContraindications] = useState({
    homeO2: false,
    smoker: false,
    cancer: false,
    infection: false,
    abuse: false,
    homeless: false,
    noSupport: false,
    noncompliance: false,
  });

  const [screeningResult, setScreeningResult] = useState(null);
  const [error, setError] = useState('');

  const handleCheckboxChange = (e) => {
    const { id, checked } = e.target;
    setContraindications({ ...contraindications, [id]: checked });
  };

  const handleScreening = () => {
    setError(''); // Clear previous errors
    // --- Step 0: Validation ---
    if (!egfr && !onDialysis) {
        setError('Please enter a Lowest eGFR value or check if the patient is on dialysis.');
        setScreeningResult(null);
        return;
    }

    const hgbA1cValue = parseFloat(hgbA1c);
    const efValue = parseFloat(ejectionFraction);

    // Arrays to collect all "Do Not Refer" reasons
    let reasonsNotToRefer = [];
    let nextStepsNotToRefer = [];

    // --- Step 1: Check for Absolute Contraindications ---
    // These checks will now collect reasons instead of returning immediately
    if (hgbA1cValue > 10) {
      reasonsNotToRefer.push(`HgbA1c is ${hgbA1cValue}%.`);
      nextStepsNotToRefer.push(['Work with Primary Medical Doctor/Endocrinologist, transplant refer after HbA1C<10']);
    }
    if (efValue < 15) {
      reasonsNotToRefer.push(`Ejection Fraction is ${efValue}%.`);
      nextStepsNotToRefer.push(['Consult with cardiology to evaluate for reversible causes of low EF and optimization before transplant referral']);
    }
     if (contraindications.homeO2) {
      reasonsNotToRefer.push('Patient requires home O2.');
      nextStepsNotToRefer.push(['Refer to Pulmonologist for optimization.']);
    }
    if (contraindications.smoker) {
      reasonsNotToRefer.push('Current active smoker.');
      nextStepsNotToRefer.push(['Enter a referral to Tobacco Cessation.', 'Can be re-referred after abstaining for 6 months.']);
    }
    if (contraindications.cancer) {
      reasonsNotToRefer.push('Active cancer diagnosis.');
      nextStepsNotToRefer.push(['Referral can be reconsidered after treatment and appropriate cancer-free period as determined by an oncologist.']);
    }
     if (contraindications.infection) {
      reasonsNotToRefer.push('Active infectious disease.');
      nextStepsNotToRefer.push(['Consult Infectious Disease refer after resolution of active infection and completion of course of antibiotics']);
    }
    if (contraindications.abuse) {
      reasonsNotToRefer.push('Current drug or alcohol abuse.');
      nextStepsNotToRefer.push(['Enter CD Eval for First Step (651-925-0057).', 'Can be re-referred when treatment is complete, and we have documentation from First Step.']);
    }
    if (contraindications.homeless) {
      reasonsNotToRefer.push('Patient is homeless (high risk of infection).');
      nextStepsNotToRefer.push(['Address housing situation before referral can be considered.']);
    }
    if (contraindications.noSupport) {
      reasonsNotToRefer.push('No social support system.');
      nextStepsNotToRefer.push(['Patient needs to establish a reliable social support system before referral.']);
    }
    if (contraindications.noncompliance) {
      reasonsNotToRefer.push('Missed Dialysis >50%.');
      nextStepsNotToRefer.push(['Patient must demonstrate compliance with dialysis attendance for 6 months before re-referral.']);
    }
    
    // --- Step 1b: Aggregate Contraindications ---
    // If we found any contraindications, set that as the result and stop.
    if (reasonsNotToRefer.length > 0) {
        setScreeningResult({
            decision: 'Do Not Refer',
            reasons: reasonsNotToRefer, // Pass reasons as an array
            nextSteps: nextStepsNotToRefer.flat() // Flatten all next steps arrays
        });
        return;
    }

    // --- Step 2: Check for Referral Qualifications ---
    // This part only runs if NO contraindications were found
    const egfrValue = parseFloat(egfr);

    if (onDialysis) {
        setScreeningResult({ decision: 'Refer', reason: 'Patient is currently on dialysis.', nextSteps: ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] });
        return;
    }

    if (!isNaN(egfrValue)) {
        if (egfrValue <= 20) {
            setScreeningResult({ decision: 'Refer', reason: `Lowest eGFR is ${egfrValue}, which is <= 20.`, nextSteps: ['Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] });
            return;
        }
        if (egfrValue > 20 && egfrValue <= 25 && hasUremia) {
            setScreeningResult({ decision: 'Refer', reason: `Lowest eGFR is between 20-25 and have signs of uremia.`, nextSteps: ['Ensure uremia signs are stated in MD note.', 'Refer for Transplant to Sanford Transplant Center, Fargo using EPIC Transplant Services Referral or fax referral sheet to 701-234-7341.', 'For more information, call 701-234-6715.'] });
            return;
        }
    }
    
    // --- Step 3: If no criteria met ---
    setScreeningResult({ decision: 'Do Not Refer', reason: 'Patient does not meet the Lowest eGFR or dialysis criteria for referral at this time.', nextSteps: ['Continue to monitor patient as per standard CKD management protocols.'] });
  };

  const handleReset = () => {
      setEgfr('');
      setOnDialysis(false);
      setHasUremia(false);
      setHgbA1c('');
      setEjectionFraction('');
      setContraindications({
        homeO2: false, smoker: false, cancer: false, 
        infection: false, abuse: false, homeless: false, noSupport: false, noncompliance: false,
      });
      setScreeningResult(null);
      setError('');
  };

  return (
    <div className="bg-gray-100 min-h-screen font-sans text-gray-900 relative">
      <div 
        className="absolute inset-0 bg-no-repeat bg-center bg-contain opacity-5 pointer-events-none"
        style={{ backgroundImage: "url('https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Kidney_illustration.svg/1200px-Kidney_illustration.svg.png')" }}
        aria-hidden="true"
      ></div>
      <div className="container mx-auto p-4 sm:p-6 md:p-8 max-w-4xl relative z-10">
        <header className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4">Sanford Transplant Center, Fargo</h1>
            <h2 className="text-2xl text-gray-600">Kidney Transplant Referral Screener</h2>
        </header>
        
        <div className="space-y-8">
            <Card>
                <h3 className="text-xl font-semibold text-gray-800 border-b pb-3 mb-6">Patient Information</h3>
                {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">{error}</div>}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                    <div className="space-y-4">
                       <InputField id="egfr" label="Lowest eGFR" value={egfr} onChange={(e) => setEgfr(e.target.value)} placeholder="e.g., 18" required />
                       <InputField id="hgbA1c" label="HgbA1c (%)" value={hgbA1c} onChange={(e) => setHgbA1c(e.target.value)} placeholder="e.g., 7.5 (Optional)" />
                       <InputField id="ejectionFraction" label="Ejection Fraction on last ECHO (%)" value={ejectionFraction} onChange={(e) => setEjectionFraction(e.target.value)} placeholder="e.g., 55 (Optional)" />
                       <Checkbox id="onDialysis" label="Patient is on Dialysis" checked={onDialysis} onChange={(e) => setOnDialysis(e.target.checked)} />
                       <Checkbox id="hasUremia" label="Signs of Uremia (must be in MD note)" checked={hasUremia} onChange={(e) => setHasUremia(e.target.checked)} helpText="Required if Lowest eGFR is > 20 and <= 25" />
                    </div>
                    <div className="space-y-4 md:pl-6 md:border-l">
                         <h4 className="font-semibold text-gray-600">Current History</h4>
                         <Checkbox id="homeO2" label="Requires Home O2" checked={contraindications.homeO2} onChange={handleCheckboxChange} />
                         <Checkbox id="smoker" label="Current Active Smoker" checked={contraindications.smoker} onChange={handleCheckboxChange} />
                         <Checkbox id="cancer" label="Active Cancer" checked={contraindications.cancer} onChange={handleCheckboxChange} />
                         <Checkbox id="infection" label="Active Infectious Disease" checked={contraindications.infection} onChange={handleCheckboxChange} />
                         <Checkbox id="abuse" label="Current Drug/Alcohol Abuse" checked={contraindications.abuse} onChange={handleCheckboxChange} />
                         <Checkbox id="homeless" label="Homeless" checked={contraindications.homeless} onChange={handleCheckboxChange} />
                         <Checkbox id="noSupport" label="No Social Support" checked={contraindications.noSupport} onChange={handleCheckboxChange} />
                         <Checkbox id="noncompliance" label="Missed Dialysis >50%" checked={contraindications.noncompliance} onChange={handleCheckboxChange} />
                    </div>
                </div>
                 <div className="mt-8 flex justify-end space-x-4">
                    <button type="button" onClick={handleReset} className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Reset
                    </button>
                    <button type="button" onClick={handleScreening} className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Evaluate
                    </button>
                </div>
            </Card>

            <ResultCard result={screeningResult} />

        </div>
        <footer className="text-center mt-12 text-gray-500 text-sm space-y-2">
            <p><strong>Disclaimer:</strong> The information and results provided by this tool are for guidance only and are not a substitute for professional medical advice, diagnosis, or treatment. All referral decisions must be made by qualified medical personnel based on a comprehensive evaluation of the patient.</p>
            <p>&copy; 2025 Anant Dinesh, MD Transplant Surgeon Sanford Transplant Center, Fargo. All Rights Reserved.</p>
        </footer>
      </div>
    </div>
  );
}

