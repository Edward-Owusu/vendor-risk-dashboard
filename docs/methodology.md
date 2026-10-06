# Methodology

## Purpose

The tool gives a small or mid-sized organization a consistent, explainable way to rank the security risk its vendors and service providers introduce, and a list of concrete fixes in contracts, assessments, and vendor controls. It supports the supply chain risk management practices in NIST SP 800-53 Rev. 5 (the SR family and related controls) and the Cybersecurity Supply Chain Risk Management category (GV.SC) of the NIST Cybersecurity Framework 2.0.

## Impact (1 to 5)

Impact reflects how much harm the organization would suffer if the vendor were compromised:

```
impact = max(data sensitivity score, business criticality score) + 1 if the vendor has privileged access
```

| Data sensitivity | Score | Business criticality | Score |
|---|---|---|---|
| none | 1 | low | 1 |
| internal | 2 | medium | 2 |
| confidential | 3 | high | 3 |
| regulated (for example personal, health, or financial data) | 4 | critical | 4 |

Impact is capped at 5. **Tier** follows impact: 4 or 5 is Tier 1, 3 is Tier 2, and 1 or 2 is Tier 3.

## Likelihood (1 to 5)

Likelihood reflects how likely the vendor is to be compromised, based on its security controls:

1. **Control strength (0 to 100)** is the weighted share of eight questionnaire items answered yes (partial counts half, and unanswered counts as not in place): MFA (weight 3), encryption, patching, backups, incident response (2 each), access reviews, training, and oversight of their own suppliers (1 each). A recognized certification (such as SOC 2 or ISO 27001) adds 10 points, capped at 100.
2. Control strength maps to likelihood: 85 or more is 1, 70 or more is 2, 50 or more is 3, 30 or more is 4, below 30 is 5.
3. Add 1 for a breach reported in the last 24 months, and 1 for remote access without confirmed MFA. Likelihood is capped at 5.

## Residual risk

```
risk score = impact x likelihood   (1 to 25)
```

Bands: 15 or more Critical, 10 to 14 High, 5 to 9 Moderate, 1 to 4 Low. The heat map places each vendor at its impact and likelihood.

## Findings

| Rule | Finding | Applies when | Controls | CSF 2.0 |
|---|---|---|---|---|
| VR-01 | Assessment overdue or never done | Past the tier's reassessment period (Tier 1: 12 months, Tier 2: 24, Tier 3: 36) | SR-6 | GV.SC-07 |
| VR-02 | No security requirements in the contract | Tier 1 or 2 | SA-9, SA-4 | GV.SC-05 |
| VR-03 | No breach notification clause | Tier 1 or 2, or confidential or regulated data | SR-8 | GV.SC-05 |
| VR-04 | No right to audit or assess | Tier 1 | SR-6 | GV.SC-05 |
| VR-05 | No data return or destruction terms | Confidential or regulated data | SA-9 | GV.SC-10 |
| VR-06 | Remote access without MFA | Vendor has remote access | AC-17, SA-9 | GV.SC-05, PR.AA-03 |
| VR-07 | Breach in the last 24 months | Reported breach | SR-6 | GV.SC-07 |
| VR-08 | Weak controls protecting sensitive data | Control strength below 50 with confidential or regulated data | SA-9, SR-6 | GV.SC-07 |
| VR-09 | Questionnaire incomplete | Some, but not all, items unanswered | SR-6 | GV.SC-07 |

## Adjusting the model

All weights, scores, thresholds, and reassessment periods are in `src/vendor_risk/data/model.json`. Copy the file, change values, and pass it with `--model`.

## Limitations

- Scores depend on the accuracy of the inventory and the vendors' questionnaire answers, which are self-reported.
- The model is a transparent prioritization aid, not a statistical prediction of breach probability. Weights reflect the author's judgment and should be adjusted to each organization's risk appetite.
