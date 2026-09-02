# Has Bled Score Calculator

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

HAS-BLED Score Calculator for Major Bleeding Risk in Atrial Fibrillation.

Validates bleeding risk in AF patients on anticoagulation therapy.
Score range: 0-9 points. Stdlib only.

Reference: Lip GY, et al. "A novel user-friendly score (HAS-BLED) to assess
1-year risk of major bleeding in patients with atrial fibrillation."
Chest. 2010;138(5):1093-1100.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_score()`**: Calculate HAS-BLED score from boolean risk factor flags.

Returns a dict with:
  - score (int): 0-9
  - risk_level (str): "Low", "Moderate", "High", "Very High"
  - annual_bleeding_risk (float): estimated % per year
  - factors_present (list[str]): names of present factors
  - modifiable (list[str]): modifiable factors present
  - non_modifiable (list[str]): non-modifiable factors present
  - category_breakdown (dict): category letter -> points from that category
  - guidance (str): clinical guidance text
- **`assess_with_chadsvasc()`**: Combined assessment integrating HAS-BLED bleeding risk with
CHA₂DS₂-VASc stroke risk for balanced anticoagulation decisions.

Args:
    hasbled_score: int 0-9
    chadsvasc_score: int 0-9

Returns:
    dict with stroke_risk, bleeding_risk, net_benefit, recommendation
- **`calculate_modified_score()`**: Modified HAS-BLED that adds:
  - Anemia (Hb <12 g/dL women, <13 g/dL men): +1
  - Low platelets (<150 × 10⁹/L): +1

These are sometimes included in extended bleeding risk assessments.
Score range: 0-11.
- **`format_result()`**: Format a standard HAS-BLED result dict as a readable string.
- **`format_assessment()`**: Format a combined HAS-BLED + CHA₂DS₂-VASc assessment.

---

## 📐 Mathematical Formulation & Logic

```text
  BLEEDING_RISK = {
  Calculate HAS-BLED score from boolean risk factor flags.
  score = len(factors_present)
  elif score == 2:
  annual_risk = BLEEDING_RISK.get(min(score, 6), 12.50)
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --hypertension <value> --renal <value> --elderly <value> --nsaids <value>
```

### Parameter Reference
- `--hypertension`: Specifies input measurement or parameter value.
- `--renal`: Specifies input measurement or parameter value.
- `--elderly`: Specifies input measurement or parameter value.
- `--nsaids`: Specifies input measurement or parameter value.
- `--liver`: Specifies input measurement or parameter value.
- `--stroke`: Specifies input measurement or parameter value.
- `--bleeding`: Specifies input measurement or parameter value.
- `--labile-inr`: Specifies input measurement or parameter value.
- `--drugs`: Specifies input measurement or parameter value.
- `--alcohol`: Specifies input measurement or parameter value.

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t has-bled-score-calculator .
docker run -p 8000:8000 has-bled-score-calculator
```
