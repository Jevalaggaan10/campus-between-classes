"""Reproducible public-timetable pressure model; no observed occupancy is inferred."""
from __future__ import annotations
import csv, json, re, math, collections, unicodedata, difflib, pathlib
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parent
OUT = (__import__('pathlib').Path(__file__).resolve().parents[2] / 'reports')
OUT.mkdir(exist_ok=True)
START, END = date(2026, 10, 26), date(2027, 2, 5)
BREAK_START, BREAK_END = date(2026, 12, 21), date(2027, 1, 1)
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
MINUTE_BINS = list(range(360, 1321, 5))
CALENDAR = [START + timedelta(days=i) for i in range((END-START).days+1)]
CALENDAR = [d for d in CALENDAR if d.weekday()<5 and not BREAK_START<=d<=BREAK_END]
BY_DAY = {i: [d for d in CALENDAR if d.isoweekday()==i] for i in range(1,6)}
EXCLUDED = []
DEDUP = []

def read_csv(name):
    path = ROOT/name
    return list(csv.DictReader(path.open(encoding='utf-8-sig', newline=''))) if path.exists() else []

def write_csv(path, rows, fields=None):
    if not fields:
        fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def norm(value):
    value=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode().lower()
    value=re.sub(r'\b(?:winter|sommer|summer|ws|wise|term|semester)\s*(?:20)?\d{2}(?:\s*/\s*(?:20)?\d{2})?',' ',value)
    value=re.sub(r'\([^)]*(?:2026|2027)[^)]*\)',' ',value)
    value=re.sub(r'[^a-z0-9]+',' ',value)
    value=re.sub(r'\biii\b','3',value);value=re.sub(r'\bii\b','2',value);value=re.sub(r'\bi\b','1',value)
    return ' '.join(value.split())

def title_norm(value):
    value=norm(value)
    value=re.sub(r'^(?:vorlesung|ubung|tutorial|exercise|lecture|proseminar|seminar)\s+(?:zu\s+)?','',value)
    value=re.sub(r'\b(?:vorlesung|ubungen?|tutorials?)$','',value).strip()
    return value

def minutes(t):
    m=re.search(r'(\d{1,2}):(\d{2})',str(t))
    return 60*int(m[1])+int(m[2]) if m else None

def clock(t):
    return f'{int(t)//60:02d}:{int(t)%60:02d}'

def parse_date(s, default=None):
    if not s:return default
    m=re.search(r'20\d\d-\d\d-\d\d',str(s))
    if m:
        try:return date.fromisoformat(m[0])
        except ValueError:return default
    return default

def parse_dates(s):
    return sorted({date.fromisoformat(x) for x in re.findall(r'20\d\d-\d\d-\d\d',str(s))})

def event_kind(r):
    t=norm(r.get('event_type',''))
    if any(x in t for x in ['office','consult','sprech','klausur','exam','deadline','prufung','kickoff','einfuhrungsveranstaltung']):return 'excluded'
    if any(x in t for x in ['lecture','vorlesung','v ', ' v']):return 'lecture'
    if any(x in t for x in ['tutorial','exercise','ubung','repetitorium']):return 'tutorial'
    if any(x in t for x in ['seminar','kolloquium']):return 'seminar'
    if any(x in t for x in ['praktikum','lab','labor']):return 'lab'
    return t or 'class'

def dates_and_weight(r):
    weekday=int(r['weekday'])
    explicit=parse_dates(r.get('scheduled_dates','') or r.get('occurrence_dates','') or r.get('dates',''))
    first=parse_date(r.get('first_date'),START); last=parse_date(r.get('last_date'),END)
    avail=[d for d in BY_DAY[weekday] if first<=d<=last]
    if explicit:
        dates=[d for d in explicit if d in BY_DAY[weekday] and first<=d<=last]
        return dates, len(dates)/len(BY_DAY[weekday]), 'explicit dates'
    freq=norm(r.get('frequency',''))
    if any(x in freq for x in ['irregular','unregel','listed','einzel','block','einmal','one off']):
        return [],0.0,'irregular/block with no usable explicit dates'
    if 'fortnight' in freq or 'biweek' in freq or '14' in freq or 'zweiwoch' in freq or '2 woch' in freq:
        if 'first23oct' in freq or ('fortnight' in freq and r.get('first_date')=='2026-10-23'):
            anchor=date(2026,10,23); dates=[d for d in avail if (d-anchor).days%14==0]
            return dates,len(dates)/len(BY_DAY[weekday]),'known fortnightly phase'
        return [],len(avail)/len(BY_DAY[weekday])*0.5,'fortnightly expected frequency; phase unknown'
    dates=avail
    cid=r.get('course_id','')
    if cid=='lfa': dates=[d for d in dates if not date(2026,11,9)<=d<=date(2026,11,15) and not date(2026,12,21)<=d<=date(2027,1,3)]
    if cid=='cysec1_2627': dates=[d for d in dates if d not in {date(2026,10,22),date(2026,11,17)}]
    if cid=='theory_2627': dates=[d for d in dates if d!=date(2026,10,23)]
    if cid=='spacesecurity2627': dates=[d for d in dates if d!=date(2026,10,30)]
    cancelled=set(parse_dates(r.get('canceled_dates','') or r.get('cancelled_dates','')))
    dates=[d for d in dates if d not in cancelled]
    return dates,len(dates)/len(BY_DAY[weekday]),'weekly within published date range'

def timing_variants(r):
    start,end=minutes(r['start_time']),minutes(r['end_time'])
    convention=r.get('time_convention','unknown').lower()
    nominal=(start,end)
    alt=nominal
    if convention in {'ct','c.t.','c.t','cum tempore'}:
        start2=start+(30 if r.get('course_id')=='hmi32627' and start==480 else 15) if start%60==0 else start
        nominal=(start2,end)
        alt=(start2,end-15) if end%60==0 and end-start>=90 else nominal
    elif convention in {'unknown','','nominal','unspecified'} and start%60==0 and end%60==0 and end-start>=90:
        alt=(start+15,end-15)
    if r.get('course_id')=='emlw26' and event_kind(r)=='lecture': alt=(start,17*60+35)
    return nominal,alt

def same_room(a,b):
    a,b=norm(a),norm(b)
    for w in ['gebaude','gebaudes','building','raum','room','saarbrucken','campus','geb']:
        a=re.sub(r'\b'+w+r'\b','',a);b=re.sub(r'\b'+w+r'\b','',b)
    a=''.join(a.split());b=''.join(b.split())
    return not a or not b or a in b or b in a or difflib.SequenceMatcher(None,a,b).ratio()>.86

# Explicit multilingual title equivalences, not inferred participant equivalences.
TITLE_ALIASES = {
 'einfuh rung in die theoretische informatik':'introduction to theoretical computer science',
 'einfuhrung in die theoretische informatik':'introduction to theoretical computer science',
 'theoretische informatik':'introduction to theoretical computer science',
 'programmierung 1':'programming 1',
 'algorithmen und datenstrukturen':'introduction to algorithms and data structures',
 'datenbanksysteme':'database systems',
 'computergraphik':'computer graphics',
 'grundlagen der kunstlichen intelligenz':'artificial intelligence',
 'kunstliche intelligenz':'artificial intelligence',
 'mathematik fur informatiker 1':'mathematics for computer scientists 1',
 'mathematik fur informatiker 3':'mathematics for computer scientists 3',
 'mathmatik fur informatiker 1':'mathematics for computer scientists 1',
 'mathematics for computer scientists i':'mathematics for computer scientists 1',
 'mathematics for computer scientists iii':'mathematics for computer scientists 3',
 'foundations of cybersecurity i':'foundations of cybersecurity 1',
 'foundations of cyber security 1 grundlagen der cybersicherheit 1':'foundations of cybersecurity 1',
 'grundzuge der theoretischen informatik':'introduction to theoretical computer science',
 'grundzuge von algorithmen und datenstrukturen':'introduction to algorithms and data structures',
 'mathematik fur informatiker 3 mathematics for computer scientists 3':'mathematics for computer scientists 3',
 'mathematik fur studierende der biologie und des lehramtes chemie':'mathematik fur biologen und chemiker lehramt',
 'audio visual communication and networks telecommunications 2':'audio visual communication networks',
 'spezialvorlesung der bioinformatik algorithms for sequence analysis':'algorithms for sequence analysis',
 'pro seminar integralgleichungen':'integralgleichungen',
 'artificially empathic technology':'artificial empathic technology',
 'seminar zur stochastik':'stochastik',
}

def canonical_title(t):
    t=title_norm(t)
    return TITLE_ALIASES.get(t,t)

def load_merge():
    sources=[('cms_meetings.csv','CMS'),('cispa_meetings.csv','CISPA/seminars'),('broader_meetings.csv','LSF')]
    all_rows=[]; source_counts={}
    for fn,source in sources:
        rows=read_csv(fn);source_counts[source]={'input_rows':len(rows),'input_courses':len({r.get('course_id') for r in rows})}
        for i,raw in enumerate(rows):
            r={**raw,'input_file':fn,'input_row':i+2,'collection':source}
            if r.get('course_id')=='lsf_167487':
                r['source_start_time'],r['source_end_time']=r['start_time'],r['end_time']
                r['start_time'],r['end_time'],r['time_convention']='16:15','19:45','exact'
                r['notes']+='; Model uses explicit teaching hours in title/remark over nominal 16-20 room envelope.'
            reason=''
            if r.get('include_in_demand','1') in {'0','False','false','no'}:reason='source marks excluded'
            elif event_kind(r)=='excluded':reason='consultation, exam, deadline or kickoff'
            elif not str(r.get('weekday','')).isdigit() or not 1<=int(r['weekday'])<=5:reason='not a valid weekday'
            elif minutes(r.get('start_time')) is None or minutes(r.get('end_time')) is None:reason='incomplete interval'
            elif minutes(r['end_time'])<=minutes(r['start_time']):reason='non-positive duration'
            elif re.search(r'homburg|hamburg|online only|remote only',norm(r.get('campus',''))):reason='off-campus or online-only'
            elif r.get('attendance_mode')=='unknown':reason='physical attendance/location unconfirmed'
            elif r.get('course_id')=='orgsec26':reason='irregular dates unpublished'
            elif r.get('course_id')=='tml26':reason='moving/online weekly dates unresolved'
            elif source=='LSF' and 'umzugsvorbereitung' in norm(r.get('title','')):reason='non-teaching move-preparation room booking'
            elif source=='LSF' and 'team besprechung' in norm(r.get('notes','')):reason='internal staff team meeting, not a class'
            elif source=='LSF' and 'online' in norm(r.get('event_type','')):reason='explicit online course type despite nominal room reservation'
            elif source=='LSF' and canonical_title(r.get('title',''))=='empirical software engineering research':reason='CMS course source overrides LSF: online uploads and Zoom Q&A'
            elif source=='LSF' and canonical_title(r.get('title',''))=='differential equations in image processing and computer vision' and event_kind(r)=='lecture':reason='CMS course source overrides LSF: online lecture'
            if reason:EXCLUDED.append({**r,'exclusion_reason':reason});continue
            r['weekday']=int(r['weekday']);r['kind']=event_kind(r)
            r['canonical_title']=canonical_title(r.get('title',''))
            dates,weight,date_rule=dates_and_weight(r)
            r['model_dates']=';'.join(d.isoformat() for d in dates)
            r['frequency_weight']=round(weight,6);r['date_rule']=date_rule
            if not weight:EXCLUDED.append({**r,'exclusion_reason':'no eligible remaining teaching occurrences: '+date_rule});continue
            r['start_minute'],r['end_minute']=minutes(r['start_time']),minutes(r['end_time'])
            (r['start_nominal'],r['end_nominal']),(r['start_quarter'],r['end_quarter'])=timing_variants(r)
            all_rows.append(r)
    # Authoritative CMS/CISPA rows have priority over nominal LSF room slots.
    kept=[];course_ids={};course_titles={};crosswalk=[]
    for r in all_rows:
        key=(r['collection'],r.get('course_id',''))
        title=r['canonical_title']
        if key in course_ids:cid=course_ids[key]
        elif r['collection']=='LSF' and r.get('course_id')=='lsf_167417':cid='lsf_167414'
        elif title in course_titles and r['collection'] not in course_titles[title][1]:cid=course_titles[title][0]
        else:
            cid=r.get('course_id') or ('course_'+str(len(course_ids)))
            if any(cid==v for k,v in course_ids.items() if k!=key):cid=r['collection'].lower().replace('/','_')+'_'+cid
        course_ids[key]=cid
        if title not in course_titles:course_titles[title]=[cid,{r['collection']}]
        elif course_titles[title][0]==cid:course_titles[title][1].add(r['collection'])
        r['canonical_course_id']=cid
        crosswalk.append({'collection':r['collection'],'course_id':r.get('course_id'),'title':r.get('title'),'canonical_course_id':cid,'canonical_title':title})
        duplicate=None
        for k in kept:
            if k['canonical_course_id']!=cid or k['weekday']!=r['weekday']:continue
            # Combined sessions can include either corresponding LSF component.
            kinds_compatible=k['kind']==r['kind'] or ('combined' in k.get('event_type','') and r['kind'] in {'lecture','tutorial'})
            mixed_lsf=r['collection']=='LSF' and 'vorlesung' in norm(r.get('event_type','')) and 'ubung' in norm(r.get('event_type',''))
            if mixed_lsf and k['kind'] in {'lecture','tutorial'}:kinds_compatible=True
            if not kinds_compatible:continue
            if r['collection']==k['collection']:
                exact=(r['start_minute'],r['end_minute'],norm(r.get('location','')),r.get('group_id',''))==(k['start_minute'],k['end_minute'],norm(k.get('location','')),k.get('group_id',''))
                if exact and r['model_dates']==k['model_dates']:duplicate=k;break
                continue
            if abs(k['start_minute']-r['start_minute'])>30 or abs(k['end_minute']-r['end_minute'])>30:continue
            if r['kind'] in {'tutorial','lab'} and not same_room(k.get('location',''),r.get('location','')):continue
            # Distinct explicit tutorial group ids remain separate.
            if k.get('group_id') and r.get('group_id') and k['group_id']!=r['group_id'] and r['kind']=='tutorial':continue
            duplicate=k;break
        if duplicate:
            DEDUP.append({**r,'kept_input_file':duplicate['input_file'],'kept_input_row':duplicate['input_row'],'dedup_reason':'same canonical course/day/meeting type and overlapping nominal/exact slot'})
            duplicate['additional_sources']=';'.join(dict.fromkeys((duplicate.get('additional_sources','')+';'+r.get('source_url','')).strip(';').split(';')))
        else:kept.append(r)
    # Multiple unlabelled LSF room reservations are not verified independent
    # groups. Count one course/time slot, retaining labelled groups separately.
    collapsed=[];slots={}
    for r in kept:
        key=(r['canonical_course_id'],r['kind'],r['weekday'],r['start_minute'],r['end_minute'])
        if r['collection']!='LSF' or r.get('group_id'):
            collapsed.append(r);continue
        if key not in slots:
            slots[key]=r;collapsed.append(r);continue
        prev=slots[key]
        DEDUP.append({**r,'kept_input_file':prev['input_file'],'kept_input_row':prev['input_row'],'dedup_reason':'unlabelled same-course simultaneous room reservations consolidated; distinct groups unverified'})
        dates=sorted(set(parse_dates(prev['model_dates']))|set(parse_dates(r['model_dates'])))
        prev['model_dates']=';'.join(d.isoformat() for d in dates)
        prev['frequency_weight']=max(prev['frequency_weight'],r['frequency_weight'],len(dates)/len(BY_DAY[r['weekday']]))
        prev['consolidated_locations']=' | '.join(dict.fromkeys((prev.get('consolidated_locations',prev.get('location',''))+' | '+r.get('location','')).split(' | ')))
        prev['consolidated_room_rows']=int(prev.get('consolidated_room_rows',1))+1
    write_csv(ROOT/'course_crosswalk.csv',list({tuple(r.values()):r for r in crosswalk}.values()))
    return collapsed,source_counts

def triangle(x,left,peak,right):
    if x<=left or x>=right:return 0.0
    return (x-left)/(peak-left) if x<=peak else (right-x)/(right-peak)

def row_pressure(r,t,direction,scenario):
    start,end=(r['start_nominal'],r['end_nominal']) if scenario=='nominal' else (r['start_quarter'],r['end_quarter'])
    # Guard tails avoid the false conclusion that a bus arriving two minutes
    # before class is empty. They cover late arrivals, early finishes and queues.
    return r['frequency_weight']*(triangle(start-t,-10,10,35) if direction=='incoming' else triangle(t-end,-5,10,40))

def score(rows,day,t,direction,scenario):
    return sum(row_pressure(r,t,direction,scenario) for r in rows if r['weekday']==day)

def build_vectors(rows):
    vectors=[]
    for day in range(1,6):
        dr=[r for r in rows if r['weekday']==day]
        for t in MINUTE_BINS:
            v={'weekday':day,'weekday_name':DAYS[day-1],'time':clock(t),'minute':t}
            for direction in ['incoming','outgoing']:
                a=score(dr,day,t,direction,'nominal');b=score(dr,day,t,direction,'quarter')
                v[direction+'_nominal']=round(a,6);v[direction+'_quarter']=round(b,6)
                v[direction+'_score']=round((a+b)/2,6);v[direction+'_timing_low']=round(min(a,b),6);v[direction+'_timing_high']=round(max(a,b),6)
                lectures=[r for r in dr if r['kind']=='lecture']
                v[direction+'_lecture_only']=round((score(lectures,day,t,direction,'nominal')+score(lectures,day,t,direction,'quarter'))/2,6)
            v['starts_count']=round(sum(r['frequency_weight'] for r in dr if t<=r['start_minute']<t+5),6)
            v['ends_count']=round(sum(r['frequency_weight'] for r in dr if t<=r['end_minute']<t+5),6)
            vectors.append(v)
    return vectors

def build_rankings(rows):
    bus=read_csv('bus_trips.csv');candidates=[]
    sensitivity_sets={
        'lecture_only':[r for r in rows if r['kind']=='lecture'],
        'exclude_long_slots':[r for r in rows if r['end_minute']-r['start_minute']<240],
        'core_faculties':[r for r in rows if r['collection']!='LSF' or set(re.split(r'[;,| ]+',r.get('faculty_branches','')))&{'HW','MI','NT','P','R'}],
    }
    for day in range(1,6):
        for b in bus:
            if b['home_stop']!='HTW / SWS':continue
            if 'Friday' in b.get('weekdays','') and b['weekdays']!='Monday-Friday' and day!=5:continue
            direction='incoming' if b['direction']=='to_university' else 'outgoing'
            t=minutes(b['campus_time'])
            if t is None or not 360<=t<=1320:continue
            a=score(rows,day,t,direction,'nominal');q=score(rows,day,t,direction,'quarter')
            c={**b,'weekday':day,'weekday_name':DAYS[day-1],'model_direction':direction,'central_score':round((a+q)/2,3),'nominal_score':round(a,3),'quarter_score':round(q,3),'timing_low':round(min(a,q),3),'timing_high':round(max(a,q),3),'robust_sort_key':round(max(a,q),1)}
            c['daytime_option']=int((direction=='incoming' and 480<=t<=660) or (direction=='outgoing' and 900<=t<=1170))
            c['campus_minute']=t
            for label,subset in sensitivity_sets.items():
                c[label+'_timing_high']=round(max(score(subset,day,t,direction,'nominal'),score(subset,day,t,direction,'quarter')),3)
            candidates.append(c)
    candidates.sort(key=lambda c:(c['weekday'],c['model_direction'],c['robust_sort_key'],c['campus_minute'],c['route']))
    for day in range(1,6):
        for direction in ['incoming','outgoing']:
            sub=[c for c in candidates if c['weekday']==day and c['model_direction']==direction]
            levels=sorted({c['robust_sort_key'] for c in sub})
            dlevels=sorted({c['robust_sort_key'] for c in sub if c['daytime_option']})
            for c in sub:
                c['full_day_tied_rank']=levels.index(c['robust_sort_key'])+1
                c['daytime_tied_rank']=dlevels.index(c['robust_sort_key'])+1 if c['daytime_option'] else ''
    return candidates

def summarize(rows,source_counts,vectors,candidates):
    by_collection={s:{'retained_patterns':sum(r['collection']==s for r in rows),'retained_canonical_courses':len({r['canonical_course_id'] for r in rows if r['collection']==s})} for s in source_counts}
    peak={}
    for day in range(1,6):
        peak[DAYS[day-1]]={}
        for direction in ['incoming','outgoing']:
            dr=[v for v in vectors if v['weekday']==day]
            peak[DAYS[day-1]][direction]=[{k:v[k] for k in ['time',direction+'_score',direction+'_timing_low',direction+'_timing_high']} for v in sorted(dr,key=lambda v:-v[direction+'_score'])[:4]]
    all_htw=[c for c in read_csv('bus_trips.csv') if c.get('home_stop')=='HTW / SWS']
    cross_source=sum(r['input_file']!=r.get('kept_input_file') for r in DEDUP)
    summary={'profile_start':START.isoformat(),'profile_end':END.isoformat(),'teaching_days':len(CALENDAR),'teaching_weeks':len(BY_DAY[1]),'catalog_source_counts':source_counts,'retained_by_collection':by_collection,'retained_meeting_patterns':len(rows),'retained_unique_canonical_courses':len({r['canonical_course_id'] for r in rows}),'excluded_rows':len(EXCLUDED),'merged_duplicate_rows':len(DEDUP),'cross_source_duplicate_rows':cross_source,'within_source_shared_meeting_rows':len(DEDUP)-cross_source,'dedup_breakdown':dict(collections.Counter(r['input_file']+' -> '+r.get('kept_input_file','') for r in DEDUP)),'unknown_time_patterns':sum(r.get('time_convention','unknown') in {'unknown',''} for r in rows),'timing_vectors':len(vectors),'vector_bin_minutes':5,'time_span':'06:00–22:00','htw_timetable_options':len({c['trip_id'] for c in all_htw}),'htw_options_in_06_to_22_model_range':len({c['trip_id'] for c in candidates}),'weekday_expanded_ranked_options':len(candidates),'peaks':peak}
    (ROOT/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    return summary

def main():
    rows,source_counts=load_merge()
    vectors=build_vectors(rows);candidates=build_rankings(rows)
    summary=summarize(rows,source_counts,vectors,candidates)
    write_csv(ROOT/'canonical_meetings.csv',rows)
    write_csv(ROOT/'model_exclusions.csv',EXCLUDED)
    write_csv(ROOT/'model_duplicate_rows.csv',DEDUP)
    write_csv(OUT/'saarland-class-time-vectors.csv',vectors)
    write_csv(OUT/'saarland-bus-ranked-departures.csv',candidates)
    write_csv(OUT/'saarland-canonical-class-meetings.csv',rows)
    (ROOT/'model_data.json').write_text(json.dumps({'summary':summary,'vectors':vectors,'meetings':rows,'ranked_bus_options':candidates},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    sparse={}
    for r in rows:
        cid=r['canonical_course_id']
        entry=sparse.setdefault(cid,{'title':r['title'],'start':{},'end':{}})
        for channel,minute in [('start',r['start_minute']),('end',r['end_minute'])]:
            if 360<=minute<=1320:
                index=(r['weekday']-1)*len(MINUTE_BINS)+(minute-360)//5
                entry[channel][index]=round(entry[channel].get(index,0)+r['frequency_weight'],6)
    (OUT/'saarland-course-time-embeddings.json').write_text(json.dumps({'representation':'two sparse 965-dimensional weekday/5-minute vectors per course: nominal advertised starts and ends; not semantic embeddings','weekdays':DAYS,'time_start':'06:00','time_end':'22:00','minutes_per_bin':5,'bins_per_day':len(MINUTE_BINS),'courses':sparse},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))
    for day in range(1,6):
        print(DAYS[day-1])
        for direction in ['incoming','outgoing']:
            opts=[c for c in candidates if c['weekday']==day and c['model_direction']==direction and c['daytime_option']]
            print(direction,[(c['route'],c['home_time'],c['campus_time'],c['central_score'],c['timing_low'],c['timing_high'],c['terminal_time']) for c in opts[:8]])

if __name__=='__main__':main()
