# CISPA and seminar course timing evidence

## Which semester and course listings are covered?

### Takeaway
This pass uses winter 2026/27. It inventories all 27 current CISPA CMS entries, all 50 current seminar listings and all 9 proseminar listings, with unresolved times retained in the audit inventory rather than invented. The 86 index entries resolve to 63 provisional canonical course identifiers before reconciliation with the broader CMS inventory. [CISPA catalog](https://cms.cispa.saarland/system/courses), [seminars](https://seminars.cs.uni-saarland.de/wise2627seminars), [proseminars](https://seminars.cs.uni-saarland.de/wise2627proseminars)

### Cited Findings
- The official current-semester page identifies the lecture period as 12 October 2026 to 5 February 2027. [SIC semester information](https://saarland-informatics-campus.de/en/semesterinfo/)
- All three listing pages were enumerated programmatically. Linked course pages and relevant public timetable pages were fetched, then four official instructor-hosted GitHub course pages were added. There are 93 saved page responses, with one auxiliary chair website connection failure. The 27 CISPA calendar exports were separately fetched successfully; 5 contain events, for 142 raw dated occurrences. Empty calendars were supplemented from public course-page prose. Counts are extraction results from the three official listing sources and their linked calendars, not university-wide completeness claims. [CISPA catalog](https://cms.cispa.saarland/system/courses), [seminars](https://seminars.cs.uni-saarland.de/wise2627seminars), [proseminars](https://seminars.cs.uni-saarland.de/wise2627proseminars)
- The supplied normalized CSV contains 42 time-pattern rows covering 27 courses: 17 CISPA courses and 10 supplemental seminar/chair sources. Several rows represent irregular sessions or time patterns with uncertain physical attendance, not 42 classes occurring every week. [CISPA catalog](https://cms.cispa.saarland/system/courses), [seminar listing](https://seminars.cs.uni-saarland.de/wise2627seminars)
- Entry-level statuses in the exported inventory are: 39 recurring/irregular timed entries; 29 entries without a public recurring time found; 4 one-off/date-only entries; 9 block/kickoff entries; 4 entrusted to the separate SIC CMS researcher; 1 online-only entry. Cross-listing causes repeated entries, and the counts should never be summed with the other researcher's course counts without deduplication. [CISPA catalog](https://cms.cispa.saarland/system/courses), [seminars](https://seminars.cs.uni-saarland.de/wise2627seminars), [proseminars](https://seminars.cs.uni-saarland.de/wise2627proseminars)

### Inferences
- Timed coverage is incomplete even after enumerating all index entries. No quiet time should be interpreted as proof of zero campus activity, and the CS/CISPA sources alone cannot represent all UdS students.
- Proseminar and seminar listings often share one physical class, so their separate assigned-place capacities may be combined only after confirming a shared meeting. Places are capacity allocations, not attendance counts.

### Gaps
- This pass does not enumerate LSF for other faculties. Seminar locations and final dates are often TBA or behind authentication. One auxiliary URL, group.cispa.io/abbasi/, failed TLS, although the relevant CISPA course pages were accessible.
- LLM-based Multi-Agent Systems rendered only a skeleton through direct HTTP; searchable official text supplies only its 26 October introductory session, which is excluded from normal recurring demand. [Official seminar](https://llm-mas-w2026.mpi-sws.org/)
- The sports analytics PDF link was inventoried but not parsed for time evidence; this entry remains unresolved. [Seminar listing](https://seminars.cs.uni-saarland.de/wise2627seminars)

## What recurring meeting times and release waves are supported?

### Takeaway
The sources support substantial boundaries near noon, 14:00 and 16:00, with precise release boundaries often 11:45, 13:45 or 15:45. Wednesday late-afternoon and Friday afternoon also have several timed classes. These are class release opportunities, not measured bus loads. [Foundations of Cybersecurity](https://cms.cispa.saarland/cysec1_2627/), [Security](https://cms.cispa.saarland/sec2627/), [Systems Security](https://cms.cispa.saarland/syssec_26/)

### Cited Findings
- Foundations of Cybersecurity 1: Tue 10:15–11:45 in GHH; Thu 14:15–15:45 in E1 3 HS0.01. Public calendar tutorials are Mon 10:15–11:45, Mon 12:15–13:45, and Fri 12:15–13:45 in CISPA. The old Fri 10–12 tutorial was moved to Mon 12–14. The tentative topic plan stops Thursday lectures after 3 December. [Course page](https://cms.cispa.saarland/cysec1_2627/), [public calendar](https://cms.cispa.saarland/cysec1_2627/termine/events/download)
- Security: Mon/Wed 12:15–13:45 in GHH; tutorials Mon 10–12, Tue 10–12, Wed 10–12, Wed 16–18 and Fri 10–12. An optional Mon 16–18 office hour is separately flagged in the dataset. Tutorial academic-quarter precision is not stated. [Security course](https://cms.cispa.saarland/sec2627/)
- Formal Analysis of Real-World Security Protocols is Mon 10–12 c.t. in CISPA C0 lecture hall; Side-Channel Attacks and Defenses is Tue 10–12 c.t. in the same hall. SCAD's calendar stores nominal 10–12 despite the explicit c.t. prose. [FARWSP](https://cms.cispa.saarland/farwsp2627/), [SCAD](https://cms.cispa.saarland/scad2627/)
- Lean for Algorithms lists Tue lecture and Thu exercises at 14:00; the welcome notice specifies Tue 14:15–16:00 and extends the Thu exercise session to 14:00–17:00. It has a special teaching break 9–15 November, in addition to the winter break. The exercise end is supported by the welcome notice rather than a populated public calendar. [Lean for Algorithms](https://cms.cispa.saarland/lfa/)
- Systems Security: Friday lecture scheduled 14–16, with a notice explicitly clarifying 14:15 start, and Monday tutorial 14–16. The lecturer reports 200 registrations, of which 170 are UdS, but only 90 seats in the physical hall and asks some students to attend online. These numbers demonstrate why course registrations cannot simply become bus-passenger weights. [Systems Security](https://cms.cispa.saarland/syssec_26/)
- Imprecise Probabilistic Machine Learning: Friday 10–12 lecture and Friday 12–14 biweekly exercises. The same course provides UdS, Hamburg and online locations; physical campus attendance is unknown. Exercise phase must be verified for a specific Friday. [Official instructor course](https://muandet-lab.github.io/ipml-course/2026-2027/)
- Usable Security in the Last Decade: Tue 10–12, CISPA. Its calendar also includes zero-length and one-minute submission deadlines; those must be excluded. Privacy Systems and Applications has Wed 09–11 in CISPA, but a 26 October news item warns of a possible schedule shift. [Usable Security](https://cms.cispa.saarland/usld/), [Privacy Systems](https://cms.cispa.saarland/psas26/)
- Two official chair pages fill otherwise missing current CMS timing: Interpreting and Analyzing Neural Language Models (CMS probing_2627), Tue 14:15–15:45, C7.3 room 1.14; Theoretical Abilities and Limitations of Language Models (CMS theory_2627), Fri 12:15–13:45, same room. The latter's CMS hyperlink points to the previous year's page; the current /theory-26/ page has a 2026/27 syllabus. [Interpreting](https://lacoco-lab.github.io/courses/interpreting-2026), [Theory](https://lacoco-lab.github.io/courses/theory-26/)
- The official seminar index supplies Monday 14–16 mandatory in-person Human Oversight of AI, Thursday 10–12 Foundation Models of the Human Mind, Tuesday 10–12 Game Development with Agents and Human-AI Co-Creativity, Thursday 10–11:30 Intelligent Multimodal Interaction in AR, and Friday 15–17 Selected Topics in LLM Post-training. Most of these listing snippets omit rooms. Reconcile with any equivalent SIC CMS rows and avoid double counting. [Seminar listing](https://seminars.cs.uni-saarland.de/wise2627seminars)
- DFKI Hybrid AI is Tue 16:15–18:00, regular topical sessions from 24 November; Quantum AI is Thu 16:15–18:00, topical sessions from 26 November. Both use DFKI NB +2.31. Their October introductory sessions must not create recurring October demand. [Hybrid AI](https://www.dfki.de/~klusch/HAI-seminar-ws26), [Quantum AI](https://www.dfki.de/~klusch/AQAI-seminar-ws26)

### Inferences
- Large, early-year/core courses are more plausible campus demand drivers than a small seminar. If no comparable enrollment evidence exists, provide unweighted event counts and a separate transparent size-sensitivity scenario, not invented student totals.
- For 2–6 November, the source subset supports departures after 11:45/noon, 13:45/14:00, 15:45/16:00, and Wednesday18:00. Walking time pushes boarding after the class boundary. Late morning or middle-of-class intervals can be compared to these release periods after adding the larger CMS and LSF datasets.
- Friday cannot simply be called empty: IPML 10–12 and biweekly12–14, Systems Security14–16, Trustworthy ML14–16 and LLM Post-training15–17 overlap several release times. The respective attendance and sizes differ substantially.

### Gaps
- No source provides route-level bus usage, actual class attendance, arrival/departure behavior, or line assignment. No recommendation in this pass establishes probability of a seat.
- Academic quarter conventions and nominal course boundaries are heterogeneous. Main-page exact notices should take precedence over nominal calendar boundaries; uncertainty of approximately 15 minutes should be explored, not silently resolved to one timestamp.

## How should irregular and excluded events be handled in the combined model?

### Takeaway
Use the actual dated occurrences where possible, and the CSV occurrence_dates field for irregular seminars. Do not project every seminar's advertised weekday across every teaching week.

### Cited Findings
- Humans and Trustworthy AI advertises Tue 14–17 but explicitly has no meetings on 3, 10 or 17 November. Its post-kickoff sessions are 27 October; 24 November; 1 and 15 December; 12, 19 and 26 January. [HTAI](https://cms.cispa.saarland/htai/)
- Autonomous Offensive Security meets selected Wednesdays 16:15–18:00: 28 October; 4, 11 and 25 November; 2, 9 and 16 December; 27 January. The 14 October kickoff and 3 March presentation block are outside the normal-week model. [AOS](https://cms.cispa.saarland/aos_wise26/)
- Web Security meets selected Wednesdays with a 14–16 table interval; its prose instead gives 14:15–16 and contains an invalid month typo. Keep the starting uncertainty, exclude 18 November and winter-break no-meetings, and count the shared seminar/proseminar group once. [Web Security](https://cms.cispa.saarland/websecsem_wise26/)
- Robustness in Generative AI has specific Thu 10:15–11:45 sessions on 5/12/19/26 November and 3/17 December; January proposal sessions use 10–12 on 14/21/28 January. There is no meeting 29 October, 10 December or 7 January. The dated table supersedes its generic Thu10–12 header. [Robustness](https://cms.cispa.saarland/robgenai/)
- Space Informatics Cybersecurity states seven consecutive weekly Friday09–11 sessions starting30October; the first is a kickoff, later six form the regular interval through11December. Trustworthy ML's normal Fri14–16 moves to16–18 on13November and12–14 on20November; some December/January sessions are online. [Space Security](https://cms.cispa.saarland/spacesecurity2627/), [Trustworthy ML](https://cms.cispa.saarland/tml26/)
- Hack-a-Sat has four separated dates rather than a weekly series. The CySec project gives only a6November16:15–17:45 kickoff. Automata Learning has only a30October10–12 kickoff in its public calendar. Bachelor/Master posters currently give a14October event in St Ingbert, which must not enter Saarbrücken-campus demand. [Hack-a-Sat](https://cms.cispa.saarland/hackasat/), [CySec project](https://cms.cispa.saarland/cysecproj2627/), [Automata Learning](https://cms.cispa.saarland/alprosem26/termine/events/download), [Bachelor/Master seminar](https://cms.cispa.saarland/bms_winter2627/)
- Deep Learning Efficiency uses an online kickoff and a semester-break block; its tentative March year is inconsistent. Topics in Privacy-Preserving ML uses an unscheduled1–3day block. Nature-Inspired Optimisation is explicitly Wed16:15–18 online. These are not ordinary weekly physical campus-release events. [DLE](https://cms.cispa.saarland/dle26/), [PPMLO](https://cms.cispa.saarland/ppmlo2627/), [Nature-Inspired Optimisation](https://www.mia.uni-saarland.de/Teaching/nio26.shtml)
- Both seminar and proseminar lists link Computer Architecture to summer2026. The current CISPA catalog correctly links comparch_w26, which lists dates but no public start/end times; it is therefore retained as unresolved rather than copying last semester. [Winter course](https://cms.cispa.saarland/comparch_w26/), [seminar listing](https://seminars.cs.uni-saarland.de/wise2627seminars)

### Inferences
- For a reference week2–6November, exclude HTAI, later-start DFKI topics, kickoffs, online-only courses and all deadlines/exams. Include AOS4November, Robustness5November and Space Security6November with their explicit source times. For a semester-wide model, show both common-week patterns and date-dependent exceptions.
- Meeting CSV nominal times preserve source conventions. The dated ICS raw file is an audit dataset, not already filtered physical demand. Reconcile duplicate title/URL/group records with the other researcher before any count.

### Gaps
- Program Synthesis, Reproducibility in Fuzzing, Computer Architecture and several additional index entries have no publicly confirmed recurring time in this pass. Their absence is missing data, not evidence of an uncrowded period.
- A final route-specific model must be built by the coordinator from the combined transit and university coverage.
