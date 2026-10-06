# Vendor inventory reference

One row per vendor. Start from `samples/vendors_template.csv`. Columns are not case-sensitive.

| Column | Values | Notes |
|---|---|---|
| `vendor` | text | Required, unique |
| `service`, `owner` | text | What the vendor does and who manages the relationship |
| `data_sensitivity` | none, internal, confidential, regulated | Most sensitive data the vendor stores or can see |
| `system_access` | none, limited, privileged | Access to your systems; privileged means administrator-level |
| `business_criticality` | low, medium, high, critical | How badly an outage would hurt operations |
| `remote_access` | true, false | Vendor connects into your network or systems |
| `certifications` | semicolon-separated | For example `soc2;iso27001` |
| `last_assessment_date` | YYYY-MM-DD | Blank if never assessed |
| `breach_last_24mo` | true, false | Vendor reported a security breach in the last 24 months |
| `contract_security_clause` | true, false | Contract requires security safeguards |
| `contract_breach_notification` | true, false | Contract requires incident notification |
| `contract_right_to_audit` | true, false | Contract allows you to request evidence or assess |
| `contract_data_return` | true, false | Contract requires return or destruction of data at the end |
| `q_mfa`, `q_encryption`, `q_patching`, `q_backup`, `q_incident_response`, `q_access_review`, `q_training`, `q_subprocessors` | yes, partial, no, or blank | Vendor questionnaire answers |

Blank questionnaire answers are scored as not in place. Blank contract fields are treated as not present.

The inventory may include sensitive details about your vendors and contracts. Store it and the reports securely.
