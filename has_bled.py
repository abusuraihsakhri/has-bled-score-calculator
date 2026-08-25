"""
HAS-BLED Score Calculator for Major Bleeding Risk in Atrial Fibrillation.

Validates bleeding risk in AF patients on anticoagulation therapy.
Score range: 0-9 points. Stdlib only.

Reference: Lip GY, et al. "A novel user-friendly score (HAS-BLED) to assess
1-year risk of major bleeding in patients with atrial fibrillation."
Chest. 2010;138(5):1093-1100.
"""

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
     "Cirrhosis, bilirubin >2× normal, AST/ALT/ALP >3× normal"),
    ("stroke", "Stroke history", "S", False,
     "Prior stroke or TIA"),
    ("bleeding", "Bleeding history/predisposition", "B", False,
     "Prior major bleed, anemia, Hb <10 g/dL"),
    ("labile_inr", "Labile INR", "L", True,
     "Unstable/high INR, <60% time in therapeutic range"),
    ("elderly", "Elderly", "E", False,
     "Age >65 years"),
    ("drugs", "Drugs (antiplatelet/NSAIDs)", "D", True,
     "Concomitant antiplatelet agents or NSAIDs"),
    ("alcohol", "Alcohol excess", "D", True,
     "≥8 drinks per week"),
]

# Annual bleeding risk percentages by score (Lip et al. 2010)
BLEEDING_RISK = {
    0: 1.13,
    1: 1.02,
    2: 1.88,
    3: 3.74,
    4: 8.70,
    5: 12.50,
    6: 12.50,  # ≥6 grouped
    7: 12.50,
    8: 12.50,
    9: 12.50,
}

# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def calculate_score(hypertension=False, renal=False, liver=False,
                    stroke=False, bleeding=False, labile_inr=False,
                    elderly=False, drugs=False, alcohol=False):
    """
    Calculate HAS-BLED score from boolean risk factor flags.

    Returns a dict with:
      - score (int): 0-9
      - risk_level (str): "Low", "Moderate", "High", "Very High"
      - annual_bleeding_risk (float): estimated % per year
      - factors_present (list[str]): names of present factors
      - modifiable (list[str]): modifiable factors present
      - non_modifiable (list[str]): non-modifiable factors present
      - category_breakdown (dict): category letter -> points from that category
      - guidance (str): clinical guidance text
    """
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
    elif score <= 5:
        risk_level = "High"
    else:
        risk_level = "Very High"

    annual_risk = BLEEDING_RISK.get(min(score, 6), 12.50)

    # Clinical guidance
    if score <= 2:
        guidance = (
            "Anticoagulation generally safe. Regular review recommended. "
            "Address any modifiable risk factors to maintain low risk."
        )
    else:
        guidance = (
            "High bleeding risk (score >= 3). Address modifiable risk factors "
            "(e.g., control BP, improve INR control, avoid NSAIDs, reduce alcohol). "
            "Consider more frequent monitoring. Score >= 3 does NOT contraindicate "
            "anticoagulation but warrants caution and shared decision-making."
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


def assess_with_chadsvasc(hasbled_score, chadsvasc_score):
    """
    Combined assessment integrating HAS-BLED bleeding risk with
    CHA₂DS₂-VASc stroke risk for balanced anticoagulation decisions.

    Args:
        hasbled_score: int 0-9
        chadsvasc_score: int 0-9

    Returns:
        dict with stroke_risk, bleeding_risk, net_benefit, recommendation
    """
    hasbled_score = max(0, min(9, int(hasbled_score)))
    chadsvasc_score = max(0, min(9, int(chadsvasc_score)))

    stroke_pct, stroke_level = CHA2DS2VASC_RISK.get(
        chadsvasc_score, (15.2, "High")
    )
    bleed_pct = BLEEDING_RISK.get(min(hasbled_score, 6), 12.50)

    # Net clinical benefit: stroke risk minus bleeding risk
    # Positive = favors anticoagulation
    net_benefit = stroke_pct - bleed_pct

    if chadsvasc_score == 0:
        recommendation = (
            "Low stroke risk. Anticoagulation generally NOT recommended "
            "regardless of bleeding risk."
        )
    elif chadsvasc_score == 1:
        recommendation = (
            "Borderline stroke risk. Consider patient preferences. "
            "Anticoagulation may be reasonable if bleeding risk is low."
        )
    elif hasbled_score >= 3 and chadsvasc_score >= 2:
        if net_benefit > 0:
            recommendation = (
                "High bleeding risk but stroke risk outweighs bleeding risk. "
                "Anticoagulation likely still beneficial. Address modifiable "
                "bleeding risk factors and monitor closely."
            )
        else:
            recommendation = (
                "High bleeding risk with comparable or higher bleeding risk "
                "than stroke risk. Careful individualized assessment needed. "
                "Address all modifiable factors. Consider left atrial appendage "
                "closure or alternative strategies."
            )
    elif hasbled_score <= 2 and chadsvasc_score >= 2:
        recommendation = (
            "Favorable risk-benefit profile. Anticoagulation recommended. "
            "Stroke risk clearly exceeds bleeding risk."
        )
    else:
        recommendation = (
            "Individualized assessment recommended. Weigh stroke vs bleeding "
            "risk with patient preferences."
        )

    return {
        "hasbled_score": hasbled_score,
        "chadsvasc_score": chadsvasc_score,
        "stroke_annual_risk_pct": stroke_pct,
        "stroke_risk_level": stroke_level,
        "bleeding_annual_risk_pct": bleed_pct,
        "net_benefit_pct": round(net_benefit, 2),
        "favors_anticoagulation": net_benefit > 0,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Modified HAS-BLED (includes additional criteria)
# ---------------------------------------------------------------------------

def calculate_modified_score(hypertension=False, renal=False, liver=False,
                              stroke=False, bleeding=False, labile_inr=False,
                              elderly=False, drugs=False, alcohol=False,
                              anemia=False, low_platelets=False):
    """
    Modified HAS-BLED that adds:
      - Anemia (Hb <12 g/dL women, <13 g/dL men): +1
      - Low platelets (<150 × 10⁹/L): +1

    These are sometimes included in extended bleeding risk assessments.
    Score range: 0-11.
    """
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

    if modified_score <= 1:
        risk_level = "Low"
    elif modified_score == 2:
        risk_level = "Moderate"
    elif modified_score <= 5:
        risk_level = "High"
    else:
        risk_level = "Very High"

    return {
        "standard_score": base["score"],
        "modified_score": modified_score,
        "extra_factors": extra_factors,
        "risk_level": risk_level,
        "standard_result": base,
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
        f"  Annual Bleeding Risk: {result['annual_bleeding_risk']:.2f}%",
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
    """Format a combined HAS-BLED + CHA₂DS₂-VASc assessment."""
    lines = [
        "=" * 60,
        "  Combined Bleeding & Stroke Risk Assessment",
        "=" * 60,
        f"  HAS-BLED Score:      {result['hasbled_score']} / 9  "
        f"(Bleeding risk: {result['bleeding_annual_risk_pct']:.2f}%/yr)",
        f"  CHA2DS2-VASc Score:  {result['chadsvasc_score']} / 9  "
        f"(Stroke risk: {result['stroke_annual_risk_pct']:.1f}%/yr)",
        f"  Net Benefit:         {result['net_benefit_pct']:+.2f}%  "
        f"({'Favors' if result['favors_anticoagulation'] else 'Does not favor'} anticoagulation)",
        "",
        f"  Recommendation: {result['recommendation']}",
        "=" * 60,
    ]
    return "\n".join(lines)
