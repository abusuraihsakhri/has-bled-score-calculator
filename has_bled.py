"""
HAS-BLED Score Calculator for Major Bleeding Risk in Atrial Fibrillation.

Supports structured HAS-BLED assessment. Not an anticoagulation decision rule.
Score range: 0-9 points. Stdlib only.

Reference: Lip GY, et al. "A novel user-friendly score (HAS-BLED) to assess
1-year risk of major bleeding in patients with atrial fibrillation."
Chest. 2010;138(5):1093-1100.
"""


def _validate_bool(value, name):
    """Validate that a parameter is a boolean, raising TypeError if not."""
    if not isinstance(value, bool):
        raise TypeError(
            f"Parameter '{name}' must be a boolean, got {type(value).__name__}"
        )


# ---------------------------------------------------------------------------
# Risk factor definitions
# ---------------------------------------------------------------------------

# Each factor: (key, display_name, category, modifiable, description)
RISK_FACTORS = [
    ("hypertension", "Hypertension", "H", True,
     "Uncontrolled, SBP >160 mmHg"),
    ("renal", "Abnormal renal function", "A", True,
     "Dialysis, transplant, Cr >2.26 mg/dL or >200 µmol/L"),
    ("liver", "Abnormal liver function", "A", True,
     "Cirrhosis or bilirubin >2× ULN with AST/ALT/ALP >3× ULN"),
    ("stroke", "Stroke history", "S", False,
     "Prior stroke (consider TIA history in clinical context)"),
    ("bleeding", "Bleeding history/predisposition", "B", False,
     "Prior major bleed, anemia, Hb <10 g/dL"),
    ("labile_inr", "Labile INR", "L", True,
     "Unstable/high INR, <60% time in therapeutic range"),
    ("elderly", "Elderly", "E", False,
     "Age >65 years"),
    ("drugs", "Drugs (antiplatelet/NSAIDs)", "D", True,
     "Concomitant antiplatelet agents or NSAIDs"),
    ("alcohol", "Alcohol excess", "D", True,
     "≥8 alcohol units per week"),
]

# Historical major-bleeding rates per 100 patient-years (Pisters et al., 2010).
# Sparse observations preclude an estimate above score 5; do not extrapolate.
BLEEDING_RISK = {
    0: 1.13,
    1: 1.02,
    2: 1.88,
    3: 3.74,
    4: 8.70,
    5: 12.50,
    6: None,
    7: None,
    8: None,
    9: None,
}

# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------


def calculate_score(hypertension=False, renal=False, liver=False,
                    stroke=False, bleeding=False, labile_inr=False,
                    elderly=False, drugs=False, alcohol=False):
    """
    Calculate HAS-BLED score from boolean risk factor flags.

    Args:
        hypertension: Uncontrolled SBP >160 mmHg
        renal: Abnormal renal function (dialysis/transplant/Cr >2.26)
        liver: Abnormal liver function (cirrhosis/elevated LFTs)
        stroke: Prior stroke or TIA
        bleeding: Bleeding history or predisposition
        labile_inr: Labile/unstable INR (<60% TTR)
        elderly: Age >65 years
        drugs: Concomitant antiplatelet agents or NSAIDs
        alcohol: ≥8 alcohol units per week

    Returns:
        dict with:
          - score (int): 0-9
          - risk_level (str): "Low", "Moderate", "High"
          - annual_bleeding_risk (float | None): historical rate/100 patient-years
            for scores 0-5, or None if insufficient data
          - factors_present (list[str]): names of present factors
          - modifiable (list[str]): modifiable factors present
          - non_modifiable (list[str]): non-modifiable factors present
          - category_breakdown (dict): category letter -> points from that category
          - guidance (str): clinical guidance text

    Raises:
        TypeError: If any parameter is not a boolean.
    """
    _validate_bool(hypertension, "hypertension")
    _validate_bool(renal, "renal")
    _validate_bool(liver, "liver")
    _validate_bool(stroke, "stroke")
    _validate_bool(bleeding, "bleeding")
    _validate_bool(labile_inr, "labile_inr")
    _validate_bool(elderly, "elderly")
    _validate_bool(drugs, "drugs")
    _validate_bool(alcohol, "alcohol")

    flags = {
        "hypertension": hypertension,
        "renal": renal,
        "liver": liver,
        "stroke": stroke,
        "bleeding": bleeding,
        "labile_inr": labile_inr,
        "elderly": elderly,
        "drugs": drugs,
        "alcohol": alcohol,
    }

    factors_present = []
    modifiable = []
    non_modifiable = []
    category_points = {}

    for key, display, cat, is_mod, _desc in RISK_FACTORS:
        if flags.get(key, False):
            factors_present.append(display)
            if is_mod:
                modifiable.append(display)
            else:
                non_modifiable.append(display)
            category_points[cat] = category_points.get(cat, 0) + 1

    # Enforce category caps: max 2 from A (renal + liver), max 2 from D (drugs + alcohol)
    # The raw score is simply the count of present factors (max 9).
    # The category caps are inherent in the definition (A has 2 items, D has 2 items).
    score = len(factors_present)

    # Risk level
    if score <= 1:
        risk_level = "Low"
    elif score == 2:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    annual_risk = BLEEDING_RISK[score]

    # A score >=3 highlights the need to review bleeding risk factors, not
    # an automatic reason to withhold oral anticoagulation.
    if score >= 3:
        guidance = (
            "High bleeding risk: review reversible factors (blood pressure, "
            "INR control when relevant, antiplatelets/NSAIDs, alcohol). "
            "Do not use HAS-BLED alone to withhold anticoagulation."
        )
    else:
        guidance = (
            "Review bleeding risk factors periodically. A low HAS-BLED score "
            "does not establish anticoagulant safety or determine treatment."
        )

    return {
        "score": score,
        "risk_level": risk_level,
        "annual_bleeding_risk": annual_risk,
        "factors_present": factors_present,
        "modifiable": modifiable,
        "non_modifiable": non_modifiable,
        "category_breakdown": category_points,
        "guidance": guidance,
    }


# ---------------------------------------------------------------------------
# CHA₂DS₂-VASc integration
# ---------------------------------------------------------------------------

CHA2DS2VASC_RISK = {
    0: (0.0, "Low"),
    1: (1.3, "Low"),
    2: (2.2, "Low-Moderate"),
    3: (3.2, "Moderate"),
    4: (4.0, "Moderate-High"),
    5: (6.7, "High"),
    6: (9.8, "High"),
    7: (9.6, "High"),
    8: (12.5, "High"),
    9: (15.2, "High"),
}


def _validate_score(value, name):
    """Accept an integer or an unsigned integer string in the valid 0-9 range."""
    if isinstance(value, bool) or not (
        isinstance(value, int) or (isinstance(value, str) and value.isascii() and
                                   value.isdecimal())
    ):
        raise TypeError(f"{name} must be an integer from 0 to 9")
    number = int(value)
    if not 0 <= number <= 9:
        raise ValueError(f"{name} must be between 0 and 9")
    return number


def assess_with_chadsvasc(hasbled_score, chadsvasc_score):
    """Present both scores without manufacturing a net-benefit estimate.

    Historical cohort rates are descriptive only. Bleeding and stroke rates
    have different endpoints, populations, and treatment dependencies; their
    subtraction does NOT estimate the benefit of anticoagulation.

    Legacy fields net_benefit_pct and favors_anticoagulation remain for API
    compatibility, but are always None because such inference is invalid.
    """
    hasbled_score = _validate_score(hasbled_score, "hasbled_score")
    chadsvasc_score = _validate_score(chadsvasc_score, "chadsvasc_score")
    stroke_pct, stroke_level = CHA2DS2VASC_RISK[chadsvasc_score]
    bleed_pct = BLEEDING_RISK[hasbled_score]

    guidance = (
        "Assess stroke-prevention eligibility using current AF guidelines, "
        "sex-specific context and individual clinical factors. HAS-BLED "
        "identifies bleeding risk factors for review; it must not be used "
        "alone to withhold anticoagulation. The two historical event rates "
        "cannot be subtracted to estimate net clinical benefit."
    )
    if hasbled_score >= 3:
        guidance = ("High HAS-BLED (>=3): address reversible bleeding risk "
                    "factors and consider closer follow-up. " + guidance)

    return {
        "hasbled_score": hasbled_score,
        "chadsvasc_score": chadsvasc_score,
        "stroke_annual_risk_pct": stroke_pct,
        "stroke_risk_level": stroke_level,
        "bleeding_annual_risk_pct": bleed_pct,
        "net_benefit_pct": None,
        "favors_anticoagulation": None,
        "recommendation": guidance,
    }


# ---------------------------------------------------------------------------
# Modified HAS-BLED (includes additional criteria)
# ---------------------------------------------------------------------------

def calculate_modified_score(
    hypertension=False, renal=False, liver=False,
    stroke=False, bleeding=False, labile_inr=False,
    elderly=False, drugs=False, alcohol=False,
    anemia=False, low_platelets=False,
):
    """
    Modified HAS-BLED that adds:
      - Anemia (Hb <12 g/dL women, <13 g/dL men): +1
      - Low platelets (<150 × 10⁹/L): +1

    This is an unvalidated experimental extension, not a recognized
    HAS-BLED variant. Anemia can overlap with bleeding predisposition;
    do not use the 0-11 total for clinical risk stratification.

    Raises:
        TypeError: If any parameter is not a boolean.
    """
    _validate_bool(anemia, "anemia")
    _validate_bool(low_platelets, "low_platelets")

    base = calculate_score(
        hypertension=hypertension, renal=renal, liver=liver,
        stroke=stroke, bleeding=bleeding, labile_inr=labile_inr,
        elderly=elderly, drugs=drugs, alcohol=alcohol,
    )

    extra_points = 0
    extra_factors = []
    if anemia:
        extra_points += 1
        extra_factors.append("Anemia (low hemoglobin)")
    if low_platelets:
        extra_points += 1
        extra_factors.append("Thrombocytopenia (low platelets)")

    modified_score = base["score"] + extra_points

    # Standard HAS-BLED cutoffs are not validated for a modified 0-11 total.
    risk_level = "Not validated"

    return {
        "standard_score": base["score"],
        "modified_score": modified_score,
        "extra_factors": extra_factors,
        "risk_level": risk_level,
        "standard_result": base,
        "note": "Exploratory score only; no validated risk thresholds or rates.",
    }


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def format_result(result):
    """Format a standard HAS-BLED result dict as a readable string."""
    lines = [
        "=" * 55,
        "  HAS-BLED Score Assessment",
        "=" * 55,
        f"  Score: {result['score']} / 9",
        f"  Risk Level: {result['risk_level']}",
        (f"  Historical Bleeding Rate: {result['annual_bleeding_risk']:.2f}"
         " per 100 patient-years" if result['annual_bleeding_risk'] is not None
         else "  Historical Bleeding Rate: Not estimable for scores above 5"),
        "",
        "  Factors Present:",
    ]
    if result["factors_present"]:
        for f in result["factors_present"]:
            lines.append(f"    + {f}")
    else:
        lines.append("    (none)")

    lines.append("")
    lines.append("  Modifiable Factors:")
    if result["modifiable"]:
        for f in result["modifiable"]:
            lines.append(f"    * {f}")
    else:
        lines.append("    (none)")

    lines.append("")
    lines.append("  Non-Modifiable Factors:")
    if result["non_modifiable"]:
        for f in result["non_modifiable"]:
            lines.append(f"    * {f}")
    else:
        lines.append("    (none)")

    lines.append("")
    lines.append(f"  Guidance: {result['guidance']}")
    lines.append("=" * 55)
    return "\n".join(lines)


def format_assessment(result):
    """Format the descriptive combined view, without a treatment verdict."""
    bleeding = result["bleeding_annual_risk_pct"]
    bleed_text = (f"{bleeding:.2f} per 100 patient-years" if bleeding is not None
                  else "not estimable at this score")
    lines = [
        "=" * 60,
        "  HAS-BLED & CHA2DS2-VASc (descriptive comparison only)",
        "=" * 60,
        f"  HAS-BLED Score: {result['hasbled_score']} / 9",
        f"  Historical major bleeding rate: {bleed_text}",
        f"  CHA2DS2-VASc Score: {result['chadsvasc_score']} / 9",
        f"  Historical stroke rate: {result['stroke_annual_risk_pct']:.1f}%/yr",
        "  No net clinical benefit can be calculated from these rates.",
        "",
        f"  Guidance: {result['recommendation']}",
        "=" * 60,
    ]
    return "\n".join(lines)
