# Vendor risk report: Riverbend Components (fictional)

As of 2026-10-06 | 12 vendors | Generated 2026-10-06 02:38 UTC

- Risk bands: Critical **3**, High **3**, Moderate **2**, Low **4**
- Tiers: Tier 1 **6**, Tier 2 **2**, Tier 3 **4**
- Assessments current: **50%**

## Vendors by residual risk

| Vendor | Service | Tier | Impact x Likelihood | Risk | Controls | Assessment |
|---|---|---|---|---|---|---|
| Lakeshore IT Services | Managed IT provider | 1 | 5 x 4 = 20 | Critical | 54/100 | Overdue |
| QuickStaff Agency | Temporary staffing | 1 | 4 x 5 = 20 | Critical | 0/100 | Never assessed |
| Shred-Right | Document destruction | 2 | 3 x 5 = 15 | Critical | 0/100 | Overdue |
| NorthStar ERP Cloud | ERP hosting | 1 | 5 x 2 = 10 | High | 96/100 | Overdue |
| Climate Control Pros | HVAC and building controls | 3 | 2 x 5 = 10 | High | 7/100 | Never assessed |
| PrintPoint Leasing | Copier lease and scan-to-email | 3 | 2 x 5 = 10 | High | 7/100 | Never assessed |
| Midwest Freight Brokers | Freight booking portal | 2 | 3 x 3 = 9 | Moderate | 50/100 | Current |
| Barnes & Kim CPAs | Accounting and tax | 1 | 4 x 2 = 8 | Moderate | 71/100 | Current |
| CloudDesk 365 | Email and file storage | 1 | 4 x 1 = 4 | Low | 100/100 | Current |
| Payline Payroll | Payroll and HR software | 1 | 4 x 1 = 4 | Low | 100/100 | Current |
| Precision CAD Co | Design software licenses | 3 | 2 x 1 = 2 | Low | 100/100 | Current |
| WebNest Hosting | Company website hosting | 3 | 1 x 1 = 1 | Low | 100/100 | Current |

## Findings

### Lakeshore IT Services (Critical)

- **[CRITICAL] VR-06 Vendor has remote access without MFA.** Vendor connects remotely without confirmed multi-factor authentication. Fix: Require MFA for all vendor remote access, route it through your VPN or a remote access tool you control, and enable it only when needed. _(AC-17, SA-9; CSF GV.SC-05, PR.AA-03)_
- **[HIGH] VR-01 Vendor assessment is overdue or has never been done.** Overdue. Tier 1 vendors are reassessed every 12 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_
- **[HIGH] VR-03 Contract has no breach notification clause.** No obligation to tell you about incidents affecting your data or systems. Fix: Require the vendor to notify you of security incidents affecting your data or systems within a set time, such as 72 hours. _(SR-8; CSF GV.SC-05)_
- **[MEDIUM] VR-04 Contract has no right to audit or assess.** No contractual right to request evidence or assess controls. Fix: Add the right to request evidence (such as a SOC 2 report) or to assess the vendor's controls. _(SR-6; CSF GV.SC-05)_
- **[MEDIUM] VR-05 No data return or destruction terms at contract end.** Vendor holds confidential data with no return or destruction terms. Fix: Require return or certified destruction of your data when the relationship ends, and revoke the vendor's access. _(SA-9; CSF GV.SC-10)_

### QuickStaff Agency (Critical)

- **[HIGH] VR-01 Vendor assessment is overdue or has never been done.** Never assessed. Tier 1 vendors are reassessed every 12 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_
- **[HIGH] VR-03 Contract has no breach notification clause.** No obligation to tell you about incidents affecting your data or systems. Fix: Require the vendor to notify you of security incidents affecting your data or systems within a set time, such as 72 hours. _(SR-8; CSF GV.SC-05)_
- **[HIGH] VR-08 Weak vendor controls protecting sensitive data.** Control strength 0/100 for a vendor holding regulated data. Fix: Agree on a remediation plan with dates, limit the data shared, or consider an alternative vendor. _(SA-9, SR-6; CSF GV.SC-07)_
- **[MEDIUM] VR-04 Contract has no right to audit or assess.** No contractual right to request evidence or assess controls. Fix: Add the right to request evidence (such as a SOC 2 report) or to assess the vendor's controls. _(SR-6; CSF GV.SC-05)_
- **[MEDIUM] VR-05 No data return or destruction terms at contract end.** Vendor holds regulated data with no return or destruction terms. Fix: Require return or certified destruction of your data when the relationship ends, and revoke the vendor's access. _(SA-9; CSF GV.SC-10)_

### Shred-Right (Critical)

- **[HIGH] VR-02 Contract has no security requirements.** No security requirements recorded in the contract. Fix: Add a security addendum requiring the vendor to maintain safeguards appropriate to the data and access it receives. _(SA-9, SA-4; CSF GV.SC-05)_
- **[HIGH] VR-03 Contract has no breach notification clause.** No obligation to tell you about incidents affecting your data or systems. Fix: Require the vendor to notify you of security incidents affecting your data or systems within a set time, such as 72 hours. _(SR-8; CSF GV.SC-05)_
- **[HIGH] VR-08 Weak vendor controls protecting sensitive data.** Control strength 0/100 for a vendor holding confidential data. Fix: Agree on a remediation plan with dates, limit the data shared, or consider an alternative vendor. _(SA-9, SR-6; CSF GV.SC-07)_
- **[MEDIUM] VR-01 Vendor assessment is overdue or has never been done.** Overdue. Tier 2 vendors are reassessed every 24 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_

### NorthStar ERP Cloud (High)

- **[HIGH] VR-01 Vendor assessment is overdue or has never been done.** Overdue. Tier 1 vendors are reassessed every 12 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_
- **[HIGH] VR-07 Vendor reported a breach in the last 24 months.** A security breach was reported in the last 24 months. Fix: Ask for the incident report and corrective actions, confirm whether your data was affected, and reassess the vendor. _(SR-6; CSF GV.SC-07)_
- **[MEDIUM] VR-04 Contract has no right to audit or assess.** No contractual right to request evidence or assess controls. Fix: Add the right to request evidence (such as a SOC 2 report) or to assess the vendor's controls. _(SR-6; CSF GV.SC-05)_

### Climate Control Pros (High)

- **[CRITICAL] VR-06 Vendor has remote access without MFA.** Vendor connects remotely without confirmed multi-factor authentication. Fix: Require MFA for all vendor remote access, route it through your VPN or a remote access tool you control, and enable it only when needed. _(AC-17, SA-9; CSF GV.SC-05, PR.AA-03)_
- **[MEDIUM] VR-01 Vendor assessment is overdue or has never been done.** Never assessed. Tier 3 vendors are reassessed every 36 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_
- **[LOW] VR-09 Security questionnaire is incomplete.** Unanswered: Tested backups, Incident response plan, Periodic access reviews, Security awareness training, Oversight of their own suppliers. Fix: Follow up on unanswered questions; unanswered items are scored as not in place until confirmed. _(SR-6; CSF GV.SC-07)_

### PrintPoint Leasing (High)

- **[CRITICAL] VR-06 Vendor has remote access without MFA.** Vendor connects remotely without confirmed multi-factor authentication. Fix: Require MFA for all vendor remote access, route it through your VPN or a remote access tool you control, and enable it only when needed. _(AC-17, SA-9; CSF GV.SC-05, PR.AA-03)_
- **[MEDIUM] VR-01 Vendor assessment is overdue or has never been done.** Never assessed. Tier 3 vendors are reassessed every 36 months. Fix: Send the security questionnaire, review the vendor's certifications, and record the assessment date; Tier 1 vendors should be reassessed at least yearly. _(SR-6; CSF GV.SC-07)_

### Midwest Freight Brokers (Moderate)

- **[HIGH] VR-02 Contract has no security requirements.** No security requirements recorded in the contract. Fix: Add a security addendum requiring the vendor to maintain safeguards appropriate to the data and access it receives. _(SA-9, SA-4; CSF GV.SC-05)_
- **[HIGH] VR-03 Contract has no breach notification clause.** No obligation to tell you about incidents affecting your data or systems. Fix: Require the vendor to notify you of security incidents affecting your data or systems within a set time, such as 72 hours. _(SR-8; CSF GV.SC-05)_

### Barnes & Kim CPAs (Moderate)

- **[MEDIUM] VR-04 Contract has no right to audit or assess.** No contractual right to request evidence or assess controls. Fix: Add the right to request evidence (such as a SOC 2 report) or to assess the vendor's controls. _(SR-6; CSF GV.SC-05)_
- **[MEDIUM] VR-05 No data return or destruction terms at contract end.** Vendor holds regulated data with no return or destruction terms. Fix: Require return or certified destruction of your data when the relationship ends, and revoke the vendor's access. _(SA-9; CSF GV.SC-10)_

_Scores are produced by a transparent scoring model from the vendor information supplied. They support, and do not replace, professional judgment about third-party risk. Unanswered questionnaire items are scored as not in place until confirmed._
