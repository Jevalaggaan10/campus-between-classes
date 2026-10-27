from pathlib import Path
import json, requests, bs4, concurrent.futures, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).parent
R=P/'cms_raw'; R.mkdir(exist_ok=True)
def fetch(url):
    r=requests.get(url,timeout=40); r.raise_for_status(); r.encoding='utf-8'
    return r.text
h=fetch('https://cms.sic.saarland/system/courses')
(P/'cms_catalog.html').write_text(h,encoding='utf-8')
s=bs4.BeautifulSoup(h,'html.parser')
t=s.find('h3',string=re.compile('Winter term 2026/2027')).find_next('table')
items=[]
for a in t.select('h6 a'):
    u=urllib.parse.urljoin('https://cms.sic.saarland',a['href']).rstrip('/')+'/'
    items.append(dict(title=a.get_text(' ',strip=True),url=u,id=u.rstrip('/').split('/')[-1]))
def one(x):
    try:
        h=fetch(x['url']); (R/(x['id']+'.html')).write_text(h,encoding='utf-8')
        s=bs4.BeautifulSoup(h,'html.parser')
        for el in s.select('script,style'): el.decompose()
        txt=s.get_text('\n',strip=True)
        (R/(x['id']+'.txt')).write_text(txt,encoding='utf-8')
        x['status']='ok'; x['characters']=len(txt)
        x['links']=[dict(text=a.get_text(' ',strip=True),url=urllib.parse.urljoin(x['url'],a['href'])) for a in s.select('a[href]')]
    except Exception as e:x['status']='error';x['error']=str(e)
    return x
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    items=list(pool.map(one,items))
(P/'cms_inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print('COURSES',len(items),'OK',sum(x['status']=='ok' for x in items))
for x in items:
    print(x['id'],x['title'],x['characters'] if x['status']=='ok' else x['error'])
