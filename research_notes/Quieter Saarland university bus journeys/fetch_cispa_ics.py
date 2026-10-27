from pathlib import Path
import json,requests,concurrent.futures,datetime,csv,re,sys
from zoneinfo import ZoneInfo
sys.stdout.reconfigure(encoding='utf-8')
b=Path(__file__).resolve().parent;raw=b/'cispa_ics';raw.mkdir(exist_ok=True)
inventory=json.loads((b/'cispa_inventory.json').read_text(encoding='utf-8'))
courses=[x for x in inventory if x['group']=='cispa_catalog']
def fetch(x):
 u=x['url'].rstrip('/')+'/termine/events/download';root=x['url'].rstrip('/').split('/')[-1]
 try:
  r=requests.get(u,timeout=30);r.raise_for_status();h=r.content.decode('utf-8-sig');(raw/(root+'.ics')).write_text(h,encoding='utf-8')
  return x,h,u,''
 except Exception as e:return x,'',u,str(e)
rows=[];summ=[]
for x,h,u,err in concurrent.futures.ThreadPoolExecutor(6).map(fetch,courses):
 h=re.sub(r'\r?\n[ \t]','',h.replace('\r\r\n','\n'));events=re.findall(r'BEGIN:VEVENT(.*?)END:VEVENT',h,re.S)
 summ.append({'title':x['title'],'course_url':x['url'],'calendar_url':u,'event_count':len(events),'error':err})
 for event in events:
  props={}
  for line in event.splitlines():
   if ':' in line:
    key,value=line.split(':',1);props[key.split(';')[0]]=value
  if not props.get('DTSTART') or not props.get('DTEND'):continue
  def dt(v):
   if v.endswith('Z'):return datetime.datetime.strptime(v,'%Y%m%dT%H%M%SZ').replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo('Europe/Berlin'))
   return datetime.datetime.strptime(v,'%Y%m%dT%H%M%S').replace(tzinfo=ZoneInfo('Europe/Berlin'))
  try:start,end=dt(props['DTSTART']),dt(props['DTEND'])
  except ValueError:continue
  unesc=lambda v:v.replace('\\n',' ').replace('\\,',',').replace('\\;',';').replace('\\\\','\\')
  rows.append({'source_group':'cispa_ics','course_id':x['url'].rstrip('/').split('/')[-1],'title':x['title'],'event_title':unesc(props.get('SUMMARY','')),'date':start.date().isoformat(),'weekday':start.isoweekday(),'start_time':start.strftime('%H:%M'),'end_time':end.strftime('%H:%M'),'location':unesc(props.get('LOCATION','')),'description':unesc(props.get('DESCRIPTION','')),'start_iso':start.isoformat(),'end_iso':end.isoformat(),'source_url':x['url'],'calendar_url':u,'uid':props.get('UID','')})
with (b/'cispa_calendar_occurrences.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['source_group','course_id','date']);w.writeheader();w.writerows(rows)
(b/'cispa_calendar_coverage.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8')
print('Calendars',len(summ),'nonempty',sum(bool(x['event_count']) for x in summ),'occurrences',len(rows),'errors',sum(bool(x['error']) for x in summ))
for x in summ:print(x)
print('NORMAL WEEK 2-6 NOV 2026')
for r in rows:
 if '2026-11-02'<=r['date']<='2026-11-06':print(r['course_id'],r['event_title'],r['date'],r['start_time'],r['end_time'],r['location'])
