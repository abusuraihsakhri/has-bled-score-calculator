# HAS-BLED Score Calculator

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines:** AHA/ACC Practice Guidelines & ESC Clinical Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)

</div>

---

## What It Does

HAS-BLED Score Calculator for Major Bleeding Risk in Atrial Fibrillation.

Validates bleeding risk in AF patients on anticoagulation therapy.
Score range: 0-9 points. Pure Python, stdlib only — no external dependencies.

Reference: Lip GY, et al. "A novel user-friendly score (HAS-BLED) to assess
1-year risk of major bleeding in patients with atrial fibrillation."
Chest. 2010;138(5):1093-1100.

---

## Installation

No installation required beyond Python 3.10+. Clone the repository and run directly:

```bash
git clone https://github.com/abusuraihsakhri/has-bled-score-calculator.git
cd has-bled-score-calculator
```

---

## Usage

### 1. Calculate HAS-BLED Score (standard)

```bash
# Score with specific risk factors
python cli.py score --hypertension --renal --elderly --drugs

# Output as JSON
python cli.py score --hypertension --json

# All risk factors
python cli.py score --hypertension --renal --liver --stroke --bleeding --labile-inr --elderly --drugs --alcohol
```

### 2. Combined Assessment with CHA₂DS₂-VASc

```bash
python cli.py assess --hasbled 3 --chadsvasc 4

# Output as JSON
python cli.py assess --hasbled 2 --chadsvasc 5 --json
```

### 3. Modified HAS-BLED (extended criteria)

Includes additional criteria: anemia and thrombocytopenia (score range 0-11).

```bash
python cli.py modified --hypertension --anemia

# Output as JSON
python cli.py modified --hypertension --renal --anemia --low-platelets --json
```

### 4. Python API

```python
from has_bled import calculate_score, assess_with_chadsvasc, calculate_modified_score

# Calculate standard HAS-BLED score
result = calculate_score(hypertension=True, renal=True, elderly=True)
print(result["score"])           # 3
print(result["risk_level"])      # "High"
print(result["annual_bleeding_risk"])  # 3.74

# Combined assessment
assessment = assess_with_chadsvasc(hasbled_score=3, chadsvasc_score=4)
print(assessment["recommendation"])

# Modified HAS-BLED
modified = calculate_modified_score(hypertension=True, anemia=True)
print(modified["modified_score"])  # 2
```

---

## CLI Parameters

### `score` subcommand

| Flag | Description |
|------|-------------|
| `--hypertension` | Uncontrolled SBP >160 mmHg |
| `--renal` | Abnormal renal function (dialysis/transplant/Cr >2.26 mg/dL) |
| `--liver` | Abnormal liver function (cirrhosis/elevated LFTs) |
| `--stroke` | Prior stroke or TIA |
| `--bleeding` | Bleeding history or predisposition |
| `--labile-inr` | Labile/unstable INR (<60% TTR) |
| `--elderly` | Age >65 years |
| `--drugs`, `--nsaids` | Antiplatelet agents or NSAIDs |
| `--alcohol` | ≥8 drinks per week |
| `--json` | Output as JSON |

### `assess` subcommand

| Flag | Description |
|------|-------------|
| `--hasbled` | HAS-BLED score (0-9) |
| `--chadsvasc` | CHA₂DS₂-VASc score (0-9) |
| `--json` | Output as JSON |

### `modified` subcommand

All standard flags plus:

| Flag | Description |
|------|-------------|
| `--anemia` | Anemia (Hb <12 g/dL women, <13 g/dL men) |
| `--low-platelets` | Thrombocytopenia (platelets <150×10⁹/L) |

---

## Testing

Run the automated test suite:

```bash
python -m pytest test_hasbled.py -v
```

Tests cover:
- Score calculation across all risk levels (0-9)
- Category breakdown (H, A, S, B, L, E, D)
- Modifiable vs non-modifiable factor identification
- CHA₂DS₂-VASc integration
- Modified HAS-BLED scoring
- CLI output formatting and JSON mode
- Input validation and edge cases

---

## Algorithm Summary

The HAS-BLED score is the count of present risk factors (max 9):

| Letter | Factor | Modifiable |
|--------|--------|-----------|
| H | Hypertension (SBP >160) | Yes |
| A | Abnormal renal function | Yes |
| A | Abnormal liver function | Yes |
| S | Stroke history | No |
| B | Bleeding history | No |
| L | Labile INR | Yes |
| E | Elderly (>65) | No |
| D | Drugs (antiplatelet/NSAIDs) | Yes |
| D | Alcohol (≥8 drinks/week) | Yes |

**Risk levels:**
- 0-1: Low risk
- 2: Moderate risk
- 3-5: High risk
- ≥6: Very High risk

---

## License

MIT License. See [LICENSE](LICENSE) for details.
