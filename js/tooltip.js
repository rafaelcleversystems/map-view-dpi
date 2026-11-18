"use strict";
MV.tooltip=c=>{
 const e=MV.escape,i=MV.active();if(!c)return '<b>Sem registro na planilha</b>';
 const row=(label,key)=>`<div class="tip-row"><span>${e(label)}</span><strong>${e(MV.format(c[key]))}</strong></div>`;
 return `<div class="tip-toolbar"><button type="button" class="tip-copy" data-copy-country="${e(c.iso3)}" title="Copiar conteúdo do popup" aria-label="Copiar conteúdo do popup"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h3"/></svg><span>Copiar</span></button><span class="tip-copy-status" role="status"></span></div><div class="tip-content"><div class="tip-title">${e(c.pais)} <small>${e(c.iso3)}</small></div><div class="tip-active">${e(MV.label(i))}: ${e(MV.format(c[i.key]))} <small>${e(i.unit)}</small></div><div class="tip-grid"><div class="tip-section"><b>DPI MAP · UCL/IIPP</b>${row('Identidade digital','dpi_id_contabilizados')}${row('Pagamentos','dpi_pagamentos_contabilizados')}${row('Intercâmbio de dados','dpi_dados_contabilizados')}<div class="tip-systems">${['id','pagamentos','dados'].map(k=>e(c['dpi_'+k+'_sistemas']??'N/D')).join(' · ')}</div></div><div class="tip-section"><b>GTMI · BANCO MUNDIAL</b>${['gtmi','cgsi','psdi','dcei','gtei','grupo'].map(k=>row(k.toUpperCase(),'gtmi_'+k)).join('')}</div><div class="tip-section"><b>OXFORD INSIGHTS</b>${['total','policy_capacity','ai_infrastructure','governance','public_sector_adoption','development_diffusion','resilience'].map(k=>row(MV.labels['oxford_'+k],'oxford_'+k)).join('')}</div><div class="tip-section"><b>OCDE</b>${row('DGI','ocde_dg')}${row('OURdata','ocde_our')}</div></div></div><small class="tip-help">Clique no país para fixar. Clique fora para voltar ao mouse over.</small>`;
};
MV.selectCountry=(code,zoom=false)=>{
 const c=MV.countries.get(code);if(!c)return;MV.state.selected=code;const e=MV.escape,i=MV.active();
 const fields=MV.data.metadata.dictionary.filter(d=>/^(dpi|gtmi|oxford|ocde)_/.test(d.campo));
 document.getElementById('country-panel').innerHTML=`<div class="country-header"><small>${e(c.iso3)} / ${e(c.iso2)} · ${e(c.regiao_analitica)}</small><h2>${e(c.pais)}</h2><small>${c.recorte_prioritario===1?'● País prioritário do Tema 2':'Base internacional'} · ${e(c.criterio_inclusao)}</small>${MV.geometry.has(code)?'':'<p>Sem correspondência ISO3 exata na cartografia. Dados disponíveis abaixo.</p>'}<div class="featured">${e(MV.label(i))}<strong>${e(MV.format(c[i.key]))}</strong><small>${e(i.unit)} · ${e(i.year)} · ${c[i.key]==null?'N/D':'Disponível'}</small></div><button class="export" id="export">↓ Exportar dados do país · CSV</button></div>`+Object.entries(MV.sources).map(([group,title])=>`<details class="country-source" open><summary>${e(title)}</summary>${fields.filter(d=>MV.group(d.campo)===group).map(d=>{const meta=MV.data.indicators.find(x=>x.key===d.campo)||MV.data.metadata.references[d.campo]||{};return `<div class="metric"><div><span>${e(MV.labels[d.campo]||d.campo)}</span><strong>${e(MV.format(c[d.campo],true))}</strong></div><p>${e(d.descricao)}</p><small>${e(d.unidade)} · ${c[d.campo]==null?'N/D · indisponível':'Disponível'}${meta.weighted?' · Contribuição ponderada':''}<br>${e(meta.year??meta.ano_ref)} · ${meta.url||meta.url_fonte?`<a target="_blank" rel="noopener" href="${e(meta.url||meta.url_fonte)}">Fonte original ↗</a>`:e(d.origem)}</small></div>`;}).join('')}</details>`).join('');
 document.getElementById('export').onclick=()=>MV.exportCountry(c);
 if(zoom){const layers=MV.geometry.get(code);if(layers){const bounds=L.featureGroup(layers).getBounds();MV.map.fitBounds(bounds,{animate:false,maxZoom:5,padding:[30,30]});}}
 MV.paint();
};
MV.exportCountry=c=>{
 const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const header=['iso3','pais','indicador','valor','unidade','descricao','fonte','ano_ref','url_fonte'];
 const rows=MV.data.metadata.dictionary.map(d=>{const m=MV.data.indicators.find(i=>i.key===d.campo)||MV.data.metadata.references[d.campo]||{};return [c.iso3,c.pais,d.campo,c[d.campo],d.unidade,d.descricao,d.fonte,m.year??m.ano_ref,m.url??m.url_fonte];});
 const blob=new Blob(['\ufeff'+[header,...rows].map(r=>r.map(cell).join(';')).join('\r\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=c.iso3+'_mapview.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};

// Copy exactly the displayed country summary, without toolbar and interaction hints.
MV.copyTooltip=async button=>{
 const root=button.closest('.mv-tooltip,.mv-country-popup');
 const status=root.querySelector('.tip-copy-status');
 const text=root.querySelector('.tip-content').innerText;
 const fallback=()=>{
  const area=document.createElement('textarea');area.value=text;
  area.style.cssText='position:fixed;left:-9999px;top:0';document.body.appendChild(area);
  area.select();const copied=document.execCommand('copy');area.remove();button.focus();
  if(!copied)throw new Error('Copy unavailable');
 };
 try{
  if(navigator.clipboard&&navigator.clipboard.writeText){try{await navigator.clipboard.writeText(text);}catch(error){fallback();}}
  else fallback();
  status.textContent='Conteúdo copiado';
 }catch(error){status.textContent='Não foi possível copiar. Selecione o texto para copiar manualmente.';}
};
document.addEventListener('click',event=>{
 const button=event.target.closest('[data-copy-country]');
 if(button){event.preventDefault();event.stopPropagation();MV.copyTooltip(button);}
});
