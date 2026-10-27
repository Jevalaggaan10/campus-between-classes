# Between Classes

A weekday bus reference between HTW/SWS and Saarland University for Winter 2026/27. Both web versions are preserved side by side.

| Version | Open locally | Source |
| --- | --- | --- |
| Simplified app | [versions/simplified/dist/index.html](versions/simplified/dist/index.html) | [versions/simplified](versions/simplified) |
| Previous full page | [versions/full/dist/index.html](versions/full/dist/index.html) | [versions/full](versions/full) |
| Original standalone heatmap | [reports/saarland-bus-heatmap.html](reports/saarland-bus-heatmap.html) | [research scripts](research_notes/Quieter%20Saarland%20university%20bus%20journeys) |
| Earlier compact reference | [reports/saarland-bus-reference.html](reports/saarland-bus-reference.html) | [reference generator](research_notes/Quieter%20Saarland%20university%20bus%20journeys/build_reference_sheet.py) |

Download/clone this repository and open the root `index.html` for the version chooser. GitHub's file viewer displays HTML source; it does not execute the app. Each app also runs directly from its own `dist/index.html`, without a build or server. The existing private [live simplified app](https://campus-between-classes.truenova261.chatgpt.site) is unchanged.

## Included

- Both app layouts, templates, scripts, self-hosted fonts and font licenses.
- [Research report](reports/Quieter%20Saarland%20university%20bus%20journeys.md), class meetings, sparse timing embeddings, weekday options and ranked departures.
- Public-source snapshots, extraction/model scripts, source inventories and audit notes in `research_notes/`.
- Focused interaction checks for each layout. Original workstation screenshots, hosting credentials and hosting configuration are excluded.

## Editing and checks

The apps have no runtime dependencies. To rebuild their HTML:

```sh
python -m pip install -r requirements.txt
python versions/simplified/build.py
python versions/full/build.py
```

Edit each version's `page.html`, `dist/styles.css` or `dist/app.js`. Builds read the bundled `reports/` data and retain the existing fonts. A Hallmark installation is not required.

For development checks, install Node.js and Chrome, then:

```sh
npm ci
npm run verify
```

Set `CHROME_PATH` when Chrome is not at the platform's default path. Tests write ignored review artifacts to each version's `.hallmark/` folder.

The archived research scripts are supplied for audit and reproduction. The main model/heatmap/reference generators use repository-relative report paths; crawl scripts require their own Python libraries (`requests`, `beautifulsoup4`) and live public sites. Re-crawling can change the dataset. Opening or rebuilding the saved apps does not re-crawl anything.

## Data meaning and coverage

The model retains 1,471 meeting patterns across 1,062 canonical timed courses. It combines public CMS, CISPA, seminar/proseminar and LSF sources, with bus timetables checked on 26 October 2026. Unknown timings, inaccessible pages and excluded campuses limit coverage. This is not a complete university attendance census.

Heatmaps show estimated pressure from scheduled class starts/ends, not measured bus occupancy or guaranteed empty seats. Lecture-day restrictions and official timetable links are retained. See the report and source audit for assumptions, exclusions and timing uncertainty.

Design developed with [Hallmark](https://github.com/Nutlope/hallmark). Bundled fonts retain their OFL licenses. Public-source snapshots retain their original ownership; no blanket license is asserted over third-party course or timetable content.
