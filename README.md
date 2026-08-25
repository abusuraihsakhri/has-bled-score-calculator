# HAS-BLED Score Calculator

A Python CLI tool for calculating the HAS-BLED bleeding risk score in atrial fibrillation patients on anticoagulation therapy.

## What is HAS-BLED?

HAS-BLED is a validated clinical scoring system that estimates the annual risk of major bleeding in patients with atrial fibrillation who are on oral anticoagulation. It was developed by Lip et al. (2010) and is recommended by ESC guidelines for bleeding risk assessment.

**Score range:** 0-9 points

### Risk Factors

| Letter | Factor | Points | Modifiable? |
|--------|--------|--------|-------------|
| **H** | Hypertension (uncontrolled, SBP >160 mmHg) | +1 | Yes |
| **A** | Abnormal renal function (dialysis, transplant, Cr >2.26 mg/dL) | +1 | Yes |
| **A** | Abnormal liver function (cirrhosis, elevated LFTs) | +1 | Yes |
| **S** | Stroke history | +1 | No |
| **B** | Bleeding history or predisposition (prior major bleed, anemia) | +1 | No |
| **L** | Labile INR (<60% time in therapeutic range) | +1 | Yes |
| **E** | Elderly (age >65) | +1 | No |
| **D** | Drugs (antiplatelet agents, NSAIDs) | +1 | Yes |
| **D** | Alcohol (≥8 drinks/week) | +1 | Yes |

### Annual Bleeding Risk

| Score | Risk Level | Annual Bleeding Risk |
|-------|------------|---------------------|
| 0 | Low | 1.13% |
| 1 | Low | 1.02% |
| 2 | Moderate | 1.88% |
| 3 | High | 3.74% |
| 4 | High | 8.70% |
| 5 | High | 12.50% |
| ≥6 | Very High | ~12.50%+ |

### Clinical Guidance

- **Score 0-2:** Anticoagulation generally safe. Regular review recommended.
- **Score ≥3:** High risk. Address modifiable factors (control BP, improve INR control, avoid NSAIDs, reduce alcohol). More frequent monitoring. Score ≥3 does **NOT** contraindicate anticoagulation but warrants caution.

## Installation

No dependencies required. Python 3.8+ stdlib only.

```bash
git clone <repo-url>
cd has-bled-score-calculator
```

## Usage

### Calculate HAS-BLED Score

```bash
# Minimal example: elderly patient on NSAIDs
python cli.py score --elderly --drugs

# High-risk patient with multiple factors
python cli.py score --hypertension --renal --liver --stroke --bleeding --labile-inr --elderly --drugs --alcohol

# JSON output
python cli.py score --hypertension --renal --elderly --json
```

### Combined Assessment (HAS-BLED + CHA₂DS₂-VASc)

```bash
# Patient with HAS-BLED 3 and CHA₂DS₂-VASc 4
python cli.py assess --hasbled 3 --chadsvasc 4

# Low-risk patient
python cli.py assess --hasbled 1 --chadsvasc 0
```

### Modified HAS-BLED (Extended Criteria)

```bash
# Include anemia and thrombocytopenia
python cli.py modified --hypertension --renal --anemia --low-platelets
```

## Python API

```python
from has_bled import calculate_score, assess_with_chadsvasc, calculate_modified_score

# Basic score
result = calculate_score(hypertension=True, renal=True, elderly=True, drugs=True)
print(result["score"])           # 4
print(result["risk_level"])      # "High"
print(result["modifiable"])      # ["Hypertension", "Abnormal renal function", "Drugs (antiplatelet/NSAIDs)"]

# Combined assessment
assessment = assess_with_chadsvasc(hasbled_score=3, chadsvasc_score=4)
print(assessment["recommendation"])

# Modified score with extra factors
mod = calculate_modified_score(hypertension=True, renal=True, anemia=True)
print(mod["modified_score"])     # 3
```

## Important Disclaimers

- This tool is for **educational and clinical decision support purposes only**.
- It does **not** replace clinical judgment or guideline-directed care.
- HAS-BLED is designed for patients with atrial fibrillation on anticoagulation.
- A high HAS-BLED score does **not** contraindicate anticoagulation.
- Always consider the individual patient context and shared decision-making.

## References

1. Lip GY, Nieuwlaat R, Pisters R, Lane DA, Crijns HJ. Refining clinical risk stratification for predicting stroke and thromboembolism in atrial fibrillation using a novel risk factor-based approach: the Euro Heart Survey on Atrial Fibrillation. *Chest*. 2010;138(5):1093-1100.
2. Hindricks G, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. *Eur Heart J*. 2021;42(5):373-498.

## License

MIT License. See [LICENSE](LICENSE).
