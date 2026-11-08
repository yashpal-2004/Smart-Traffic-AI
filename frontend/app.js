const API = window.TRAFFIC_API_URL || 'http://127.0.0.1:8000/api';
const $ = (id) => document.getElementById(id);
let runId = null;
let timer = null;
let snapshot = null;
let episode = 0;
let seed = Math.floor(Math.random() * 9000) + 1000;
let latestReport = null;

function toast(message) {
  const node = $('toast'); node.textContent = message; node.classList.add('show');
  setTimeout(() => node.classList.remove('show'), 2600);
}
async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, { headers: {'Content-Type':'application/json'}, ...options });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return response.json();
}
function showSnapshot(data) {
  snapshot = data;
  for (const direction of ['north','east','south','west']) {
    const count = data.queues[direction] || 0;
    $(`queue-${direction}`).textContent = count;
    $(`load-${direction}`).textContent = count;
    $(`bar-${direction}`).style.width = `${Math.min(100, count * 8)}%`;
    drawCars(direction, count);
  }
  const total = Object.values(data.queues).reduce((a,b)=>a+b,0);
  $('served-metric').textContent = data.served;
  $('wait-metric').textContent = data.average_wait_seconds.toFixed(1);
  $('queue-metric').textContent = total;
  $('peak-metric').textContent = data.max_queue;
  $('sim-time').textContent = `${String(Math.floor(data.time/60)).padStart(2,'0')}:${String(data.time%60).padStart(2,'0')}`;
  $('phase-duration').textContent = `${data.phase_elapsed}s`;
  $('phase-label').textContent = phaseName(data.phase);
  $('decision-phase').textContent = phaseName(data.phase);
  $('seed-label').textContent = seed;
  $('episode-number').textContent = String(episode).padStart(3,'0');
  const ns = data.phase === 'north_south';
  document.querySelectorAll('#signal-ns .lamp').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('#signal-ew .lamp').forEach(x=>x.classList.remove('on'));
  const active = data.transitioning ? 'amber' : 'green';
  const other = data.transitioning ? 'amber' : 'red';
  document.querySelector(`#signal-ns .lamp.${ns ? active : other}`).classList.add('on');
  document.querySelector(`#signal-ew .lamp.${ns ? other : active}`).classList.add('on');
  $('phase-arrows').textContent = ns ? '↕' : '↔';
  $('decision-note').textContent = data.transitioning ? 'Amber transition · vehicles stopped' : 'Serving active approaches';
  const names={fixed_time:'Fixed-time baseline',q_learning:'Hold/switch Q-learning',duration_q_learning:'Green-duration Q-learning'};
  $('policy-name').textContent = names[data.controller] || data.controller;
  $('policy-desc').textContent = data.controller === 'fixed_time' ? 'Cycles between phases on a fixed schedule.' : data.controller === 'duration_q_learning' ? 'Selects a target green duration using its learned policy.' : 'Chooses to hold or switch using its learned Q-table.';
  if(data.controller==='duration_q_learning' && data.green_target){$('decision-note').textContent=`Chosen green target · ${data.green_target}s`}
  $('run-state').classList.toggle('running', !data.paused);
  $('run-state').innerHTML = `<i></i> ${data.paused ? 'PAUSED' : 'RUNNING'}`;
  $('run-button').innerHTML = data.paused ? '<span class="play-icon">▶</span> Resume simulation' : '<span>Ⅱ</span> Pause simulation';
  $('served-progress').style.width = `${Math.min(100, data.served / 3)}%`;
  drawHistory(data.history || []);
}
function phaseName(phase) { return phase === 'north_south' ? 'North ↔ South' : 'East ↔ West'; }
function drawCars(direction, count) {
  const group = $(`cars-${direction}`); group.replaceChildren();
  const colors = ['#53d4b1','#79a9ef','#e9b45f','#df8291','#b89aed'];
  const positions = {
    north: i => [275 + (i%2)*24, 14 + Math.floor(i/2)*24, 15, 24],
    south: i => [330 - (i%2)*24, 402 - Math.floor(i/2)*24, 15, 24],
    west: i => [8 + Math.floor(i/2)*25, 180 + (i%2)*26, 24, 15],
    east: i => [588 - Math.floor(i/2)*25, 225 - (i%2)*26, 24, 15]
  };
  for(let i=0;i<Math.min(count,12);i++){
    const [x,y,w,h]=positions[direction](i); const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('x',x);rect.setAttribute('y',y);rect.setAttribute('width',w);rect.setAttribute('height',h);rect.setAttribute('rx','4');rect.setAttribute('class','car');rect.setAttribute('fill',colors[i%colors.length]);group.append(rect);
  }
}
function drawHistory(history) {
  const svg = $('history-chart'); svg.replaceChildren();
  const ns='http://www.w3.org/2000/svg', width=800, height=160, left=35, top=12, plotW=750, plotH=118;
  const line=(x1,y1,x2,y2,cls)=>{const el=document.createElementNS(ns,'line');Object.entries({x1,y1,x2,y2,class:cls}).forEach(([k,v])=>el.setAttribute(k,v));svg.append(el)};
  [0,.5,1].forEach(t=>line(left,top+t*plotH,left+plotW,top+t*plotH,'grid-line'));
  if(history.length<2){const label=document.createElementNS(ns,'text');label.setAttribute('x','400');label.setAttribute('y','88');label.setAttribute('text-anchor','middle');label.textContent='Step the simulation to see history';svg.append(label);return}
  const maxQ=Math.max(5,...history.map(x=>x.queue)), maxW=Math.max(5,...history.map(x=>x.wait));
  const pts=history.map((x,i)=>[left+i/(history.length-1)*plotW,top+plotH-(x.queue/maxQ)*plotH]);
  const waitPts=history.map((x,i)=>[left+i/(history.length-1)*plotW,top+plotH-(x.wait/maxW)*plotH]);
  const path=(points,cls,area=false)=>{const el=document.createElementNS(ns,'path');const d=points.map((p,i)=>`${i?'L':'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')+(area?` L${points.at(-1)[0]},${top+plotH} L${points[0][0]},${top+plotH} Z`:'');el.setAttribute('d',d);el.setAttribute('class',cls);svg.append(el)};
  path(pts,'queue-area',true);path(pts,'queue-line');path(waitPts,'wait-line');
}
async function createRun() {
  stopTimer();
  seed = Math.floor(Math.random() * 9000) + 1000;
  episode++;
  const data = await request('/runs',{method:'POST',body:JSON.stringify({scenario:$('scenario').value,controller:$('controller').value,seed})});
  runId=data.id;showSnapshot(data);
}
async function doStep(steps=1) {
  if(!runId) await createRun();
  const data=await request(`/runs/${runId}/step`,{method:'POST',body:JSON.stringify({steps})});showSnapshot(data);
}
function stopTimer(){if(timer){clearInterval(timer);timer=null}}
async function runLoop(){
  if(!runId) await createRun();
  if(snapshot?.paused){const data=await request(`/runs/${runId}/control/resume`,{method:'POST'});showSnapshot(data)}
  stopTimer();timer=setInterval(()=>doStep(1).catch(e=>{stopTimer();toast(e.message)}),180);
}
async function pause(){stopTimer();if(runId){const data=await request(`/runs/${runId}/control/pause`,{method:'POST'});showSnapshot(data)}}
$('run-button').addEventListener('click',()=> (snapshot&&!snapshot.paused ? pause():runLoop()).catch(e=>toast(e.message)));
$('step-button').addEventListener('click',()=>doStep().catch(e=>toast(e.message)));
$('reset-button').addEventListener('click',async()=>{stopTimer();try{if(!runId)await createRun();const data=await request(`/runs/${runId}/control/reset`,{method:'POST'});showSnapshot(data)}catch(e){toast(e.message)}});
$('scenario').addEventListener('change',()=>createRun().catch(e=>toast(e.message)));
$('controller').addEventListener('change',()=>createRun().catch(e=>toast(e.message)));
$('compare-button').addEventListener('click',async()=>{
  const selected=[...$('compare-scenarios').selectedOptions].map(o=>o.value);
  $('compare-button').disabled=true;$('compare-button').textContent='Evaluating…';
  try{const report=await request('/evaluations',{method:'POST',body:JSON.stringify({scenarios:selected,seeds:[101,202,303],steps:Number($('compare-steps').value)})});renderReport(report)}catch(e){toast(e.message)}finally{$('compare-button').disabled=false;$('compare-button').textContent='Run evaluation'}
});
$('train-button').addEventListener('click',async()=>{
  const button=$('train-button');button.disabled=true;button.textContent='Training…';
  $('training-progress').classList.remove('hidden');$('training-status').textContent='Training policy…';
  try{
    await request('/training',{method:'POST',body:JSON.stringify({episodes:500,steps:500})});
    let status;
    do{
      await new Promise(resolve=>setTimeout(resolve,500));status=await request('/training');
      $('training-count').textContent=`${status.completed} / ${status.total} episodes`;
      $('training-bar').style.width=`${status.total?100*status.completed/status.total:0}%`;
      $('training-status').textContent=status.status==='running'?'Training policy…':status.status==='queued'?'Starting training…':'Training policy…';
    }while(['queued','running'].includes(status.status));
    if(status.status==='failed')throw new Error(status.error||'Training failed');
    toast(`Training complete · ${status.states} states learned`);$('training-status').textContent='Training complete';await createRun();
  }catch(e){toast(e.message);$('training-status').textContent='Training failed'}
  finally{button.disabled=false;button.textContent='Train Q-learning'}
});
function renderReport(report){
 latestReport=report;
 const target=$('compare-results');target.replaceChildren();
 const toolbar=document.createElement('div');toolbar.className='results-toolbar';
 const quality=document.createElement('span');quality.textContent=report.protocol.trained_policy?`Trained policy · ${report.protocol.model_state_count} learned states`:'Untrained policy · train before interpreting model performance';
 const exportButton=document.createElement('button');exportButton.className='export-button';exportButton.textContent='Export episode CSV';exportButton.addEventListener('click',exportEpisodes);
 toolbar.append(quality,exportButton);target.append(toolbar);
 const bars=document.createElement('div');bars.className='comparison-bars';
 for(const [label,key] of [['Mean served wait','average_wait_seconds'],['Mean queue length','average_queue_length'],['Mean vehicles served','vehicles_served']]){
   const card=document.createElement('div');card.className='comparison-bar';const heading=document.createElement('div');heading.className='comparison-bar-label';heading.textContent=label;card.append(heading);
   const max=Math.max(1,...Object.values(report.summary).map(x=>x[key].mean));
   for(const [name,colorClass,label] of [['fixed_time','','Fixed'],['q_learning','q','Hold/switch'],['duration_q_learning','duration','Duration']]){if(!report.summary[name])continue;const row=document.createElement('div');row.className=`bar-row ${colorClass}`;const labelNode=document.createElement('span');labelNode.textContent=label;const bar=document.createElement('i');bar.style.width=`${Math.max(2,report.summary[name][key].mean/max*75)}%`;const value=document.createElement('span');value.textContent=report.summary[name][key].mean.toFixed(1);row.append(labelNode,bar,value);card.append(row)}bars.append(card)
 }
 target.append(bars);const grid=document.createElement('div');grid.className='results-grid';
 const names={fixed_time:'Fixed-time baseline',q_learning:'Hold/switch Q-learning',duration_q_learning:'Green-duration Q-learning'};
 for(const [name,m] of Object.entries(report.summary)){const col=document.createElement('article');col.className='result-column';const title=document.createElement('h3');title.textContent=names[name]||name;col.append(title);
  const rows=[['Mean served wait',`${m.average_wait_seconds.mean.toFixed(2)} s`],['Median served wait',`${m.average_wait_seconds.median.toFixed(2)} s`],['Mean queue length',m.average_queue_length.mean.toFixed(2)],['Mean vehicles served',m.vehicles_served.mean.toFixed(1)],['Episodes',m.sample_count]];
  rows.forEach(([label,value])=>{const row=document.createElement('div');row.className='result-value';const l=document.createElement('span');l.textContent=label;const v=document.createElement('b');v.textContent=value;row.append(l,v);col.append(row)});grid.append(col)}
 target.append(grid);const note=document.createElement('p');note.className='compare-note';note.textContent=`Matched seeds: ${report.protocol.paired_seeds.join(', ')} · ${report.protocol.steps_per_episode} steps each · ${report.protocol.training_data_excluded?'training data excluded':''}. ${report.protocol.wait_definition}.`;target.append(note)
}
function exportEpisodes(){
 if(!latestReport)return;const rows=latestReport.episodes;const columns=Object.keys(rows[0]||{});const escape=value=>`"${String(value??'').replaceAll('"','""')}"`;
 const csv=[columns.map(escape).join(','),...rows.map(row=>columns.map(key=>escape(row[key])).join(','))].join('\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));const link=document.createElement('a');link.href=url;link.download='smart-traffic-evaluation.csv';link.click();URL.revokeObjectURL(url)
}
document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>{
 document.querySelectorAll('.nav-item').forEach(x=>x.classList.toggle('active',x===button));
 document.querySelectorAll('.page').forEach(x=>x.classList.add('hidden'));
 const page=button.dataset.page;$(`${page}-page`).classList.remove('hidden');$('page-title').textContent=page[0].toUpperCase()+page.slice(1);
}));
$('api-status').classList.add('offline');request('/health').then(()=>{$('api-status').classList.remove('offline');$('api-status').innerHTML='<i></i> API ONLINE';return createRun()}).catch(()=>{$('api-status').classList.add('offline');$('api-status').innerHTML='<i></i> API OFFLINE';toast('Start the backend API to connect the simulation.')});
request('/model').then(model=>{$('model-status').textContent=model.trained?`Hold/switch model · ${model.states} states · Duration model · ${model.duration_states} states`:'No trained model yet · train before interpreting Q-learning results'}).catch(()=>{$('model-status').textContent='Model status unavailable'});
