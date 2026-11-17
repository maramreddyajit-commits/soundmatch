const $=s=>document.querySelector(s), app=$('#app');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct=v=>v==null?'—':(v*100).toFixed(1)+'%';
const num=v=>Number(v).toLocaleString('en-US',{maximumFractionDigits:1});
import {api} from './data.js';
const shell=(name,sub)=>`<div class="topline"><span>PRODUCT LAB / ${esc(name.toUpperCase())}</span><span class="badge">SYNTHETIC DEMO</span></div><h1>${esc(name)}</h1><p class="lede">${sub}</p>`;
const card=(label,value,hint)=>`<div class="card"><div class="label">${label}</div><div class="value">${value}</div><div class="hint">${hint}</div></div>`;
const bars=(rows,max=1)=>rows.map(r=>`<div class="barrow"><span>${esc(r.name)}</span><div class="bartrack"><div class="barfill ${r.assumption?'assumption':''}" style="width:${Math.max(0,Math.min(100,r.value/max*100))}%"></div></div><strong>${esc(r.label??pct(r.value))}</strong></div>`).join('');
const error=e=>{const d=document.createElement('div');d.className='notice error';d.setAttribute('role','alert');d.textContent=e.message;app.prepend(d);};

export {$,app,api,esc,pct,num,shell,card,bars,error};
