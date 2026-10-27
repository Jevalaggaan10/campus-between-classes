import pathlib,json,csv
ROOT=pathlib.Path(__file__).resolve().parent
OUT=(__import__('pathlib').Path(__file__).resolve().parents[2] / 'reports')
raw=json.loads((ROOT/'model_data.json').read_text(encoding='utf-8'))
courses=[];course_indices={}
meetings=[]
for r in raw['meetings']:
    cid=r['canonical_course_id']
    if cid not in course_indices:
        course_indices[cid]=len(courses)
        courses.append([r['title'],r['source_url']])
    meetings.append([course_indices[cid],r['weekday'],r['start_nominal'],r['end_nominal'],r['start_quarter'],r['end_quarter'],r['frequency_weight'],r.get('location',''),r['kind']])
vectors=[[r['weekday'],r['minute'],r['incoming_score'],r['outgoing_score'],r['starts_count'],r['ends_count']] for r in raw['vectors']]
buses=[[r['weekday'],r['model_direction'],r['route'],r['home_time'],r['terminal_time'],r['campus_minute'],r['service_condition'],r['central_score'],r['timing_low'],r['timing_high'],r['robust_sort_key']] for r in raw['ranked_bus_options']]
data={'summary':{'courses':raw['summary']['retained_unique_canonical_courses'],'patterns':raw['summary']['retained_meeting_patterns']},'courses':courses,'meetings':meetings,'vectors':vectors,'buses':buses}
encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
html=(ROOT/'heatmap-template.html').read_text(encoding='utf-8').replace('__TIMING_DATA__',encoded)
path=OUT/'saarland-bus-heatmap.html';path.write_text(html,encoding='utf-8')
assert path.stat().st_size<1_000_000
script=html.split('<script>')[1].split('</script>')[0]
(ROOT/'heatmap-runtime.js').write_text(script,encoding='utf-8')
print(str(path),path.stat().st_size,'bytes')
