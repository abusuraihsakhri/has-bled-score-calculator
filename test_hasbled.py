"""
Tests for the HAS-BLED Score Calculator.

Covers:
- Score 0 (no risk factors, low risk)
- Score ≥3 (high risk)
- Dual A category scoring (renal + liver)
- Dual D category scoring (drugs + alcohol)
- Modifiable vs non-modifiable factor identification
- Integration with CHA₂DS₂-VASc
- Modified HAS-BLED
- Edge cases and boundary conditions
"""
import json
import subprocess
import sys
import unittest

from has_bled import (
    calculate_score,
    calculate_modified_score,
    assess_with_chadsvasc,
    format_result,
    format_assessment,
    RISK_FACTORS,
    BLEEDING_RISK,
)


class TestScoreZero(unittest.TestCase):
    """Score 0: no risk factors present — lowest risk."""

    def test_no_factors(self):
        result = calculate_score()
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "Low")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 1.13)
        self.assertEqual(result["factors_present"], [])
        self.assertEqual(result["modifiable"], [])
        self.assertEqual(result["non_modifiable"], [])

    def test_all_false(self):
        result = calculate_score(
            hypertension=False, renal=False, liver=False,
            stroke=False, bleeding=False, labile_inr=False,
            elderly=False, drugs=False, alcohol=False,
        )
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["risk_level"], "Low")


class TestScoreLowRisk(unittest.TestCase):
    """Score 1: single factor — still low risk."""

    def test_single_modifiable(self):
        result = calculate_score(hypertension=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["risk_level"], "Low")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 1.02)
        self.assertIn("Hypertension", result["modifiable"])
        self.assertEqual(len(result["non_modifiable"]), 0)

    def test_single_non_modifiable(self):
        result = calculate_score(elderly=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["risk_level"], "Low")
        self.assertIn("Elderly", result["non_modifiable"])
        self.assertEqual(len(result["modifiable"]), 0)


class TestScoreModerateRisk(unittest.TestCase):
    """Score 2: moderate risk."""

    def test_two_factors(self):
        result = calculate_score(hypertension=True, elderly=True)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["risk_level"], "Moderate")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 1.88)

    def test_two_modifiable(self):
        result = calculate_score(hypertension=True, drugs=True)
        self.assertEqual(result["score"], 2)
        self.assertEqual(len(result["modifiable"]), 2)
        self.assertEqual(len(result["non_modifiable"]), 0)


class TestScoreHighRisk(unittest.TestCase):
    """Score ≥3: high risk threshold."""

    def test_score_3(self):
        result = calculate_score(
            hypertension=True, stroke=True, elderly=True,
        )
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["risk_level"], "High")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 3.74)

    def test_score_4(self):
        result = calculate_score(
            hypertension=True, renal=True, stroke=True, elderly=True,
        )
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["risk_level"], "High")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 8.70)

    def test_score_5(self):
        result = calculate_score(
            hypertension=True, renal=True, liver=True,
            stroke=True, elderly=True,
        )
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["risk_level"], "High")
        self.assertAlmostEqual(result["annual_bleeding_risk"], 12.50)

    def test_score_6_plus_very_high(self):
        result = calculate_score(
            hypertension=True, renal=True, liver=True,
            stroke=True, bleeding=True, elderly=True,
        )
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["risk_level"], "Very High")

    def test_max_score_9(self):
        result = calculate_score(
            hypertension=True, renal=True, liver=True,
            stroke=True, bleeding=True, labile_inr=True,
            elderly=True, drugs=True, alcohol=True,
        )
        self.assertEqual(result["score"], 9)
        self.assertEqual(result["risk_level"], "Very High")
        self.assertEqual(len(result["factors_present"]), 9)


class TestDualACategory(unittest.TestCase):
    """Both A-category factors (renal + liver) can score simultaneously."""

    def test_renal_only(self):
        result = calculate_score(renal=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["category_breakdown"].get("A", 0), 1)

    def test_liver_only(self):
        result = calculate_score(liver=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["category_breakdown"].get("A", 0), 1)

    def test_both_renal_and_liver(self):
        result = calculate_score(renal=True, liver=True)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["category_breakdown"]["A"], 2)
        self.assertIn("Abnormal renal function", result["factors_present"])
        self.assertIn("Abnormal liver function", result["factors_present"])


class TestDualDCategory(unittest.TestCase):
    """Both D-category factors (drugs + alcohol) can score simultaneously."""

    def test_drugs_only(self):
        result = calculate_score(drugs=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["category_breakdown"].get("D", 0), 1)

    def test_alcohol_only(self):
        result = calculate_score(alcohol=True)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["category_breakdown"].get("D", 0), 1)

    def test_both_drugs_and_alcohol(self):
        result = calculate_score(drugs=True, alcohol=True)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["category_breakdown"]["D"], 2)
        self.assertIn("Drugs (antiplatelet/NSAIDs)", result["factors_present"])
        self.assertIn("Alcohol excess", result["factors_present"])


class TestModifiableFactors(unittest.TestCase):
    """Correct identification of modifiable vs non-modifiable factors."""

    def test_all_modifiable(self):
        result = calculate_score(
            hypertension=True, renal=True, liver=True,
            labile_inr=True, drugs=True, alcohol=True,
        )
        self.assertEqual(result["score"], 6)
        self.assertEqual(len(result["modifiable"]), 6)
        self.assertEqual(len(result["non_modifiable"]), 0)

    def test_all_non_modifiable(self):
        result = calculate_score(stroke=True, bleeding=True, elderly=True)
        self.assertEqual(result["score"], 3)
        self.assertEqual(len(result["modifiable"]), 0)
        self.assertEqual(len(result["non_modifiable"]), 3)

    def test_mixed(self):
        result = calculate_score(
            hypertension=True, stroke=True, elderly=True, drugs=True,
        )
        self.assertEqual(result["score"], 4)
        self.assertEqual(len(result["modifiable"]), 2)  # hypertension, drugs
        self.assertEqual(len(result["non_modifiable"]), 2)  # stroke, elderly
        self.assertIn("Hypertension", result["modifiable"])
        self.assertIn("Drugs (antiplatelet/NSAIDs)", result["modifiable"])
        self.assertIn("Stroke history", result["non_modifiable"])
        self.assertIn("Elderly", result["non_modifiable"])

    def test_modifiable_count_matches_spec(self):
        """Verify the 6 modifiable and 3 non-modifiable factors from the spec."""
        modifiable_keys = [f[0] for f in RISK_FACTORS if f[3]]
        non_modifiable_keys = [f[0] for f in RISK_FACTORS if not f[3]]
        self.assertEqual(len(modifiable_keys), 6)
        self.assertEqual(len(non_modifiable_keys), 3)
        self.assertIn("hypertension", modifiable_keys)
        self.assertIn("renal", modifiable_keys)
        self.assertIn("liver", modifiable_keys)
        self.assertIn("labile_inr", modifiable_keys)
        self.assertIn("drugs", modifiable_keys)
        self.assertIn("alcohol", modifiable_keys)
        self.assertIn("stroke", non_modifiable_keys)
        self.assertIn("bleeding", non_modifiable_keys)
        self.assertIn("elderly", non_modifiable_keys)


class TestChadsvascIntegration(unittest.TestCase):
    """Combined HAS-BLED + CHA₂DS₂-VASc assessment."""

    def test_low_bleed_low_stroke(self):
        result = assess_with_chadsvasc(hasbled_score=1, chadsvasc_score=0)
        self.assertEqual(result["hasbled_score"], 1)
        self.assertEqual(result["chadsvasc_score"], 0)
        self.assertFalse(result["favors_anticoagulation"])
        self.assertIn("NOT recommended", result["recommendation"])

    def test_low_bleed_high_stroke(self):
        result = assess_with_chadsvasc(hasbled_score=1, chadsvasc_score=5)
        self.assertTrue(result["favors_anticoagulation"])
        self.assertIn("recommended", result["recommendation"].lower())

    def test_high_bleed_high_stroke_net_positive(self):
        """Stroke risk (6.7%) > bleeding risk (3.74%) => net positive."""
        result = assess_with_chadsvasc(hasbled_score=3, chadsvasc_score=5)
        self.assertTrue(result["favors_anticoagulation"])
        self.assertGreater(result["net_benefit_pct"], 0)

    def test_high_bleed_low_stroke(self):
        """Bleeding risk exceeds stroke risk."""
        result = assess_with_chadsvasc(hasbled_score=5, chadsvasc_score=2)
        self.assertFalse(result["favors_anticoagulation"])
        self.assertLess(result["net_benefit_pct"], 0)

    def test_borderline_chadsvasc_1(self):
        result = assess_with_chadsvasc(hasbled_score=0, chadsvasc_score=1)
        self.assertIn("Borderline", result["recommendation"])

    def test_score_clamping(self):
        """Scores outside 0-9 should be clamped."""
        result = assess_with_chadsvasc(hasbled_score=-1, chadsvasc_score=15)
        self.assertEqual(result["hasbled_score"], 0)
        self.assertEqual(result["chadsvasc_score"], 9)

    def test_high_bleed_high_stroke_careful(self):
        """When bleeding risk >= stroke risk, careful assessment needed."""
        result = assess_with_chadsvasc(hasbled_score=4, chadsvasc_score=3)
        # stroke 3.2% vs bleeding 8.7% => net negative
        self.assertFalse(result["favors_anticoagulation"])
        self.assertIn("individualized", result["recommendation"].lower())


class TestModifiedHasbled(unittest.TestCase):
    """Modified HAS-BLED with extended criteria."""

    def test_standard_only(self):
        result = calculate_modified_score(hypertension=True, elderly=True)
        self.assertEqual(result["standard_score"], 2)
        self.assertEqual(result["modified_score"], 2)
        self.assertEqual(result["extra_factors"], [])

    def test_with_anemia(self):
        result = calculate_modified_score(hypertension=True, anemia=True)
        self.assertEqual(result["standard_score"], 1)
        self.assertEqual(result["modified_score"], 2)
        self.assertIn("Anemia (low hemoglobin)", result["extra_factors"])

    def test_with_low_platelets(self):
        result = calculate_modified_score(elderly=True, low_platelets=True)
        self.assertEqual(result["standard_score"], 1)
        self.assertEqual(result["modified_score"], 2)
        self.assertIn("Thrombocytopenia (low platelets)", result["extra_factors"])

    def test_with_both_extra(self):
        result = calculate_modified_score(
            hypertension=True, renal=True, anemia=True, low_platelets=True,
        )
        self.assertEqual(result["standard_score"], 2)
        self.assertEqual(result["modified_score"], 4)
        self.assertEqual(result["risk_level"], "High")

    def test_modified_very_high(self):
        result = calculate_modified_score(
            hypertension=True, renal=True, liver=True,
            stroke=True, bleeding=True, elderly=True,
            anemia=True, low_platelets=True,
        )
        self.assertEqual(result["standard_score"], 6)
        self.assertEqual(result["modified_score"], 8)
        self.assertEqual(result["risk_level"], "Very High")


class TestFormatOutput(unittest.TestCase):
    """Formatting functions produce readable output."""

    def test_format_result_contains_score(self):
        result = calculate_score(hypertension=True, elderly=True)
        text = format_result(result)
        self.assertIn("Score: 2", text)
        self.assertIn("Moderate", text)
        self.assertIn("Hypertension", text)
        self.assertIn("Elderly", text)

    def test_format_result_zero(self):
        result = calculate_score()
        text = format_result(result)
        self.assertIn("Score: 0", text)
        self.assertIn("(none)", text)

    def test_format_assessment(self):
        result = assess_with_chadsvasc(hasbled_score=3, chadsvasc_score=4)
        text = format_assessment(result)
        self.assertIn("HAS-BLED", text)
        self.assertIn("3", text)
        self.assertIn("4", text)


class TestCliScoreCommand(unittest.TestCase):
    """Test the CLI score subcommand."""

    def _run_cli(self, args):
        result = subprocess.run(
            [sys.executable, "cli.py"] + args,
            capture_output=True, text=True, cwd=_get_project_dir(),
        )
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        return result.stdout

    def test_score_no_factors(self):
        out = self._run_cli(["score"])
        self.assertIn("Score: 0", out)
        self.assertIn("Low", out)

    def test_score_with_flags(self):
        out = self._run_cli(["score", "--hypertension", "--elderly", "--nsaids"])
        self.assertIn("Score: 3", out)
        self.assertIn("High", out)

    def test_score_json(self):
        out = self._run_cli(["score", "--hypertension", "--json"])
        data = json.loads(out)
        self.assertEqual(data["score"], 1)
        self.assertEqual(data["risk_level"], "Low")

    def test_score_all_factors(self):
        out = self._run_cli([
            "score", "--hypertension", "--renal", "--liver",
            "--stroke", "--bleeding", "--labile-inr",
            "--elderly", "--drugs", "--alcohol",
        ])
        self.assertIn("Score: 9", out)
        self.assertIn("Very High", out)


class TestCliAssessCommand(unittest.TestCase):
    """Test the CLI assess subcommand."""

    def _run_cli(self, args):
        result = subprocess.run(
            [sys.executable, "cli.py"] + args,
            capture_output=True, text=True, cwd=_get_project_dir(),
        )
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        return result.stdout

    def test_assess_basic(self):
        out = self._run_cli(["assess", "--hasbled", "3", "--chadsvasc", "4"])
        self.assertIn("HAS-BLED", out)
        self.assertIn("3", out)

    def test_assess_json(self):
        out = self._run_cli(["assess", "--hasbled", "2", "--chadsvasc", "5", "--json"])
        data = json.loads(out)
        self.assertEqual(data["hasbled_score"], 2)
        self.assertEqual(data["chadsvasc_score"], 5)


class TestCliModifiedCommand(unittest.TestCase):
    """Test the CLI modified subcommand."""

    def _run_cli(self, args):
        result = subprocess.run(
            [sys.executable, "cli.py"] + args,
            capture_output=True, text=True, cwd=_get_project_dir(),
        )
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        return result.stdout

    def test_modified_basic(self):
        out = self._run_cli(["modified", "--hypertension", "--anemia"])
        self.assertIn("Modified Score", out)

    def test_modified_json(self):
        out = self._run_cli([
            "modified", "--hypertension", "--renal",
            "--anemia", "--low-platelets", "--json",
        ])
        data = json.loads(out)
        self.assertEqual(data["standard_score"], 2)
        self.assertEqual(data["modified_score"], 4)


class TestBleedingRiskTable(unittest.TestCase):
    """Verify the bleeding risk lookup table is internally consistent."""

    def test_all_scores_0_to_9_present(self):
        for i in range(10):
            self.assertIn(i, BLEEDING_RISK)

    def test_risk_increases_from_score_1_to_5(self):
        """Risk increases from score 1 onward (score 0 is slightly higher than 1 per Lip 2010)."""
        for i in range(1, 5):
            self.assertLessEqual(BLEEDING_RISK[i], BLEEDING_RISK[i + 1])

    def test_score_0_and_1_are_low(self):
        """Both score 0 and 1 are low risk (<2%)."""
        self.assertLess(BLEEDING_RISK[0], 2.0)
        self.assertLess(BLEEDING_RISK[1], 2.0)

    def test_score_0_risk(self):
        self.assertAlmostEqual(BLEEDING_RISK[0], 1.13)

    def test_score_3_risk(self):
        self.assertAlmostEqual(BLEEDING_RISK[3], 3.74)


class TestRiskFactorDefinitions(unittest.TestCase):
    """Verify the risk factor table has exactly 9 entries with correct structure."""

    def test_nine_factors(self):
        self.assertEqual(len(RISK_FACTORS), 9)

    def test_factor_structure(self):
        for factor in RISK_FACTORS:
            self.assertEqual(len(factor), 5, f"Factor {factor[0]} has wrong tuple length")
            key, display, cat, modifiable, desc = factor
            self.assertIsInstance(key, str)
            self.assertIsInstance(display, str)
            self.assertIn(cat, ["H", "A", "S", "B", "L", "E", "D"])
            self.assertIsInstance(modifiable, bool)
            self.assertIsInstance(desc, str)

    def test_category_letters(self):
        cats = [f[2] for f in RISK_FACTORS]
        self.assertEqual(cats, ["H", "A", "A", "S", "B", "L", "E", "D", "D"])


def _get_project_dir():
    """Return the project directory for CLI subprocess calls."""
    import os
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    unittest.main()
