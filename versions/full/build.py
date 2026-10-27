from __future__ import annotations

import csv
import gzip
import html
import json
import re
import shutil
import urllib.request
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
REPORTS = ROOT.parents[1] / 'reports'
DIST.mkdir(exist_ok=True)
(DIST / 'downloads').mkdir(exist_ok=True)
(DIST / 'fonts').mkdir(exist_ok=True)

source = (REPORTS / 'saarland-bus-heatmap.html').read_text(encoding='utf-8')
payload = json.loads(re.findall(r'<script[^>]+application/json[^>]*>(.*?)</script>', source, re.S)[0])
assert payload['summary'] == {'courses': 1062, 'patterns': 1471}
with (REPORTS / 'saarland-weekday-bus-options.csv').open(encoding='utf-8-sig', newline='') as f:
    plans = list(csv.DictReader(f))
with (REPORTS / 'saarland-bus-ranked-departures.csv').open(encoding='utf-8-sig', newline='') as f:
    ranked = list(csv.DictReader(f))

friday = next(r for r in ranked if r['weekday'] == '5' and r['route'] == '112'
              and r['model_direction'] == 'outgoing' and r['campus_departure'] == '15:30')
assert friday['home_arrival'] == '15:51'
plans[-1].update(return_route='112', campus_departure='15:30', terminal_departure=friday['terminal_time'],
                 htw_arrival='15:51', outbound_source=friday['source_url'])

bus_sources = {(int(r['weekday']), r['model_direction'], r['route'], r['home_time'], int(r['campus_minute'])):
               r['source_url'] for r in ranked}
for bus in payload['buses']:
    bus.append(bus_sources[(bus[0], bus[1], bus[2], bus[3], bus[5])])
payload['plans'] = plans

def esc(value):
    return html.escape(str(value), quote=True)

week_rows = []
for p in plans:
    week_rows.append(f'''<tr><th scope="row">{esc(p['day'])}</th>
      <td><a href="{esc(p['inbound_source'])}" target="_blank" rel="noopener"><span class="route-number">{p['to_university_route']}</span> <span class="measured">{p['htw_departure']}</span></a><span class="arrival">Campus {p['campus_arrival']}</span></td>
      <td><a href="{esc(p['outbound_source'])}" target="_blank" rel="noopener"><span class="route-number">{p['return_route']}</span> <span class="measured">{p['campus_departure']}</span></a><span class="arrival">HTW/SWS, arrive {p['htw_arrival']}</span></td></tr>''')

def static_heatmap(direction):
    cells = []
    values = []
    column = 2 if direction == 'incoming' else 3
    for day in range(1, 6):
        for bucket in range(64):
            matches = [v[column] for v in payload['vectors'] if v[0] == day and
                       360 + 15 * bucket <= v[1] < 375 + 15 * bucket]
            val = sum(matches) / max(1, len(matches))
            values.append((day, bucket, val))
    maximum = max(v[2] for v in values)
    for day, bucket, val in values:
        opacity = .045 + .955 * val / maximum
        cells.append(f'<rect class="pressure-cell" x="{64 + bucket * 14.25:.2f}" y="{16 + (day - 1) * 35}" width="13.25" height="30" opacity="{opacity:.3f}"/>')
    labels = ''.join(f'<text x="48" y="{37 + i * 35}" text-anchor="end">{day}</text>'
                     for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri']))
    ticks = ''.join(f'<text x="{64 + (minute-360)/960*912:.1f}" y="218" text-anchor="middle">{minute//60:02d}:00</text>'
                    for minute in [360, 600, 840, 1080, 1320])
    return f'<svg class="heatmap-svg" viewBox="0 0 1000 240" role="img" aria-label="Weekday {direction} scheduled class pressure">{labels}{"".join(cells)}{ticks}</svg>'

download_files = {
    'saarland-bus-ranked-departures.csv': 'departures.csv',
    'saarland-class-time-vectors.csv': 'timing-vectors.csv',
    'saarland-course-time-embeddings.json': 'course-embeddings.json',
    'saarland-canonical-class-meetings.csv': 'class-meetings.csv',
    'saarland-weekday-bus-options.csv': 'weekday-options.csv',
    'Quieter Saarland university bus journeys.md': 'research.md',
}
for original, name in download_files.items():
    shutil.copyfile(REPORTS / original, DIST / 'downloads' / name)
report = (REPORTS / 'Quieter Saarland university bus journeys.md').read_text(encoding='utf-8')
for original, name in download_files.items():
    report = report.replace('C:/codex/reports/' + original, 'downloads/' + name)
report = report.replace('C:/codex/reports/saarland-bus-heatmap.html', '#heatmaps')
report = report.replace('\u2013', ' to ').replace('\u2014', ', ')
full_report = markdown.markdown(report, extensions=['tables'])
full_report = full_report.replace('<h1>', '<h3>').replace('</h1>', '</h3>')
full_report = full_report.replace('<h2>', '<h4>').replace('</h2>', '</h4>')

fonts = [
    ('Host Grotesk', 'Host+Grotesk:wght@400;500', 'host-grotesk.woff2', 'hostgrotesk'),
    ('Atkinson Hyperlegible Mono', 'Atkinson+Hyperlegible+Mono:wght@400;500', 'atkinson-mono.woff2', 'atkinsonhyperlegiblemono'),
]
font_sources = []
for family, query, filename, license_dir in fonts:
    dest = DIST / 'fonts' / filename
    if not dest.exists() or dest.read_bytes()[:4] != b'wOF2':
        request = urllib.request.Request('https://fonts.googleapis.com/css2?family=' + query + '&display=swap',
                                         headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'})
        css = urllib.request.urlopen(request, timeout=30).read().decode()
        latin = css.rsplit('/* latin */', 1)[-1]
        url = re.findall(r'url\((https://[^)]+)\)', latin)[0]
        raw_font = urllib.request.urlopen(url, timeout=30).read()
        if raw_font[:4] != b'wOF2':
            from io import BytesIO
            from fontTools.ttLib import TTFont
            font = TTFont(BytesIO(raw_font))
            font.flavor = 'woff2'
            font.save(dest)
        else:
            dest.write_bytes(raw_font)
        font_sources.append({'family': family, 'source': url, 'bytes': dest.stat().st_size})
        try:
            license_text = urllib.request.urlopen('https://raw.githubusercontent.com/google/fonts/main/ofl/' + license_dir + '/OFL.txt', timeout=20).read()
            (DIST / 'fonts' / (license_dir + '-OFL.txt')).write_bytes(license_text)
        except Exception as exc:
            raise RuntimeError('Could not retain the font license for ' + family) from exc

template = (ROOT / 'page.html').read_text(encoding='utf-8')
replacements = {
    '{{WEEK_ROWS}}': '\n'.join(week_rows),
    '{{INCOMING_MAP}}': static_heatmap('incoming'),
    '{{OUTGOING_MAP}}': static_heatmap('outgoing'),
    '{{FULL_REPORT}}': full_report,
    '{{DATA}}': json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'),
}
for key, value in replacements.items():
    template = template.replace(key, value)
assert '{{' not in template
(DIST / 'index.html').write_text(template, encoding='utf-8')

preflight = {
    'scanned': '2026-10-27',
    'findings': {
        'source': 'C:/codex/reports/saarland-bus-reference.html:37, source model and interactions',
        'research': 'C:/codex/reports/Quieter Saarland university bus journeys.md:1, verified findings',
        'fonts': 'Host Grotesk and Atkinson Hyperlegible Mono, self-hosted',
        'palette': 'Hallmark Console graphite', 'framework': 'buildless HTML, CSS and JavaScript',
        'motion': 'state transitions and one chart draw, reduced-motion fallback',
    },
    'preserve': ['all verified schedules, model data, source links and exports'],
    'introduce': ['responsive page, accessible heatmap inspection, URL state, source coverage and research reader'],
}
(ROOT / '.hallmark').mkdir(exist_ok=True)
(ROOT / '.hallmark' / 'preflight.json').write_text(json.dumps(preflight, indent=2), encoding='utf-8')

transfer_files = ['index.html', 'styles.css', 'app.js', 'tokens.css', 'base.css']
sizes = {}
for name in transfer_files:
    path = DIST / name
    if path.exists():
        raw = path.read_bytes()
        sizes[name] = {'raw': len(raw), 'gzip': len(gzip.compress(raw, mtime=0))}
print(json.dumps({'built': str(DIST / 'index.html'), 'model': payload['summary'],
                  'weekday_plans': len(plans), 'ranked_options': len(payload['buses']),
                  'transfer_files': sizes, 'fonts': font_sources}, indent=2))
