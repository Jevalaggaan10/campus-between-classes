from pathlib import Path
import json,re,datetime as dt,collections,csv,sys
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).parent; Z=ZoneInfo('Europe/Berlin')
items=json.loads((P/'cms_inventory.json').read_text(encoding='utf-8'))
def parse_date(k,v):
    if len(v)==8:return dt.datetime.strptime(v,'%Y%m%d').replace(tzinfo=Z)
    if v.endswith('Z'):return dt.datetime.strptime(v,'%Y%m%dT%H%M%SZ').replace(tzinfo=dt.timezone.utc).astimezone(Z)
    return dt.datetime.strptime(v,'%Y%m%dT%H%M%S').replace(tzinfo=Z)
events=[]
for x in items:
    h=(P/'cms_raw'/(x['id']+'.ics')).read_text(encoding='utf-8')
    h=re.sub(r'\n[ \t]','',h)
    for body in h.split('BEGIN:VEVENT')[1:]:
        body=body.split('END:VEVENT')[0]; d={}
        for l in body.splitlines():
            if ':' not in l:continue
            k,v=l.split(':',1);d[k.split(';')[0]]=v.replace('\\n','\n').replace('\\,',',').replace('\\;',';')
        if 'DTSTART' not in d or 'DTEND' not in d:continue
        st=parse_date('DTSTART',d['DTSTART']);en=parse_date('DTEND',d['DTEND'])
        e=dict(course_id=x['id'],title=x['title'],summary=d.get('SUMMARY',''),start=st.isoformat(),end=en.isoformat(),weekday=st.isoweekday(),date=str(st.date()),start_time=st.strftime('%H:%M'),end_time=en.strftime('%H:%M'),duration_minutes=(en-st).total_seconds()/60,location=d.get('LOCATION',''),description=d.get('DESCRIPTION',''),status=d.get('STATUS',''),source_url=x['url']+'termine/events/download',uid=d.get('UID',''))
        events.append(e)
(P/'cms_occurrences.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'cms_occurrences.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(events[0]));w.writeheader();w.writerows(events)
out=[]
for x in items:
    ee=[e for e in events if e['course_id']==x['id'] and '2026-10-12'<=e['date']<='2027-02-05']
    groups=collections.defaultdict(list)
    for e in ee:
        if 15<=e['duration_minutes']<=300 and e['weekday']<=5:
            groups[(e['weekday'],e['start_time'],e['end_time'],e['summary'],e['location'])].append(e['date'])
    out.append('\n### '+x['id']+' '+x['title']+' '+str(len(ee))+' raw dates')
    for k,dates in groups.items():out.append(str(k)+' N='+str(len(dates))+' first='+min(dates)+' last='+max(dates))
(P/'cms_calendar_patterns.txt').write_text('\n'.join(out),encoding='utf-8')
print('\n'.join(out))
