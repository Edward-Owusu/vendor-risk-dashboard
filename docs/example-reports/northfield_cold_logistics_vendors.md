# Vendor risk report: Northfield Cold Logistics (fictional)

As of 2026-10-06 | 8 vendors | Generated 2026-10-06 02:38 UTC

- Risk bands: Critical **0**, High **0**, Moderate **1**, Low **7**
- Tiers: Tier 1 **6**, Tier 2 **2**, Tier 3 **0**
- Assessments current: **88%**

## Vendors by residual risk

| Vendor | Service | Tier | Impact x Likelihood | Risk | Controls | Assessment |
|---|---|---|---|---|---|---|
| Frontier Managed Security | Managed detection and IT support | 1 | 5 x 1 = 5 | Moderate | 100/100 | Current |
| Arctic Refrigeration Services | Refrigeration control maintenance | 1 | 4 x 1 = 4 | Low | 89/100 | Current |
| CloudDesk 365 | Email and file storage | 1 | 4 x 1 = 4 | Low | 100/100 | Current |
| ColdTrack WMS | Warehouse management SaaS | 1 | 4 x 1 = 4 | Low | 100/100 | Current |
| Harbor CPA Group | Accounting and tax | 1 | 4 x 1 = 4 | Low | 96/100 | Current |
| Ledgerline Payroll | Payroll and HR software | 1 | 4 x 1 = 4 | Low | 100/100 | Current |
| FleetLink Telematics | Truck tracking SaaS | 2 | 3 x 1 = 3 | Low | 100/100 | Overdue |
| SecureShred | Document destruction | 2 | 3 x 1 = 3 | Low | 100/100 | Current |

## Findings

### FleetLink Telematics (Low)

- **[MEDIUM] VR-01 Vendor assessment is overdue or has never been done.** Overdue. Tier 2 vendors are reassessed every 24 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_

_Scores are produced by a transparent scoring model from the vendor information supplied. They support, and do not replace, professional judgment about third-party risk. Unanswered questionnaire items are scored as not in place until confirmed._
