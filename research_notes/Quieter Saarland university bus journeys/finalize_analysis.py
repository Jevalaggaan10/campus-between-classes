"""Generate audit notes and focused integrity checks from the final model outputs."""
import pathlib,json,csv,collections,importlib.util
ROOT=pathlib.Path(__file__).resolve().parent
data=json.loads((ROOT/'model_data.json').read_text(encoding='utf-8'))
s,rows,buses,vectors=data['summary'],data['meetings'],data['ranked_bus_options'],data['vectors']
sp=importlib.util.spec_from_file_location('timing_model',ROOT/'build_timing_model.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

checks={
 'source_accounting':sum(v['input_rows'] for v in s['catalog_source_counts'].values())==len(rows)+s['excluded_rows']+s['merged_duplicate_rows'],
 'positive_intervals':all(r['end_minute']>r['start_minute'] for r in rows),
 'weekday_bounds':all(1<=r['weekday']<=5 for r in rows),
 'weights_in_0_to_1':all(0<r['frequency_weight']<=1 for r in rows),
 'all_meetings_sourced':all(r.get('source_url','').startswith('https://') for r in rows),
 'no_christmas_meetings':all(not m.BREAK_START<=d<=m.BREAK_END for r in rows for d in m.parse_dates(r['model_dates'])),
 'cybersecurity_17_nov_cancelled':all('2026-11-17' not in r['model_dates'] for r in rows if r.get('course_id')=='cysec1_2627'),
 'five_weekdays_193_bins':len(vectors)==5*193 and all(sum(v['weekday']==day for v in vectors)==193 for day in range(1,6)),
 'all_bus_pairs_htw':all(r['home_stop']=='HTW / SWS' for r in buses),
 'no_unverified_101_return':all(not(r['route']=='101' and r['model_direction']=='outgoing') for r in buses),
 'unique_weekday_bus_trip':len(buses)==len({(r['weekday'],r['trip_id']) for r in buses}),
 'nonnegative_scores':all(r['timing_low']>=0 and r['timing_low']<=r['timing_high'] for r in buses),
}
assert all(checks.values()),checks
(ROOT/'model_validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')

def options(day,direction,band=True):
    return [b for b in buses if b['weekday']==day and b['model_direction']==direction and (not band or b['daytime_option'])]
def show(b):
    journey=(b['home_time']+' → '+b['campus_time']) if b['model_direction']=='incoming' else (b['campus_time']+' → '+b['home_time'])
    return b['route']+' '+journey
def link(b):return '['+show(b)+']('+b['source_url']+')'

chosen=[]
for day in range(1,6):
    inbound=options(day,'incoming')[0];outbound=options(day,'outgoing')[0]
    chosen.append({'weekday':day,'day':m.DAYS[day-1],'to_university_route':inbound['route'],'htw_departure':inbound['home_time'],'campus_arrival':inbound['campus_time'],'to_university_timing_low':inbound['timing_low'],'to_university_timing_high':inbound['timing_high'],'return_route':outbound['route'],'campus_departure':outbound['campus_time'],'terminal_departure':outbound['terminal_time'],'htw_arrival':outbound['home_time'],'return_timing_low':outbound['timing_low'],'return_timing_high':outbound['timing_high'],'inbound_source':inbound['source_url'],'outbound_source':outbound['source_url']})
m.write_csv(pathlib.Path('C:/codex/reports/saarland-weekday-bus-options.csv'),chosen)

lines=['# Quantitative class timing and bus mapping','', '## What was merged and what remains uncertain?', '', '### Takeaway',
f'The final remaining-semester profile retains **{len(rows):,} meeting patterns across {s["retained_unique_canonical_courses"]:,} canonical timed courses**, based on published campus schedules. This is an estimate of scheduled class pressure, not an occupancy forecast or a complete census of physical attendees.', '', '### Cited Findings',
'- Official lecture dates are12October2026–5February2027. The actionable model covers26October2026–5February2027:13 ordinary teaching weeks, excluding21December–1January. Earlier startup weeks are not reconstructed because public CMS calendar exports predominantly begin26October. [Semester dates](https://saarland-informatics-campus.de/en/semesterinfo/)',
'- Source enumeration audited74CMS catalog listings,27CISPA listings,50seminars,9proseminars, and1,991 uniqueLSF IDs across14 downloaded branches. These are overlapping catalogs and must not be added as unique course counts. [CMS](https://cms.sic.saarland/system/courses), [CISPA](https://cms.cispa.saarland/system/courses), [Seminars](https://seminars.cs.uni-saarland.de/wise2627seminars), [Proseminars](https://seminars.cs.uni-saarland.de/wise2627proseminars), [LSF](https://www.lsf.uni-saarland.de/qisserver/rds?state=wtree&search=1&root120262=461590)',
f'- The3,210 normalized input patterns reconcile exactly: {len(rows):,} retained +{s["excluded_rows"]:,} excluded +{s["merged_duplicate_rows"]} merged duplicates. {s["cross_source_duplicate_rows"]} are cross-source mirrors and{s["within_source_shared_meeting_rows"]} are same-source shared physical slots. Detailed row-level reasons are in model_exclusions.csv and model_duplicate_rows.csv. Source priorities are CMS/CISPA current exact notices and calendars, then nominal LSF. [CMS](https://cms.sic.saarland/system/courses), [LSF](https://www.lsf.uni-saarland.de/qisserver/rds?state=wtree&search=1&root120262=461590)',
'- Cross-source matching uses normalized exact titles plus documented multilingual aliases, matching weekday/meeting kind and start/end within30minutes, with compatible rooms and preservation of explicit distinct tutorial groups. CMS room/date/online corrections override nominal LSF. Two LSF HMI-I catalog IDs share both exact weekday/time/room slots and were combined. Same-source generic titles otherwise remain separate IDs; uncertain matches are not silently fuzzy-merged.',
f'- LSF alone supplies2,955 raw patterns,1,360 default physical recurring representatives across1,038 courses before cross-source merging.95 unlabelled simultaneous room/source rows were suppressed upstream.876 unknown-room rows and70 unverified-location rows are excluded; these categories overlap with other exclusions. {sum(r["end_minute"]-r["start_minute"]>=240 for r in rows)} retained long slots of4hours or more are present before the no-long-slot sensitivity. A finite semantic audit additionally removed five Umzugsvorbereitung bookings, one internal staff meeting and one explicitly Online/Seminar interval; genuine long teaching and practicals remain. [LSF branch evidence](https://www.lsf.uni-saarland.de/qisserver/rds?P.vx=lang&root120262=461590%7C469204&search=1&state=wtree&trex=total)',
f'- Retained sources contribute{sum(r["collection"]=="CMS" for r in rows)}CMS,{sum(r["collection"]=="CISPA/seminars" for r in rows)}CISPA/seminar and{sum(r["collection"]=="LSF" for r in rows)}LSF meeting patterns. {s["unknown_time_patterns"]} retained patterns have unknown nominal time convention; literal minute spans are preserved as printed and are not proof of actual release precision.',
'', '### Inferences',
'- The numeric embedding is two sparse965-dimensional vectors per course:5weekdays×193five-minute bins from06:00through22:00, one channel for advertised starts and one for ends. Entries are expected weekly meeting frequencies, preserving labelled tutorial groups; semantic text embeddings add no useful timing information.',
'- Each recurring pattern has weight1 when weekly throughout the13-week profile, explicit-date count/13 when dates exist, or expected0.5for fortnightly phase-unknown meetings. Dated/fortnightly models respect start/end restrictions and documented cancellations. Unknown irregular meetings and uncertain physical-location seminar rows are excluded; hybrid rows do not imply full physical attendance.',
'- For campus arrival time t and class start S, incoming pressure is a triangular kernel in lead(S−t), with support−10to35minutes and peak10minutes. The guard tail permits near-start/late arrivals so a bus arriving10:13before a10:15class does not score falsely zero. For campus departure t and class end E, the outgoing kernel in lag(t−E) has support−5to40minutes and peak10minutes, allowing early release, walking and waiting. These are planning assumptions, not measured travel behavior.',
'- Timing scenario A uses published intervals with explicit c.t starts shifted15minutes (HMI08:00→08:30 exception). Scenario B also shortens uncertain full-hour ends15minutes and shifts unknown whole-hour class starts15minutes. Exact/literal minute spans remain as printed. EML uses17:35–18:00 release sensitivity. The displayed central score averages the two scenarios; the displayed range is their low/high, not statistical confidence or a true occupancy bound.',
'- Real HTW/SWS bus options are ranked by the higher timing-scenario score, rounded0.1for ties. Inbound is scored at campus ARRIVAL; outbound at campus DEPARTURE.165 uniqueHTW timetable options were sourced,160 fall within06:00–22:00, giving800 weekday-expanded options. The overnight23:49→00:14trip is excluded. The101return has no verified printed HTW minute and is not fabricated into the HTW ranking. [Operator schedules](https://www.saarbahn.de/fahrplan/fahrplaene)',
'', '### Gaps',
'- No measured passenger counts, route shares, attendance, bus capacities/assignments, student home locations or individual final-class times were found. An equal meeting-weight index treats a small seminar and a large lecture as one pattern; actual bus loads can differ greatly.',
'- Catalog merging is conservative and auditable, not proof every cross-listing is resolved. Missing tutorials, unknown rooms, unscheduled/block activity, staff, schools, library/canteen users and lingering students remain outside the pressure model. Unknown-room exclusions can create deceptively light cells.',
'- The model is a remaining-semester ordinary-week average; it is not an exact itinerary forecast for any one date. Christmas, cancellations, changing seminar schedules and future timetable revisions need date-specific checking.',
'', '## Which verified weekday options rank well?', '', '### Takeaway',
'The clearest reusable morning gap is Campus arrival around09:20–09:25; Tuesday and Friday also have a low-pressure10:43–10:55gap. Homebound gaps depend more on weekday. The table below picks the first tied option within a useful daytime band, not an objectively unique optimum.', '', '### Cited Findings',
'| Day | HTW/SWS → Universität Campus | Inbound timing range | Campus → HTW/SWS | Return timing range | Earlier terminal boarding |',
'|---|---|---:|---|---:|---|']
for day in range(1,6):
    a=options(day,'incoming')[0];b=options(day,'outgoing')[0]
    lines.append(f'|{m.DAYS[day-1]}|{link(a)}|{a["timing_low"]:.1f}–{a["timing_high"]:.1f}|{link(b)}|{b["timing_low"]:.1f}–{b["timing_high"]:.1f}|{b["route"]} terminal {b["terminal_time"]}|')
lines += ['', '- All bus clock times above come from the current linked operator PDFs, valid from1July2026, checked26October. The crowd index is derived from the course dataset. A model score0.0 means no collected meeting pressure inside the kernel; it never means an empty bus. [Official bus index](https://www.saarbahn.de/fahrplan/fahrplaene)',
'- Monday/Thursday alternatives include124 Campus15:20→HTW15:41 (terminal15:17), avoiding the large15:45/16:00 release waves. Monday also has112Campus15:30→HTW15:51 and15:40→16:01. Tuesday124Campus16:50→HTW17:11; Wednesday124Campus17:20→17:41. [124 toward town](https://www.saarbruecken.de/media/download-6a26645116974), [112 toward town](https://www.saarbruecken.de/media/download-6a26644d6cf50)',
'- Friday’s first minimum in the15:00–19:30band is late18:50 (124). An earlier practical choice is109Campus15:29→HTW16:00 or112Campus15:30→HTW15:51; these are still near the bottom of the model, with high timing scenario about1.0. [109 toward town](https://www.saarbruecken.de/media/download-6a26644b8fc21), [112 toward town](https://www.saarbruecken.de/media/download-6a26644d6cf50)',
'', '### Inferences',
'- A simple consistent morning routine is101HTW09:02→Campus09:23every weekday;112has a same-time lecture-day trip. The model cannot say which line has fewer existing riders, so the two are timing ties. Tuesday/Friday12410:22→10:43is a later alternative, not a necessary delay for a tiny score difference.',
'- Boarding112/109/124at the terminal3minutes before Campus can place the user ahead of later Campus pickups. It may improve boarding order, but terminal queues still exist;101is a through service fromDudweiler. [Campus access](https://www.uni-saarland.de/standort/saarbruecken/bahn-bus.html)',
'- Do not blindly choose124 :50 homeward: it can fall just after :45 class releases, while :20 may be between waves. Day-specific courses and late-hour differences mean a universal :20rule is also unsupported.',
'', '### Gaps',
'- The daytime bands (arrival08:00–11:00; return15:00–19:30) are presentation conveniences only. User requested no time constraints; the interactive sorter and fullCSV also include all06:00–22:00and midday options. Early/late model zeros are trivial ties, not meaningful evidence that those buses are empty.',
'', '## Where are the waves and how was the output verified?', '', '### Takeaway',
'The broad data strongly supports synchronized class-start and class-ending waves around the familiar even-hour transitions. The maps and ranked data retain uncertainty instead of claiming measured crowd probabilities.', '', '### Cited Findings']
for day in range(1,6):
    dr=[v for v in vectors if v['weekday']==day]
    peaks=[]
    for direction in ['incoming','outgoing']:
        p=max(dr,key=lambda r:r[direction+'_score']);peaks.append(direction+' '+p['time']+f' ({p[direction+"_score"]:.1f})')
    lines.append('- '+m.DAYS[day-1]+': strongest model peaks '+', '.join(peaks)+'. Derived from the normalized source-linked meeting data; these are index values, not passengers.')
lines += ['', '### Inferences',
'- Across weekdays, incoming waves cluster around09:45–10:15,11:45–12:15and13:45–14:15; outgoing waves around11:50–12:25,13:50–14:25and15:50–16:25, with evening variation. Published :45ends plus a walk explain crowds at even hours; nominal full-hour endings add a later component.',
'- Friday has substantially fewer collected scheduled meetings than Tuesday, but actual student totals and route loads cannot be inferred from this ratio. Counts use a common map scale across weekdays so Friday is not independently normalized to look equally busy.',
'- BusCSV includes lecture-only, no-long-slot and core-faculty-only higher-scenario scores. These sensitivities remove different possible artifacts; agreement is evidence about the timing proxy only, not about measured occupancy.',
'', '### Gaps',
'- The heatmap has passed data and script validation; the parent coordinator must still inspect it using html_preview and show it with html_render. No live browser or server was used for verification.',
'', 'Local deliverables: reports/saarland-bus-heatmap.html; saarland-class-time-vectors.csv (965rows); saarland-bus-ranked-departures.csv (800rows); saarland-course-time-embeddings.json (two sparse965dimvectors/course); saarland-canonical-class-meetings.csv; saarland-weekday-bus-options.csv. Reproduce with build_timing_model.py then build_heatmap.py then finalize_analysis.py. Validation details: model_validation.json; all'+str(len(checks))+'checks passed.']
(ROOT/'analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Numerical sensitivity checkpoint, with meaningful exact options rather than invented percentages.
sens=[]
for c in chosen:
    for direction in ['incoming','outgoing']:
        chosen_bus=options(c['weekday'],direction)[0]
        opts=options(c['weekday'],direction)
        row={'weekday':c['day'],'direction':direction,'chosen':show(chosen_bus)}
        for label in ['lecture_only','exclude_long_slots','core_faculties']:
            metric=label+'_timing_high'
            best=min(opts,key=lambda x:(round(x[metric],1),x['campus_minute'],x['route']))
            row[label+'_chosen_score']=chosen_bus[metric];row[label+'_best']=show(best);row[label+'_best_score']=best[metric]
        sens.append(row)
m.write_csv(ROOT/'sensitivity_summary.csv',sens)
print(json.dumps({'validation':checks,'final_patterns':len(rows),'canonical_courses':s['retained_unique_canonical_courses'],'cross_source_duplicates':s['cross_source_duplicate_rows'],'within_source_duplicates':s['within_source_shared_meeting_rows'],'files_ready':True},indent=2))
