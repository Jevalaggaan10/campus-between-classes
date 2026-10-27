import puppeteer from 'puppeteer-core';
import { pathToFileURL } from 'node:url';
import { writeFileSync, mkdirSync } from 'node:fs';

mkdirSync('.hallmark',{recursive:true});
const browser = await puppeteer.launch({executablePath:process.env.CHROME_PATH || (process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':process.platform==='darwin'?'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome':'/usr/bin/google-chrome'),headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
const page = await browser.newPage();
const errors=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('requestfailed',r=>console.log(JSON.stringify({failed_request:r.url(),reason:r.failure()?.errorText})));
const checks=[];
const check=(condition,name)=>{if(!condition)throw new Error(name);checks.push(name);};
const clickVisible=async selector=>{await page.$eval(selector,e=>e.scrollIntoView({block:'center',behavior:'instant'}));await page.click(selector);};
try {
  await page.setViewport({width:1440,height:900});
  await page.goto(pathToFileURL(process.cwd()+'/dist/index.html').href,{waitUntil:'networkidle0'});
  await page.evaluate(()=>document.fonts.ready);
  check(await page.evaluate(()=>document.fonts.check('16px "Host Grotesk"')&&document.fonts.check('16px "Atkinson Hyperlegible Mono"')),'Both self-hosted fonts decode');
  check((await page.$$('.pressure-cell')).length===640,'Both heatmaps contain all 640 weekday/time cells');
  check((await page.$$('.week-table tbody tr')).length===5,'Five-day static reference is present');
  check((await page.$$('.service-condition')).length>0,'Lecture-day restrictions are visible in departure results');
  check((await page.$$('#contributor-list li')).length>0,'Initial selection includes its contributing classes');
  for(let day=1;day<=5;day++)for(const direction of ['incoming','outgoing'])for(const band of ['daytime','all','midday']){
    await page.select('#day',String(day));await page.select('#direction',direction);await page.select('#band',band);
    const result=await page.evaluate(({day,direction,band})=>{
      const d=JSON.parse(document.getElementById('timing-data').textContent);
      const options=d.buses.filter(b=>b[0]===day&&b[1]===direction&&(band==='all'||(band==='midday'?b[5]>=660&&b[5]<=900:direction==='incoming'?b[5]>=480&&b[5]<=660:b[5]>=900&&b[5]<=1170))).sort((a,b)=>a[10]-b[10]||a[5]-b[5]||String(a[2]).localeCompare(String(b[2])));
      const expected=options[0];const time=t=>String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0');
      return{actual:document.querySelector('.time-button')?.textContent,expected:expected?(direction==='incoming'?expected[3]:time(expected[5])):undefined,count:document.querySelectorAll('#ranking-body tr').length,total:options.length,route:document.getElementById('plan-in-route').textContent,expectedRoute:d.plans[day-1].to_university_route};
    },{day,direction,band});
    check(result.actual===result.expected&&result.count===Math.min(8,result.total)&&result.route===result.expectedRoute,`Correct ranking and plan: day${day}/${direction}/${band}`);
  }
  await page.select('#day','1');await page.select('#direction','incoming');await page.select('#band','all');
  await clickVisible('#more-results');
  check((await page.$$('#ranking-body tr')).length===16,'Show more extends the ranking');
  await clickVisible('#ranking-body .time-button');
  check(await page.evaluate(()=>document.activeElement.id==='inspector'),'Departure activation moves focus to the inspector');
  check((await page.$eval('#inspect-announcement',e=>e.textContent)).includes('Timing range'),'Inspector selection has a live announcement');
  await clickVisible('#outgoing-map rect[data-day="2"][data-minute="840"]');
  check((await page.$eval('#inspect-title',e=>e.textContent)).includes('Tuesday, 14:05 campus departure'),'Heatmap selection updates the inspector');
  await page.focus('#outgoing-map');await page.keyboard.press('ArrowRight');
  check((await page.$eval('#inspect-time',e=>e.value))==='14:20','Heatmap is keyboard-operable');
  await page.$eval('#inspect-time',e=>{e.value='02:00';e.dispatchEvent(new Event('input',{bubbles:true}));});
  check((await page.$eval('#inspect-time',e=>e.getAttribute('aria-invalid')))==='true','Invalid campus time has an accessible error');
  await page.$eval('#inspect-time',e=>{e.value='15:10';e.dispatchEvent(new Event('input',{bubbles:true}));});
  check((await page.$eval('#inspect-time',e=>e.getAttribute('aria-invalid')))==='false','Valid campus time recovers the result state');
  await page.evaluate(()=>document.querySelector('#complete-report').open=true);
  for(const width of [320,375,414,768,1024,1440,1920]){
    await page.setViewport({width,height:900});
    await new Promise(resolve=>setTimeout(resolve,60));
    const metrics=await page.evaluate(()=>({inner:innerWidth,body:document.body.scrollWidth,document:document.documentElement.scrollWidth}));
    check(metrics.body<=width+1&&metrics.document<=width+1,`No horizontal page overflow with expanded report: ${width}px`);
  }
  await page.emulateMediaFeatures([{name:'prefers-reduced-motion',value:'reduce'}]);
  check(await page.evaluate(()=>getComputedStyle(document.querySelector('.heat-row')).animationName==='none'),'Reduced motion disables chart animation');
  await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  await new Promise(resolve=>setTimeout(resolve,100));
  check((await page.$$('nav a[aria-current]')).length===0,'Navigation selection clears above the observed sections');
  await page.goto(pathToFileURL(process.cwd()+'/dist/index.html').href+'?day=2&direction=outgoing&time=14:05',{waitUntil:'networkidle0'});
  check((await page.$$('#contributor-list li')).length>0&&(await page.$eval('#inspect-title',e=>e.textContent)).includes('Tuesday, 14:05'),'Shared URL restores contributing classes and selected time');
  const navigation=await page.evaluate(()=>{const n=performance.getEntriesByType('navigation')[0];return {dom_ready_ms:Math.round(n.domContentLoadedEventEnd),load_ms:Math.round(n.loadEventEnd)};});
  check(errors.length===0,'No JavaScript runtime errors');
  const report={passed:checks.length,checks,errors,local_file_navigation:navigation};
  writeFileSync('.hallmark/interaction-checks.json',JSON.stringify(report,null,2));
  console.log(JSON.stringify({passed:checks.length,errors,navigation}));
} finally {await browser.close();}
