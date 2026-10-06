"""Write vendor risk results as JSON, CSV, Markdown, or a self-contained HTML report."""

from __future__ import annotations

import csv
import io
import json
from html import escape

from .engine import Result

DISCLAIMER = (
    "Scores are produced by a transparent scoring model from the vendor information supplied. They support, "
    "and do not replace, professional judgment about third-party risk. Unanswered questionnaire items are "
    "scored as not in place until confirmed."
)
BAND_COLOR = {"Critical": "#9f1d1d", "High": "#c2410c", "Moderate": "#d97706", "Low": "#4d7c0f"}


def cell_band(score: int) -> str:
    return "Critical" if score >= 15 else "High" if score >= 10 else "Moderate" if score >= 5 else "Low"


def to_json(r: Result) -> str:
    return json.dumps(r.to_dict(), indent=2, default=str)


def to_csv(r: Result) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["vendor", "service", "tier", "impact", "likelihood", "risk_score", "risk_band", "control_strength",
                "assessment_status", "next_assessment_due", "findings"])
    for s in r.scorecards:
        w.writerow([s.vendor, s.service, s.tier, s.impact, s.likelihood, s.risk_score, s.risk_band, s.control_strength,
                    s.assessment_status, s.next_assessment_due or "", " | ".join(f"{f.rule_id} {f.title}" for f in s.findings)])
    return buf.getvalue()


def to_markdown(r: Result) -> str:
    c = r.counts()
    lines = [f"# Vendor risk report: {r.organization}", "",
             f"As of {r.as_of} | {c['vendors']} vendors | Generated {r.generated_at}", "",
             f"- Risk bands: Critical **{c['bands']['Critical']}**, High **{c['bands']['High']}**, "
             f"Moderate **{c['bands']['Moderate']}**, Low **{c['bands']['Low']}**",
             f"- Tiers: Tier 1 **{c['tiers'][1]}**, Tier 2 **{c['tiers'][2]}**, Tier 3 **{c['tiers'][3]}**",
             f"- Assessments current: **{c['assessed_on_time_pct']:.0f}%**", "",
             "## Vendors by residual risk", "",
             "| Vendor | Service | Tier | Impact x Likelihood | Risk | Controls | Assessment |", "|---|---|---|---|---|---|---|"]
    for s in r.scorecards:
        lines.append(f"| {s.vendor} | {s.service} | {s.tier} | {s.impact} x {s.likelihood} = {s.risk_score} | {s.risk_band} | "
                     f"{s.control_strength:.0f}/100 | {s.assessment_status} |")
    lines += ["", "## Findings", ""]
    for s in r.scorecards:
        if not s.findings:
            continue
        lines += [f"### {s.vendor} ({s.risk_band})", ""]
        for f in s.findings:
            lines.append(f"- **[{f.severity.upper()}] {f.rule_id} {f.title}.** {f.detail} Fix: {f.remediation} "
                         f"_({', '.join(f.controls)}; CSF {', '.join(f.csf)})_")
        lines.append("")
    lines += [f"_{DISCLAIMER}_", ""]
    return "\n".join(lines)


_CSS = """
:root{--ink:#2b1a10;--muted:#7a5a46;--line:#f1d9c6;--paper:#fff;--wash:#fff8f1;--accent:#c2410c}
*{box-sizing:border-box}
body{margin:0;background:var(--wash);color:var(--ink);font:15px/1.55 "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
main{max-width:1060px;margin:0 auto;padding:34px 24px 60px}
h1{font-size:30px;margin:0;letter-spacing:-.01em}
.sub{color:var(--muted);margin:4px 0 0}
h2{font-size:19px;margin:36px 0 12px;color:var(--accent)}
.kpis{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}
.kpi{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:14px 18px;min-width:150px}
.kpi b{display:block;font-size:28px}.kpi span{color:var(--muted);font-size:13px}
.hm{display:grid;grid-template-columns:90px repeat(5,1fr);gap:4px;max-width:760px}
.hm .ax{display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:12px;text-align:center}
.hm .c{min-height:74px;border-radius:8px;padding:6px;color:#fff;font-size:11px;line-height:1.3}
.hm .c b{display:block;font-size:12px;opacity:.85}
.hm .c.empty{opacity:.28}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.card .top{padding:12px 16px;color:#fff;display:flex;justify-content:space-between;align-items:center}
.card .top b{font-size:16px}.card .top span{font-size:12px;font-weight:700;background:rgba(255,255,255,.2);padding:2px 8px;border-radius:999px}
.card .body{padding:12px 16px}
.card .meta{color:var(--muted);font-size:13px;margin:0 0 8px}
.bar{height:8px;background:#f3e3d6;border-radius:4px;overflow:hidden;margin:4px 0 10px}.bar i{display:block;height:100%;background:var(--accent)}
.card ul{margin:6px 0 0 18px;padding:0;font-size:13px}
.ok{color:#4d7c0f;font-size:13px}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;background:var(--paper);font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{color:var(--muted)}
.note{color:var(--muted);font-size:13px;margin-top:30px}
"""


def heatmap_html(r: Result) -> str:
    e = escape
    grid = r.heatmap()
    parts = ['<div class="hm">']
    for impact in range(5, 0, -1):
        parts.append(f'<div class="ax">Impact {impact}</div>')
        for lk in range(1, 6):
            names = grid[impact - 1][lk - 1]
            band = cell_band(impact * lk)
            label = "<br>".join(e(n) for n in names[:4]) + (f"<br>+{len(names) - 4} more" if len(names) > 4 else "")
            parts.append(f'<div class="c{"" if names else " empty"}" style="background:{BAND_COLOR[band]}" '
                         f'title="Impact {impact} x Likelihood {lk} = {impact * lk}"><b>{impact * lk}</b>{label}</div>')
    parts.append('<div></div>' + "".join(f'<div class="ax">Likelihood {lk}</div>' for lk in range(1, 6)) + "</div>")
    return "".join(parts)


def to_html(r: Result) -> str:
    e = escape
    c = r.counts()
    cards = []
    for s in r.scorecards:
        items = "".join(f"<li><strong>{e(f.severity.title())}:</strong> {e(f.title)}</li>" for f in s.findings[:4])
        more = f"<li>and {len(s.findings) - 4} more</li>" if len(s.findings) > 4 else ""
        body = f"<ul>{items}{more}</ul>" if s.findings else '<p class="ok">No open findings.</p>'
        cards.append(
            f'<div class="card"><div class="top" style="background:{BAND_COLOR[s.risk_band]}"><b>{e(s.vendor)}</b>'
            f'<span>{e(s.risk_band)} · {s.risk_score}</span></div><div class="body">'
            f'<p class="meta">{e(s.service)} · Tier {s.tier} · Impact {s.impact} × Likelihood {s.likelihood}<br>'
            f'Assessment: {e(s.assessment_status)}{" · due " + e(s.next_assessment_due) if s.next_assessment_due else ""}</p>'
            f'<div style="font-size:13px">Control strength {s.control_strength:.0f}/100</div>'
            f'<div class="bar"><i style="width:{s.control_strength:.0f}%"></i></div>{body}</div></div>')
    rows = "".join(
        f"<tr><td>{e(s.vendor)}</td><td>{e(f.rule_id)}</td><td>{e(f.severity.title())}</td><td>{e(f.title)}. {e(f.detail)}</td>"
        f"<td>{e(', '.join(f.controls))}<br>CSF {e(', '.join(f.csf))}</td><td>{e(f.remediation)}</td></tr>"
        for s in r.scorecards for f in s.findings)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vendor risk report: {e(r.organization)}</title><style>{_CSS}</style></head><body><main>
<h1>Vendor risk report: {e(r.organization)}</h1>
<p class="sub">As of {e(r.as_of)}. {c['vendors']} vendors. Generated {e(r.generated_at)} by vendor_risk {e(r.tool_version)}.</p>
<div class="kpis"><div class="kpi"><b style="color:{BAND_COLOR['Critical']}">{c['bands']['Critical']}</b><span>Critical-risk vendors</span></div>
<div class="kpi"><b style="color:{BAND_COLOR['High']}">{c['bands']['High']}</b><span>High-risk vendors</span></div>
<div class="kpi"><b>{c['tiers'][1]}</b><span>Tier 1 (most critical) vendors</span></div>
<div class="kpi"><b>{c['assessed_on_time_pct']:.0f}%</b><span>Assessments current</span></div>
<div class="kpi"><b>{c['findings']}</b><span>Open findings</span></div></div>
<h2>Risk heat map</h2>{heatmap_html(r)}
<h2>Vendor scorecards</h2><div class="cards">{''.join(cards)}</div>
<h2>All findings</h2><div class="table-wrap"><table><thead><tr><th>Vendor</th><th>Rule</th><th>Severity</th><th>Finding</th><th>Controls</th><th>Fix</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{e(DISCLAIMER)}</p></main></body></html>"""


WRITERS = {"json": to_json, "csv": to_csv, "md": to_markdown, "html": to_html}
