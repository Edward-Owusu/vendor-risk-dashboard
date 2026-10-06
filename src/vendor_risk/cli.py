"""Command-line interface.

Examples:
    vendor-risk samples/riverbend_components_vendors.csv --org "Riverbend Components"
    vendor-risk vendors.csv --format html csv --out reports --fail-on-band High
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .engine import DataError, assess, load_model, load_vendors
from .reporting import WRITERS

BANDS = ["Critical", "High", "Moderate", "Low"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vendor-risk", description="Score third-party and supply chain risk across your vendors.")
    p.add_argument("vendors", help="Path to the vendor inventory CSV")
    p.add_argument("--org", help="Organization name for the report (default: file name)")
    p.add_argument("--as-of", help="Date to measure assessment due dates against (YYYY-MM-DD, default: today)")
    p.add_argument("--format", nargs="+", choices=sorted(WRITERS), default=["html", "csv"])
    p.add_argument("--out", default="reports", help="Output directory (default: reports)")
    p.add_argument("--model", help="JSON file overriding the scoring model")
    p.add_argument("--fail-on-band", choices=BANDS, help="Exit with code 2 if any vendor is in this band or worse")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        model = load_model(args.model)
        vendors = load_vendors(args.vendors, model)
        as_of = date.fromisoformat(args.as_of) if args.as_of else None
    except (OSError, DataError, ValueError) as exc:
        print(f"Could not read input: {exc}", file=sys.stderr)
        return 1
    r = assess(vendors, args.org or Path(args.vendors).stem.replace("_", " "), model, as_of)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for fmt in args.format:
        path = out / f"{Path(args.vendors).stem}.{fmt}"
        path.write_text(WRITERS[fmt](r), encoding="utf-8")
        print(f"Wrote {path}")
    c = r.counts()
    print(f"\n{r.organization} | {c['vendors']} vendors | as of {r.as_of}")
    print(f"Critical {c['bands']['Critical']} | High {c['bands']['High']} | Moderate {c['bands']['Moderate']} | "
          f"Low {c['bands']['Low']} | Assessments current {c['assessed_on_time_pct']:.0f}%")
    for s in r.scorecards[:5]:
        print(f"  {s.risk_band:<9} {s.risk_score:>2}  {s.vendor} (Tier {s.tier}, {len(s.findings)} findings)")
    if args.fail_on_band:
        limit = BANDS.index(args.fail_on_band)
        if any(BANDS.index(s.risk_band) <= limit for s in r.scorecards):
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
