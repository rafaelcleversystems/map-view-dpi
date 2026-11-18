"use strict";
MV.initMap=()=>{
 MV.map=L.map('map',{zoomAnimation:false,minZoom:1,maxZoom:8,zoomSnap:.25,worldCopyJump:false,preferCanvas:true,attributionControl:true}).fitBounds([[-58,-175],[80,180]],{padding:[12,12],animate:false});
 MV.map.attributionControl.addAttribution('Natural Earth · domínio público');MV.geometry=new Map();
 MV.layer=L.geoJSON(MV.data.geo,{style:()=>({color:'#fff',weight:.7,fillOpacity:1,fillColor:'#d5dce1'}),onEachFeature:(feature,layer)=>{
  const code=feature.properties.iso3,c=MV.countries.get(code);if(!MV.geometry.has(code))MV.geometry.set(code,[]);MV.geometry.get(code).push(layer);
  layer.bindTooltip(()=>c?MV.tooltip(c):`<b>${MV.escape(feature.properties.name)}</b><br>Sem registro na planilha`,{className:'mv-tooltip',interactive:true,sticky:true,direction:'auto',opacity:1});
  layer.on('mouseover',()=>{layer.setStyle({weight:2,color:'#718da1'});layer.bringToFront();});layer.on('mouseout',()=>MV.paintLayer(layer));layer.on('click',()=>{if(c)MV.selectCountry(code);});
 }}).addTo(MV.map);
 document.getElementById('global').onclick=()=>MV.map.stop().fitBounds([[-58,-175],[80,180]],{padding:[12,12],animate:false});
 document.getElementById('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.getElementById('map-wrap').requestFullscreen();}catch(e){document.getElementById('scale-note').textContent='Tela cheia indisponível neste navegador.';}};
 document.addEventListener('fullscreenchange',()=>setTimeout(()=>MV.map.invalidateSize(),100));
};
MV.color=(value,range)=>{if(!MV.numeric(value)||!range)return '#d5dce1';const t=range[1]===range[0]?.5:Math.max(0,Math.min(1,(value-range[0])/(range[1]-range[0])));const stops=[[226,240,250],[23,99,157],[8,45,86]],x=t*2,j=Math.min(1,Math.floor(x)),f=x-j;return 'rgb('+stops[j].map((v,k)=>Math.round(v+(stops[j+1][k]-v)*f)).join(',')+')';};
MV.paintLayer=layer=>{const c=MV.countries.get(layer.feature.properties.iso3),eligible=MV.eligible(c),selected=c&&c.iso3===MV.state.selected,highlight=c&&c.recorte_prioritario===1&&MV.state.highlight;layer.setStyle({fillColor:MV.color(eligible?c[MV.state.indicator]:null,MV.currentRange),fillOpacity:c&&!eligible?.18:1,color:selected?'#153a53':highlight?'#b57b1a':'#fff',weight:selected?2.6:highlight?2:.6,opacity:c&&!eligible?.3:1});};
MV.paint=()=>{MV.currentRange=MV.range();MV.layer.eachLayer(MV.paintLayer);};
