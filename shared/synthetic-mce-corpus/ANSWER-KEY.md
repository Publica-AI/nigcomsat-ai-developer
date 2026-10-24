# Answer Key (instructor only)

Do not give this file to participants. It records the true facts in each document and the traps built into them, so demos and test sets can be checked against known answers.

## NOC-INC-2026-0417 - NOC incident report

| Field | Value |
|---|---|
| Incident ID | NOC-INC-2026-0417 |
| Affected link | KU-HUB1-GW3 |
| Severity | P2 - High |
| Customers affected | 3 (Harmattan Telecom Ltd, Savanna Rural Connect, Rivers Basin Logistics) |
| Terminals affected | 41 |
| Detected | 2026-04-17 02:14 WAT |
| Escalated | 2026-04-17 02:31 WAT |
| Mitigation applied | 2026-04-17 03:05 WAT (backup carrier KU-HUB1-GW3-B, 60% capacity) |
| Restored | 2026-04-17 03:52 WAT |
| Impact duration from timestamps | 1 hour 38 minutes |
| Root cause | Failed cooling fan caused over-temperature shutdown of uplink power amplifier HPA-2 at Hub 1 |
| Post-incident review due | 2026-04-24 |

**Trap:** the summary says the outage "lasted approximately two hours", but the timestamps give 1 hour 38 minutes. An extractor that copies the narrative instead of computing from timestamps is wrong. Use it in Module 1 Topic 5 (validation) and Topic 6 (verification).

## MCE-CN-2026-031 - Notice of non-compliance

| Field | Value |
|---|---|
| Notice reference | MCE-CN-2026-031 |
| Date of notice | 2026-03-09 |
| Addressee | Sahel Link Networks Ltd |
| Licence number | VSAT-OP-0192 (Class B VSAT Service Operator) |
| Condition breached | Licence Condition 7.2 (Quarterly Reporting) |
| Report missing | Q4 2025 Quarterly Service Quality Report |
| Original report due date | 2026-01-30 (30 days after quarter end) |
| Original deadline in notice | 2026-03-30 (21 days from the notice) |
| Revised deadline | 2026-04-13 (Revision Notice dated 2026-03-20; supersedes 2(a)) |
| Representations window | 7 days from the date of the notice |
| Penalty | NGN 2,500,000 per full week of continued default, maximum NGN 10,000,000 |

**Trap:** two deadlines appear in the document. The correct current deadline is 2026-04-13. An answer of 2026-03-30 is outdated. Use it in Module 1 Topic 6 and again in Module 4 (current versus superseded documents).

## MCE-EC-2025-118 - Enforcement case file

| Field | Value |
|---|---|
| Case number | MCE-EC-2025-118 |
| Respondent | Delta Coast Broadband Ltd (licence VSAT-OP-0077) |
| Breach | Six unregistered VSAT terminals at Warri Industrial Park, Licence Condition 4.5 (Terminal Registration) |
| Inspection / case opened | 2025-08-14 |
| Notice of Violation | 2025-08-28 (14-day response period, so due 2025-09-11) |
| Response received | 2025-09-19 (late) |
| Hearing | 2025-11-05 |
| Decision | 2025-11-26: penalty NGN 5,000,000 and register all terminals by 2026-01-25 |
| Payments | NGN 3,000,000 on 2025-12-10 and NGN 2,000,000 on 2026-01-28, paid in full |
| Remediation verified | 2026-01-20 |
| Case closed | 2026-02-02, compliant |

**Trap:** the header still reads "Current status: OPEN - awaiting remediation", but the timeline closes the case on 2026-02-02. The correct status is closed. An answer based on the header alone is wrong.

## Questions the corpus cannot answer (cite-or-refuse tests)

A correct assistant or extractor must say the information is not in the documents:

- Who is the Director of Monitoring, Compliance and Enforcement?
- Which vendor made the failed HPA-2 amplifier?
- Was Sahel Link Networks Ltd's Q4 report eventually submitted?

## Suggested checks by topic

| Topic | Check |
|---|---|
| Module 1 Topic 2 | Ask about MCE-CN-2026-031 with no document supplied. Any specific licence number or deadline is a hallucination. |
| Module 1 Topic 5 | Extract incident fields. Severity, link ID and timestamps must match the table above. |
| Module 1 Topic 6 | Run the extractor and question set. Flag the "two hours" trap, the superseded deadline and the stale OPEN header. |
