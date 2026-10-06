# Desktop UAT

This document separates observed Desktop behavior from checks still available for a reviewer to reproduce. File validation alone does not prove Power BI engine evaluation or rendering.

## Recorded evidence — 5 October 2026

| Check | Observed result |
| --- | --- |
| Executive overview | Won ACV, win rate, target attainment, and snapshot pipeline reconciled to the fictional baseline |
| 2026 Q3 sales performance | Won ACV $4,494,500; 100 won deals; win rate about 50.5%; target $2,871,000; attainment about 156.5% |
| Rep selection | Alex Rivera Q3 selection displayed $226,000 won ACV, 9 won deals, and about 97.8% attainment; rep scorecard and scatter filtered |
| Account drill-through | Account detail showed the selected Beacon 029 account; the drill-through filter was subsequently cleared |
| Source/outcome flow | SVG rendered in Desktop; image height increased to 220 and both label groups set to 20 to improve readability |
| Stage reach funnel | Counts displayed as whole values with display units disabled |
| Formatting | Owner reviewed the ombré background, sales scorecard spacing, chart colors, and filter-pane readability |
| Probability data type | Fractional probabilities retained as decimal values in Opportunities and Stages; weighted pipeline corrected from about $2.68M to $3.70M |
| Published evidence | Actual Desktop screenshots are included in `design/` and displayed in the README |

The Power BI Desktop version was not recorded. These are owner-observed checks, not a claim that every scenario below was executed.

## Reproduce the baseline

Open `VelaCRM.pbip`, refresh, and clear slicers. Compare the overview with `expected-results.json`:

- Won ACV: $24,290,300
- Open pipeline: $8,515,400; 176 open deals
- Weighted pipeline: $3,703,000
- Win rate: 47.3856%
- Target ACV: $19,053,000; attainment about 127.487%
- At-risk deals: 110; at-risk ACV: $4,969,400
- Overdue deals: 13

## Interaction scenarios

1. Select Year 2026 and Q3. Closed sales and targets change; snapshot open pipeline stays fixed. Clear filters afterward.
2. Select West. Closed sales and snapshot pipeline should respond. Clear the selection.
3. Select customer segment or industry. Target and attainment must be blank because quotas are not allocated at that grain.
4. On Pipeline intelligence, change the creation period. Stage-reach counts and the source/outcome flow should respond; snapshot cards remain fixed. Reconcile the flow counts to the selected cohort. The flow links are not independently selectable.
5. Confirm funnel order Qualified → Discovery → Demo → Proposal → Negotiation. Stage-history counts describe cohort reach, not the current stage distribution.
6. In the attention queue, confirm every displayed deal is open, has positive flagged ACV, and has an attention reason.
7. Right-click an AccountName and drill through to Account detail. Confirm only that account appears. Clear the drill-through filter after testing.
8. Select a rep on Sales performance. Check the scorecard, scatter, monthly won ACV, and targets. Scatter bubble size describes snapshot pipeline exposure.
9. Confirm table scrolling, slicer dropdowns, native tooltips, label readability, and scaling. The rep scorecard may require scrolling to view all 12 reps.
10. Check empty-filter selections and unsupported target breakdowns for clear blank behavior.

## Technical validation and remaining scope

Field bindings, canvas bounds, IDs, history dates, close dates, and decimal probability types were checked in Python. The original generated report was checked against vendored Microsoft JSON schemas.

Desktop upgraded the report definitions to newer schema versions that are not vendored here. Run `python tools/validate_project.py --allow-newer-schemas` for the available schema and structural checks; this explicitly skips missing schema versions and does not establish full newer-schema validation.

Full reconciliation of every DAX measure and every interaction scenario remains available for further review. Service deployment, scheduled refresh, RLS, and cross-report drill-through have not been tested.
