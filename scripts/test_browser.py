"""Development browser QA. Requires websocket-client in .tools or Python environment."""
import sys,pathlib,subprocess,time,json,urllib.request,base64
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools'))
import websocket
chrome=pathlib.Path(r'C:/Program Files/Google/Chrome/Application/chrome.exe')
proc=subprocess.Popen([str(chrome),'--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=9237','--remote-allow-origins=http://localhost:9237','--user-data-dir='+str(ROOT/'validation/chrome-profile'),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ws=None
try:
 for _ in range(100):
  try:
   tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9237/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(tabs[0]['webSocketDebuggerUrl'],origin='http://localhost:9237',timeout=30)
 counter=0;events=[]
 def call(method,params={}):
  global counter
  counter+=1;ident=counter;ws.send(json.dumps(dict(id=ident,method=method,params=params)))
  while True:
   result=json.loads(ws.recv())
   if result.get('id')==ident:
    if 'error' in result:raise RuntimeError(result['error'])
    return result.get('result',{})
   events.append(result)
 def js(expression):
  result=call('Runtime.evaluate',dict(expression=expression,returnByValue=True,awaitPromise=True))
  if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
  return result.get('result',{}).get('value')
 call('Runtime.enable');call('Log.enable');call('Network.enable');call('Network.emulateNetworkConditions',dict(offline=True,latency=0,downloadThroughput=0,uploadThroughput=0))
 call('Page.navigate',dict(url=(ROOT/'index.html').as_uri()))
 for _ in range(150):
  if js("typeof MV!=='undefined' && !!MV.layer && document.getElementById('active-name').textContent.length>0"):break
  time.sleep(.1)
 tests=[]
 def test(name,expression):
  result=js(expression);tests.append(dict(name=name,passed=bool(result),result=result));assert result,name
 test('Offline file opening and 214 records',"MV.data.countries.length===214 && MV.layer.getLayers().length>200")
 for iso,key,value in [('BRA','gtmi_gtmi',.9859831686754061),('USA','oxford_total',88.36),('EST','ocde_dg',.828),('CHN','oxford_ai_infrastructure',78.36),('BRA','dpi_pagamentos_contabilizados',1),('USA','ocde_dg',None)]:
  expected=json.dumps(value)
  test(iso+' '+key,f"(()=>{{MV.state.indicator='{key}';MV.update();MV.selectCountry('{iso}');return MV.countries.get('{iso}')['{key}']==={expected} && document.querySelector('.featured strong').textContent===MV.format({expected});}})()")
 test('Indicator change preserves viewport',"(()=>{MV.map.setView([12,20],3);const c=MV.map.getCenter(),z=MV.map.getZoom();MV.state.indicator='oxford_total';MV.update();return MV.map.getCenter().equals(c)&&MV.map.getZoom()===z;})()")
 test('All indicator selections and tooltips',"(()=>{for(const i of MV.data.indicators){MV.state.indicator=i.key;MV.update();if(!document.getElementById('active-name').textContent||!MV.tooltip(MV.countries.get('BRA')).includes('OCDE'))return false;}return true;})()")
 test('Priority 13 and availability',"(()=>{MV.state.indicator='gtmi_gtmi';MV.state.scope='priority';MV.state.availability='all';MV.update();if(MV.data.countries.filter(MV.eligible).length!==13)return false;MV.state.availability='data';return MV.data.countries.filter(MV.eligible).every(c=>MV.numeric(c.gtmi_gtmi));})()")
 test('Zero distinct from missing',"MV.color(0,[0,1])!==MV.color(null,[0,1]) && MV.format(0)==='0' && MV.format(null)==='N/D'")
 test('Search includes country without geometry',"(()=>{MV.state.scope='all';MV.state.availability='all';document.getElementById('search').value='XKX';MV.update();document.querySelector('#results button').click();return MV.state.selected==='XKX' && document.getElementById('country-panel').textContent.includes('Sem correspondência');})()")
 test('CSV exported without failure',"(()=>{MV.exportCountry(MV.countries.get('BRA'));return true;})()")
 test('Hover creates visible tooltip',"(()=>{const layer=MV.geometry.get('BRA')[0];layer.fire('mouseover',{latlng:L.latLng(-10,-50)});layer.openTooltip(L.latLng(-10,-50));return document.querySelector('.mv-tooltip').textContent.includes('Brasil');})()")
 test('Reset restores initial state',"(()=>{document.getElementById('reset').click();return MV.state.indicator==='gtmi_gtmi'&&MV.state.scope==='all'&&!MV.state.highlight&&MV.map.getZoom()<2;})()")
 test('Workbook notes contain source values',"MV.data.metadata.notes.every(r=>Object.keys(r).length===2)")
 time.sleep(.6)
 test('Global view remains stable after reset',"MV.map.getZoom()<2")
 call('Emulation.setDeviceMetricsOverride',dict(width=1440,height=1050,deviceScaleFactor=1,mobile=False));time.sleep(.4)
 png=call('Page.captureScreenshot',dict(format='png',captureBeyondViewport=True));(ROOT/'validation/desktop.png').write_bytes(base64.b64decode(png['data']))
 call('Emulation.setDeviceMetricsOverride',dict(width=390,height=844,deviceScaleFactor=1,mobile=True));time.sleep(.4)
 test('Mobile layout has no horizontal overflow',"document.documentElement.scrollWidth<=window.innerWidth")
 png=call('Page.captureScreenshot',dict(format='png',captureBeyondViewport=True));(ROOT/'validation/mobile.png').write_bytes(base64.b64decode(png['data']))
 errors=[x for x in events if x.get('method')=='Runtime.exceptionThrown' or x.get('method')=='Log.entryAdded' and x.get('params',{}).get('entry',{}).get('level')=='error']
 tests.append(dict(name='No browser console errors',passed=not errors,result=errors))
 external=[x for x in events if x.get('method')=='Network.requestWillBeSent' and x.get('params',{}).get('request',{}).get('url','').startswith(('http:','https:'))]
 tests.append(dict(name='No external runtime requests',passed=not external,result=len(external)))
 report=dict(browser='Chrome headless',offline=True,tests=tests,passed=all(x['passed'] for x in tests))
 (ROOT/'validation/browser_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(report,ensure_ascii=True,indent=2))
finally:
 if ws:
  try:call('Browser.close')
  except Exception:pass
  ws.close()
 proc.terminate()
