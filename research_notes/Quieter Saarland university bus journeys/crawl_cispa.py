from pathlib import Path
import requests, bs4, re, json, hashlib, concurrent.futures, urllib.parse, time
BASE=Path(__file__).resolve().parent
RAW=BASE/'cispa_raw'; RAW.mkdir(exist_ok=True)
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (public academic timetable research)'
def get(u):
 try:
  r=S.get(u,timeout=35); r.raise_for_status(); s=bs4.BeautifulSoup(r.text,'html.parser')
  key=hashlib.sha256(u.encode()).hexdigest()[:16]
  (RAW/(key+'.html')).write_text(r.text,encoding='utf-8')
  for el in s(['script','style','nav','header','footer']): el.decompose()
  text=s.get_text('\n',strip=True)
  (RAW/(key+'.txt')).write_text(text,encoding='utf-8')
  return {'url':u,'final_url':r.url,'key':key,'title':s.title.get_text(' ',strip=True) if s.title else '', 'text':text, 'html':r.text,'error':''}
 except Exception as e:return {'url':u,'error':str(e)}
urls=['https://cms.cispa.saarland/system/courses','https://seminars.cs.uni-saarland.de/wise2627seminars','https://seminars.cs.uni-saarland.de/wise2627proseminars']
pages=list(concurrent.futures.ThreadPoolExecutor(3).map(get,urls)); inventory=[]
s=bs4.BeautifulSoup(pages[0]['html'],'html.parser')
sec=next(x.parent for x in s.find_all('h3') if 'Winter term 2026/2027' in x.get_text())
for row in sec.select('tr'):
 a=row.select_one('h6 a')
 if a: inventory.append({'group':'cispa_catalog','title':a.get_text(' ',strip=True),'url':urllib.parse.urljoin(urls[0],a['href']),'description':row.get_text(' ',strip=True)})
for p in pages[1:]:
 s=bs4.BeautifulSoup(p['html'],'html.parser')
 for h in s.find_all('h3'):
  chunks=[];links=[]
  for sib in h.next_siblings:
   if getattr(sib,'name',None)=='h3':break
   if isinstance(sib,str):chunks.append(sib)
   else:
    chunks.append(sib.get_text(' ',strip=True))
    links.extend(urllib.parse.urljoin(p['url'],a['href']) for a in sib.find_all('a',href=True))
  txt=' '.join(chunks); cap=re.search(r'Places:\s*(\d+)',txt)
  inventory.append({'group':'seminars' if 'proseminars' not in p['url'] else 'proseminars','title':h.get_text(' ',strip=True),'url':p['url'],'links':list(dict.fromkeys(links)),'description':txt,'capacity':int(cap[1]) if cap else None})
targets=set(x['url'] for x in inventory if x['group']=='cispa_catalog')
for x in inventory:targets.update(u for u in x.get('links',[]) if any(z in u for z in ['cms.','mpi-','mpi.','uni-saarland','dfki.de','cispa','saarland']))
pages.extend(concurrent.futures.ThreadPoolExecutor(6).map(get,sorted(targets)))
# On CISPA courses inspect public information/timetable and public tutorial pages too.
follow=set()
for p in pages:
 if p.get('error') or 'cms.cispa.saarland/' not in p['url'] or '/system/' in p['url']: continue
 s=bs4.BeautifulSoup(p['html'],'html.parser'); root=urllib.parse.urlparse(p['url']).path.strip('/').split('/')[0]
 for a in s.find_all('a',href=True):
  u=urllib.parse.urljoin(p['url'],a['href']); text=a.get_text(' ',strip=True).lower()
  if urllib.parse.urlparse(u).netloc=='cms.cispa.saarland' and urllib.parse.urlparse(u).path.strip('/').split('/')[0]==root and any(k in text for k in ['timetable','schedule','tutorial','organization','information','organis','calendar']):follow.add(u)
seen={p['url'] for p in pages};follow-=seen
pages.extend(concurrent.futures.ThreadPoolExecutor(6).map(get,sorted(follow)))
(BASE/'cispa_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'cispa_pages.json').write_text(json.dumps([{k:v for k,v in p.items() if k!='html'} for p in pages],ensure_ascii=False,indent=2),encoding='utf-8')
print('Inventory:',len(inventory),'CISPA:',sum(x['group']=='cispa_catalog' for x in inventory),'Seminars:',sum(x['group']=='seminars' for x in inventory),'Proseminars:',sum(x['group']=='proseminars' for x in inventory),'Fetched:',len(pages),'Errors:',sum(bool(p.get('error')) for p in pages))
# Show timetable-bearing chunks, not full descriptions.
for p in pages:
 if p.get('error'): print('ERROR',p['url'],p['error']);continue
 lines=p['text'].splitlines(); out=[]
 for i,l in enumerate(lines):
  if re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|\bTime\b|\bSchedule\b|\bLecture\b|\bTutorial\b|\bWhen\b|\bweekly\b|\bwöchentlich\b|\b[0-2]?\d:[0-5]\d\b)',l,re.I):
   out.append(' | '.join(lines[max(0,i-1):min(len(lines),i+3)]))
 print('\nPAGE',p['url'],p['key'],'\n'+'\n'.join(dict.fromkeys(out))[:10000])
