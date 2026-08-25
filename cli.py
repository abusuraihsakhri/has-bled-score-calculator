#!/usr/bin/env python3
"""
CLI for the HAS-BLED Score Calculator.

Usage:
    python cli.py score --hypertension --renal --elderly --nsaids
    python cli.py score --hypertension --liver --stroke --bleeding --labile-inr --elderly --drugs --alcohol
    python cli.py assess --chadsvasc 4 --hasbled 3
    python cli.py modified --hypertension --renal --anemia
"""
import argparse
import json
import sys

from has_bled import (
    calculate_score,
    calculate_modified_score,
    assess_with_chadsvasc,
    format_result,
    format_assessment,
)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="has-bled",
        description="HAS-BLED Score Calculator — Major bleeding risk in AF patients on anticoagulation",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- score subcommand ---
    p_score = sub.add_parser(
        "score",
        help="Calculate HAS-BLED score from risk factors",
    )
    p_score.add_argument("--hypertension", action="store_true",
                         help="Uncontrolled SBP >160 mmHg")
    p_score.add_argument("--renal", action="store_true",
                         help="Abnormal renal function (dialysis/transplant/Cr>2.26)")
    p_score.add_argument("--liver", action="store_true",
                         help="Abnormal liver function (cirrhosis/elevated LFTs)")
    p_score.add_argument("--stroke", action="store_true",
                         help="Prior stroke or TIA")
    p_score.add_argument("--bleeding", action="store_true",
                         help="Bleeding history or predisposition")
    p_score.add_argument("--labile-inr", action="store_true",
                         help="Labile/unstable INR (<60% TTR)")
    p_score.add_argument("--elderly", action="store_true",
                         help="Age >65 years")
    p_score.add_argument("--drugs", "--nsaids", action="store_true",
                         help="Antiplatelet agents or NSAIDs")
    p_score.add_argument("--alcohol", action="store_true",
                         help="≥8 drinks per week")
    p_score.add_argument("--json", action="store_true",
                         help="Output as JSON")

    # --- assess subcommand ---
    p_assess = sub.add_parser(
        "assess",
        help="Combined HAS-BLED + CHA₂DS₂-VASc assessment",
    )
    p_assess.add_argument("--hasbled", type=int, required=True,
                          help="HAS-BLED score (0-9)")
    p_assess.add_argument("--chadsvasc", type=int, required=True,
                          help="CHA₂DS₂-VASc score (0-9)")
    p_assess.add_argument("--json", action="store_true",
                          help="Output as JSON")

    # --- modified subcommand ---
    p_mod = sub.add_parser(
        "modified",
        help="Modified HAS-BLED with extended criteria (anemia, thrombocytopenia)",
    )
    p_mod.add_argument("--hypertension", action="store_true")
    p_mod.add_argument("--renal", action="store_true")
    p_mod.add_argument("--liver", action="store_true")
    p_mod.add_argument("--stroke", action="store_true")
    p_mod.add_argument("--bleeding", action="store_true")
    p_mod.add_argument("--labile-inr", action="store_true")
    p_mod.add_argument("--elderly", action="store_true")
    p_mod.add_argument("--drugs", "--nsaids", action="store_true")
    p_mod.add_argument("--alcohol", action="store_true")
    p_mod.add_argument("--anemia", action="store_true",
                       help="Anemia (low hemoglobin)")
    p_mod.add_argument("--low-platelets", action="store_true",
                       help="Thrombocytopenia (platelets <150×10⁹/L)")
    p_mod.add_argument("--json", action="store_true",
                       help="Output as JSON")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "score":
        result = calculate_score(
            hypertension=args.hypertension,
            renal=args.renal,
            liver=args.liver,
            stroke=args.stroke,
            bleeding=args.bleeding,
            labile_inr=args.labile_inr,
            elderly=args.elderly,
            drugs=args.drugs,
            alcohol=args.alcohol,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_result(result))
        return 0

    if args.command == "assess":
        result = assess_with_chadsvasc(
            hasbled_score=args.hasbled,
            chadsvasc_score=args.chadsvasc,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_assessment(result))
        return 0

    if args.command == "modified":
        result = calculate_modified_score(
            hypertension=args.hypertension,
            renal=args.renal,
            liver=args.liver,
            stroke=args.stroke,
            bleeding=args.bleeding,
            labile_inr=args.labile_inr,
            elderly=args.elderly,
            drugs=args.drugs,
            alcohol=args.alcohol,
            anemia=args.anemia,
            low_platelets=args.low_platelets,
        )
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            base = result["standard_result"]
            print(format_result(base))
            print(f"\n  Modified Score: {result['modified_score']} "
                  f"(standard: {result['standard_score']})")
            if result["extra_factors"]:
                print(f"  Extra factors: {', '.join(result['extra_factors'])}")
            print(f"  Modified Risk Level: {result['risk_level']}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
