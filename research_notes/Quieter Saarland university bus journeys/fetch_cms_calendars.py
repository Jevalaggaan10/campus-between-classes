from pathlib import Path
import json, requests, concurrent.futures, re, sys, urllib.parse, bs4
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).parent; R=P/'cms_raw'
items=json.loads((P/'cms_inventory.json').read_text(encoding='utf-8'))
def one(x):
    u=x['url']+'termine/events/download'
    try:
        r=requests.get(u,timeout=40);r.raise_for_status();r.encoding='utf-8';h=r.text
        (R/(x['id']+'.ics')).write_text(h,encoding='utf-8')
        x['calendar_events']=h.count('BEGIN:VEVENT')
        x['calendar_status']='ics' if h.startswith('BEGIN:VCALENDAR') else 'no_ics'
        if x['calendar_events']:
            print(x['id'],x['calendar_events'],flush=True)
    except Exception as e: x['calendar_status']='error';x['calendar_error']=str(e)
    return x
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:items=list(pool.map(one,items))
(P/'cms_inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print('CALENDARS',len(items),'ICS',sum(x['calendar_status']=='ics' for x in items),'NONEMPTY',sum(x.get('calendar_events',0)>0 for x in items))
