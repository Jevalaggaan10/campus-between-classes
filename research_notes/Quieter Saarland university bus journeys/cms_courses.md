# CMS and dCMS course timing evidence

## Which semester and catalog entries were covered?

### Takeaway
The public SIC CMS catalog currently lists 74 courses under Winter term 2026/2027. Every one of those 74 root pages and every course's public calendar export was successfully fetched on 26 October 2026; 31 calendar exports contain events. The current dCMS public catalog contains no Winter 2026/27 section, so its older courses were not imported into the current-semester model.

### Cited Findings
- The current term is Winter 2026/27, with lectures from 12 October 2026 through 5 February 2027. — [SIC current semester information](https://saarland-informatics-campus.de/en/semesterinfo/)
- The 74-entry current CMS catalog covers computer science, mathematics, computational linguistics and bioinformatics, including several current seminars. The count is this extraction's count of catalog course links under the Winter term 2026/2027 heading, not a university-wide course total. — [SIC CMS catalog](https://cms.sic.saarland/system/courses)
- dCMS's latest listed term is Summer 2026, followed by Winter 2025/26 and older terms. No dCMS Winter 2026/27 entries were used. — [dCMS catalog](https://dcms.cs.uni-saarland.de/system/courses)
- Public ICS calendars can enumerate actual dates, start/end times, locations, canceled entries and topic names. For example, Programming 1 has Monday 08:30–10:00 and Thursday 10:15–12:00 lectures, plus Tuesday tutorial slots and optional office hours. — [Programming 1 timetable](https://cms.sic.saarland/prog1_26/termine/calendar/index), [calendar export](https://cms.sic.saarland/prog1_26/termine/events/download)

### Inferences
- This is a systematic CMS sample, not a census of every Saarland University class or every potential bus rider. The other faculties remain a separate coverage requirement.
- Course count and simultaneous meeting count do not establish attendance or bus passenger numbers. A tutorial row must not be weighted as a whole-course cohort.

### Gaps
- Twelve CMS entries have no current recurring in-person interval in this dataset. Some are completed block courses, online-only, block/TBA seminars, or provide only a first start time. Every entry and reason is recorded in `cms_source_inventory.csv`.
- `probing_2627` and `theory_2627` are intentionally left for the separate seminar researcher, who has current external course pages; avoid duplicating those external rows in the final combined model.
- Public small-group tutorial schedules remain incomplete for Mathematics for Computer Scientists I and III, Introduction to Theoretical Computer Science, and Neural Networks; several schedules are behind registration or materials pages. — [MfCS I](https://cms.sic.saarland/mfi1_mfcs1_wise2627/), [MfCS III](https://cms.sic.saarland/mfcs3_wise2627/), [NNTI](https://cms.sic.saarland/nnti_2627/)

## What timing data is available for modeling?

### Takeaway
The normalized output has 213 recurring-pattern rows, of which 186 are eligible for the default in-person demand proxy across 62 current CMS courses; the other 27 are optional consultations excluded by `include_in_demand=0`. Raw calendars contain 1,803 dated events, including non-class items and dates outside the selected teaching period; use their exclusion flags and the normalized schedule rather than treating all raw events as travelers.

### Cited Findings
- HCI has Tuesday 10:15–12:00 and Wednesday 14:15–16:00 lectures. Its public calendar includes nine separately numbered tutorial groups, including parallel Friday groups. The course is capped at 250 participants; that cap is not an actual attendance measurement. — [HCI page](https://cms.sic.saarland/hci_2627/), [HCI timetable](https://cms.sic.saarland/hci_2627/termine/calendar/index)
- Algorithms for Sequence Analysis has Tuesday and Thursday 08:30–10:00 lectures, Tuesday 14:30–16:00 and Wednesday 10:30–12:00 equivalent tutorials. A 20 October news post says 55 students were enrolled; enrollment can include nonattenders. — [ALSA course](https://cms.sic.saarland/alsa26/)
- Differential Equations in Image Processing and Computer Vision has online-only lectures but an in-person Tuesday 16:15–18:00 tutorial, and a registration cap of 40. The online lectures were excluded from campus bus demand. — [DIC course](https://cms.sic.saarland/dic_26/)
- Statistical Data Compression explicitly advertises Wednesday/Thursday 14:00–16:00 c.t. sessions split between lecture and tutorial. The ICS lecture and tutorial intervals overlap; this dataset merges them into one session per day. — [Statistical Data Compression](https://cms.sic.saarland/statdc26/)
- Higher Mathematics for Engineers III explicitly states c.t. times, with an 08:00 exception that begins at 08:30. Its eight tutorial groups and two lectures are retained with raw nominal times and a note describing the physical start offset. — [HMI III](https://cms.sic.saarland/hmi32627/)
- Visual Generative Models explicitly starts its Monday lecture at 16:00 from the second lecture onward; its Wednesday tutorial begins at 12:15. — [VGM course](https://cms.sic.saarland/vgm/)
- Continually Learning Agents uses Wednesday 12:15–13:45 in C7.2 SR1.12, with a published semester date list. — [Instructor's official seminar repository](https://github.com/at-lab-uds/continually-learning-agents-seminar)

### Inferences
- For each eligible row, use start/end times to create timing vectors. Semantic embeddings are unnecessary for identifying synchronized starts and releases.
- Preserve course, event type and tutorial group. Split tutorial groups are distinct physical meetings; multiple dated copies of one weekly lecture are one recurring pattern.
- A whole-hour calendar interval may be a nominal room slot. ICS timestamps do not by themselves prove that students enter and leave exactly at those advertised clock minutes. Seventy eligible rows retain `time_convention=unknown`; sensitivity testing should allow an academic-quarter and release uncertainty.
- Where `time_convention=ct`, the source explicitly establishes c.t. but may only explain the start shift. Do not assume an exact physical end. HMI 08:00 starts at 08:30, which differs from a generic 15-minute c.t. correction.
- For rows with `scheduled_dates`, model only those dates, or normalize their contribution by the number of relevant teaching weeks. Do not count an irregular seminar block as a weekly full-semester course.
- The 27 consultation rows are not in the default model. They are available for sensitivity analysis at small weights if needed, since many are drop-in offers with tiny or variable attendance.

### Gaps
- No CMS source supplied verified bus-use fractions, daily attendance, student home locations, or how many students continue to another class instead of leaving campus.
- Most courses publish no cohort-size evidence. The HCI and DIC caps are upper limits, not observed student totals; do not sum a course cap once per tutorial row.
- BioStatsLab publishes tutorial starts on Wednesday at 14:15 and Thursday at 12:15 but no public end time in the root or ICS. Those incomplete intervals were omitted instead of inventing an end. — [BioStatsLab](https://cms.sic.saarland/biostatslab26/)

## Which exceptions and source conflicts matter?

### Takeaway
The current lecture news and the date-specific calendars contain material corrections. A final model should respect these exceptions and label its bus recommendations as predictions from published schedules.

### Cited Findings
- A 22 October news update changes Who Does the Science in the Age of Agents? to Wednesday 10:15–12:00; its ICS still says 10:00. The normalized rows use 10:15. Presentations begin on 4 November. — [Course and correction](https://cms.sic.saarland/sem_agents_ak_w26/)
- Elements of Machine Learning's nominal Thursday slot is 16:00–18:00, but a 15 October update states that it starts at 16:00 and aims to finish around 17:35. The dataset retains the published 18:00 end and flags a possible earlier release rather than claiming an exact end. — [EML course news](https://cms.sic.saarland/emlw26/)
- The 3D and 4D Computer Vision calendar labels multiple Wednesday lectures remote and omits others; remote dates are excluded from physical demand. Its in-person lecture/exercise slots are Wednesday/Thursday 14:15–15:45 on the relevant listed dates. — [3D/4D course](https://cms.sic.saarland/cv4d/), [calendar](https://cms.sic.saarland/cv4d/termine/calendar/index)
- Empirical Software Engineering Research uses Monday video uploads and Thursday Zoom Q&A, so none of those calendar entries is in the physical bus-demand model. — [EMSE course](https://cms.sic.saarland/emse_26/)
- Linear Algebra I considered moving its Thursday 16:00–18:00 general exercise; the latest news confirms retaining Thursday. — [Linear Algebra I](https://cms.sic.saarland/la12627/)
- ATOS's 26 October news schedules Monday 11:30–13:00 and Thursday 11:00–12:30 tutorials, but explicitly cancels Monday 26 October. The first Friday lecture is advertised at 08:30; the LSF weekly room interval is 08:00–10:00. — [ATOS course](https://cms.sic.saarland/atos/), [official LSF ATOS entry](https://www.lsf.uni-saarland.de/qisserver/rds?moduleCall=webInfo&publishConfFile=webInfo&publishSubDir=veranstaltung&publishid=166864&state=verpublish&status=init&vmfile=no)
- NNTI's CMS gives first class 20 October at 14:15; the linked chair page says 27 October. LSF corroborates the recurring Tuesday 14:00–16:00 nominal interval. The recurring Tuesday pattern is included, with the first-date conflict documented. — [NNTI CMS](https://cms.sic.saarland/nnti_2627/), [chair page](https://www.lsv.uni-saarland.de/neural-networks-theory-and-implementation-nnti-winter-2026-2027/), [official LSF NNTI](https://www.lsf.uni-saarland.de/qisserver/rds?moduleCall=webInfo&publishConfFile=webInfo&publishSubDir=veranstaltung&publishid=166412&state=verpublish&status=init&vmfile=no)

### Inferences
- A useful representative full teaching week is 2–6 November 2026: it avoids most kickoff meetings and lies after the new tutorial assignments. However, irregular seminars and fortnightly mathematics groups still require date-aware treatment.
- The dense nominal end times around 12:00, 14:00, 16:00 and 18:00 plausibly generate departure waves after walking to the stop. These are predictions, not measured occupancy, and must be combined with buses' actual service frequency and direction.

### Gaps
- Some ICS entries fall on the Christmas break despite generic weekly scheduling. The normalized extraction excludes 21 December 2026–1 January 2027 and preserves these raw dates in the exclusion file. — [ALSA explicit holiday break](https://cms.sic.saarland/alsa26/)
- The Integral Equations seminar calendar has zero-duration entries for early talks and later 12:15–13:15 entries, while the root advertises Monday 12:00–14:00 and early double-talk sessions beginning at 12:00 s.t. The normalized row is a flagged session envelope, with low confidence about actual release time. — [Integral Equations seminar](https://cms.sic.saarland/inteq/)
- OSCAR advertises a Monday recurring meeting but a first date of 21 October 2026, which is Wednesday. The recurring Monday pattern is retained at medium confidence. — [OSCAR](https://cms.sic.saarland/oscar/)

Local files for integration: `cms_meetings.csv`/`.json`, `cms_source_inventory.csv`, `cms_occurrences.csv`/`.json`, `cms_excluded_occurrences.csv`, `cms_coverage_summary.json`, raw HTML/text/ICS in `cms_raw`, and reproducible scripts `fetch_cms.py`, `fetch_cms_calendars.py`, `parse_cms_calendars.py`, `build_cms_meetings.py`. All timestamps extracted from UTC calendars were converted with the Europe/Berlin timezone, including the 25 October daylight-saving transition.
