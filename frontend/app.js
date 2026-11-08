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
  try{const count=Number($('evaluation-seeds').value);if(!Number.isInteger(count)||count<1||count>30)throw new Error('Choose between 1 and 30 matched seeds');const report=await request('/evaluations',{method:'POST',body:JSON.stringify({scenarios:selected,seeds:Array.from({length:count},(_,i)=>101+i),steps:Number($('compare-steps').value)})});renderReport(report)}catch(e){toast(e.message)}finally{$('compare-button').disabled=false;$('compare-button').textContent='Run evaluation'}
});
$('train-button').addEventListener('click',async()=>{
  const button=$('train-button');button.disabled=true;button.textContent='Training…';
  $('training-progress').classList.remove('hidden');$('training-status').textContent='Training policy…';
  try{
    const episodes=Number($('train-episodes').value), steps=Number($('train-steps').value);
    await request('/training',{method:'POST',body:JSON.stringify({episodes,steps})});
    let status;
    do{
      await new Promise(resolve=>setTimeout(resolve,500));status=await request('/training');
      $('training-count').textContent=`${status.completed} / ${status.total} episodes`;
      $('training-bar').style.width=`${status.total?100*status.completed/status.total:0}%`;
      $('training-status').textContent=status.status==='running'?`Training both policies · ${status.states||0} / ${status.duration_states||0} learned states`:status.status==='queued'?'Starting training…':'Training both policies…';
    }while(['queued','running'].includes(status.status));
    if(status.status==='failed')throw new Error(status.error||'Training failed');
    toast(`Training complete · hold/switch ${status.states} states · duration ${status.duration_states} states`);$('training-status').textContent=`Training complete · ${status.states} / ${status.duration_states} states`;await createRun();
  }catch(e){toast(e.message);$('training-status').textContent='Training failed'}
  finally{button.disabled=false;button.textContent='Train both agents'}
});
function intervalLabel(metric){return metric.ci95_low==null?'CI unavailable (1 sample)':`[${metric.ci95_low.toFixed(2)}, ${metric.ci95_high.toFixed(2)}]`}
function renderReport(report){
 latestReport=report;
 const target=$('compare-results');target.replaceChildren();
 const toolbar=document.createElement('div');toolbar.className='results-toolbar';
 const quality=document.createElement('span');quality.textContent=report.protocol.trained_policy?`Trained policy · ${report.protocol.model_state_count} learned states`:'Untrained policy · train before interpreting model performance';
 const reportMeta=document.createElement('span');reportMeta.className='report-meta';reportMeta.textContent=`Report ${report.metadata?.report_id?.slice(0,8)||'local'} · ${report.metadata?.generated_at?new Date(report.metadata.generated_at).toLocaleString():'timestamp unavailable'}`;reportMeta.title=JSON.stringify(report.metadata||{});
 const actions=document.createElement('div');actions.className='export-actions';
 const exportButton=document.createElement('button');exportButton.className='export-button';exportButton.textContent='Export full report CSV';exportButton.title='Includes protocol, controller summaries, paired intervals, per-seed deltas, and full episode records.';exportButton.addEventListener('click',exportEpisodes);
 const jsonButton=document.createElement('button');jsonButton.className='export-button';jsonButton.textContent='Download JSON';jsonButton.title='Download the complete report as structured JSON.';jsonButton.addEventListener('click',exportReportJson);
 actions.append(exportButton,jsonButton);toolbar.append(quality,reportMeta,actions);target.append(toolbar);
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
 target.append(grid);
 const deltas=report.paired_deltas_vs_fixed_time||[];
 const pairedSummary=report.paired_summary_vs_fixed_time||{};
 if(Object.keys(pairedSummary).length){const section=document.createElement('section');section.className='paired-summary';const heading=document.createElement('h3');heading.className='delta-heading';heading.textContent='Paired results vs fixed-time · 95% t intervals';section.append(heading);const cards=document.createElement('div');cards.className='paired-summary-grid';const labels={q_learning:'Hold/switch',duration_q_learning:'Duration'};for(const [controller,result] of Object.entries(pairedSummary)){const card=document.createElement('article');card.className='paired-summary-card';const title=document.createElement('strong');title.textContent=labels[controller]||controller;card.append(title);const wait=result.wait_seconds;const queue=result.queue_length;const waitRow=document.createElement('p');waitRow.textContent=`Wait Δ ${wait.mean.toFixed(2)} s ${intervalLabel(wait)}`;const queueRow=document.createElement('p');queueRow.textContent=`Queue Δ ${queue.mean.toFixed(2)} ${intervalLabel(queue)}`;const wins=document.createElement('p');wins.textContent=`Lower wait in ${result.wait_improvements}/${result.sample_count} paired episodes${result.wait_ties?` · ${result.wait_ties} ties`:''}`;card.append(waitRow,queueRow,wins);cards.append(card)}section.append(cards);target.append(section)}
 const scenarioSummaries=report.paired_summary_by_scenario||{};
 if(Object.keys(scenarioSummaries).length){const section=document.createElement('section');section.className='paired-summary';const heading=document.createElement('h3');heading.className='delta-heading';heading.textContent='Results by traffic scenario';section.append(heading);const labels={q_learning:'Hold/switch',duration_q_learning:'Duration'};const pretty={balanced:'Balanced flow',rush_hour:'Rush hour',north_surge:'Northbound surge'};for(const [scenario,controllers] of Object.entries(scenarioSummaries)){const block=document.createElement('div');block.className='scenario-summary';const title=document.createElement('h4');title.textContent=pretty[scenario]||scenario;block.append(title);const cards=document.createElement('div');cards.className='paired-summary-grid';for(const [controller,result] of Object.entries(controllers)){const card=document.createElement('article');card.className='paired-summary-card';const name=document.createElement('strong');name.textContent=labels[controller]||controller;const wait=result.wait_seconds;const queue=result.queue_length;const waitRow=document.createElement('p');waitRow.textContent=`Wait Δ ${wait.mean.toFixed(2)} s ${intervalLabel(wait)}`;const queueRow=document.createElement('p');queueRow.textContent=`Queue Δ ${queue.mean.toFixed(2)} ${intervalLabel(queue)}`;const wins=document.createElement('p');wins.textContent=`Lower wait in ${result.wait_improvements}/${result.sample_count} seeds`;card.append(name,waitRow,queueRow,wins);cards.append(card)}block.append(cards);section.append(block)}target.append(section)}
 if(deltas.length){const heading=document.createElement('h3');heading.className='delta-heading';heading.textContent='Matched episode deltas vs fixed-time';target.append(heading);const wrap=document.createElement('div');wrap.className='delta-table-wrap';const table=document.createElement('table');table.className='delta-table';table.innerHTML='<caption class="sr-only">Per-seed wait, queue, and throughput differences against the fixed-time controller</caption><thead><tr><th scope="col">Scenario</th><th scope="col">Seed</th><th scope="col">Policy</th><th scope="col">Wait Δ (s)</th><th scope="col">Queue Δ</th><th scope="col">Served Δ</th></tr></thead>';const body=document.createElement('tbody');const controllerLabel={q_learning:'Hold/switch',duration_q_learning:'Duration'};for(const d of deltas){const row=document.createElement('tr');for(const value of [d.scenario,d.seed,controllerLabel[d.controller]||d.controller,d.wait_seconds.toFixed(3),d.queue_length.toFixed(3),d.vehicles_served>0?`+${d.vehicles_served}`:String(d.vehicles_served)]){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}body.append(row)}table.append(body);wrap.append(table);target.append(wrap);const key=document.createElement('p');key.className='compare-note';key.textContent='Negative wait and queue deltas are lower than baseline; positive served delta means more vehicles cleared.';target.append(key)}
 const note=document.createElement('p');note.className='compare-note';const metadata=report.metadata||{};const config=metadata.signal_config||{};const checkpoints=metadata.model_checkpoints||{};const source=metadata.source||{};const shortHash=value=>value?value.slice(0,12):'unavailable';const treeStatus=source.source_working_tree_clean===true?'clean':source.source_working_tree_clean===false?'dirty':'status unknown';note.textContent=`Matched seeds: ${report.protocol.paired_seeds.join(', ')} · ${report.protocol.steps_per_episode} steps each · ${report.protocol.training_data_excluded?'training data excluded':''}. ${report.protocol.wait_definition}. Signal: green ${config.min_green_seconds??'?'}–${config.max_green_seconds??'?'}s, amber ${config.amber_seconds??'?'}s · Q-table SHA-256: hold ${shortHash(checkpoints.hold_switch_q_table_sha256)}, duration ${shortHash(checkpoints.duration_q_table_sha256)} · Source ${source.revision?source.revision.slice(0,12):'unavailable'} (${treeStatus}).`;target.append(note)
}
function exportEpisodes(){
 if(!latestReport)return;
 const columns=['record_type','scenario','seed','controller','metric','mean','median','population_stddev','ci95_low','ci95_high','sample_count','improvements','ties','value','details_json'];
 const rows=[];const add=(type,data={})=>rows.push({record_type:type,...data});
 add('protocol',{metric:'csv_record_types',value:'protocol; controller_summary; paired_summary_pooled; paired_summary_scenario; paired_delta; episode'});
 for(const [key,value] of Object.entries(latestReport.metadata||{}))add('protocol',{metric:key,value});
 for(const [key,value] of Object.entries(latestReport.protocol||{}))add('protocol',{metric:key,value:Array.isArray(value)||typeof value==='object'?JSON.stringify(value):value});
 for(const [controller,metrics] of Object.entries(latestReport.summary||{}))for(const [metric,stats] of Object.entries(metrics)){
  if(metric==='sample_count')continue;add('controller_summary',{controller,metric,mean:stats.mean,median:stats.median,population_stddev:stats.population_stddev,sample_count:metrics.sample_count});
 }
 const addPaired=(recordType,groups)=>{for(const [group,controllers] of Object.entries(groups||{}))for(const [controller,metrics] of Object.entries(controllers))for(const [metric,stats] of Object.entries(metrics))if(typeof stats==='object'&&stats!==null)add(recordType,{scenario:group||undefined,controller,metric,mean:stats.mean,ci95_low:stats.ci95_low,ci95_high:stats.ci95_high,sample_count:metrics.sample_count,improvements:metric==='wait_seconds'?metrics.wait_improvements:undefined,ties:metric==='wait_seconds'?metrics.wait_ties:undefined})};
 addPaired('paired_summary_pooled',{'':latestReport.paired_summary_vs_fixed_time});
 addPaired('paired_summary_scenario',latestReport.paired_summary_by_scenario);
 for(const delta of latestReport.paired_deltas_vs_fixed_time||[])for(const metric of ['wait_seconds','queue_length','vehicles_served'])add('paired_delta',{scenario:delta.scenario,seed:delta.seed,controller:delta.controller,metric,value:delta[metric]});
 for(const episode of latestReport.episodes||[])add('episode',{scenario:episode.scenario,seed:episode.seed,controller:episode.controller,details_json:JSON.stringify(episode)});
 const escape=value=>`"${String(value??'').replaceAll('"','""')}"`;
 const csv=[columns.map(escape).join(','),...rows.map(row=>columns.map(key=>escape(row[key])).join(','))].join('\r\n');
 downloadReport(csv,'text/csv;charset=utf-8',`smart-traffic-evaluation-${reportFileId()}.csv`)
}
function reportFileId(){return (latestReport?.metadata?.report_id||new Date().toISOString().replaceAll(':','-')).slice(0,8)}
function downloadReport(content,type,filename){const url=URL.createObjectURL(new Blob([content],{type}));const link=document.createElement('a');link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function exportReportJson(){if(!latestReport)return;downloadReport(JSON.stringify(latestReport,null,2),'application/json;charset=utf-8',`smart-traffic-evaluation-${reportFileId()}.json`)}
document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>{
 document.querySelectorAll('.nav-item').forEach(x=>x.classList.toggle('active',x===button));
 document.querySelectorAll('.page').forEach(x=>x.classList.add('hidden'));
 const page=button.dataset.page;$(`${page}-page`).classList.remove('hidden');$('page-title').textContent=page==='city-feed'?'City Feed':page[0].toUpperCase()+page.slice(1);
 if(page==='city-feed'){loadTrafficFeed();loadTrafficHistory()}
}));
$('traffic-refresh').addEventListener('click',loadTrafficFeed);
$('traffic-capture').addEventListener('click',captureTrafficSnapshot);
$('forecast-button').addEventListener('click',runTrafficForecast);
async function loadTrafficHistory(){
 try{
  const data=await request('/traffic/history'),select=$('forecast-site'),selected=select.value;
  $('history-observation-count').textContent=`${data.total_observations.toLocaleString()} observations · ${data.site_count} sites`;
  select.replaceChildren();const prompt=document.createElement('option');prompt.value='';prompt.textContent=data.sites.length?'Select a signal site':'Capture a snapshot to discover sites';select.append(prompt);
  for(const site of data.sites){const option=document.createElement('option');option.value=site.site_id;option.textContent=`Site ${site.site_id} · ${site.observations} samples`;select.append(option)}
  if(data.sites.some(site=>site.site_id===selected))select.value=selected;
 }catch(error){$('history-status').textContent=`Local history is unavailable: ${error.message}`}
}
async function captureTrafficSnapshot(){
 const button=$('traffic-capture'),site=$('forecast-site').value;button.disabled=true;button.textContent='Capturing…';$('history-status').textContent=site?`Fetching recent complete cycle records for site ${site}…`:'Fetching the public feed and storing new source timestamps…';
 try{const result=await request(`/traffic/history/collect${site?`?site_id=${encodeURIComponent(site)}`:''}`,{method:'POST'});$('history-status').textContent=`Saved ${result.inserted} new observations${site?` for site ${site}`:''}; ${result.already_present_or_missing_timestamp} were duplicates or missing timestamps. ${site?'Selected-site records were backfilled where available. Keep collecting after each source update to build a validation set.':`The source feed currently reports ${result.site_count} sites; select one site before targeted collection for a complete local series.`}`;await loadTrafficHistory();await loadTrafficFeed()}
 catch(error){$('history-status').textContent=`Snapshot collection failed: ${error.message}`}
 finally{button.disabled=false;button.textContent='Capture snapshot'}
}
async function runTrafficForecast(){
 const site=$('forecast-site').value;if(!site){$('history-status').textContent='Select a site after capturing at least one traffic snapshot.';return}
 const button=$('forecast-button');button.disabled=true;button.textContent='Training & evaluating…';$('history-status').textContent=`Building a chronological one-step forecast for site ${site}…`;
 try{
  const report=await request(`/traffic/forecast?site_id=${encodeURIComponent(site)}`);
  if(report.status==='insufficient_data'){$('forecast-section').classList.add('hidden');$('history-status').textContent=`Site ${site} has ${report.observation_count} unique observations; at least ${report.minimum_observations} are required. Run the collector every 60 seconds and retry after new source timestamps arrive.`;return}
  $('forecast-section').classList.remove('hidden');$('history-status').textContent=`Site ${site}: evaluated on a chronological holdout. Lower MAE is better; the model is useful only if it beats the persistence baseline on held-out data.`;
  $('forecast-sample-count').textContent=report.metrics.ridge_regression.sample_count;
  $('forecast-naive-mae').textContent=report.metrics.persistence_baseline.mae.toFixed(2);
  $('forecast-model-mae').textContent=report.metrics.ridge_regression.mae.toFixed(2);
  $('forecast-next-value').textContent=report.next_cycle_forecast.ridge_regression.toFixed(1);
  $('forecast-next-time').textContent=`Model count / cycle · ${new Date(report.next_cycle_forecast.estimated_for).toLocaleTimeString()}`;
  $('forecast-validation-window').textContent=`${new Date(report.validation_start).toLocaleString()} — ${new Date(report.validation_end).toLocaleString()}`;
  $('forecast-method-note').textContent=`${report.validation_method}. Features: previous three cycle counts and hour-of-day sine/cosine. Regularization ${report.model.regularization}. Forecast horizon is one next observed source cycle (estimated median interval ${report.next_cycle_forecast.estimated_interval_seconds}s); it is not an hourly forecast.`;
  drawForecastChart(report.validation);
 }catch(error){$('history-status').textContent=`Forecast failed: ${error.message}`}
 finally{button.disabled=false;button.textContent='Train & evaluate forecast'}
}
function drawForecastChart(rows){
 const svg=$('forecast-chart'),ns='http://www.w3.org/2000/svg';svg.replaceChildren();if(!rows?.length)return;
 const values=rows.flatMap(row=>[row.actual,row.naive,row.model]),min=Math.min(0,...values),max=Math.max(1,...values),left=48,right=878,top=20,bottom=218;
 const x=index=>left+(rows.length===1?0:index*(right-left)/(rows.length-1));const y=value=>bottom-(value-min)*(bottom-top)/(max-min||1);
 for(let tick=0;tick<=4;tick++){const yy=top+tick*(bottom-top)/4,line=document.createElementNS(ns,'line');line.setAttribute('x1',left);line.setAttribute('x2',right);line.setAttribute('y1',yy);line.setAttribute('y2',yy);line.setAttribute('class','forecast-grid');svg.append(line);const label=document.createElementNS(ns,'text');label.setAttribute('x','4');label.setAttribute('y',yy+4);label.textContent=(max-(max-min)*tick/4).toFixed(1);label.setAttribute('class','forecast-axis-label');svg.append(label)}
 for(const [key,klass] of [['actual','actual-line'],['naive','naive-line'],['model','model-line']]){const path=document.createElementNS(ns,'polyline');path.setAttribute('points',rows.map((row,index)=>`${x(index)},${y(row[key])}`).join(' '));path.setAttribute('class',klass);path.setAttribute('fill','none');svg.append(path)}
 const start=document.createElementNS(ns,'text');start.setAttribute('x',left);start.setAttribute('y','248');start.textContent=new Date(rows[0].recorded_at).toLocaleTimeString();start.setAttribute('class','forecast-axis-label');svg.append(start);const end=document.createElementNS(ns,'text');end.setAttribute('x',right);end.setAttribute('y','248');end.setAttribute('text-anchor','end');end.textContent=new Date(rows[rows.length-1].recorded_at).toLocaleTimeString();end.setAttribute('class','forecast-axis-label');svg.append(end);
}
function formatFeedAge(seconds){if(seconds==null)return 'Unknown';if(seconds<60)return `${seconds}s`;if(seconds<3600)return `${Math.floor(seconds/60)}m`;return `${Math.floor(seconds/3600)}h`}
async function loadTrafficFeed(){
 const button=$('traffic-refresh'),status=$('traffic-feed-status');button.disabled=true;button.textContent='Refreshing…';status.textContent='Fetching the latest public signal records…';
 try{
  const data=await request('/traffic/live');
  $('feed-site-count').textContent=data.site_count.toLocaleString();$('feed-record-count').textContent=data.record_count.toLocaleString();$('feed-age').textContent=formatFeedAge(data.age_seconds);
  $('feed-timestamp').textContent=data.latest_recorded_at?`Latest record ${new Date(data.latest_recorded_at).toLocaleString()}`:'No timestamp provided';
  $('feed-row-count').textContent=`${data.sites.length} sites`;
  const body=$('traffic-feed-rows');body.replaceChildren();
  for(const site of data.sites){const row=document.createElement('tr');const values=[site.site_id,site.recorded_at?new Date(site.recorded_at).toLocaleString():'—',String(site.lane_count),site.flow_lane_samples?site.measured_vehicles_per_cycle.toFixed(1):'—',site.occupancy_lane_samples?`${site.average_detector_occupancy_percent.toFixed(1)}%`:'—'];for(const value of values){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}body.append(row)}
  if(!data.sites.length){const row=document.createElement('tr'),cell=document.createElement('td');cell.colSpan=5;cell.textContent='The feed returned no site records.';row.append(cell);body.append(row)}
  status.textContent=`Connected to ${data.source}. Retrieved ${new Date(data.retrieved_at).toLocaleTimeString()}. ${data.measurement_note}`;
 }catch(error){status.textContent=`Could not load the live city feed. ${error.message} Try refreshing in a moment.`;}
 finally{button.disabled=false;button.textContent='Refresh feed'}
}
$('api-status').classList.add('offline');request('/health').then(()=>{$('api-status').classList.remove('offline');$('api-status').innerHTML='<i></i> API ONLINE';return createRun()}).catch(()=>{$('api-status').classList.add('offline');$('api-status').innerHTML='<i></i> API OFFLINE';toast('Start the backend API to connect the simulation.')});
request('/model').then(model=>{$('model-status').textContent=model.trained?`Hold/switch model · ${model.states} states · Duration model · ${model.duration_states} states`:'No trained model yet · train before interpreting Q-learning results'}).catch(()=>{$('model-status').textContent='Model status unavailable'});
