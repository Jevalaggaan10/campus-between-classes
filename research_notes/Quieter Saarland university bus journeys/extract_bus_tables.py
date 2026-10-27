"""Extract official July 2026 Saarbahn weekday tables, preserving blank cells.

No calls to public services: PDF inputs were downloaded from current operator
links (transit_links.json).  Only columns containing a Universität Campus time
are used for commute trip pairing, so depot/Hbf short runs cannot appear as
home-to-campus rides. Raw tables are retained for audit.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path
import pymupdf

BASE = Path(__file__).resolve().parent
RAW = BASE / 'transit_raw'
FILES = [
    ('101', 'to_university', '6a2664471a35c', 2),
    ('101', 'from_university', '6a2664474ef0f', 2),
    ('109', 'to_university', '6a26644b33c3a', 2),
    ('109', 'from_university', '6a26644b8fc21', 2),
    ('112', 'to_university', '6a26644c9f73e', 3),
    ('112', 'from_university', '6a26644d6cf50', 2),
    ('124', 'to_university', '6a2664516933a', 2),
    ('124', 'from_university', '6a26645116974', 2),
]

def clean_time(value):
    value = re.sub(r'\s+', '', value or '')
    if re.fullmatch(r'\d{3,4}', value):
        h, m = int(value[:-2]), int(value[-2:])
        if h <= 25 and m < 60:
            return f'{h:02}:{m:02}'
    return ''

def label(raw):
    # PDF geometric extraction collapses spaces. Preserve original in raw JSON.
    known = {
        'UniversitätCampus': 'Universität Campus',
        'UniversitätMensa': 'Universität Mensa',
        'UniBotanischerGarten': 'Universität Botanischer Garten',
        'HTW/SWS': 'HTW / SWS',
        'Deutschherrnstraße': 'Deutschherrnstraße',
        'HauptbahnhofC': 'Hauptbahnhof C',
        'HauptbahnhofD': 'Hauptbahnhof D',
    }
    if raw in known:
        return known[raw]
    match = re.fullmatch(r'UniversitätBusterminal([A-H])', raw)
    if match:
        return 'Universität Busterminal ' + match[1]
    return raw

all_tables, departures, pairs = [], [], []
for route, direction, source_id, pages in FILES:
    path = RAW / f'{route}_{source_id}.pdf'
    doc = pymupdf.open(path)
    source_url = f'https://www.saarbruecken.de/media/download-{source_id}'
    for page_no in range(pages):
        page = doc[page_no]
        assert 'Montag - Freitag' in page.get_text(), (path, page_no)
        found = page.find_tables().tables
        assert len(found) == 1, (path, page_no, len(found))
        data = found[0].extract()
        all_tables.append({'route': route, 'direction': direction, 'page': page_no + 1, 'source_url': source_url, 'table': data})
        campus = next(row for row in data if re.sub(r'\s+', '', row[0] or '') == 'UniversitätCampus')
        header = data[0]
        for col in range(1, len(campus)):
            campus_time = clean_time(campus[col])
            if not campus_time:
                continue
            trip_id = f'{route}_{direction}_{page_no+1}_{col}'
            condition = (header[col] or '').strip()
            if route == '112':
                condition = 'lecture days only' + (f'; {condition}' if condition else '')
            trip = {}
            for row in data[1:]:
                if col >= len(row):
                    continue
                time = clean_time(row[col])
                if not time:
                    continue
                raw_label = re.sub(r'\s+', '', row[0] or '')
                stop = label(raw_label)
                trip[stop] = time
                for weekday in range(1, 6):
                    if condition == '5' and weekday != 5:
                        continue
                    departures.append(dict(route=route, direction=direction, trip_id=trip_id, stop=stop, weekday=weekday, departure_time=time, validity='from 2026-07-01; current operator link checked 2026-10-26', service_condition=condition or 'Monday-Friday', source_url=source_url, evidence=f'PDF page {page_no+1}, column {col}, {stop}: {time}'))
            home_stops = ['HTW / SWS', 'Deutschherrnstraße']
            if route == '101':
                home_stops.append('Betriebshof')
            for home_stop in home_stops:
                if home_stop not in trip:
                    continue
                terminal_stop = next((k for k in trip if k.startswith('Universität Busterminal')), '')
                pairs.append(dict(route=route,direction=direction,trip_id=trip_id,weekdays='Monday-Friday' if condition!='5' else 'Friday',home_stop=home_stop,home_time=trip[home_stop],campus_stop='Universität Campus',campus_time=campus_time,terminal_stop=terminal_stop,terminal_time=trip.get(terminal_stop,''),mensa_time=trip.get('Universität Mensa',''),home_departure=trip[home_stop] if direction=='to_university' else '',campus_arrival=campus_time if direction=='to_university' else '',campus_departure=campus_time if direction=='from_university' else '',home_arrival=trip[home_stop] if direction=='from_university' else '',service_condition=condition or 'Monday-Friday',valid_from='2026-07-01',checked_on='2026-10-26',source_url=source_url,source_page=page_no+1,source_column=col))

(BASE/'bus_raw_tables.json').write_text(json.dumps(all_tables, ensure_ascii=False, indent=2),encoding='utf8')
for filename, rows in [('bus_departures.csv',departures),('bus_trips.csv',pairs)]:
    with (BASE/filename).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('departure rows',len(departures),'home-campus pairs',len(pairs))
print(Counter((x['route'],x['direction'],x['home_stop']) for x in pairs))
for row in pairs:
    if row['direction']=='from_university' and row['campus_time'].startswith(('14:','16:','18:')):
        print(row['route'],row['home_stop'],row['terminal_time'],row['campus_time'],row['home_time'],row['service_condition'])
