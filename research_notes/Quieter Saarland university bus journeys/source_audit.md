# Independent source and extraction audit

## Are the direct bus options correctly extracted and counted?

### Takeaway
No material daytime minute or column-alignment error was found in the sampled official tables. The 165 HTW/SWS records are 165 distinct selected timetable journeys, with the three campus-stop times stored as columns on the same vehicle; they are not 165 observations of bus occupancy.

### Cited Findings
- The archived operator flyers for all four lines explicitly print a valid-from date of 1 July 2026. I checked the saved flyer text independently for this date. The direction tables used in the extraction are linked by the archived operator timetable index. [Timetable index](https://www.saarbahn.de/fahrplan/fahrplaene), [101 flyer](https://www.saarbruecken.de/media/download-6a26a0ac19e0f), [109 flyer](https://www.saarbruecken.de/media/download-6a26a0b2e2a97), [111/112 flyer](https://www.saarbruecken.de/media/download-6a26a0b46d1fd), [124 flyer](https://www.saarbruecken.de/media/download-6a26a0b7eeb86).
- Independent CSV counts give 271 total home-stop/campus pairs, 165 for HTW/SWS. Those 165 have 165 distinct trip IDs and 165 distinct `(route, direction, home time, Campus time)` signatures. Every one uses Universitat Campus as its primary campus endpoint; terminal and Mensa times are columns, not extra records. There are no alternative lecture-day/non-lecture-day duplicates. The HTW subset has 120 ordinary weekday options and 45 lecture-day-only 112 options. This is an extraction-coverage result from the linked timetable tables, not a count of the complete bus network. [Timetable index](https://www.saarbahn.de/fahrplan/fahrplaene).
- The HTW rows divide into: 101 inbound 35; 109 inbound 18 and outbound 20; 112 inbound 21 and outbound 24; 124 inbound 22 and outbound 25. I checked signatures and conditions programmatically without rerunning or modifying the source extraction. [101 inbound](https://www.saarbruecken.de/media/download-6a2664471a35c), [109 inbound](https://www.saarbruecken.de/media/download-6a26644b33c3a), [109 outbound](https://www.saarbruecken.de/media/download-6a26644b8fc21), [112 inbound](https://www.saarbruecken.de/media/download-6a26644c9f73e), [112 outbound](https://www.saarbruecken.de/media/download-6a26644d6cf50), [124 inbound](https://www.saarbruecken.de/media/download-6a2664516933a), [124 outbound](https://www.saarbruecken.de/media/download-6a26645116974).
- I rasterized and visually inspected the relevant pages of 101 inbound, 101 outbound, 109 outbound, 112 outbound, and both 124 directions. Sample cross-checks include 101 HTW08:02 -> Campus08:23 and HTW09:32 -> Campus09:53; 124 HTW08:22 -> Campus08:43 and HTW10:22 -> Campus10:43; 124 terminal14:17 -> Campus14:20 -> HTW14:41; and 112 Campus16:40 -> HTW17:01 and Campus17:35 -> HTW17:56. These matched the CSV. [101 inbound](https://www.saarbruecken.de/media/download-6a2664471a35c), [124 inbound](https://www.saarbruecken.de/media/download-6a2664516933a), [124 outbound](https://www.saarbruecken.de/media/download-6a26645116974), [112 outbound](https://www.saarbruecken.de/media/download-6a26644d6cf50).
- The 109 Campus08:29 through12:29 columns end at Rathaus, and the 112 Campus14:10 column ends at Hauptbahnhof. They have no HTW time and are correctly absent from direct-home options. The 124 school-day-only columns on its first page are short runs without a university time, so they do not create school-day-dependent campus pairs. [109 outbound](https://www.saarbruecken.de/media/download-6a26644b8fc21), [112 outbound](https://www.saarbruecken.de/media/download-6a26644d6cf50), [124 outbound](https://www.saarbruecken.de/media/download-6a26645116974).
- The 101 outbound table does not supply an HTW/SWS row. The dataset correctly uses the separately identified Betriebshof alternative and does not interpolate an HTW return time. The line arrives at the university from Dudweiler rather than starting empty there. [101 outbound](https://www.saarbruecken.de/media/download-6a2664474ef0f).
- Three pairs cross midnight: `101_to_university_2_16` HTW23:49 -> Campus00:14; the same vehicle Betriebshof23:48 -> Campus00:14; and `101_from_university_2_16` Campus23:41 -> Betriebshof00:08. Duration calculations need modulo24h, and the after-midnight clock time must not be scored as an early-morning same-service-day trip. The HTW subset therefore contains one crossing-midnight option. [101 inbound](https://www.saarbruecken.de/media/download-6a2664471a35c), [101 outbound](https://www.saarbruecken.de/media/download-6a2664474ef0f).

### Inferences
- Rank inbound options at their Campus arrival time and outbound options at their Campus departure time. Boarding at the terminal is an earlier point on the same outbound journey for 109/112/124; it does not add another vehicle to the frequency denominator.
- A selected timetable-option count should not be called a passenger count, a measurement of service reliability, or a complete daily network census.

### Gaps
- This audit checked a meaningful selection of exact daytime pairs and all four lines' relevant structural traps, not every cell in every PDF. No live date-specific journey-planner recheck was performed.
- No passenger counts, vehicle capacities, attendance, or seat probabilities were independently available in these sources.

## Are the consequential class-time corrections supported by primary sources?

### Takeaway
The main documented source corrections are supported. One small date-handling trap needs explicit model logic: the Cybersecurity Tuesday cancellation appears only in the Thursday row's notes in the normalized input.

### Cited Findings
- Hohere Mathematik fur Ingenieure III advertises nominal08-10 lectures and its first lecture at08:30. The tutorial instructions explicitly give08:30 for an08:00 tutorial and10:15 for a10:00 tutorial. The normalized HMI rows preserve the nominal interval and flag the special start convention; the source does not establish an exact physical end. This should not be expanded into an invented exact09:45 or10:00 release. [HMI32627](https://cms.sic.saarland/hmi32627/).
- The agents seminar has a22October notice changing the start from10:00 to10:15 and current organization text10:15-12:00 with first presentation4November. The normalized10:15 start correctly overrides the older ICS boundary. [Agents seminar](https://cms.sic.saarland/sem_agents_ak_w26/).
- Elements of Machine Learning explicitly begins at16:00 and says the hope is to finish around17:35. That is a source-supported release uncertainty, not an exact17:35 end. The normalized record retains18:00 nominal end and documents the possible earlier finish. [EML](https://cms.sic.saarland/emlw26/).
- Foundations of Cybersecurity1 explicitly lists no lecture on22October and17November. Its normalized Thursday lecture notes carry both cancellations, but the Tuesday row has no date-exclusion field. A date-aware model must explicitly remove Tuesday17November even though the relevant note sits on the other weekday row. The Thursday row's3December last date is material to semester averages. I verified the cancellation against the saved primary course topic plan and alerted the quantitative researcher. [Foundations of Cybersecurity1](https://cms.cispa.saarland/cysec1_2627/).
- The HTAI normalized row supplies exactly seven post-kickoff dates and does not include3,10 or17November. Its primary dated table distinguishes preparation weeks from meetings. Robustness in Generative AI similarly uses dated10:15-11:45 sessions before Christmas and separate January10:00-12:00 dates. The CSV's date lists and split timing rows reflect those distinctions. [HTAI](https://cms.cispa.saarland/htai/), [Robustness](https://cms.cispa.saarland/robgenai/).

### Inferences
- For semester averages the single Cybersecurity cancellation has a small numerical effect, but it matters to a specific-week visualization. Do not present exact-week numbers as fully date-aware unless these prose exceptions are handled.
- A sensitivity scenario is appropriate for unspecified nominal ends and the EML approximate release. Explicit course starts should remain fixed across scenarios.

### Gaps
- I did not independently audit every class record, every tutorial group, or cross-source deduplication. Those remain the quantitative merge's responsibility.
- At audit completion the combined model outputs had not yet been written, so this is a source/input audit, not a claim that all final rankings or visual values have been verified.

Audit performed26October2026 using saved primary source documents and normalized local data. Raster audit images are retained in `audit_images/`. No source data files were modified.
