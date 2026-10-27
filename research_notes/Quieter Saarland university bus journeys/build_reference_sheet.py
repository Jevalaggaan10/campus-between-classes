"""Repackage the verified timing model as a compact, standalone reference."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from html import escape
from html.parser import HTMLParser
from pathlib import Path


REPORTS = (__import__('pathlib').Path(__file__).resolve().parents[2] / 'reports')
SOURCE = REPORTS / "saarland-bus-heatmap.html"
DESTINATION = REPORTS / "saarland-bus-reference.html"


def read_csv(name: str) -> list[dict[str, str]]:
    with (REPORTS / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def trip_cell(route: str, departure: str, arrival: str, source: str) -> str:
    return (
        f'<a class="departure" href="{escape(source, quote=True)}" '
        f'target="_blank" rel="noopener">'
        f'<span class="bus-number">{escape(route)}</span> {escape(departure)}</a>'
        f'<span class="arrival small secondary">arrives {escape(arrival)}</span>'
    )


original = SOURCE.read_text(encoding="utf-8")
data_text = re.search(
    r'<script id="timing-data" type="application/json">(.*?)</script>',
    original,
    re.DOTALL,
).group(1)
data = json.loads(data_text)
assert data["summary"] == {"courses": 1062, "patterns": 1471}

options = read_csv("saarland-weekday-bus-options.csv")
ranked = read_csv("saarland-bus-ranked-departures.csv")
friday_early = next(
    row for row in ranked
    if row["weekday"] == "5" and row["route"] == "112"
    and row["model_direction"] == "outgoing"
    and row["campus_departure"] == "15:30" and row["home_arrival"] == "15:51"
)
rows = []
for option in options:
    inbound = trip_cell(
        option["to_university_route"], option["htw_departure"],
        option["campus_arrival"], option["inbound_source"],
    )
    if option["weekday"] == "5":
        outbound = trip_cell(
            friday_early["route"], friday_early["campus_departure"],
            friday_early["home_arrival"], friday_early["source_url"],
        )
    else:
        outbound = trip_cell(
            option["return_route"], option["campus_departure"],
            option["htw_arrival"], option["outbound_source"],
        )
    day = escape(option["day"])
    rows.append(
        f'<tr><th scope="row"><abbr title="{day}">{day[:3]}</abbr></th>'
        f'<td>{inbound}</td><td>{outbound}</td></tr>'
    )

markup = """
<main id="saarland-timing-map">
<h2>Your weekday bus reference</h2>
<p class="small secondary">HTW/SWS ↔ Universität Campus · Winter 2026/27<br>Schedules checked 26 October 2026 · Class-pressure estimate</p>
<table class="week-table" aria-label="Suggested daytime buses, with departure and arrival times">
<thead><tr><th scope="col">Day</th><th scope="col">From HTW/SWS<br><span class="secondary small">toward university</span></th><th scope="col">From campus<br><span class="secondary small">toward home</span></th></tr></thead>
<tbody>__WEEK_ROWS__</tbody>
</table>
<p class="small secondary">Bus number + departure time. Suggested daytime options; the 112 trips run on university lecture days. The 101 at 09:02 is also a useful morning option every weekday.</p>
<h3>To university · when you reach campus</h3>
<div id="incoming-plot" class="plot"></div>
<h3>Going home · when you leave campus</h3>
<div id="outgoing-plot" class="plot"></div>
<div class="legend small secondary"><span class="swatch" aria-hidden="true"></span><span>Fainter = less scheduled class pressure. Same scale across weekdays; separate scales by direction.</span></div>
<details id="explore" class="reference-details">
<summary>Explore other times and contributing classes</summary>
<div class="fields">
<label>Weekday<select id="day"><option value="1">Monday</option><option value="2">Tuesday</option><option value="3">Wednesday</option><option value="4">Thursday</option><option value="5">Friday</option></select></label>
<label>Travel<select id="direction"><option value="incoming">To university</option><option value="outgoing">To HTW/SWS</option></select></label>
<label>Ranked times<select id="band"><option value="daytime">Daytime choices</option><option value="all">All 06:00–22:00</option><option value="midday">Midday choices</option></select></label>
</div>
<h3>Departures sorted by class timing</h3>
<p class="small secondary" id="rank-caption"></p>
<div class="tablewrap"><table><thead id="ranking-head"></thead><tbody id="ranking-body"></tbody></table></div>
<p class="small secondary">Equal scores are tied. A score is a class-meeting index; passenger counts and seat availability are unknown.</p>
<div class="fields"><label>Inspect campus time<input id="inspect-time" type="time" value="09:23" step="60"></label></div>
<section class="detail" aria-live="polite"><h3 id="selection-label"></h3><p id="selection-score"></p><ul id="contributors"></ul></section>
</details>
<details class="reference-details" id="source-coverage">
<summary>Sources: CMS · CISPA · seminars · LSF</summary>
<table class="coverage-table"><thead><tr><th scope="col">Public source</th><th scope="col">Listings reviewed</th></tr></thead><tbody>
<tr><td><a href="https://cms.sic.saarland/system/courses" target="_blank" rel="noopener">CMS</a></td><td>74</td></tr>
<tr><td><a href="https://cms.cispa.saarland/system/courses" target="_blank" rel="noopener">CISPA</a></td><td>27</td></tr>
<tr><td><a href="https://seminars.cs.uni-saarland.de/wise2627seminars" target="_blank" rel="noopener">Seminars</a> / <a href="https://seminars.cs.uni-saarland.de/wise2627proseminars" target="_blank" rel="noopener">proseminars</a></td><td>50 / 9</td></tr>
<tr><td><a href="https://www.lsf.uni-saarland.de/qisserver/rds?P.vx=kurz&amp;root120262=461590&amp;search=1&amp;state=wtree&amp;trex=step" target="_blank" rel="noopener">LSF</a></td><td>1,991 course IDs across 14 branches</td></tr>
<tr><td><a href="https://dcms.cs.uni-saarland.de/system/courses" target="_blank" rel="noopener">dCMS</a></td><td>Checked; no public Winter 2026/27 section</td></tr>
</tbody></table>
<p class="small secondary" id="coverage"></p>
<p class="small secondary">Catalogs overlap. LSF collection covered the five main Saarbrücken faculties plus supplementary offers; it is not a complete university census. Homburg, unknown campus locations, online-only meetings and unusable times were excluded. No LSF login was used.</p>
<p class="small secondary">Published starts and endings are spread over plausible arrival, walking and waiting buffers. Academic-quarter timing is tested in two scenarios. Each meeting has equal weight; attendance, course size and existing bus loads remain unmeasured.</p>
</details>
<p class="small secondary note">Remaining teaching-week average: 26 Oct–5 Feb, excluding 21 Dec–1 Jan. This is a saved timetable reference, not live bus information.</p>
</main>
""".replace("__WEEK_ROWS__", "\n".join(rows))

result = re.sub(
    r'<main id="saarland-timing-map">.*?</main>', markup.strip(),
    original, count=1, flags=re.DOTALL,
)
result = result.replace(
    "<title>Saarland university class timing and bus choices</title>",
    "<title>Saarland weekday bus reference</title>",
)
result = result.replace("height:218px", "height:182px")
result = result.replace("height=218;", "height=182;")
result = result.replace(
    "selectedDirection=direction;sync();});svg.appendChild(hit);",
    "selectedDirection=direction;root.querySelector('#explore').open=true;sync();});svg.appendChild(hit);",
)

extra_css = """
:root{color-scheme:light dark}
#saarland-timing-map .week-table{table-layout:fixed;margin:12px 0 8px}
#saarland-timing-map .week-table th:first-child{width:38px}
#saarland-timing-map .week-table th,#saarland-timing-map .week-table td{padding-top:10px;padding-bottom:10px}
#saarland-timing-map abbr{text-decoration:none}
#saarland-timing-map .departure{display:block;white-space:nowrap;text-decoration:none;color:var(--foreground)}
#saarland-timing-map .bus-number{font-weight:500;display:inline-block;min-width:30px}
#saarland-timing-map .arrival{display:block;margin-top:3px}
#saarland-timing-map .reference-details{margin:14px 0 0;border-top:1px solid var(--border);padding-top:12px}
#saarland-timing-map summary{font-weight:500}
#saarland-timing-map .coverage-table td:last-child{overflow-wrap:anywhere}
@media(max-width:420px){#saarland-timing-map .week-table th,#saarland-timing-map .week-table td{padding-right:3px;padding-left:3px}#saarland-timing-map .week-table th:first-child{padding-left:0;width:32px}}
@media print{#saarland-timing-map{-webkit-print-color-adjust:exact;print-color-adjust:exact}#saarland-timing-map .reference-details{display:none}#saarland-timing-map .week-table a{text-decoration:none}#saarland-timing-map .plot{break-inside:avoid}}
"""
result = result.replace("</style>", extra_css + "\n</style>", 1)

# System color fallbacks make the saved file usable outside the host's theme.
fallback_script = """
<script>
(function(){
 const root=document.documentElement;
 if(getComputedStyle(root).getPropertyValue('--foreground').trim())return;
 const fallback={'--foreground':'CanvasText','--background':'Canvas','--muted-foreground':'GrayText','--border':'color-mix(in srgb, CanvasText 18%, Canvas)','--primary':'LinkText','--chart-1':'LinkText','--font-sans':'ui-sans-serif,system-ui,sans-serif','--font-size-base':'16px','--radius':'8px'};
 Object.keys(fallback).forEach(function(key){root.style.setProperty(key,fallback[key]);});
})();
</script>
"""
result = result.replace("<body>", "<body>\n" + fallback_script, 1)


class IDCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids.append(value)


collector = IDCollector()
collector.feed(result)
assert len(collector.ids) == len(set(collector.ids)), "Duplicate HTML IDs"
for expected in (
    "day", "direction", "band", "inspect-time", "coverage", "incoming-plot",
    "outgoing-plot", "ranking-head", "ranking-body", "rank-caption",
    "selection-label", "selection-score", "contributors", "explore", "timing-data",
):
    assert expected in collector.ids, expected
assert data_text in result, "The source model must remain unchanged"
assert result.count('scope="row"') == 5
scripts = re.findall(r"<script>(.*?)</script>", result, re.DOTALL)
for script in scripts:
    checked = subprocess.run(
        ["node", "--check"], input=script, text=True, capture_output=True,
        encoding="utf-8", check=False,
    )
    if checked.returncode:
        raise RuntimeError(checked.stderr)
DESTINATION.write_text(result, encoding="utf-8", newline="\n")
print(json.dumps({
    "file": str(DESTINATION), "bytes": DESTINATION.stat().st_size,
    "model_unchanged": True, "weekday_rows": 5,
    "unique_ids": len(collector.ids), "scripts_checked": len(scripts),
    "friday_earlier_trip_verified": friday_early["trip_id"],
}))
