# Quantitative class timing and bus mapping

## What was merged and what remains uncertain?

### Takeaway
The final remaining-semester profile retains **1,471 meeting patterns across 1,062 canonical timed courses**, based on published campus schedules. This is an estimate of scheduled class pressure, not an occupancy forecast or a complete census of physical attendees.

### Cited Findings
- Official lecture dates are12October2026–5February2027. The actionable model covers26October2026–5February2027:13 ordinary teaching weeks, excluding21December–1January. Earlier startup weeks are not reconstructed because public CMS calendar exports predominantly begin26October. [Semester dates](https://saarland-informatics-campus.de/en/semesterinfo/)
- Source enumeration audited74CMS catalog listings,27CISPA listings,50seminars,9proseminars, and1,991 uniqueLSF IDs across14 downloaded branches. These are overlapping catalogs and must not be added as unique course counts. [CMS](https://cms.sic.saarland/system/courses), [CISPA](https://cms.cispa.saarland/system/courses), [Seminars](https://seminars.cs.uni-saarland.de/wise2627seminars), [Proseminars](https://seminars.cs.uni-saarland.de/wise2627proseminars), [LSF](https://www.lsf.uni-saarland.de/qisserver/rds?state=wtree&search=1&root120262=461590)
- The3,210 normalized input patterns reconcile exactly: 1,471 retained +1,656 excluded +83 merged duplicates. 74 are cross-source mirrors and9 are same-source shared physical slots. Detailed row-level reasons are in model_exclusions.csv and model_duplicate_rows.csv. Source priorities are CMS/CISPA current exact notices and calendars, then nominal LSF. [CMS](https://cms.sic.saarland/system/courses), [LSF](https://www.lsf.uni-saarland.de/qisserver/rds?state=wtree&search=1&root120262=461590)
- Cross-source matching uses normalized exact titles plus documented multilingual aliases, matching weekday/meeting kind and start/end within30minutes, with compatible rooms and preservation of explicit distinct tutorial groups. CMS room/date/online corrections override nominal LSF. Two LSF HMI-I catalog IDs share both exact weekday/time/room slots and were combined. Same-source generic titles otherwise remain separate IDs; uncertain matches are not silently fuzzy-merged.
- LSF alone supplies2,955 raw patterns,1,360 default physical recurring representatives across1,038 courses before cross-source merging.95 unlabelled simultaneous room/source rows were suppressed upstream.876 unknown-room rows and70 unverified-location rows are excluded; these categories overlap with other exclusions. 32 retained long slots of4hours or more are present before the no-long-slot sensitivity. A finite semantic audit additionally removed five Umzugsvorbereitung bookings, one internal staff meeting and one explicitly Online/Seminar interval; genuine long teaching and practicals remain. [LSF branch evidence](https://www.lsf.uni-saarland.de/qisserver/rds?P.vx=lang&root120262=461590%7C469204&search=1&state=wtree&trex=total)
- Retained sources contribute186CMS,33CISPA/seminar and1252LSF meeting patterns. 683 retained patterns have unknown nominal time convention; literal minute spans are preserved as printed and are not proof of actual release precision.

### Inferences
- The numeric embedding is two sparse965-dimensional vectors per course:5weekdays×193five-minute bins from06:00through22:00, one channel for advertised starts and one for ends. Entries are expected weekly meeting frequencies, preserving labelled tutorial groups; semantic text embeddings add no useful timing information.
- Each recurring pattern has weight1 when weekly throughout the13-week profile, explicit-date count/13 when dates exist, or expected0.5for fortnightly phase-unknown meetings. Dated/fortnightly models respect start/end restrictions and documented cancellations. Unknown irregular meetings and uncertain physical-location seminar rows are excluded; hybrid rows do not imply full physical attendance.
- For campus arrival time t and class start S, incoming pressure is a triangular kernel in lead(S−t), with support−10to35minutes and peak10minutes. The guard tail permits near-start/late arrivals so a bus arriving10:13before a10:15class does not score falsely zero. For campus departure t and class end E, the outgoing kernel in lag(t−E) has support−5to40minutes and peak10minutes, allowing early release, walking and waiting. These are planning assumptions, not measured travel behavior.
- Timing scenario A uses published intervals with explicit c.t starts shifted15minutes (HMI08:00→08:30 exception). Scenario B also shortens uncertain full-hour ends15minutes and shifts unknown whole-hour class starts15minutes. Exact/literal minute spans remain as printed. EML uses17:35–18:00 release sensitivity. The displayed central score averages the two scenarios; the displayed range is their low/high, not statistical confidence or a true occupancy bound.
- Real HTW/SWS bus options are ranked by the higher timing-scenario score, rounded0.1for ties. Inbound is scored at campus ARRIVAL; outbound at campus DEPARTURE.165 uniqueHTW timetable options were sourced,160 fall within06:00–22:00, giving800 weekday-expanded options. The overnight23:49→00:14trip is excluded. The101return has no verified printed HTW minute and is not fabricated into the HTW ranking. [Operator schedules](https://www.saarbahn.de/fahrplan/fahrplaene)

### Gaps
- No measured passenger counts, route shares, attendance, bus capacities/assignments, student home locations or individual final-class times were found. An equal meeting-weight index treats a small seminar and a large lecture as one pattern; actual bus loads can differ greatly.
- Catalog merging is conservative and auditable, not proof every cross-listing is resolved. Missing tutorials, unknown rooms, unscheduled/block activity, staff, schools, library/canteen users and lingering students remain outside the pressure model. Unknown-room exclusions can create deceptively light cells.
- The model is a remaining-semester ordinary-week average; it is not an exact itinerary forecast for any one date. Christmas, cancellations, changing seminar schedules and future timetable revisions need date-specific checking.

## Which verified weekday options rank well?

### Takeaway
The clearest reusable morning gap is Campus arrival around09:20–09:25; Tuesday and Friday also have a low-pressure10:43–10:55gap. Homebound gaps depend more on weekday. The table below picks the first tied option within a useful daytime band, not an objectively unique optimum.

### Cited Findings
| Day | HTW/SWS → Universität Campus | Inbound timing range | Campus → HTW/SWS | Return timing range | Earlier terminal boarding |
|---|---|---:|---|---:|---|
|Monday|[101 09:02 → 09:23](https://www.saarbruecken.de/media/download-6a2664471a35c)|0.0–0.1|[112 15:10 → 15:31](https://www.saarbruecken.de/media/download-6a26644d6cf50)|0.0–0.0|112 terminal 15:07|
|Tuesday|[124 10:22 → 10:43](https://www.saarbruecken.de/media/download-6a2664516933a)|0.0–0.0|[124 16:50 → 17:11](https://www.saarbruecken.de/media/download-6a26645116974)|0.7–0.7|124 terminal 16:47|
|Wednesday|[101 09:02 → 09:23](https://www.saarbruecken.de/media/download-6a2664471a35c)|0.8–1.1|[124 17:20 → 17:41](https://www.saarbruecken.de/media/download-6a26645116974)|0.2–0.7|124 terminal 17:17|
|Thursday|[101 09:02 → 09:23](https://www.saarbruecken.de/media/download-6a2664471a35c)|0.0–0.1|[112 15:10 → 15:31](https://www.saarbruecken.de/media/download-6a26644d6cf50)|0.0–0.0|112 terminal 15:07|
|Friday|[124 10:22 → 10:43](https://www.saarbruecken.de/media/download-6a2664516933a)|0.0–0.0|[124 18:50 → 19:11](https://www.saarbruecken.de/media/download-6a26645116974)|0.0–0.0|124 terminal 18:47|

- All bus clock times above come from the current linked operator PDFs, valid from1July2026, checked26October. The crowd index is derived from the course dataset. A model score0.0 means no collected meeting pressure inside the kernel; it never means an empty bus. [Official bus index](https://www.saarbahn.de/fahrplan/fahrplaene)
- Monday/Thursday alternatives include124 Campus15:20→HTW15:41 (terminal15:17), avoiding the large15:45/16:00 release waves. Monday also has112Campus15:30→HTW15:51 and15:40→16:01. Tuesday124Campus16:50→HTW17:11; Wednesday124Campus17:20→17:41. [124 toward town](https://www.saarbruecken.de/media/download-6a26645116974), [112 toward town](https://www.saarbruecken.de/media/download-6a26644d6cf50)
- Friday’s first minimum in the15:00–19:30band is late18:50 (124). An earlier practical choice is109Campus15:29→HTW16:00 or112Campus15:30→HTW15:51; these are still near the bottom of the model, with high timing scenario about1.0. [109 toward town](https://www.saarbruecken.de/media/download-6a26644b8fc21), [112 toward town](https://www.saarbruecken.de/media/download-6a26644d6cf50)

### Inferences
- A simple consistent morning routine is101HTW09:02→Campus09:23every weekday;112has a same-time lecture-day trip. The model cannot say which line has fewer existing riders, so the two are timing ties. Tuesday/Friday12410:22→10:43is a later alternative, not a necessary delay for a tiny score difference.
- Boarding112/109/124at the terminal3minutes before Campus can place the user ahead of later Campus pickups. It may improve boarding order, but terminal queues still exist;101is a through service fromDudweiler. [Campus access](https://www.uni-saarland.de/standort/saarbruecken/bahn-bus.html)
- Do not blindly choose124 :50 homeward: it can fall just after :45 class releases, while :20 may be between waves. Day-specific courses and late-hour differences mean a universal :20rule is also unsupported.

### Gaps
- The daytime bands (arrival08:00–11:00; return15:00–19:30) are presentation conveniences only. User requested no time constraints; the interactive sorter and fullCSV also include all06:00–22:00and midday options. Early/late model zeros are trivial ties, not meaningful evidence that those buses are empty.

## Where are the waves and how was the output verified?

### Takeaway
The broad data strongly supports synchronized class-start and class-ending waves around the familiar even-hour transitions. The maps and ranked data retain uncertainty instead of claiming measured crowd probabilities.

### Cited Findings
- Monday: strongest model peaks incoming 10:05 (62.2), outgoing 11:55 (53.1). Derived from the normalized source-linked meeting data; these are index values, not passengers.
- Tuesday: strongest model peaks incoming 10:05 (72.2), outgoing 11:55 (64.0). Derived from the normalized source-linked meeting data; these are index values, not passengers.
- Wednesday: strongest model peaks incoming 10:05 (64.9), outgoing 11:55 (56.9). Derived from the normalized source-linked meeting data; these are index values, not passengers.
- Thursday: strongest model peaks incoming 14:05 (65.5), outgoing 15:55 (59.8). Derived from the normalized source-linked meeting data; these are index values, not passengers.
- Friday: strongest model peaks incoming 10:05 (44.4), outgoing 11:55 (37.2). Derived from the normalized source-linked meeting data; these are index values, not passengers.

### Inferences
- Across weekdays, incoming waves cluster around09:45–10:15,11:45–12:15and13:45–14:15; outgoing waves around11:50–12:25,13:50–14:25and15:50–16:25, with evening variation. Published :45ends plus a walk explain crowds at even hours; nominal full-hour endings add a later component.
- Friday has substantially fewer collected scheduled meetings than Tuesday, but actual student totals and route loads cannot be inferred from this ratio. Counts use a common map scale across weekdays so Friday is not independently normalized to look equally busy.
- BusCSV includes lecture-only, no-long-slot and core-faculty-only higher-scenario scores. These sensitivities remove different possible artifacts; agreement is evidence about the timing proxy only, not about measured occupancy.

### Gaps
- The heatmap has passed data and script validation; the parent coordinator must still inspect it using html_preview and show it with html_render. No live browser or server was used for verification.

Local deliverables: reports/saarland-bus-heatmap.html; saarland-class-time-vectors.csv (965rows); saarland-bus-ranked-departures.csv (800rows); saarland-course-time-embeddings.json (two sparse965dimvectors/course); saarland-canonical-class-meetings.csv; saarland-weekday-bus-options.csv. Reproduce with build_timing_model.py then build_heatmap.py then finalize_analysis.py. Validation details: model_validation.json; all12checks passed.
