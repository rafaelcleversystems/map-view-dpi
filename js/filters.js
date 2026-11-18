"use strict";
MV.populate=()=>{
 const select=document.getElementById('indicator'),source=document.getElementById('source').value;select.innerHTML='';
 for(const [group,title] of Object.entries(MV.sources)){if(source!=='all'&&source!==group)continue;const optgroup=document.createElement('optgroup');optgroup.label=title;for(const i of MV.data.indicators.filter(i=>MV.group(i.key)===group)){const option=document.createElement('option');option.value=i.key;option.textContent=MV.label(i)+(i.weighted?' · contribuição ponderada':'');optgroup.appendChild(option);}select.appendChild(optgroup);}
 if([...select.options].some(o=>o.value===MV.state.indicator))select.value=MV.state.indicator;else MV.state.indicator=select.value;
};
MV.update=()=>{
 const i=MV.active();MV.paint();document.getElementById('active-source').textContent=MV.sources[MV.group(i.key)]+' / '+i.year;document.getElementById('active-name').textContent=MV.label(i);document.getElementById('active-description').textContent=i.description+(i.weighted?' · Contribuição ponderada ao índice, não uma pontuação independente.':'');
 const subset=MV.data.countries.filter(MV.eligible),count=subset.filter(c=>MV.numeric(c[i.key])).length;document.getElementById('coverage').textContent=`${count} / ${subset.length} com dados`;
 const range=MV.currentRange;document.getElementById('min').textContent=range?MV.format(range[0]):'N/D';document.getElementById('max').textContent=range?MV.format(range[1]):'N/D';document.getElementById('scale-note').textContent=`${i.unit} · ${MV.state.scale==='fixed'&&i.fixed?'limites fixos originais':'mínimo e máximo observados no recorte'}${!i.fixed?' · escala fixa não definida na base':''}`;
 const fixed=document.querySelector('#scale option[value=fixed]');fixed.disabled=!i.fixed;if(!i.fixed){document.getElementById('scale').value='observed';MV.state.scale='observed';}
 if(MV.state.selected)MV.selectCountry(MV.state.selected);MV.search();
};
MV.search=()=>{
 const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();const q=normalize(document.getElementById('search').value.trim()),box=document.getElementById('results');box.innerHTML='';if(!q)return;
 const found=MV.data.countries.filter(c=>MV.eligible(c)&&normalize(c.pais+' '+c.iso3+' '+c.iso2).includes(q));
 if(!found.length){box.textContent='Nenhum país neste recorte.';return;}
 for(const c of found){const button=document.createElement('button');button.type='button';button.textContent=`${c.pais} · ${c.iso3}${MV.geometry.has(c.iso3)?'':' · sem geometria'}`;button.onclick=()=>MV.selectCountry(c.iso3,true);box.appendChild(button);}
};
MV.initFilters=()=>{
 MV.populate();document.getElementById('source').onchange=()=>{MV.populate();MV.update();};document.getElementById('indicator').onchange=e=>{MV.state.indicator=e.target.value;MV.update();};
 for(const id of ['scope','availability','scale'])document.getElementById(id).onchange=e=>{MV.state[id]=e.target.value;MV.update();};
 document.getElementById('highlight').onchange=e=>{MV.state.highlight=e.target.checked;MV.paint();};document.getElementById('search').oninput=MV.search;
 document.getElementById('reset').onclick=()=>{MV.unpinTooltip();Object.assign(MV.state,{indicator:'gtmi_gtmi',scope:'all',availability:'all',scale:'fixed',highlight:false,selected:null});for(const id of ['source','scope','availability'])document.getElementById(id).value='all';document.getElementById('scale').value='fixed';document.getElementById('highlight').checked=false;document.getElementById('search').value='';document.getElementById('country-panel').innerHTML=MV.emptyPanel;document.getElementById('brazil').onclick=()=>MV.selectCountry('BRA',true);MV.populate();MV.update();MV.layer.eachLayer(layer=>layer.closeTooltip());MV.map.stop().fitBounds([[-58,-175],[80,180]],{padding:[12,12],animate:false});};
 document.getElementById('brazil').onclick=()=>MV.selectCountry('BRA',true);MV.update();
};
