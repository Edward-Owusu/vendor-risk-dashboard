"""Load a vendor inventory and score third-party risk."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DATA = Path(__file__).parent / "data"
ANSWER_VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0}
SEV_ORDER = ["critical", "high", "medium", "low"]
_TRUE, _FALSE = {"true", "yes", "y", "1"}, {"false", "no", "n", "0"}


class DataError(ValueError):
    """Raised when the vendor file cannot be read."""


def load_model(path: str | Path | None = None) -> dict:
    model = json.loads((DATA / "model.json").read_text(encoding="utf-8"))
    if path:
        model.update(json.loads(Path(path).read_text(encoding="utf-8")))
    return model


def _rules() -> dict[str, dict]:
    return {r["id"]: r for r in json.loads((DATA / "rules.json").read_text(encoding="utf-8"))["rules"]}


@dataclass
class Vendor:
    name: str
    service: str
    owner: str
    data_sensitivity: str
    system_access: str
    business_criticality: str
    remote_access: bool
    certifications: list[str]
    last_assessment: date | None
    breach_last_24mo: bool
    contract: dict[str, bool | None]
    answers: dict[str, str | None]


def _bool(v: str, col: str, row: int) -> bool | None:
    v = (v or "").strip().lower()
    if not v:
        return None
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise DataError(f"Row {row}: '{col}' must be true or false, got '{v}'.")


def _choice(v: str, allowed, col: str, row: int, default: str) -> str:
    v = (v or "").strip().lower() or default
    if v not in allowed:
        raise DataError(f"Row {row}: '{col}' must be one of {', '.join(allowed)}, got '{v}'.")
    return v


def parse_vendors(text: str, model: dict | None = None) -> list[Vendor]:
    model = model or load_model()
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    if not reader.fieldnames or "vendor" not in [f.strip().lower() for f in reader.fieldnames]:
        raise DataError("The file needs a header row with at least a 'vendor' column.")
    vendors, seen = [], set()
    for i, raw in enumerate(reader, start=2):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        name = r.get("vendor", "")
        if not name:
            continue
        if name.lower() in seen:
            raise DataError(f"Row {i}: vendor '{name}' appears more than once.")
        seen.add(name.lower())
        last = r.get("last_assessment_date", "")
        try:
            last_d = date.fromisoformat(last) if last else None
        except ValueError as exc:
            raise DataError(f"Row {i}: last_assessment_date must look like 2026-03-31, got '{last}'.") from exc
        answers = {}
        for q in model["controls"]:
            a = r.get(q, "").lower()
            if a and a not in ANSWER_VALUE:
                raise DataError(f"Row {i}: '{q}' must be yes, partial, or no, got '{a}'.")
            answers[q] = a or None
        vendors.append(Vendor(
            name=name, service=r.get("service", ""), owner=r.get("owner", ""),
            data_sensitivity=_choice(r.get("data_sensitivity"), model["sensitivity"], "data_sensitivity", i, "internal"),
            system_access=_choice(r.get("system_access"), model["access"], "system_access", i, "none"),
            business_criticality=_choice(r.get("business_criticality"), model["criticality"], "business_criticality", i, "medium"),
            remote_access=bool(_bool(r.get("remote_access", ""), "remote_access", i)),
            certifications=[c.strip().lower().replace(" ", "") for c in r.get("certifications", "").split(";") if c.strip()],
            last_assessment=last_d,
            breach_last_24mo=bool(_bool(r.get("breach_last_24mo", ""), "breach_last_24mo", i)),
            contract={k: _bool(r.get(k, ""), k, i) for k in
                      ("contract_security_clause", "contract_breach_notification", "contract_right_to_audit", "contract_data_return")},
            answers=answers,
        ))
    if not vendors:
        raise DataError("The file has a header but no vendor rows.")
    return vendors


def load_vendors(path: str | Path, model: dict | None = None) -> list[Vendor]:
    return parse_vendors(Path(path).read_text(encoding="utf-8-sig"), model)


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str
    controls: list[str]
    csf: list[str]
    detail: str
    remediation: str


@dataclass
class Scorecard:
    vendor: str
    service: str
    owner: str
    tier: int
    impact: int
    likelihood: int
    risk_score: int
    risk_band: str
    control_strength: float
    certifications: list[str]
    unanswered: list[str]
    weak_controls: list[str]
    last_assessment: str | None
    next_assessment_due: str | None
    assessment_status: str
    findings: list[Finding] = field(default_factory=list)


@dataclass
class Result:
    organization: str
    as_of: str
    generated_at: str
    tool_version: str
    scorecards: list[Scorecard]

    def heatmap(self) -> list[list[list[str]]]:
        """5x5 grid indexed [impact-1][likelihood-1] holding vendor names."""
        grid = [[[] for _ in range(5)] for _ in range(5)]
        for s in self.scorecards:
            grid[s.impact - 1][s.likelihood - 1].append(s.vendor)
        return grid

    def counts(self) -> dict[str, Any]:
        bands = {b: 0 for b in ("Critical", "High", "Moderate", "Low")}
        tiers = {1: 0, 2: 0, 3: 0}
        for s in self.scorecards:
            bands[s.risk_band] += 1
            tiers[s.tier] += 1
        on_time = sum(1 for s in self.scorecards if s.assessment_status == "Current")
        n = len(self.scorecards)
        return {"vendors": n, "bands": bands, "tiers": tiers,
                "assessed_on_time_pct": round(100 * on_time / n, 1) if n else 0.0,
                "findings": sum(len(s.findings) for s in self.scorecards),
                "critical_findings": sum(1 for s in self.scorecards for f in s.findings if f.severity == "critical")}

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["counts"] = self.counts()
        return d


def _band(score: int, model: dict) -> str:
    for floor, label in model["risk_bands"]:
        if score >= floor:
            return label
    return "Low"


def _add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def score_vendor(v: Vendor, model: dict, as_of: date) -> Scorecard:
    rules = _rules()
    # Impact: the larger of data sensitivity and business criticality, plus one for privileged access.
    impact = min(5, max(model["sensitivity"][v.data_sensitivity], model["criticality"][v.business_criticality])
                 + model["access"][v.system_access])
    tier = 1 if impact >= 4 else (2 if impact == 3 else 3)

    total = sum(c["weight"] for c in model["controls"].values())
    earned = sum(c["weight"] * ANSWER_VALUE.get(v.answers.get(q) or "no", 0.0) for q, c in model["controls"].items())
    certified = any(c in model["recognized_certifications"] for c in v.certifications)
    strength = min(100.0, round(100 * earned / total + (model["certification_bonus"] if certified else 0), 1))
    likelihood = next(l for floor, l in model["likelihood_from_strength"] if strength >= floor)
    if v.breach_last_24mo:
        likelihood += 1
    if v.remote_access and v.answers.get("q_mfa") != "yes":
        likelihood += 1
    likelihood = min(5, likelihood)
    score = impact * likelihood

    months = model["reassessment_months"][str(tier)]
    due = _add_months(v.last_assessment, months) if v.last_assessment else None
    status = "Never assessed" if not v.last_assessment else ("Overdue" if due < as_of else "Current")

    unanswered = [model["controls"][q]["label"] for q, a in v.answers.items() if not a]
    weak = [model["controls"][q]["label"] for q, a in v.answers.items() if a in ("no", "partial")]
    sensitive = model["sensitivity"][v.data_sensitivity] >= 3

    findings: list[Finding] = []

    def add(rid: str, detail: str, severity: str | None = None) -> None:
        m = rules[rid]
        findings.append(Finding(rid, m["title"], severity or m["severity"], m["controls"], m["csf"], detail, m["remediation"]))

    if status != "Current":
        add("VR-01", f"{status}. Tier {tier} vendors are reassessed every {months} months.",
            None if tier == 1 else "medium")
    if tier <= 2 and v.contract["contract_security_clause"] is not True:
        add("VR-02", "No security requirements recorded in the contract.")
    if (tier <= 2 or sensitive) and v.contract["contract_breach_notification"] is not True:
        add("VR-03", "No obligation to tell you about incidents affecting your data or systems.")
    if tier == 1 and v.contract["contract_right_to_audit"] is not True:
        add("VR-04", "No contractual right to request evidence or assess controls.")
    if sensitive and v.contract["contract_data_return"] is not True:
        add("VR-05", f"Vendor holds {v.data_sensitivity} data with no return or destruction terms.")
    if v.remote_access and v.answers.get("q_mfa") != "yes":
        add("VR-06", "Vendor connects remotely without confirmed multi-factor authentication.")
    if v.breach_last_24mo:
        add("VR-07", "A security breach was reported in the last 24 months.")
    if sensitive and strength < 50:
        add("VR-08", f"Control strength {strength:.0f}/100 for a vendor holding {v.data_sensitivity} data.")
    if unanswered and len(unanswered) < len(model["controls"]):
        add("VR-09", f"Unanswered: {', '.join(unanswered)}.")
    findings.sort(key=lambda f: (SEV_ORDER.index(f.severity), f.rule_id))

    return Scorecard(
        vendor=v.name, service=v.service, owner=v.owner, tier=tier, impact=impact, likelihood=likelihood,
        risk_score=score, risk_band=_band(score, model), control_strength=strength, certifications=v.certifications,
        unanswered=unanswered, weak_controls=weak,
        last_assessment=v.last_assessment.isoformat() if v.last_assessment else None,
        next_assessment_due=due.isoformat() if due else None, assessment_status=status, findings=findings,
    )


def assess(vendors: list[Vendor], organization: str = "Unnamed organization", model: dict | None = None,
           as_of: date | None = None) -> Result:
    from . import __version__

    model = model or load_model()
    as_of = as_of or date.today()
    cards = sorted((score_vendor(v, model, as_of) for v in vendors),
                   key=lambda s: (-s.risk_score, s.tier, s.vendor.lower()))
    return Result(organization, as_of.isoformat(), datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                  __version__, cards)
