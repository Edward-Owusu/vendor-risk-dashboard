"""Interactive dashboard for the Vendor Risk Dashboard.

Run locally:   streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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

st.set_page_config(page_title="Vendor Risk Dashboard", page_icon="🔗", layout="wide")
st.title("🔗 Vendor risk dashboard")
st.write("Score the security risk your vendors and service providers bring, see them on a heat map, and get a "
         "prioritized list of what to fix in contracts and assessments. Findings map to NIST SP 800-53 supply chain "
         "controls and the NIST Cybersecurity Framework 2.0.")

with st.sidebar:
    st.header("1. Choose data")
    source = st.radio("Vendor inventory", ["Use a sample", "Upload my own CSV"], label_visibility="collapsed")
    text, org = None, "My organization"
    if source == "Use a sample":
        org, path = SAMPLES[st.selectbox("Sample organization", list(SAMPLES))]
        text = path.read_text(encoding="utf-8")
    else:
        up = st.file_uploader("Vendor inventory (.csv)", type=["csv"])
        st.download_button("Download blank template", (S / "vendors_template.csv").read_bytes(),
                           "vendors_template.csv", "text/csv")
        org = st.text_input("Organization name", "My organization")
        if up:
            text = up.getvalue().decode("utf-8-sig", errors="replace")
    st.header("2. Filter")
    band_filter = st.multiselect("Risk band", BANDS, default=BANDS)
    tier_filter = st.multiselect("Tier", [1, 2, 3], default=[1, 2, 3],
                                 format_func=lambda t: {1: "Tier 1 (most critical)", 2: "Tier 2", 3: "Tier 3"}[t])
    st.caption(f"vendor_risk {__version__}. Runs entirely in this session; uploaded files are not stored.")

if text is None:
    st.info("Upload a vendor inventory in the sidebar, or switch to a sample, to see results.")
    st.stop()
try:
    vendors = parse_vendors(text)
except DataError as exc:
    st.error(f"The file could not be read. {exc} Fix the file and upload it again.")
    st.stop()

r = assess(vendors, org)
c = r.counts()
st.subheader(r.organization)
m = st.columns(5)
m[0].metric("Critical-risk vendors", c["bands"]["Critical"])
m[1].metric("High-risk vendors", c["bands"]["High"])
m[2].metric("Tier 1 vendors", c["tiers"][1])
m[3].metric("Assessments current", f"{c['assessed_on_time_pct']:.0f}%")
m[4].metric("Open findings", c["findings"])

left, right = st.columns([3, 2])
with left:
    st.markdown("#### Risk heat map")
    st.markdown("<style>.hm{display:grid;grid-template-columns:80px repeat(5,1fr);gap:4px}"
                ".hm .ax{display:flex;align-items:center;justify-content:center;font-size:12px;opacity:.75;text-align:center}"
                ".hm .c{min-height:70px;border-radius:8px;padding:6px;color:#fff;font-size:11px;line-height:1.3}"
                ".hm .c b{display:block;font-size:12px;opacity:.85}.hm .c.empty{opacity:.28}</style>"
                + heatmap_html(r), unsafe_allow_html=True)
with right:
    st.markdown("#### How to read it")
    st.write("**Impact** reflects the data a vendor holds, how critical its service is, and whether it has "
             "privileged access. **Likelihood** reflects the strength of its security controls, any recent breach, "
             "and remote access without MFA. Vendors in the top-right need attention first.")
    st.dataframe(pd.DataFrame([{"Band": b, "Vendors": c["bands"][b]} for b in BANDS]), hide_index=True)

shown = [s for s in r.scorecards if s.risk_band in band_filter and s.tier in tier_filter]
tab_cards, tab_find, tab_list = st.tabs([f"Vendor scorecards ({len(shown)})", "All findings", "Vendor list"])
with tab_cards:
    if not shown:
        st.info("No vendors match the filters.")
    cols = st.columns(3)
    for i, s in enumerate(shown):
        with cols[i % 3].container(border=True):
            st.markdown(f"<div style='background:{BAND_COLOR[s.risk_band]};color:#fff;padding:8px 12px;border-radius:8px;"
                        f"display:flex;justify-content:space-between'><b>{escape(s.vendor)}</b>"
                        f"<span>{escape(s.risk_band)} · {s.risk_score}</span></div>", unsafe_allow_html=True)
            st.caption(f"{s.service} · Tier {s.tier} · Impact {s.impact} × Likelihood {s.likelihood}  \n"
                       f"Assessment: {s.assessment_status}" + (f" · due {s.next_assessment_due}" if s.next_assessment_due else ""))
            st.progress(s.control_strength / 100, text=f"Control strength {s.control_strength:.0f}/100")
            if s.findings:
                with st.expander(f"{len(s.findings)} finding{'s' if len(s.findings) != 1 else ''}"):
                    for f in s.findings:
                        st.markdown(f"**{f.severity.title()} · {f.rule_id}** {f.title}. {f.detail}  \n"
                                    f"*Fix:* {f.remediation}  \n*Controls:* {', '.join(f.controls)} · CSF {', '.join(f.csf)}")
            else:
                st.success("No open findings.")
with tab_find:
    rows = [{"Vendor": s.vendor, "Severity": f.severity.title(), "Rule": f.rule_id, "Finding": f.title,
             "Detail": f.detail, "Controls": ", ".join(f.controls), "CSF": ", ".join(f.csf)}
            for s in shown for f in s.findings]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    else:
        st.success("No findings for the selected vendors.")
with tab_list:
    st.dataframe(pd.DataFrame([{"Vendor": s.vendor, "Service": s.service, "Owner": s.owner, "Tier": s.tier,
                                "Impact": s.impact, "Likelihood": s.likelihood, "Risk score": s.risk_score,
                                "Band": s.risk_band, "Control strength": s.control_strength,
                                "Assessment": s.assessment_status, "Next due": s.next_assessment_due}
                               for s in shown]), hide_index=True)

st.markdown("#### Download the report")
d = st.columns(4)
d[0].download_button("HTML report", to_html(r), "vendor_risk_report.html", "text/html")
d[1].download_button("Markdown", to_markdown(r), "vendor_risk_report.md", "text/markdown")
d[2].download_button("CSV scorecards", to_csv(r), "vendor_scorecards.csv", "text/csv")
d[3].download_button("JSON results", to_json(r), "vendor_risk.json", "application/json")
st.caption(DISCLAIMER)
