import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vendor_risk import assess, load_vendors, parse_vendors  # noqa: E402
from vendor_risk.cli import main  # noqa: E402
from vendor_risk.engine import DataError  # noqa: E402
from vendor_risk.reporting import WRITERS  # noqa: E402

AS_OF = date(2026, 10, 6)
WEAK = ROOT / "samples" / "riverbend_components_vendors.csv"
STRONG = ROOT / "samples" / "northfield_cold_logistics_vendors.csv"
HEADER = ("vendor,service,data_sensitivity,system_access,business_criticality,remote_access,certifications,"
          "last_assessment_date,breach_last_24mo,contract_security_clause,contract_breach_notification,"
          "contract_right_to_audit,contract_data_return,q_mfa,q_encryption,q_patching,q_backup,q_incident_response,"
          "q_access_review,q_training,q_subprocessors")
GOOD = "true,true,true,true,yes,yes,yes,yes,yes,yes,yes,yes"


def card(row: str):
    return assess(parse_vendors(HEADER + "\n" + row), "T", as_of=AS_OF).scorecards[0]


def rules(sc):
    return {f.rule_id for f in sc.findings}


class TestParsing(unittest.TestCase):
    def test_rejects_bad_input(self):
        with self.assertRaisesRegex(DataError, "'vendor' column"):
            parse_vendors("name,service\nA,B\n")
        with self.assertRaisesRegex(DataError, "data_sensitivity"):
            parse_vendors(HEADER + "\nA,svc,secret,none,low,false,,,false," + GOOD)
        with self.assertRaisesRegex(DataError, "more than once"):
            parse_vendors(HEADER + "\nA,s,internal,none,low,false,,,false," + GOOD + "\na,s,internal,none,low,false,,,false," + GOOD)
        with self.assertRaisesRegex(DataError, "2026-03-31"):
            parse_vendors(HEADER + "\nA,s,internal,none,low,false,,03/31/2026,false," + GOOD)


class TestScoring(unittest.TestCase):
    def test_impact_and_tier(self):
        s = card("A,s,regulated,privileged,low,false,soc2,2026-09-01,false," + GOOD)
        self.assertEqual((s.impact, s.tier), (5, 1))
        s = card("B,s,none,none,low,false,soc2,2026-09-01,false," + GOOD)
        self.assertEqual((s.impact, s.tier), (1, 3))

    def test_strong_vendor_is_low_risk_with_no_findings(self):
        s = card("A,s,confidential,limited,high,false,soc2,2026-09-01,false," + GOOD)
        self.assertEqual(s.likelihood, 1)
        self.assertEqual(s.risk_band, "Low")
        self.assertEqual(s.findings, [])

    def test_remote_access_without_mfa(self):
        s = card("A,s,internal,limited,medium,true,,2026-09-01,false,true,true,true,true,no,yes,yes,yes,yes,yes,yes,yes")
        self.assertIn("VR-06", rules(s))
        self.assertEqual(s.findings[0].severity, "critical")

    def test_breach_raises_likelihood(self):
        a = card("A,s,confidential,limited,high,false,soc2,2026-09-01,false," + GOOD)
        b = card("A,s,confidential,limited,high,false,soc2,2026-09-01,true," + GOOD)
        self.assertEqual(b.likelihood, a.likelihood + 1)
        self.assertIn("VR-07", rules(b))

    def test_unanswered_scored_as_not_in_place(self):
        s = card("A,s,confidential,none,medium,false,,2026-09-01,false,true,true,true,true,,,,,,,,")
        self.assertEqual(s.control_strength, 0)
        self.assertIn("VR-08", rules(s))

    def test_assessment_due_dates(self):
        overdue = card("A,s,regulated,none,high,false,soc2,2025-09-30,false," + GOOD)  # Tier 1: 12 months
        self.assertEqual(overdue.assessment_status, "Overdue")
        current = card("B,s,none,none,low,false,soc2,2024-01-15,false," + GOOD)  # Tier 3: 36 months
        self.assertEqual(current.assessment_status, "Current")
        never = card("C,s,internal,none,low,false,,,false," + GOOD)
        self.assertEqual(never.assessment_status, "Never assessed")

    def test_contract_rules_follow_tier(self):
        s = card("A,s,regulated,none,high,false,soc2,2026-09-01,false,false,false,false,false,yes,yes,yes,yes,yes,yes,yes,yes")
        self.assertTrue({"VR-02", "VR-03", "VR-04", "VR-05"} <= rules(s))
        low = card("B,s,none,none,low,false,soc2,2026-09-01,false,false,false,false,false,yes,yes,yes,yes,yes,yes,yes,yes")
        self.assertEqual(rules(low), set())


class TestSamples(unittest.TestCase):
    def test_samples(self):
        weak = assess(load_vendors(WEAK), "W", as_of=AS_OF)
        self.assertGreaterEqual(weak.counts()["bands"]["Critical"], 1)
        self.assertEqual(sum(len(row) for grid_row in weak.heatmap() for row in grid_row), len(weak.scorecards))
        strong = assess(load_vendors(STRONG), "S", as_of=AS_OF)
        self.assertEqual(strong.counts()["bands"]["Critical"] + strong.counts()["bands"]["High"], 0)
        self.assertEqual(weak.scorecards, sorted(weak.scorecards, key=lambda s: (-s.risk_score, s.tier, s.vendor.lower())))


class TestOutput(unittest.TestCase):
    def test_writers_and_escaping(self):
        r = assess(load_vendors(WEAK), "<script>x</script>", as_of=AS_OF)
        for fmt, w in WRITERS.items():
            self.assertTrue(w(r).strip(), fmt)
        self.assertNotIn("<script>x</script>", WRITERS["html"](r))
        json.loads(WRITERS["json"](r))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(main([str(WEAK), "--as-of", "2026-10-06", "--out", tmp, "--fail-on-band", "Critical"]), 2)
            self.assertEqual(main([str(STRONG), "--as-of", "2026-10-06", "--out", tmp, "--fail-on-band", "High"]), 0)
            bad = Path(tmp) / "bad.csv"
            bad.write_text("x,y\n1,2\n", encoding="utf-8")
            self.assertEqual(main([str(bad), "--out", tmp]), 1)


if __name__ == "__main__":
    unittest.main()
