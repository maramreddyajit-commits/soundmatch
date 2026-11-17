export const genres=['ambient','electronic','hip-hop','indie','jazz','pop'];
export const defaults={genres:[],energy:.5,tempo:110};
export function validate(p){if(!p||!Array.isArray(p.genres)||p.genres.some(g=>!genres.includes(g))||typeof p.energy!=='number'||!Number.isFinite(p.energy)||p.energy<0||p.energy>1||typeof p.tempo!=='number'||!Number.isFinite(p.tempo)||p.tempo<50||p.tempo>190)throw Error('Choose valid genres, energy 0–1 and tempo 50–190');return {...p,genres:[...new Set(p.genres)].sort()};}
export function recommend(tracks,profile,saved=[],skipped=[],k=12){
 if(!Number.isInteger(k)||k<1||k>100)throw Error('Invalid recommendation count');
 const p=validate(profile),liked=tracks.filter(t=>saved.includes(t.id)),learned={};for(const t of liked)learned[t.genre]=(learned[t.genre]||0)+1;
 const mean=key=>liked.reduce((a,t)=>a+t[key],0)/liked.length;
 const energy=liked.length?(p.energy+mean('energy'))/2:p.energy,tempo=liked.length?(p.tempo+mean('tempo'))/2:p.tempo,cold=!p.genres.length&&!liked.length;
 const candidates=tracks.filter(t=>!saved.includes(t.id)&&!skipped.includes(t.id)).map(t=>{const g=p.genres.includes(t.genre)?1:liked.length?.8*(learned[t.genre]||0)/liked.length:cold?1/genres.length:0;const components={genre:.5*g,energy:.3*(1-Math.abs(t.energy-energy)),tempo:.2*(1-Math.min(1,Math.abs(t.tempo-tempo)/140))};return {...t,components,score:components.genre+components.energy+components.tempo,cold_start:cold,why:`Genre ${components.genre.toFixed(3)} + energy ${components.energy.toFixed(3)} + tempo ${components.tempo.toFixed(3)}. ${cold?'No genre preference yet: neutral discovery.':'Based on selected genres and saved metadata.'}`};});
 candidates.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));const artists=new Set(),result=[];for(const t of candidates){if(artists.has(t.artist))continue;artists.add(t.artist);result.push(t);if(result.length>=k)break;}return result;
}
