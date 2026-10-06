# Semantic model

Dimensions: Accounts (AccountID), Sales Reps (RepID), Stages (StageID), and Date (Date). Facts: Opportunities (one row per deal), Stage History (one stage interval per deal/stage), Activities (last activity per deal), and Targets (one quota per rep/month).

| One side | Many side | State |
| --- | --- | --- |
| Accounts.AccountID | Opportunities.AccountID | Active |
| Sales Reps.RepID | Opportunities.RepID | Active |
| Stages.StageID | Opportunities.StageID | Active |
| Date.Date | Opportunities.CloseDate | Active |
| Date.Date | Opportunities.CreatedDate | Inactive; cohort measures activate it |
| Opportunities.OpportunityID | Activities.OpportunityID | Active |
| Opportunities.OpportunityID | Stage History.OpportunityID | Inactive; cohort measures transfer IDs explicitly |
| Stages.StageID | Stage History.StageID | Active |
| Sales Reps.RepID | Targets.RepID | Active |
| Date.Date | Targets.MonthDate | Active |

All relationships filter from one to many. The inactive Opportunity→Stage History link prevents ambiguous stage filtering through both the current-stage and historical-stage routes. Cohort measures disable CloseDate filtering, activate CreatedDate, then pass the filtered opportunity IDs to Stage History using TREATAS.

StageName sorts by StageOrder; MonthYear sorts by YearMonth. ID columns are hidden and raw columns default to no summarization. The Date table is marked as a time table with a unique Date key.

## Reproducibility and handling

M reads embedded JSON rows in base64 and explicitly converts types. No external connection or Windows folder path is required. CSV files expose the same data for review. Rebuilding the project overwrites report definitions; retain Desktop refinements separately or incorporate them into the builder before running it again.

The sample contains no actual CRM connection, RLS, or credentials. Production adaptation would require source validation, refresh strategy, access policy, calibrated forecasting, complete activity logging, and periodized pipeline snapshots.
