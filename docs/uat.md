# Desktop UAT

An owner-provided screenshot confirmed the first Desktop open and overview rendering. The remaining checks and latest formatting refinements are pending. File validation does not prove engine evaluation or rendering.

1. Open VelaCRM.pbip, refresh, and confirm all four pages render without model or visual errors.
2. With all slicers clear, match the overview to expected-results.json: Won ACV $24,290,300; open pipeline $8,515,400; win rate 47.3856%; target ACV $19,053,000; attainment gauge about 127.487%. Open deals 176; at-risk deals 110; at-risk ACV $4,969,400; overdue deals 13.
3. Change the Year to 2026 and select Q3. Closed sales and targets must change; snapshot open pipeline must remain fixed. Clear filters after checking.
4. Select West. Both closed sales and pipeline must respond. Clear the selection.
5. Select a customer segment or industry. Target/attainment must be blank, because quotas are not allocated at that grain. Clear filters.
6. On Pipeline intelligence, change creation MonthYear. Stage-reach counts must change; snapshot cards must remain fixed. Confirm the source→outcome SVG renders, counts reconcile to the selected cohort, and changes with creation-period and rep filters. Its links are not selectable. Check Stage Reach Rate in a temporary table if evaluating this optional measure.
7. Check stage order Qualified → Discovery → Demo → Proposal → Negotiation. Stage-history totals must not be mistaken for current-stage distribution.
8. In the attention queue, confirm every displayed deal is open, has positive flagged ACV, and has an attention reason. Right-click an AccountName and drill through to Account detail. The chosen account should appear alone. Return using the native page tabs.
9. Confirm table scrolling, slicer dropdowns, native chart tooltips, selection interactions, card formatting, and fit-to-page scaling on the Surface.
10. Save the working project. Replace the design preview with actual Desktop screenshots for GitHub once UAT passes. Record Desktop version and any corrections below.

## Verification log

- Generated PBIR files: checked against vendored Microsoft JSON schemas.
- Field bindings, canvas bounds, IDs, history dates and close dates: checked in Python.
- Design preview: visually inspected, generated separately from synthetic CSVs.
- First Desktop open and overview rendering: confirmed by owner screenshot on 5 October 2026; win rate 47.4% and attainment 127.5% matched expected results. Currency values displayed rounded ($24M / $9M / $5M).
- Latest refinements: added currency precision, removed duplicated slicer titles, reduced textbox padding, and gave lower charts more height; Desktop verification pending.
- Refresh, all-page DAX reconciliation, and interactions: pending.

## Graphics revision pending Desktop checks

- Overview: quota gauge target 100%, dynamic maximum >=150%, and risk donut reconciles to total open pipeline.
- Pipeline: source-to-outcome SVG ImageUrl measure in a native table; inspect image scaling and empty-cohort behavior.
- Stage funnel: verify Stage Reached Deals is bound to stage categories and correctly ordered.
- Performance: scatter x=Won ACV, y=Win Rate, bubble size=Open Pipeline ACV, point=rep; hover to check values. Bubble size deliberately describes snapshot exposure, not closed-period volume.
- Account and rep filters should affect risk donut and bubble measures; quotas remain blank for unsupported account breakdowns.

## Desktop evidence and formatting correction

Owner screenshot on 5 October confirmed the source/outcome SVG computed and rendered, but its table cell was tiny. Native funnel and attention queue rendered. Numeric formatting settings were incorrectly encoded without type suffixes, so Desktop ignored image sizing and currency precision. Builder now writes typed D/L literals, explicitly sizes the flow column and image, disables conflicting table presets, and assigns stage/risk category colors. The corrected build passes schema and typed-literal checks; re-open and visual inspection are pending.

## Ombré and scorecard revision
Verify the embedded navy-to-violet background on all four pages. Sales performance now uses a taller 1440 × 1020 canvas with a 270-pixel rep scorecard, 10-point values, 2-pixel row padding, and columns set to grow to fill the table. Verify all 12 reps and the total are readable in Power BI Desktop.
