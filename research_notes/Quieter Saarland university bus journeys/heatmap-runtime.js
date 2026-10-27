
(function(){
'use strict';
const root=document.getElementById('saarland-timing-map');
const data=JSON.parse(document.getElementById('timing-data').textContent);
const days=['Monday','Tuesday','Wednesday','Thursday','Friday'];
const shortDays=['Mon','Tue','Wed','Thu','Fri'];
const ns='http://www.w3.org/2000/svg';
const dayEl=root.querySelector('#day'),dirEl=root.querySelector('#direction'),bandEl=root.querySelector('#band'),timeEl=root.querySelector('#inspect-time');
let selectedDay=1,selectedDirection='incoming',selectedTime=563;
const formatTime=function(t){return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0');};
const formatScore=function(x){return x.toFixed(1);};
const svgEl=function(name,attrs,text){const e=document.createElementNS(ns,name);Object.keys(attrs||{}).forEach(function(k){e.setAttribute(k,attrs[k]);});if(text!==undefined)e.textContent=text;return e;};
const tri=function(x,left,peak,right){if(x<=left||x>=right)return 0;return x<=peak?(x-left)/(peak-left):(right-x)/(right-peak);};
const pressure=function(row,t,dir,scenario){const start=row[scenario===0?2:4],end=row[scenario===0?3:5];return row[6]*(dir==='incoming'?tri(start-t,-10,10,35):tri(t-end,-5,10,40));};
const calc=function(day,t,dir){let a=0,b=0;data.meetings.forEach(function(r){if(r[1]===day){a+=pressure(r,t,dir,0);b+=pressure(r,t,dir,1);}});return {central:(a+b)/2,low:Math.min(a,b),high:Math.max(a,b)};};
root.querySelector('#coverage').textContent=data.summary.courses+' timed courses · '+data.summary.patterns+' meeting patterns · Winter 2026/27. Ordinary-week profile, 26 Oct–5 Feb (Christmas break excluded). Class pressure estimate; actual bus occupancy is unknown.';
function drawPlot(direction){
 const box=root.querySelector('#'+direction+'-plot'),width=box.clientWidth||640,height=218;
 const left=60,right=10,top=12,bottom=45,plotW=Math.max(220,width-left-right),rowH=(height-top-bottom)/5;
 const svg=svgEl('svg',{viewBox:'0 0 '+width+' '+height,width:'100%',height:height,role:'img','aria-label':direction==='incoming'?'Weekday heatmap of class start pressure at campus arrival times':'Weekday heatmap of class ending pressure at campus departure times'});
 svg.appendChild(svgEl('title',{},direction==='incoming'?'Campus arrivals before class starts':'Campus departures after class endings'));
 let cells=[],max=0;
 for(let day=1;day<=5;day++)for(let j=0;j<64;j++){
  const vals=data.vectors.filter(function(v){return v[0]===day&&v[1]>=360+j*15&&v[1]<375+j*15;});
  const value=vals.reduce(function(s,v){return s+v[direction==='incoming'?2:3];},0)/Math.max(1,vals.length);
  cells.push({day:day,j:j,value:value});max=Math.max(max,value);
 }
 cells.forEach(function(c){const rect=svgEl('rect',{x:left+c.j*plotW/64,y:top+(c.day-1)*rowH,width:plotW/64+.2,height:rowH-2,fill:'var(--chart-1)',opacity:.035+.965*c.value/Math.max(1,max)});svg.appendChild(rect);});
 for(let i=0;i<5;i++)svg.appendChild(svgEl('text',{x:left-8,y:top+i*rowH+rowH/2+4,'text-anchor':'end'},shortDays[i]));
 svg.appendChild(svgEl('text',{x:12,y:top+rowH*2.5,transform:'rotate(-90 12 '+(top+rowH*2.5)+')','text-anchor':'middle','class':'axis-title','data-axis':'y'},'Weekday'));
 const ticks=width<430?[360,840,1320]:[360,600,840,1080,1320];
 ticks.forEach(function(t){svg.appendChild(svgEl('text',{x:left+(t-360)/960*plotW,y:height-23,'text-anchor':t===360?'start':t===1320?'end':'middle'},formatTime(t)));});
 svg.appendChild(svgEl('text',{x:left,y:height-5,'text-anchor':'start','class':'axis-title','data-axis':'x'},'Local campus time'));
 svg.appendChild(svgEl('text',{x:left+plotW,y:height-5,'text-anchor':'end'},'Peak '+formatScore(max)));
 if(selectedDirection===direction){const j=Math.min(63,Math.max(0,Math.floor((selectedTime-360)/15)));svg.appendChild(svgEl('rect',{x:left+j*plotW/64,y:top+(selectedDay-1)*rowH,width:plotW/64,height:rowH-2,fill:'none',stroke:'var(--foreground)','stroke-width':1.5}));}
 const hit=svgEl('rect',{x:left,y:top,width:plotW,height:5*rowH,fill:'transparent','data-chart-hit':'true'});
 hit.addEventListener('click',function(e){const b=svg.getBoundingClientRect(),x=(e.clientX-b.left)*width/b.width,y=(e.clientY-b.top)*height/b.height;selectedDay=Math.max(1,Math.min(5,Math.floor((y-top)/rowH)+1));selectedTime=360+Math.max(0,Math.min(63,Math.floor((x-left)/plotW*64)))*15+5;selectedDirection=direction;sync();});svg.appendChild(hit);
 box.replaceChildren(svg);
}
function renderRanks(){
 const dir=selectedDirection,band=bandEl.value;
 const opts=data.buses.filter(function(b){if(b[0]!==selectedDay||b[1]!==dir)return false;const t=b[5];if(band==='all')return true;if(band==='midday')return t>=660&&t<=900;return dir==='incoming'?(t>=480&&t<=660):(t>=900&&t<=1170);});
 const levels=Array.from(new Set(opts.map(function(b){return b[10];}))).sort(function(a,b){return a-b;});
 opts.sort(function(a,b){return a[10]-b[10]||a[5]-b[5]||String(a[2]).localeCompare(String(b[2]));});
 const head=root.querySelector('#ranking-head');head.innerHTML='';const hr=document.createElement('tr');
 ['Rank','Bus',dir==='incoming'?'HTW dep.':'Campus dep.',dir==='incoming'?'Campus arr.':'HTW arr.','Timing range'].forEach(function(s){const th=document.createElement('th');th.scope='col';th.textContent=s;hr.appendChild(th);});head.appendChild(hr);
 const body=root.querySelector('#ranking-body');body.innerHTML='';
 opts.slice(0,6).forEach(function(b){const tr=document.createElement('tr');const rank=levels.indexOf(b[10])+1;const cells=['='+rank,b[2],dir==='incoming'?b[3]:formatTime(b[5]),dir==='incoming'?formatTime(b[5]):b[3],formatScore(b[8])+'–'+formatScore(b[9])];
 cells.forEach(function(s,i){const td=document.createElement('td');if(i===2){const button=document.createElement('button');button.type='button';button.textContent=s;button.setAttribute('aria-label','Inspect bus '+b[2]+' at campus '+formatTime(b[5]));button.addEventListener('click',function(){selectedTime=b[5];sync();});td.appendChild(button);}else td.textContent=s;tr.appendChild(td);});body.appendChild(tr);});
 root.querySelector('#rank-caption').textContent=days[selectedDay-1]+' · '+(band==='all'?'all modelled times':band==='midday'?'campus times 11:00–15:00':dir==='incoming'?'campus arrival 08:00–11:00':'campus departure 15:00–19:30')+' · '+opts.length+' verified direct HTW/SWS options, showing the first '+Math.min(6,opts.length)+'. Sorted by the higher timing scenario; 0.1-point ties retained.';
}
function renderDetails(){
 const s=calc(selectedDay,selectedTime,selectedDirection);
 root.querySelector('#selection-label').textContent=days[selectedDay-1]+' '+formatTime(selectedTime)+' · '+(selectedDirection==='incoming'?'arriving at campus':'leaving campus');
 root.querySelector('#selection-score').textContent='Class pressure '+formatScore(s.central)+'; timing sensitivity '+formatScore(s.low)+'–'+formatScore(s.high)+'.';
 const contributions=data.meetings.filter(function(r){return r[1]===selectedDay;}).map(function(r){return {row:r,score:(pressure(r,selectedTime,selectedDirection,0)+pressure(r,selectedTime,selectedDirection,1))/2};}).filter(function(x){return x.score>.001;}).sort(function(a,b){return b.score-a.score;});
 const list=root.querySelector('#contributors');list.innerHTML='';
 if(!contributions.length){const li=document.createElement('li');li.textContent='No collected class contributes inside this model’s buffer. This does not mean an empty bus.';list.appendChild(li);}
 contributions.slice(0,5).forEach(function(c){const r=c.row,course=data.courses[r[0]],li=document.createElement('li'),a=document.createElement('a');a.href=course[1];a.target='_blank';a.rel='noopener';a.textContent=course[0];li.appendChild(a);li.appendChild(document.createTextNode(' · '+formatTime(r[2])+'–'+formatTime(r[3])+' · '+r[8]+(r[7]?' · '+r[7]:'')));list.appendChild(li);});
 if(contributions.length>5){const li=document.createElement('li');li.className='small secondary';li.textContent='+'+(contributions.length-5)+' other contributing meeting patterns.';list.appendChild(li);}
}
function sync(){dayEl.value=String(selectedDay);dirEl.value=selectedDirection;timeEl.value=formatTime(selectedTime);drawPlot('incoming');drawPlot('outgoing');renderRanks();renderDetails();}
dayEl.addEventListener('change',function(){selectedDay=Number(dayEl.value);sync();});
dirEl.addEventListener('change',function(){selectedDirection=dirEl.value;selectedTime=selectedDirection==='incoming'?563:920;sync();});
bandEl.addEventListener('change',renderRanks);
timeEl.addEventListener('input',function(){const v=timeEl.value.split(':').map(Number);if(v.length===2&&v.every(Number.isFinite)){selectedTime=Math.max(360,Math.min(1320,v[0]*60+v[1]));drawPlot('incoming');drawPlot('outgoing');renderDetails();}});
let resizeTimer;new ResizeObserver(function(){clearTimeout(resizeTimer);resizeTimer=setTimeout(function(){drawPlot('incoming');drawPlot('outgoing');},30);}).observe(root);
sync();
})();
