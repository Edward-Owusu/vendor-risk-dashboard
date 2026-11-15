"""Interactive dashboard for the Vendor Risk Dashboard.

Run locally:   streamlit run app/streamlit_app.py

Layout: no sidebar. The heat map is the main screen, with a vendor drill-down panel beside it.
Data and filters sit in the top row.
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ui  # noqa: E402
from vendor_risk import __version__, assess, parse_vendors  # noqa: E402
from vendor_risk.engine import DataError  # noqa: E402
from vendor_risk.reporting import BAND_COLOR, DISCLAIMER, heatmap_html, to_csv, to_html, to_json, to_markdown  # noqa: E402

S = ROOT / "samples"
SAMPLES = {
    "Small manufacturer, informal vendor program (fictional)":
        ("Riverbend Components (fictional)", S / "riverbend_components_vendors.csv"),
    "Cold storage company, mature vendor program (fictional)":
        ("Northfield Cold Logistics (fictional)", S / "northfield_cold_logistics_vendors.csv"),
}
BANDS = ["Critical", "High", "Moderate", "Low"]
TIERS = {1: "Tier 1", 2: "Tier 2", 3: "Tier 3"}

PAL = ui.Palette(accent="#C2410C", band="#2B1A10", band_text="#FFF8F1", band_sub="#E8CDB8",
                 card="#FFFFFF", line="#F0DCCB", ink="#2B1A10", muted="#7A5B48")
ui.setup("Vendor risk heat map", "Third-party risk · NIST SP 800-53 SR · CSF 2.0 GV.SC",
         "Score the security risk your vendors and service providers bring, see them on a heat map, and get a "
         "prioritized list of what to fix in contracts and assessments.", "🔗", PAL)
st.markdown("<style>.hm{display:grid;grid-template-columns:70px repeat(5,1fr);gap:5px}"
            ".hm .ax{display:flex;align-items:center;justify-content:center;font-size:12px;color:#7A5B48;text-align:center}"
            ".hm .c{min-height:86px;border-radius:9px;padding:7px;color:#fff;font-size:11.5px;line-height:1.3}"
            ".hm .c b{display:block;font-size:12px;opacity:.85}.hm .c.empty{opacity:.22}</style>",
            unsafe_allow_html=True)

# ---- Top row: data and filters -----------------------------------------------------------------------
t1, t2, t3, t4 = st.columns([1.6, 2.4, 1.6, 1.4], vertical_alignment="top")
text, org = None, "My organization"
with t1:
    st.caption("Vendor inventory")
    source = ui.choose("Vendor inventory", ["Use a sample", "Upload my own CSV"], key="source", format_func=ui.source_label)
with t2:
    if source == "Use a sample":
        st.caption("Sample organization")
        org, path = SAMPLES[st.selectbox("Sample organization", list(SAMPLES), label_visibility="collapsed")]
        text = path.read_text(encoding="utf-8")
    else:
        st.caption("Your vendor inventory (.csv)")
        up = st.file_uploader("Vendor inventory (.csv)", type=["csv"], label_visibility="collapsed")
        if up:
            text = up.getvalue().decode("utf-8-sig", errors="replace")
with t3:
    st.caption("Show risk bands")
    band_filter = ui.multi("Risk band", BANDS, key="bands")
with t4:
    st.caption("Show tiers")
    tier_filter = ui.multi("Tier", [1, 2, 3], key="tiers", format_func=lambda t: TIERS[t])
if source != "Use a sample":
    with st.expander("Organization name and blank template"):
        org = st.text_input("Organization name", "My organization")
        st.download_button("Download blank template", (S / "vendors_template.csv").read_bytes(),
                           "vendors_template.csv", "text/csv")

if text is None:
    st.info("Upload a vendor inventory above, or switch to a sample, to see the heat map.")
    ui.footer("vendor_risk", __version__, "vendor-risk-dashboard", DISCLAIMER)
    st.stop()
try:
    vendors = parse_vendors(text)
except DataError as exc:
    st.error(f"The file could not be read. {exc} Fix the file and upload it again.")
    st.stop()

r = assess(vendors, org)
c = r.counts()
shown = sorted([s for s in r.scorecards if s.risk_band in band_filter and s.tier in tier_filter],
               key=lambda s: -s.risk_score)

st.markdown(f"<div class='g-sec'>{escape(r.organization)}</div>", unsafe_allow_html=True)
ui.tiles([(c["bands"]["Critical"], "Critical-risk vendors", BAND_COLOR["Critical"]),
          (c["bands"]["High"], "High-risk vendors", BAND_COLOR["High"]),
          (c["tiers"][1], "Tier 1 vendors"),
          (f"{c['assessed_on_time_pct']:.0f}%", "Assessments current", BAND_COLOR["Low"]),
          (c["findings"], "Open findings")], PAL)

# ---- Heat map with drill-down ------------------------------------------------------------------------
left, right = st.columns([3, 2], gap="large")
with left:
    ui.section("Risk heat map", "Impact: the data a vendor holds, how critical its service is, and privileged "
               "access. Likelihood: control strength, any recent breach, and remote access without MFA. "
               "Top-right needs attention first.")
    st.markdown(heatmap_html(r), unsafe_allow_html=True)
with right:
    ui.section("Vendor drill-down", "Ordered by risk score. Filters in the top row apply.")
    if not shown:
        st.info("No vendors match the filters.")
    else:
        pick = st.selectbox("Vendor", [s.vendor for s in shown], label_visibility="collapsed",
                            format_func=lambda v: next(f"{v} · {s.risk_band} {s.risk_score}" for s in shown
                                                       if s.vendor == v))
        s = next(x for x in shown if x.vendor == pick)
        col = BAND_COLOR[s.risk_band]
        due = f" · next due {escape(str(s.next_assessment_due))}" if s.next_assessment_due else ""
        st.markdown(f"<div style='background:{col};color:#fff;border-radius:12px;padding:14px 16px;margin-bottom:10px'>"
                    f"<div style='font:600 20px Georgia,serif'>{escape(s.vendor)}</div>"
                    f"<div style='opacity:.9;font-size:13px'>{escape(s.service)} · {TIERS[s.tier]} · owner "
                    f"{escape(s.owner or 'none')}</div><div style='display:flex;gap:22px;margin-top:8px'>"
                    f"<div><b style='font-size:26px'>{s.risk_score}</b><br><small>{escape(s.risk_band)} risk</small></div>"
                    f"<div><b style='font-size:26px'>{s.impact}×{s.likelihood}</b><br><small>impact × likelihood</small></div>"
                    f"<div><b style='font-size:26px'>{s.control_strength:.0f}</b><br><small>control strength</small></div>"
                    f"</div><div style='font-size:12.5px;margin-top:6px;opacity:.9'>Assessment: "
                    f"{escape(str(s.assessment_status))}{due}</div></div>", unsafe_allow_html=True)
        if not s.findings:
            st.success("No open findings.")
        for f in s.findings:
            ui.card(f"<div class='h'>{ui.sev_pill(f.severity)}{escape(f.rule_id)} · {escape(f.title)}</div>",
                    f"<div class='d'>{escape(f.detail)}</div><div class='f'><b>Fix:</b> {escape(f.remediation)}</div>"
                    f"<div class='s'>Controls {escape(', '.join(f.controls))} · CSF {escape(', '.join(f.csf))}</div>",
                    accent=ui.SEV_COLORS.get(f.severity))

view = ui.choose("View", ["Watch list", "All findings", "Vendor list"], key="view")
if view == "Watch list":
    ui.section(f"Watch list · {len(shown)} vendors, highest risk first")
    cols = st.columns(4)
    for i, s in enumerate(shown):
        col = BAND_COLOR[s.risk_band]
        cols[i % 4].markdown(
            f"<div class='g-tile' style='border-top-color:{col};margin-bottom:10px'><b>{s.risk_score}</b>"
            f"<span><b style='font-size:14px;display:inline;color:#2B1A10'>{escape(s.vendor)}</b><br>"
            f"{escape(s.risk_band)} · {TIERS[s.tier]} · {len(s.findings)} finding(s)</span>"
            f"{ui.bar(s.control_strength, col)}<span>Control strength {s.control_strength:.0f}</span></div>",
            unsafe_allow_html=True)
elif view == "All findings":
    rows = [{"Vendor": s.vendor, "Severity": f.severity.title(), "Rule": f.rule_id, "Finding": f.title,
             "Detail": f.detail, "Controls": ", ".join(f.controls), "CSF": ", ".join(f.csf)}
            for s in shown for f in s.findings]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.success("No findings for the selected vendors.")
else:
    st.dataframe(pd.DataFrame([{"Vendor": s.vendor, "Service": s.service, "Owner": s.owner, "Tier": s.tier,
                                "Impact": s.impact, "Likelihood": s.likelihood, "Risk score": s.risk_score,
                                "Band": s.risk_band, "Control strength": s.control_strength,
                                "Assessment": s.assessment_status, "Next due": s.next_assessment_due}
                               for s in shown]), hide_index=True, use_container_width=True)

ui.downloads([("HTML report", to_html(r), "vendor_risk_report.html", "text/html"),
              ("Markdown", to_markdown(r), "vendor_risk_report.md", "text/markdown"),
              ("CSV scorecards", to_csv(r), "vendor_scorecards.csv", "text/csv"),
              ("JSON results", to_json(r), "vendor_risk.json", "application/json")])
ui.footer("vendor_risk", __version__, "vendor-risk-dashboard", DISCLAIMER)
