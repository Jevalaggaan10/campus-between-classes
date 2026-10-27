import concurrent.futures
import json
from pathlib import Path
import requests
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).parent
RAW = BASE / 'broader_raw'
RAW.mkdir(exist_ok=True)
BRANCHES = {
    'HW': '458383', 'MI': '469204', 'NT': '468295',
    'P': '464258', 'R': '458584',
    'international': '464811', 'languages': '467417',
    'certificates': '464914', 'career': '459606', 'GradUS': '460720',
    'entrepreneurship': '461768', 'teaching_learning': '461343',
    'Transform4Europe': '461484', 'prospective': '469899',
}

def fetch(item):
    key, ident = item
    url = ('https://www.lsf.uni-saarland.de/qisserver/rds?P.vx=lang&'
           f'root120262=461590%7C{ident}&search=1&state=wtree&trex=total')
    started = time.time()
    result = {'branch': key, 'url': url}
    try:
        r = requests.get(url, timeout=(10, 50))
        r.raise_for_status()
        data = r.content
        (RAW / (key + '.html')).write_bytes(data)
        result.update(status=r.status_code, bytes=len(data), seconds=round(time.time()-started, 1))
    except Exception as e:
        result.update(error=str(e), seconds=round(time.time()-started, 1))
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(fetch, BRANCHES.items()))
    (BASE / 'broader_fetch_log.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
