"""Derive auditable recurring meeting patterns; manually verified root-page additions below."""
from pathlib import Path
import csv,json,re,datetime as dt,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).parent
items=json.loads((P/'cms_inventory.json').read_text(encoding='utf-8'))
byid={x['id']:x for x in items}
occ=json.loads((P/'cms_occurrences.json').read_text(encoding='utf-8'))
rows=[]; exclusions=[];groups=collections.defaultdict(list)
def add(cid,typ,day,start,end,loc='',conv='unknown',freq='weekly',first='2026-10-12',last='2027-02-05',dates=None,note='',group='',url=None,confidence='high',evidence='',include=True):
    rows.append(dict(source_group='CMS SIC',course_id=cid,title=byid[cid]['title'],event_type=typ,weekday=day,start_time=start,end_time=end,time_convention=conv,location=loc,campus='Saarbrücken',semester='Winter 2026/27',first_date=first,last_date=last,frequency=freq,source_url=url or byid[cid]['url'],evidence_snippet=evidence,confidence=confidence,notes=note,group_id=group,scheduled_dates=';'.join(dates or []),include_in_demand=int(include),date_count=len(dates) if dates else '',enrolment='',capacity=''))
def kind(e):
    s=e['summary'].lower()
    if re.search(r'office.?hour|sprechstunde|counsell',s):return 'consultation'
    if e['course_id'] in ['graph_seminar26','sem_agents_ak_w26','semstoch']:return 'seminar'
    if e['course_id']=='cv4d':return 'lecture' if e['weekday']==3 else 'exercise'
    if re.search(r'tutor|übung|exercise|q.?a|recap.?lab',s):return 'tutorial'
    return 'lecture'
for e in occ:
    cid=e['course_id']; reason=''
    if not ('2026-10-12'<=e['date']<='2027-02-05'):reason='outside teaching period'
    elif e['weekday']>5:reason='weekend'
    elif '2026-12-21'<=e['date']<='2027-01-01':reason='Christmas teaching break'
    elif e['status']=='CANCELLED':reason='canceled'
    elif cid=='emse_26':reason='online/asynchronous course'
    elif cid in ['inteq','statdc26']:reason='source conflict or embedded sessions; replaced by verified root-page pattern'
    elif not (15<=e['duration_minutes']<=300):reason='all-day/deadline/zero duration/overlong item'
    elif re.search(r'exam|klausur|midterm|minitest|mini.?test|deadline|upload|knobel|prep.?course|semester opening|kick.?off|einführungsveranstaltung|hilfe bei der installation|holiday|no lecture',e['summary'],re.I):reason='assessment/deadline/kickoff/embedded activity'
    elif re.search(r'zoom|remote|online|https?://',e['location'],re.I) and not 'alternatively' in e['location']:reason='remote/online'
    elif e['date']<'2026-10-26':reason='past occurrence; retained in raw archive'
    if reason:
        exclusions.append(dict(**e,exclusion_reason=reason));continue
    typ=kind(e)
    # Groups with different tutors or rooms may be parallel; preserve explicit numbered group labels.
    m=re.search(r'(?:Tutorial|Tutorium)\s*#?\s*(\d+)',e['summary'],re.I)
    gid=m.group(1) if m else ''
    if cid=='sem_agents_ak_w26':e=dict(e,start_time='10:15')
    groups[(cid,typ,e['weekday'],e['start_time'],e['end_time'],gid)].append(e)
for (cid,typ,day,st,en,gid),ee in groups.items():
    dates=sorted(set(e['date'] for e in ee))
    if len(dates)<2:
        exclusions.extend(dict(**e,exclusion_reason='one-off/unique slot; retained outside recurring model') for e in ee);continue
    locs=list(dict.fromkeys(e['location'] for e in ee if e['location']))
    conv='exact' if st[-2:]!='00' else 'unknown'
    note='Public ICS, UTC converted to Europe/Berlin. Whole-hour calendar slots may be nominal; physical release may differ.' if conv=='unknown' else 'Public ICS, UTC converted to Europe/Berlin; explicit minute-level advertised times.'
    if cid=='sem_agents_ak_w26':note+=' Corrected ICS 10:00 start to 10:15 per 22 October news.'
    if cid=='graph_seminar26':note+=' Only listed block weeks; not a weekly all-semester meeting.'
    if cid=='cv4d':note+=' Remote lecture dates excluded; recurring dates are only listed physical sessions.'
    if typ=='consultation':note+=' Optional small consultation; excluded from default demand model.'
    freq='listed dates; see scheduled_dates'
    add(cid,typ,day,st,en,' / '.join(locs),conv,freq,min(dates),max(dates),dates,note,gid,byid[cid]['url']+'termine/events/download',evidence='; '.join(sorted(set(e['summary'] for e in ee)))[:240],include=typ!='consultation')
# Root pages supply recurring patterns absent from calendars or correct their inaccuracies.
def simple(cid,typ,slots,loc='',conv='exact',**kwargs):
    for d,st,en in slots:add(cid,typ,d,st,en,loc,conv,**kwargs)
simple('atos','tutorial',[(1,'11:30','13:00'),(4,'11:00','12:30')],'E1.1 1.21',first='2026-10-29',note='26 October news: no tutorial on 26 Oct; then Mondays/Thursdays, equivalent sessions.',evidence='Mondays 11:30-13:00 and Thursdays 11:00-12:30')
simple('atos','lecture',[(5,'08:30','10:00')],'E1.3 HS I',first='2026-10-23',url='https://www.lsf.uni-saarland.de/qisserver/rds?moduleCall=webInfo&publishConfFile=webInfo&publishSubDir=veranstaltung&publishid=166864&state=verpublish&status=init&vmfile=no',note='LSF Fri08–10 nominal; CMS first lecture08:30. Source says six lectures followed by presentations; exact later meeting continuity not guaranteed.',confidence='medium',evidence='LSF Friday08–10; CMS first lecture23Oct08:30')
simple('alg26','lecture',[(3,'14:15','15:45'),(4,'10:15','11:45')],'E2.5 Zeichensaal',evidence='Wednesdays14:15-15:45; Thursdays10:15-11:45')
simple('alg26','tutorial',[(1,'08:30','10:00')],'E2.4 SR9',first='2026-10-19',evidence='Mondays8:30-10:00 starting19October')
simple('alg_geo','lecture',[(2,'16:00','18:00'),(3,'10:00','12:00')],'E2.4 SR10',conv='unknown',evidence='Tuesdays16-18; Wednesdays10-12')
simple('alg_geo','tutorial',[(3,'14:00','16:00')],'E2.5 SR1',conv='unknown',evidence='Wednesdays14-16')
simple('alsa26','lecture',[(2,'08:30','10:00'),(4,'08:30','10:00')],'E2.1 001',first='2026-10-13',note='Root ending04.02.2026 appears typo; current semester catalog and start13Oct2026 establish2026/27.',evidence='every Tuesday08:30-10:00; every Thursday08:30-10:00')
simple('alsa26','tutorial',[(2,'14:30','16:00')],'E2.1 001',first='2026-10-27',evidence='Tuesdays14:30–16:00, Room001')
simple('alsa26','tutorial',[(3,'10:30','12:00')],'E2.1 007',first='2026-10-28',evidence='Wednesdays10:30–12:00, Room007')
simple('ana3_2627','lecture',[(1,'10:15','12:00')],'HS III',evidence='Montag10:15-12')
simple('ana3_2627','lecture',[(3,'10:15','12:00')],'E2.4 HS IV',evidence='Mittwoch10:15-12')
simple('ana3_2627','tutorial',[(2,'14:00','16:00')],'SR5',conv='unknown',group='1',evidence='Tutorium1 Di14-16 SR5')
simple('ana3_2627','tutorial',[(5,'10:00','12:00')],'SR10',conv='unknown',group='2',evidence='Tutorium2 Fr10-12 SR10')
simple('avcn_2627','lecture',[(2,'10:30','11:45'),(3,'12:15','13:45')],'E1.3 HS001',first='2026-10-13',note='Hybrid presence or Teams; no remote quiz demand counted.',evidence='Tuesday10:30–11:45 and Wednesday12:15–13:45')
simple('avcn_2627','tutorial',[(4,'14:15','15:45')],'C6.3 9.05',evidence='Thursday14:15–15:45 in presence')
simple('biostatslab26','lecture',[(3,'08:30','10:00'),(5,'12:15','13:45')],'E2.1 001',note='Lecture times explicit; confirm room from source before travel.',evidence='Wednesday08:30-10:00 and Friday12:15-13:45')
# BioStatsLab tutorial start is public but its end is not; exclude incomplete interval instead of inventing.
simple('causxai','seminar',[(2,'12:15','13:45')],'E1.1 2.06',evidence='Tuesdays12:15 to13:45')
simple('cla','seminar',[(3,'12:15','13:45')],'C7.2 SR1.12',first='2026-10-28',url='https://github.com/at-lab-uds/continually-learning-agents-seminar',evidence='Wednesday12:15–13:45; Seminarraum1.12 BuildingC7.2')
simple('das_26','seminar',[(5,'10:00','12:00')],'E1.7 3.23',conv='unknown',evidence='10am to12pm every Friday')
simple('dic_26','tutorial',[(2,'16:15','18:00')],'E1.3 SR016',first='2026-10-20',note='Online lectures excluded; only in-person tutorial counts. Registration cap40, not actual attendance.',evidence='Tuesday16:15-18:00, in person')
simple('dtsp_2627','lecture',[(2,'12:15','13:45'),(3,'08:30','10:00')],'E1.3 HS001',first='2026-10-13',note='Hybrid presence or Teams; online quiz excluded.',evidence='Tuesday12:15–13:45 and Wednesday08:30–10:00')
simple('dtsp_2627','tutorial',[(5,'10:30','11:45')],'C6.3 9.05',evidence='Friday10:30–11:45 in presence')
simple('enum26','lecture',[(2,'08:30','10:00'),(4,'14:15','15:45')],'E2.5 HS I',evidence='dienstags08:30–10:00 und donnerstags14:15–15:45')
simple('enum26','tutorial',[(2,'14:15','15:45')],'E2.4 SR9',evidence='dienstags14:15–15:45 Seminarraum9')
simple('enum26','tutorial',[(3,'14:15','15:45'),(4,'10:15','11:45')],'E2.5 SR3',evidence='mittwochs14:15–15:45 und donnerstags10:15–11:45')
simple('emlw26','lecture',[(4,'16:00','18:00')],'E2.2 GHH',conv='st',note='15Octnews: starts16:00, hopes to finish17:35ish; nominal end18:00 retained; likely release17:35–18:00, not exact.',evidence='Thursdays16:00-18:00; starts4pm not4:15; hope finish5:35ish')
simple('emlw26','tutorial',[(3,'10:00','12:00'),(3,'14:00','16:00'),(4,'10:00','12:00'),(4,'12:00','14:00'),(5,'10:00','12:00'),(5,'12:00','14:00')],'E1.3 HS001',conv='unknown',first='2026-10-28',evidence='Tutorials Wednesday10–12/14–16; Thursday10–12/12–14; Friday10–12/12–14')
simple('funcspaces26','lecture',[(3,'10:15','11:45')],'E2.5 SR9 (source roomplaceholder)',confidence='medium',note='Root contains template placeholders; actual room ambiguous.',evidence='mittwochs10:15 bis11:45')
simple('gsv_ws2627','lecture',[(4,'14:15','15:45')],'A5.1 HS-1.03',first='2026-10-22',confidence='medium',note='Thursday inferred from lecture start22Oct and all listed quiz dates; root time explicit.',evidence='14:15–15:45; Vorlesungsbeginn22.10.26; quiz datesThursdays')
simple('gsv_ws2627','tutorial',[(4,'16:00','17:30')],'A5.1',group='two groups allocation TBA',note='Two groups advertised; one common slot, actual parallel room/group split unknown. Count one slot.',evidence='zwei Gruppen; wöchentlichDo16:00–17:30')
simple('hfs_2627','lecture',[(4,'14:15','15:45')],'E2.4 HS4',evidence='Thursday14:15–15:45')
simple('hfs_2627','tutorial',[(1,'10:15','11:45')],'E2.5 SR1',evidence='Monday10:15–11:45')
simple('hmi32627','lecture',[(1,'08:00','10:00'),(4,'08:00','10:00')],'E2.5 HS I',conv='ct',note='Explicit course convention:8 Uhr means8:30. Preserve nominal interval; source does not explicitly resolve physical end.',evidence='Mo undDo08–10; alleUhrzeitenct; Ausnahme8Uhr beginnt8.30')
for day,st,en,loc,g in [(1,'10:00','12:00','E2.5 Zeichensaal','1'),(1,'12:00','14:00','E2.5 SR3','2'),(1,'14:00','16:00','E2.5 SR3','3'),(2,'08:00','10:00','E2.5 SR1','4'),(2,'10:00','12:00','E2.4 SR10','5'),(3,'14:00','16:00','E2.4 SR5','6'),(4,'12:00','14:00','E2.4 SR5','7'),(5,'10:00','12:00','E2.5 SR4','8')]:add('hmi32627','tutorial',day,st,en,loc,'ct',group=g,evidence='Public tutorial table; all timesct except08starts08:30',note='Explicitctstart+15min, except08:00means08:30. Nominal end retained.')
simple('iam26','lecture',[(1,'12:15','14:00')],'E1.3 HS001',first='2026-10-19',evidence='Monday12:15–14')
simple('iam26','tutorial',[(4,'12:00','14:00')],'E1.3 SR014',conv='unknown',first='2026-10-29',evidence='Thursday12–14')
simple('life_w26','lecture',[(4,'12:15','13:45')],'E2.4 SR6',first='2026-10-15',evidence='Thursdays12:15–13:45')
simple('life_w26','tutorial',[(5,'14:15','15:45')],'E2.4 SR9',freq='listed dates',first='2026-10-30',dates=['2026-10-30','2026-11-13','2026-11-20','2026-12-04','2027-01-08','2027-01-22','2027-02-05'],evidence='Listed Fridays30Oct,13Nov,20Nov,4Dec,8Jan,22Jan,5Feb')
simple('la12627','lecture',[(2,'10:15','11:45'),(5,'10:15','11:45')],'E2.5 HS I',evidence='Di10:15–11:45; Fr10:15–11:45')
for day,st,en,loc,g in [(1,'08:00','10:00','E2.4 SR10','1'),(2,'12:00','14:00','E2.4 SR5','2'),(2,'12:00','14:00','E2.5 Zeichensaal','3'),(2,'16:00','18:00','E2.4 SR6','4'),(4,'12:00','14:00','E2.4 SR9','5'),(4,'14:00','16:00','E2.4 SR9','6'),(5,'12:00','14:00','E2.4 SR10','7')]:add('la12627','tutorial',day,st,en,loc,'unknown',group=g,evidence='Public numbered tutorial table')
simple('la12627','general tutorial',[(4,'16:00','18:00')],'E2.5 HS II',conv='unknown',note='24Octnews explicitly retains Thursday16–18 after considering a move toWednesday.',evidence='SaalübungDo16–18; nichtverlegen')
simple('mfcs3_wise2627','lecture',[(3,'08:30','10:00'),(5,'12:15','13:45')],'E2.2 GHH',first='2026-10-14',evidence='Wednesdays8:30–10; Fridays12:15–13:45')
simple('mfcs3_wise2627','general tutorial',[(5,'14:15','15:45')],'E2.2 GHH',first='2026-10-23',evidence='Fridays14:15–15:45')
simple('math_bio_chem_la26','lecture',[(5,'12:15','13:45')],'E2.5 HS I',evidence='freitags12:15–13:45')
for day,st,en,loc,g in [(1,'08:30','10:00','E2.4 SR6','1'),(1,'16:15','17:45','E2.4 SR6','2'),(2,'08:30','10:00','E2.5 SR4','3'),(2,'16:15','17:45','E2.5 SR4','4'),(3,'10:15','11:45','E2.5 SR4','5')]:add('math_bio_chem_la26','tutorial',day,st,en,loc,'exact',group=g,evidence='Public tutorial list')
simple('mfn_i','lecture',[(2,'10:00','12:00')],'HS II',conv='unknown',evidence='Di10–12 wöchentlich')
simple('mfn_i','lecture',[(5,'10:00','12:00')],'HS II',conv='unknown',freq='fortnightly; alternates with tutorials',evidence='Fr10–12 vierzehntäglich imWechselmitÜbungen')
for st,en,loc,g in [('10:00','12:00','E2.4 SR5','1'),('16:00','18:00','E2.4 SR5','2'),('12:00','14:00','E2.4 SR6','3'),('14:00','16:00','E2.4 SR6','4')]:add('mfn_i','tutorial',5,st,en,loc,'unknown',freq='fortnightly; first23Oct2026',first='2026-10-23',group=g,evidence='Public tutorial table; first23October; lecturealternates')
simple('natcomp','lecture',[(3,'12:25','14:00')],'E1.3 HS III',first='2026-10-14',evidence='EveryWednesday12:25–14:00')
simple('nnti_2627','lecture',[(2,'14:15','16:00')],'E2.5 HS I',first='2026-10-20',url='https://www.lsf.uni-saarland.de/qisserver/rds?moduleCall=webInfo&publishConfFile=webInfo&publishSubDir=veranstaltung&publishid=166412&state=verpublish&status=init&vmfile=no',note='CMS says20Oct14:15 first; LSF Tue14–16 weekly nominal; chair webpage says27Octfirst. Start-date conflict; recurringTue slot corroborated.',confidence='medium',evidence='LSF Tue14–16; CMS starts20.10.26 14:15')
simple('ot_26','lecture',[(3,'14:15','15:45')],'E2.4 SR6',evidence='Wednesday14:15–15:45')
simple('ot_26','tutorial',[(1,'10:15','11:45')],'E2.4 SR6',freq='approximately fortnightly; dates TBA',first='2026-10-26',evidence='Monday10:15–11:45; approximatelyeverysecondweek')
simple('oscar','seminar',[(1,'10:15','11:45')],'E2.5 SR4',confidence='medium',note='Root first21Oct2026 contradicts Monday weekday (21OctisWednesday); weekly pattern retained with confidence flag.',evidence='Seminar Monday10:15–11:45')
simple('perspectives2627','lecture',[(1,'14:15','15:45')],'E2.5 HS I',first='2026-10-19',note='Attendance possible inperson; recordings available.',evidence='EveryMonday14:15–15:45 starting19.10.2026')
simple('inteq','seminar',[(1,'12:00','14:00')],'E2.4 SR6',conv='st',first='2026-10-26',note='Root recurrentMonday12–14; latestnews starts12:00st inearlyweeks withtwotalks. ICS first8talkshavezeroendduration; later talks12:15–13:15. This is a nominal full-session envelope, not proven physical release.',confidence='medium',evidence='Montag12–14; bei2Vorträgen12:00st')
simple('rmqi_2627','lecture',[(2,'14:00','16:00')],'E2.4 HS IV',conv='unknown',evidence='Tuesdays14–16')
simple('rmqi_2627','lecture',[(5,'10:00','12:00')],'E2.5 Zeichensaal',conv='unknown',evidence='Fridays10–12')
simple('srl26','seminar',[(4,'12:15','13:45')],'E1.7 0.01',evidence='Thursdays12:15–13:45')
simple('komb26','seminar',[(4,'14:00','15:30')],'E2.4 SR10',conv='exact',evidence='Donnerstags14:00–15:30')
simple('statdc26','lecture/tutorial combined',[(3,'14:00','16:00'),(4,'14:00','16:00')],'E2.5 HS II',conv='ct',note='Root explicitlyct. ICS lecture14–16 andtutorial15–16 overlap for same class; merged whole session to avoiddoublecount. Physicalreleaseunknown; nominalend16retained.',evidence='WednesdaysandThursdays14–16ct; eachsessionsplitbetweenlectureandtutorial')
simple('stoch2','lecture',[(2,'10:15','11:45'),(4,'08:30','10:00')],'E2.4 SR6',evidence='Tuesday10:15–11:45; Thursday8:30–10:0')
simple('stoch2','tutorial',[(2,'08:30','10:00')],'E2.4 SR6',first='2026-11-03',evidence='Tuesday8:30–10; first3November')
simple('vgm','lecture',[(1,'16:00','18:00')],'E1.5 R002',conv='st',first='2026-10-19',evidence='Mondays4pm–6pm; starts4pmfromsecondlecture')
simple('vgm','tutorial',[(3,'12:15','14:00')],'E1.4 R024',first='2026-10-21',evidence='Wednesdays12pm–2pm starts12:15')
# Capacity is an upper bound, not actual cohort size; signup count may include nonattenders.
for r in rows:
    if r['course_id']=='hci_2627':r['capacity']='250';r['notes']+=' Course cap250, not actual attendance.'
    if r['course_id']=='dic_26':r['capacity']='40'
    if r['course_id']=='alsa26':r['enrolment']='55 as of2026-10-20';r['notes']+=' Rootnews says55enrolled20Oct, not lectureattendance.'
    r['notes']=r['notes'].replace('doublecount','double count')
rows.sort(key=lambda r:(r['weekday'],r['start_time'],r['course_id'],r['event_type'],r['group_id']))
def writecsv(name,data):
    if not data:return
    with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
writecsv('cms_meetings.csv',rows)
(P/'cms_meetings.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
writecsv('cms_excluded_occurrences.csv',exclusions)
status_notes={
'biostatslab26':'Lectures mapped; Wed14:15/Thu12:15 tutorials have no public end time, omitted.',
'latex_2627':'Block course7–9October, beforeteachingperiod and alreadyover; omitted.',
'emse_26':'All public meetings areonline/asynchronous; excludeddefaultbusdemand.',
'exml_2627':'23Octintroonly; blockdatesTBA, no recurringphysicalpattern.',
'fof_math_ws2627':'SeeLSF; no recurringtimingonCMSpageorcalendar.',
'probing_2627':'No CMS times; externalcurrentseminarpagecoveredbyseminarsresearcher.',
'nnia_2627':'Start20Octandlocationonly; end/weeklytimeabsent; possible sharedNNTImeeting, donotdoublecount.',
'matfunc26':'15Octkickoff12:15; furtherThursdaysbyarrangement, noend/weeklypattern.',
'underwater_2627':'No timed recurringmeetingspubliclyavailableonCMS.',
'taip2627':'Blockseminar;26Oct16–17kickoffonly; finalblockafterteachingperiodTBA.',
'structbioinf':'No timetable publiconCMS.',
'theory_2627':'CMSlinktextcurrent26buthrefprevious25; currentexternalpagecoveredbyseminarresearcher.',
'tds2627':'Block12–16Oct9–17alreadycompleted; notrecurrentafter26Oct.',
'mfi1_mfcs1_wise2627':'Lectures and optionalconsultationsmapped; smallgrouptutorialtimesnotpublicinroot/calendar.',
'mfcs3_wise2627':'Lectures/general tutorialmapped; smallgrouptutorialtimesrequirematerials/access.'}
inventory=[]
for x in items:
    rr=[r for r in rows if r['course_id']==x['id']]
    nn=sum(int(r['include_in_demand']) for r in rr)
    inventory.append(dict(course_id=x['id'],title=x['title'],source_url=x['url'],semester='Winter2026/27',page_status=x['status'],calendar_status=x['calendar_status'],calendar_events=x.get('calendar_events',0),recurring_rows=len(rr),in_demand_rows=nn,coverage_status='timed' if nn else 'excluded_or_unresolved',coverage_notes=status_notes.get(x['id'],'')))
writecsv('cms_source_inventory.csv',inventory)
(P/'cms_coverage_summary.json').write_text(json.dumps(dict(catalog_entries=len(items),root_fetch_success=sum(x['status']=='ok' for x in items),calendar_exports_success=sum(x['calendar_status']=='ics' for x in items),nonempty_calendars=sum(x.get('calendar_events',0)>0 for x in items),raw_calendar_occurrences=len(occ),recurring_rows=len(rows),in_demand_rows=sum(int(r['include_in_demand']) for r in rows),courses_with_in_demand_times=sum(x['in_demand_rows']>0 for x in inventory),excluded_occurrences=len(exclusions),fetch_date='2026-10-26'),indent=2),encoding='utf-8')
print((P/'cms_coverage_summary.json').read_text(encoding='utf-8'))
print('UNRESOLVED',[(x['course_id'],x['coverage_notes']) for x in inventory if not x['in_demand_rows']])
