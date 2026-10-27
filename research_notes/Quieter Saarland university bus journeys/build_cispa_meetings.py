from pathlib import Path
import csv,json,re,collections,hashlib,datetime
b=Path(__file__).resolve().parent
inv=json.loads((b/'cispa_inventory.json').read_text(encoding='utf-8'))
catalog={x['url'].rstrip('/').split('/')[-1]:x for x in inv if x['group']=='cispa_catalog'}
rows=[]
def add(cid,day,start,end,kind='seminar',location='TBA',conv='unknown',frequency='weekly',first='',last='',dates='',note='',url=None,title=None,evidence='',mode='in_person',capacity=''):
 source=url or catalog[cid]['url']; title=title or catalog[cid]['title']
 rows.append(dict(source_group='cispa_and_seminars',course_id=cid,title=title,event_type=kind,weekday=day,start_time=start,end_time=end,time_convention=conv,location=location,campus='Saarbrücken',semester='2026/27 winter',first_date=first,last_date=last,frequency=frequency,source_url=source,evidence_snippet=evidence or f'{kind} scheduled {start}–{end}; weekday {day}.',confidence='medium' if conv=='unknown' or frequency=='irregular' or mode=='unknown' else 'high',notes=note,occurrence_dates=dates,attendance_mode=mode,seminar_assigned_places_capacity=capacity))
add('farwsp2627',1,'10:00','12:00','lecture','E9 1, 0.05',conv='ct',first='2026-10-19',note='Nominal c.t.; keep time uncertainty in model. No public ICS occurrences.')
ipml='https://muandet-lab.github.io/ipml-course/2026-2027/'
add('ipml',5,'10:00','12:00','lecture','CISPA C0 0.05',url=ipml,first='2026-10-16',mode='hybrid',note='UdS, Hamburg and online locations; physical UdS attendance unknown.')
add('ipml',5,'12:00','14:00','exercise','CISPA C0 0.05',url=ipml,frequency='biweekly',mode='hybrid',note='Biweekly exercise phase not inferred; do not count as every Friday.')
add('lfa',2,'14:15','16:00','lecture','E9 1, 0.05',first='2026-10-13',note='Recurring schedule says Tue14:00; welcome notice gives14:15–16:00. No teaching9–15Nov or21Dec–3Jan.')
add('lfa',4,'14:00','17:00','exercise','E9 1, 0.05',first='2026-10-15',note='Welcome notice extends exercise session by one hour for clashes. Main recurring schedule says Thu14:00 without end. No teaching9–15Nov/21Dec–3Jan.')
add('scad2627',2,'10:00','12:00','lecture','E9 1, 0.05',conv='ct',first='2026-10-20',note='Main page explicitly c.t.; ICS stores10:00–12:00. Calendar boundaries are nominal.')
add('syssec_26',5,'14:00','16:00','lecture','CISPA C0 0.05',conv='ct',first='2026-10-23',mode='hybrid',note='Notice explicitly says starts14:15; scheduled end16:00 retained.200 registrations total,170 UdS; hall90 seats, online encouraged. Enrollment is not attendance or bus use.')
add('syssec_26',1,'14:00','16:00','tutorial','CISPA C0 0.05',first='2026-10-26',mode='hybrid',note='Online participation possible; actual attendance unknown.')
add('cysec1_2627',2,'10:15','11:45','lecture','E2 2 GHH',conv='exact',first='2026-10-13')
add('cysec1_2627',4,'14:15','15:45','lecture','E1 3 HS0.01',conv='exact',first='2026-10-15',last='2026-12-03',note='Course topic plan ends Thursday lectures after December3; subsequent teaching Tuesdays only.22Oct lecture cancelled;17Nov Tuesday cancelled.')
for d,s,e,loc in [(1,'10:15','11:45','E9.1 0.02'),(1,'12:15','13:45','E9.1 0.05'),(5,'12:15','13:45','E9.1 0.02')]:
 add('cysec1_2627',d,s,e,'tutorial',loc,conv='exact',note='Public ICS precise boundaries supersede nominal page slots;23/26Oct temporarily office hours. Friday10–12 slot was moved to Monday12–14.')
for d in (1,3):add('sec2627',d,'12:15','13:45','lecture','E2.2 GHH',conv='exact')
for d,s,e,loc in [(1,'10:00','12:00','E9 1 0.07'),(3,'16:00','18:00','E1 3 SR016'),(3,'10:00','12:00','E1 3 SR016'),(5,'10:00','12:00','E9 1 0.07'),(2,'10:00','12:00','E9 1 0.07')]:add('sec2627',d,s,e,'tutorial',loc,note='Nominal two-hour interval on source, exact academic quarter unspecified.')
add('sec2627',1,'16:00','18:00','office_hour','E1 3 SR013',note='Optional office hour; keep separate from regular class demand.')
add('usld',2,'10:00','12:00','proseminar','CISPA C0',first='2026-10-20',note='ICS includes zero-length critique deadlines; exclude all deadlines from physical demand.')
add('algseminar_26',2,'16:00','17:30',location='TBA',note='Public course says Tuesday16–17:30; location TBA.',mode='unknown')
add('orgsec26',2,'10:15','11:45',location='TBA',conv='exact',frequency='irregular',first='2026-10-20',mode='unknown',note='Explicit irregular Tuesday meetings, exact dates to be discussed; weekly upper-envelope only.')
add('aos_wise26',3,'16:15','18:00',location='CISPA C0 0.07',conv='exact',frequency='irregular',first='2026-10-28',last='2027-01-27',dates='2026-10-28;2026-11-04;2026-11-11;2026-11-25;2026-12-02;2026-12-09;2026-12-16;2027-01-27',note='Specific schedule dates; no meeting18Nov,6/13/20Jan.14Oct kickoff and3Mar block excluded.')
add('htai',2,'14:00','17:00',location='CISPA C0 0.02',conv='exact',frequency='irregular',first='2026-10-27',last='2027-01-26',dates='2026-10-27;2026-11-24;2026-12-01;2026-12-15;2027-01-12;2027-01-19;2027-01-26',note='Main page weekly-sounding slot but dated table has no meetings3/10/17Nov,8Dec,5Jan,2Feb.20Oct kickoff excluded.')
add('psas26',3,'09:00','11:00',location='CISPA C0',note='News26Oct warns possible schedule shift; exact dates/rooms behind material link. Tentative.')
add('robgenai',4,'10:15','11:45',location='CISPA C0 rooms0.02/0.05/0.07',conv='exact',frequency='irregular',first='2026-11-05',last='2026-12-17',dates='2026-11-05;2026-11-12;2026-11-19;2026-11-26;2026-12-03;2026-12-17',note='Use dated table over nominal Thu10–12. No29Oct/10Dec/7Jan.')
add('robgenai',4,'10:00','12:00',location='CISPA C0 rooms0.02/0.07',conv='exact',frequency='irregular',first='2027-01-14',last='2027-01-28',dates='2027-01-14;2027-01-21;2027-01-28',note='January proposal presentation dates only.')
add('spacesecurity2627',5,'09:00','11:00',location='CISPA C0 0.07',first='2026-10-30',last='2026-12-11',note='Source says seven consecutive weekly meetings from30Oct; first is kickoff, later six are regular.')
add('tml26',5,'14:00','16:00',location='CISPA C0 0.02',first='2026-10-16',mode='hybrid',note='Tentative;13Nov moves16–18,20Nov moves12–14. Some December/January sessions online. Do not assume physical every Friday.')
add('websecsem_wise26',3,'14:00','16:00',location='CISPA C0 0.07',frequency='irregular',first='2026-10-28',last='2027-01-27',dates='2026-10-28;2026-11-04;2026-11-11;2026-11-25;2026-12-02;2026-12-09;2026-12-16;2027-01-13;2027-01-20;2027-01-27',note='Dated table14–16 conflicts prose14:15–16 and typo28.19.2026. Use uncertain starts. Seminar/proseminar same meeting group, count once.')
# Non-CMS source supplements. CMS-root duplicates should be reconciled by parent.
semurl='https://seminars.cs.uni-saarland.de/wise2627seminars'
extras=[
 ('hai_ws26','Advances in Hybrid Artificial Intelligence',2,'16:15','18:00','DFKI NB +2.31 Turing2','2026-11-24','https://www.dfki.de/~klusch/HAI-seminar-ws26',8,'Topical sessions start24Nov;20Oct introductory meeting excluded.'),
 ('aqai_ws26','Advances in Quantum Artificial Intelligence',4,'16:15','18:00','DFKI NB +2.31 Turing2','2026-11-26','https://www.dfki.de/~klusch/AQAI-seminar-ws26',8,'Topical sessions start26Nov;22Oct introductory meeting excluded.'),
 ('human_oversight_goodwork','Designing Human Oversight of AI for Good Work',1,'14:00','16:00','TBA','',semurl,20,'Mandatory in-person Monday2–4PM from official seminar listing; reconcile CMS equivalent if present.'),
 ('human_mind','Foundation Models of the Human Mind',4,'10:00','12:00','TBA','',semurl,20,'Location not given; campus attendance mode unconfirmed.'),
 ('game_agents','Game Development with Agents',2,'10:00','12:00','TBA','',semurl,6,'Reconcile CMS sem_agents; source confirms meeting slot but location unspecified.'),
 ('cocreativity','Human-AI Co-Creativity',2,'10:00','12:00','TBA','',semurl,6,'Location not given; actual campus attendance unconfirmed.'),
 ('imi_ar','Intelligent Multimodal Interaction in Augmented Reality',4,'10:00','11:30','TBA','2026-10-22',semurl,10,'Location not given; kickoff22Oct, subsequent recurring slot.'),
 ('llm_posttraining','Selected Topics in LLM Post-training',5,'15:00','17:00','TBA','',semurl,8,'Seminar page TBA; slot explicitly in official listing. Physical location unconfirmed.'),
 ('probing_2627','Interpreting and Analyzing Neural Language Models',2,'14:15','15:45','C7.3 R1.14','2026-10-27','https://lacoco-lab.github.io/courses/interpreting-2026',12,'Current official chair page; CMS probing_2627 has no public times. Syllabus through19Jan;20Oct no class.'),
 ('theory_2627','Theoretical Abilities and Limitations of Language Models',5,'12:15','13:45','C7.3 R1.14','2026-10-16','https://lacoco-lab.github.io/courses/theory-26/',8,'Current page has 2026/27 syllabus; CMS link text points current but href incorrectly previous year.23Oct no class.')]
for cid,title,d,s,e,loc,first,url,cap,note in extras:
 add(cid,d,s,e,location=loc,first=first,url=url,title=title,note=note,mode='unknown' if loc=='TBA' and cid!='human_oversight_goodwork' else 'in_person',capacity=cap,conv='exact' if s.endswith(':15') else 'unknown')
# Status inventory records all index entries, including timing gaps.
alias={'Automata Learning':'alprosem26','Computer Architecture':'comparch_w26','Does Copilot':'se_seminar_ws_2627','Living AI-ducation':'living_aiducation','Privacy Systems':'psas26','Real-Time Control':'underwater_2627','The Web Security':'websecsem_wise26','Usable Security':'usld','Hack a SAT':'hackasat','Advances in Hybrid':'hai_ws26','Advances in Quantum':'aqai_ws26','Designing Human':'human_oversight_goodwork','Foundation Models of':'human_mind','Game Development':'game_agents','Human-AI Co-Creativity':'cocreativity','Intelligent Multimodal':'imi_ar','Selected Topics in LLM':'llm_posttraining','Interpreting and Analyzing':'probing_2627','Theoretical Abilities':'theory_2627','Causal XAI':'causxai','Representation Learning':'srl26','Data and Society':'das_26','Nature-Inspired':'nio26'}
for root,x in catalog.items():
 alias.setdefault(x['title'],root)
count=collections.Counter(x['course_id'] for x in rows)
cms_ids={x.get('id'):x for x in json.loads((b/'cms_inventory.json').read_text(encoding='utf-8'))} if (b/'cms_inventory.json').exists() else {}
for x in inv:
 title=x['title'].split(' by ')[0].strip()
 cid=next((v for k,v in alias.items() if title.startswith(k)),None)
 if cid is None:
  for k,v in cms_ids.items():
   if title.lower().strip()==v['title'].lower().strip():cid=k;break
 if cid is None:cid=re.sub(r'[^a-z0-9]+','_',title.lower()).strip('_')
 x['canonical_course_id']=cid;x['semester']='2026/27 winter'
 x['canonical_url']='https://cms.cispa.saarland/'+cid+'/' if cid in catalog else (x.get('links') or [x['url']])[0]
 if count[cid]:status='recurring_or_irregular_timed'
 elif cid in ['cysecproj2627','alprosem26','bms_winter2627']:status='one_off_or_date_only_no_recurring_time'
 elif cid=='nio26':status='online_only_recurring'
 elif cid in ['dle26','ppmlo2627'] or 'block' in x['description'].lower():status='block_or_kickoff_not_weekly'
 elif cid in cms_ids:status='SIC_CMS_researcher_coverage'
 else:status='no_public_recurring_time_found'
 x['timing_status']=status
 # Do not dump copyrighted full descriptions into exported audit inventory.
 x['timing_evidence']='; '.join(re.findall(r'[^.!?]*(?:Monday|Tuesday|Wednesday|Thursday|Friday|block|TBA)[^.!?]*(?:[.!?]|$)',x['description']))[:700]
fields=list(rows[0])
with (b/'cispa_meetings.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
exportfields=['group','title','canonical_course_id','canonical_url','semester','url','capacity','timing_status','timing_evidence']
with (b/'cispa_course_inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=exportfields,extrasaction='ignore');w.writeheader();w.writerows(inv)
(b/'cispa_inventory_enriched.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'catalog_entries':len(inv),'cispa_catalog_entries':len(catalog),'seminar_entries':50,'proseminar_entries':9,'canonical_course_ids':len(set(x['canonical_course_id'] for x in inv)),'meeting_pattern_rows':len(rows),'courses_with_meeting_rows':len(count),'cispa_courses_with_timed_rows':len(set(catalog)&set(count)),'status_counts_by_entry':dict(collections.Counter(x['timing_status'] for x in inv))}
(b/'cispa_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
