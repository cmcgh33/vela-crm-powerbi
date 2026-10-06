# Metric definitions

All amounts are USD annual contract value (ACV). Opportunity values are single-product deal values, not ARR balances, recognized revenue, or customer lifetime value.

| Metric | Definition | Date/filter behavior |
| --- | --- | --- |
| Won ACV | Sum ACV for won opportunities | Actual CloseDate in Date context |
| Won/Lost Deals | Number of opportunities with that terminal outcome | Actual CloseDate |
| Win Rate | Won Deals / Closed Deals | Open excluded; blank when denominator is zero |
| Average Won ACV | Won ACV / Won Deals | Actual CloseDate |
| Average Sales Cycle | Mean days from CreatedDate to CloseDate for won deals | Actual CloseDate; lost and open excluded |
| Open Pipeline ACV | Sum ACV for open opportunities | Fixed snapshot; Date ignored |
| Weighted Pipeline ACV | Sum open ACV × current stage probability | Fixed snapshot; heuristic, not calibrated forecast |
| At Risk Deals / ACV | Open deals with any attention flag | Fixed snapshot; flagged deals counted once |
| Overdue Deals | Open deals with ExpectedCloseDate before snapshot | Fixed snapshot |
| Pipeline Risk Share | At Risk Pipeline ACV / Open Pipeline ACV | Fixed snapshot |
| Target ACV | Sum monthly rep quota, up to snapshot | Date, rep and region; blank for unsupported dimensional breakdowns |
| Target Attainment | Won ACV / Target ACV | Use full months/quarters/years; undefined targets return blank |
| Won ACV Prior Year / YoY | Same selected Date period shifted one year | Only 2026 has a previous data year; 2025 comparison is blank |
| Stage Reached Deals | Distinct created-cohort opportunities with an interval for each stage | Date filters CreatedDate instead of CloseDate; removes current-stage restriction when defining cohort |
| Stage Reach Rate | Stage Reached Deals / Cohort Qualified Deals | Conversion from initial qualification, not adjacent-stage conversion |
| Average Completed Stage Days | Mean duration of exited stage intervals for the creation cohort | Excludes uncompleted intervals; do not interpret as survival-adjusted stage duration |
| Last Activity Date | Latest retained activity date | Activity table holds one final activity per opportunity, not full interaction history |

## Attention rules

An open deal is flagged if expected close is before 30 September 2026, no activity for at least 14 days, or current stage age is at least 30 days. A single displayed reason is selected in that priority order. `IsAtRisk` captures any condition; reason groups are mutually exclusive and their ACV totals reconcile.

Stage probabilities are Qualified 15%, Discovery 30%, Demo 50%, Proposal 70%, Negotiation 85%, Won 100%, Lost 0%.

## Time and model caveats

The simulation starts January 2025, so early-month closed results have startup effects. Month-level quota is not daily prorated. A partial-day or arbitrary date filter would not support quota comparisons; the delivered controls use years/quarters. Pipeline ignores Date intentionally and cannot show prior snapshots. Account details deliberately do not carry additional date context on drill-through.

## Source-to-outcome graphic

Cohort Deals counts opportunities by CreatedDate, disabling the active CloseDate relationship and clearing current Stage restrictions. The SVG calculates a 4×3 matrix of source and status counts. All links and node heights are proportional to counts; source and outcome totals reconcile to cohort deals. Outcomes describe status at the fixed snapshot, not outcomes as they were on the creation date. Recent cohorts have immature outcomes; do not compare them as finalized conversion rates. The SVG includes no untrusted text or external URLs, and responds to filter context rather than providing link-level interactions.
