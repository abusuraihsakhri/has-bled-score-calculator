# HAS-BLED Score Calculator

A standard nine-factor HAS-BLED bleeding-risk assessment for atrial fibrillation,
available as a standalone browser interface, Python library, and command-line tool.
The standard score ranges from 0 to 9.

## Browser calculator

The responsive calculator is in [docs/index.html](docs/index.html). It runs
entirely in the browser with JavaScript: **no server, Python runtime, account,
patient-data upload, analytics, or network request is required** to calculate
the score. The static files can be hosted with GitHub Pages from the
`master` branch's `/docs` directory after Pages is enabled.

For local preview, open `docs/index.html` in a modern browser, or use:

```bash
python -m http.server 8000 --directory docs
```

Then visit `http://localhost:8000/`. All selections are temporary and are not
transmitted or stored by the application.

## Python and command line

Python 3.10+ is required; there are no runtime dependencies.

```bash
python cli.py score --hypertension --renal --elderly
python cli.py score --hypertension --json
python cli.py assess --hasbled 3 --chadsvasc 4
python cli.py modified --hypertension --anemia
```

Or use the Python API:

```python
from has_bled import calculate_score, assess_with_chadsvasc

score = calculate_score(hypertension=True, renal=True, elderly=True)
assert score["score"] == 3

review = assess_with_chadsvasc(hasbled_score=3, chadsvasc_score=4)
print(review["recommendation"])
```

You may also install the command with `python -m pip install -e .` and
run `has-bled score --elderly --drugs`.

## Standard scoring criteria

Each factor contributes one point.

| Component | Criterion |
| --- | --- |
| H | Uncontrolled systolic BP >160 mmHg |
| A | Abnormal renal function: dialysis, transplant, or creatinine >200 µmol/L |
| A | Abnormal liver function: cirrhosis or bilirubin >2× ULN with liver enzymes >3× ULN |
| S | Prior stroke |
| B | Bleeding history or predisposition |
| L | Labile INR (generally <60% time in therapeutic range on VKA) |
| E | Age >65 years |
| D | Concomitant antiplatelet medication or NSAIDs |
| D | Excess alcohol (at least 8 alcohol units/week) |

Scores 0–1 are labeled low, 2 moderate, and 3–9 high for review purposes.
These labels are not individualized probabilities. Historical major-bleeding
rates per 100 patient-years are displayed only for scores 0–5; scores 6–9
return `None` instead of an unsupported extrapolated rate.

**Clinical limitations:** A HAS-BLED score of 3 or above prompts review and
management of potentially modifiable bleeding risk factors. Neither a low nor a
high score independently establishes treatment eligibility or contraindicates
anticoagulation. Stroke and major-bleeding rates cannot be subtracted to
calculate net clinical benefit.

The `assess` API and CLI show HAS-BLED and CHA₂DS₂-VASc scores together for
descriptive review only. Legacy keys `net_benefit_pct` and
`favors_anticoagulation` remain in the API for compatibility but are `None`
because they cannot validly be inferred from the two rates. CHA₂DS₂-VASc
historical event rates vary by population and anticoagulation status.

The `modified` operation adds points for anemia and low platelets
(score 0–11). **This extension has not been validated** as a HAS-BLED risk
model and must not be used for clinical risk stratification. It may overlap
with bleeding predisposition in the standard score.

## Development and tests

```bash
python -m pip install -e .
python -m pip install pytest flake8
python -m pytest -q
flake8 has_bled.py cli.py --max-line-length=100
node --check docs/app.js
node docs/app.test.js
```

Node.js is required only for the browser JavaScript tests.
GitHub Actions tests Python 3.10, 3.11, and 3.12, checks lint, and runs the
browser scoring regression suite across all 512 factor combinations.

## References

- Pisters R, et al. *Chest*. 2010;138:1093–1100.
  [DOI: 10.1378/chest.10-0134](https://doi.org/10.1378/chest.10-0134)
- Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS guideline for AF.
  [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11095842/)

This project is a clinical reference/educational tool, not a substitute for
individual clinical assessment or local prescribing guidance.

## Compatibility and license

Browser: modern desktop and mobile browsers with JavaScript enabled.
Python: 3.10+. License: [MIT](LICENSE).
