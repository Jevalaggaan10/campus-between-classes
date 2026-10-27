from bs4 import BeautifulSoup
from collections import Counter, defaultdict
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import csv
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).parent
RAW=BASE/'broader_raw'
LOG=json.loads((BASE/'broader_fetch_log.json').read_text(encoding='utf-8'))
DAYS={'Montag':1,'Dienstag':2,'Mittwoch':3,'Donnerstag':4,'Freitag':5,'Samstag':6,'Sonntag':7}
TERM_FIRST=date(2026,10,12)
TERM_LAST=date(2027,2,5)
FIELDS=['source_group','course_id','title','event_type','weekday','start_time','end_time','time_convention','location','campus','semester','first_date','last_date','frequency','source_url','evidence_snippet','confidence','notes','include_in_demand','group_id','occurrence_dates','canceled_dates','raw_frequency','raw_date_span','faculty_branches','max_participants','exclusion_reason','meeting_unit_key','simultaneous_room_count']

def clean(x):return re.sub(r'\s+',' ',x or '').strip()
def dates(x):
    out=[]
    for d in re.findall(r'\b\d{2}\.\d{2}\.\d{4}\b',x):
        try: out.append(datetime.strptime(d,'%d.%m.%Y').date())
        except ValueError: pass
    return list(dict.fromkeys(out))
def csvwrite(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

courses={}
rows={}
stats=[]
for entry in LOG:
    branch=entry['branch']
    path=RAW/(branch+'.html')
    if not path.exists():continue
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'lxml')
    current=None
    branch_courses=set()
    branch_rows=0
    for node in soup.find_all(['a','table']):
        if node.name=='a' and node.find_parent('h3') and 'publishSubDir=veranstaltung' in node.get('href',''):
            q=parse_qs(urlparse(node['href']).query)
            cid=(q.get('publishid') or q.get('veranstaltung.veranstid') or [''])[0]
            title=clean(node.get_text(' ',strip=True))
            heading=node.find_parent('h3').parent
            metanode=heading.find_next_sibling('div')
            meta=clean(metanode.get_text(' ',strip=True)) if metanode else ''
            kindmatch=re.search(r'WiSe 2026/27\s+\d+\s+(.*?)(?=\d+ SWS|Fakultät|Fachrichtung|Institut|Teilnehmer|Zugeordnete|$)',meta)
            kind=clean(kindmatch.group(1)) if kindmatch else ''
            capmatch=re.search(r'Teilnehmer.{0,8}:\s*(\d+)\s+maximal',meta)
            cap=capmatch.group(1) if capmatch else ''
            current={'course_id':'lsf_'+cid,'lsf_id':cid,'title':title,'event_type':kind,'source_url':node['href'],'semester':'Winter 2026/27' if 'WiSe 2026/27' in meta else 'unverified','faculty_branches':set([branch]),'metadata':meta,'max_participants':cap,'rows':0}
            if cid in courses:
                courses[cid]['faculty_branches'].add(branch)
                current=courses[cid]
            else:courses[cid]=current
            branch_courses.add(cid)
            continue
        if not current or node.name!='table' or 'Veranstaltungstermine' not in node.get('summary',''):continue
        for tr in node.find_all('tr'):
            cells=[clean(x.get_text(' ',strip=True)) for x in tr.find_all(['th','td'],recursive=False)]
            if not cells or cells[0]=='Tag' or len(cells)!=9:continue
            day,time,turnus,span,canceled,teacher,room,remark,zug=cells
            times=re.findall(r'\b(\d{1,2}:\d{2})\b',time)
            begin,end=times[:2] if len(times)>=2 else ('','')
            if begin:begin=begin.zfill(5)
            if end:end=end.zfill(5)
            weekday=DAYS.get(day,'')
            ds=dates(span or turnus)
            freq='weekly' if 'wöchentl' in turnus else ('fortnightly' if any(s in turnus for s in ['14-t','14t','2-wöch','zweiwöch']) else ('once' if 'Einzel' in turnus else ('block' if 'Block' in turnus else 'unknown')))
            first=ds[0] if ds else TERM_FIRST
            last=ds[-1] if len(ds)>=2 else (first if freq=='once' else TERM_LAST)
            if len(ds)==1 and 'bis' in (span or turnus) and 'von' not in (span or turnus):
                first=TERM_FIRST;last=ds[0]
            context=' '.join([current['title'],current['event_type'],room,remark])
            lower=context.lower()
            physical=bool(re.search(r'\bGeb\.?\s*[A-E][0-9]\s*[0-9]',room) or re.search(r'\b(CISPA|DFKI|MPI-INF|MPI-SWS|Max.Planck)\b',room,re.I))
            if re.search(r'homburg|universitätsklinikum|\buks\b|kirrberg',room,re.I):campus='Homburg'
            elif physical:campus='Saarbruecken'
            elif re.search(r'zoom|moodle|online|virtuell|digital|e-learning',room,re.I):campus='online'
            elif room:campus='unverified_location'
            else:campus='unknown'
            conv='ct' if re.search(r'\bc\.?\s*t\.',context,re.I) else ('st' if re.search(r'\bs\.?\s*t\.',context,re.I) else ('literal' if begin and (not begin.endswith(':00') or not end.endswith(':00')) else 'unknown'))
            reasons=[]
            if current['semester']=='unverified':reasons.append('semester_not_verified')
            if weekday not in range(1,6):reasons.append('no_weekday_or_weekend')
            if not begin or not end:reasons.append('no_start_end_time')
            if begin and end and end<=begin:reasons.append('invalid_or_overnight_time')
            if campus!='Saarbruecken':reasons.append('campus_'+campus)
            if 'online-vorlesung' in current['event_type'].lower() or ('online' in current['title'].lower() and not 'hybrid' in lower):reasons.append('online_course_type')
            if freq not in ('weekly','fortnightly'):reasons.append('not_recurring_weekly')
            if last<TERM_FIRST or first>TERM_LAST:reasons.append('outside_teaching_period')
            if freq in ('weekly','fortnightly') and first==last:reasons.append('single_date_labeled_weekly')
            if re.search(r'\b(klausur|prüfung|pruefung|exam|sprechstunde|konsultation)\b',lower):reasons.append('exam_or_consultation')
            groupmatch=re.search(r'(?:[Üü]bungsgruppe|Gruppe|Group)\s*([A-Za-z0-9]+)',remark+' '+zug)
            group=groupmatch.group(1) if groupmatch else zug
            notes=[]
            if remark:notes.append(remark)
            if not ds:notes.append('Lecture-period bounds used because source gives no dates')
            if conv=='unknown':notes.append('Printed full-hour slot; c.t./s.t. not explicit')
            if freq=='fortnightly':notes.append('Alternating-week anchor requires source-date interpretation')
            row=dict(source_group='LSF',course_id=current['course_id'],title=current['title'],event_type=current['event_type'],weekday=weekday,start_time=begin,end_time=end,time_convention=conv,location=room,campus=campus,semester=current['semester'],first_date=first.isoformat(),last_date=last.isoformat(),frequency=freq,source_url=current['source_url'],evidence_snippet=f'{day} {begin}-{end}; {turnus}; {room}',confidence='medium' if conv=='unknown' else 'high',notes='; '.join(notes),include_in_demand=int(not reasons),group_id=group,occurrence_dates=';'.join(d.isoformat() for d in ds) if freq=='once' else '',canceled_dates=';'.join(d.isoformat() for d in dates(canceled)),raw_frequency=turnus,raw_date_span=span,faculty_branches=branch,max_participants=current['max_participants'],exclusion_reason=';'.join(reasons))
            key=(current['course_id'],weekday,begin,end,room,freq,row['first_date'],row['last_date'],remark,zug,canceled)
            if key in rows:
                old=rows[key];old['faculty_branches']=';'.join(sorted(set(old['faculty_branches'].split(';'))|{branch}))
            else:
                rows[key]=row;current['rows']+=1
            branch_rows+=1
    stats.append({'branch':branch,'unique_courses_in_branch':len(branch_courses),'raw_listing_schedule_rows':branch_rows,'download_bytes':entry.get('bytes',0),'url':entry['url']})
    print(json.dumps(stats[-1],ensure_ascii=False),flush=True)

out=list(rows.values())
out.sort(key=lambda r:(r['course_id'],str(r['weekday']),r['start_time'],r['location']))
units=defaultdict(list)
for row in out:
    key='|'.join(str(row[k]) for k in ['course_id','weekday','start_time','end_time','frequency','first_date','last_date','group_id','canceled_dates'])
    row['meeting_unit_key']=key
    row['simultaneous_room_count']=1
    if row['include_in_demand'] and not row['group_id']:
        units[key].append(row)
    if row['start_time'] and row['end_time']:
        duration=(int(row['end_time'][:2])*60+int(row['end_time'][3:]))-(int(row['start_time'][:2])*60+int(row['start_time'][3:]))
        if duration>=240:row['notes']+='; Long source booking block (at least 4 hours); actual teaching boundaries unverified'
collapsed=0
for key,rr in units.items():
    rooms=sorted({r['location'] for r in rr})
    if len(rr)<2:continue
    for r in rr:
        r['simultaneous_room_count']=len(rooms)
        r['notes']+='; Simultaneous source patterns without verified distinct groups: counted once per course boundary; rooms: '+' / '.join(rooms)
        r['confidence']='medium'
    for r in rr[1:]:
        r['include_in_demand']=0
        r['exclusion_reason']=(r['exclusion_reason']+';' if r['exclusion_reason'] else '')+'simultaneous_rooms_same_course_unverified_groups'
        collapsed+=1
csvwrite(BASE/'broader_meetings.csv',out,FIELDS)
inventory=[]
for cid,c in sorted(courses.items()):
    rr=[r for r in out if r['course_id']==c['course_id']]
    inventory.append(dict(course_id=c['course_id'],lsf_id=cid,title=c['title'],event_type=c['event_type'],semester=c['semester'],faculty_branches=';'.join(sorted(c['faculty_branches'])),schedule_rows=len(rr),included_recurring_rows=sum(r['include_in_demand'] for r in rr),status='recurring_timed_campus' if any(r['include_in_demand'] for r in rr) else ('no_schedule_rows' if not rr else 'excluded_or_unknown'),max_participants=c['max_participants'],source_url=c['source_url'],metadata=c['metadata']))
csvwrite(BASE/'broader_source_inventory.csv',inventory,list(inventory[0]) if inventory else ['course_id'])
csvwrite(BASE/'broader_dated_events.csv',[r for r in out if r['frequency'] in ('once','block')],FIELDS)
summary={'semester':'Winter 2026/27','fetch_date':'2026-10-26','branches_requested':len(LOG),'branches_downloaded':sum('error' not in r for r in LOG),'branches':stats,'unique_courses':len(courses),'deduplicated_schedule_rows':len(out),'included_recurring_meetings':sum(r['include_in_demand'] for r in out),'courses_with_included_recurring_meetings':len({r['course_id'] for r in out if r['include_in_demand']}),'simultaneous_unverified_room_patterns_collapsed':collapsed,'raw_frequency_counts':dict(Counter(r['frequency'] for r in out)),'campus_counts':dict(Counter(r['campus'] for r in out)),'exclusion_reason_counts':dict(Counter(e for r in out for e in r['exclusion_reason'].split(';') if e)),'included_by_weekday':dict(Counter(r['weekday'] for r in out if r['include_in_demand'])),'included_by_start_time':dict(Counter(r['start_time'] for r in out if r['include_in_demand'])),'included_by_end_time':dict(Counter(r['end_time'] for r in out if r['include_in_demand']))}
(BASE/'broader_coverage_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='branches'},ensure_ascii=False,indent=2))
