"""Convert the original XLSX using only Python standard library; never edit source values."""
import argparse, collections, json, math, pathlib, zipfile, xml.etree.ElementTree as E
ROOT=pathlib.Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_book(path):
 with zipfile.ZipFile(path) as z:
  strings=[''.join(e.itertext()) for e in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
  rels={e.get('Id'):e.get('Target') for e in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  result={}
  for sheet in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
   target=rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
   target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   rows=[]
   for row in E.fromstring(z.read(target)).findall('m:sheetData/m:row',NS):
    cells={}
    for c in row:
     col=''.join(x for x in c.get('r') if x.isalpha()); ix=0
     for x in col: ix=ix*26+ord(x)-64
     v=c.find('m:v',NS); inline=c.find('m:is',NS); value=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else None
     if c.get('t')=='s' and value is not None:value=strings[int(value)]
     elif c.get('t') not in ('inlineStr','str','e') and value is not None:
      number=float(value);value=int(number) if number.is_integer() else number
     cells[ix-1]=value
    rows.append(cells)
   headers={i:(key if key is not None else 'valor_'+str(i)) for i,key in rows[0].items()};result[sheet.get('name')]=[{key:row.get(i) for i,key in headers.items()} for row in rows[1:]]
  return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('workbook',nargs='?',default=str(ROOT/'data/Tema2_DPI_IA_Base_Global_MapView.xlsx'));args=parser.parse_args()
 book=read_book(args.workbook);countries=book['PAISES_MAPVIEW'];dictionary={x['campo']:x for x in book['DICIONARIO']};long=book['INDICADORES_LONGOS'];bycode={x['iso3']:x for x in countries}
 indicators=[];numeric=[];mismatches=[];missing_dictionary=[];unexpected=[]
 for key in countries[0]:
  if key.startswith(('dpi_','gtmi_','oxford_','ocde_')):
   definition=dictionary.get(key,{})
   if not definition:missing_dictionary.append(key)
   values=[c[key] for c in countries if isinstance(c[key],(int,float))]
   if not values:continue
   numeric.append(key);refs=[v for v in long if v['indicador']==key];meta=refs[0] if refs else {}
   coded=key in ('gtmi_I_3','gtmi_I_26_2','gtmi_I_41');weighted=key.startswith('ocde_') and key not in ('ocde_dg','ocde_our')
   fixed=[0,100] if key.startswith('oxford_') else [0,1] if key.startswith(('gtmi_','ocde_')) and not coded and not weighted else None
   if fixed:
    unexpected.extend({'iso3':c['iso3'],'field':key,'value':c[key]} for c in countries if isinstance(c[key],(int,float)) and not fixed[0]<=c[key]<=fixed[1])
   indicators.append(dict(key=key,source=meta.get('fonte',definition.get('fonte')),description=definition.get('descricao') or meta.get('descricao') or key,unit=definition.get('unidade') or meta.get('unidade'),origin=definition.get('origem'),year=meta.get('ano_ref'),url=meta.get('url_fonte'),observed=[min(values),max(values)],fixed=fixed,weighted=weighted,coded=coded,available=len(values)))
 for row in long:
  original=bycode.get(row['iso3'],{}).get(row['indicador']);value=row['valor_numerico'] if row['valor_numerico'] is not None else row['valor_texto']
  if original!=value:mismatches.append({'iso3':row['iso3'],'field':row['indicador'],'wide':original,'long':value})
 geo=json.loads((ROOT/'data/world.geojson').read_text(encoding='utf-8'));print('Geo properties:',geo['features'][0]['properties'])
 # Natural Earth supplies explicit ISO alpha-3 values; no fuzzy country-name matching.
 for f in geo['features']:
  p=f['properties'];p['iso3']=p.get('ISO3166-1-Alpha-3');p['name']=p.get('name')
 geocodes={f['properties']['iso3'] for f in geo['features']};codes=[c['iso3'] for c in countries]
 checks=[('BRA','gtmi_gtmi'),('USA','oxford_total'),('EST','ocde_dg'),('CHN','oxford_ai_infrastructure'),('BRA','dpi_pagamentos_contabilizados'),('USA','ocde_dg')]
 report=dict(country_count=len(countries),column_count=len(countries[0]),priority_count=sum(c['recorte_prioritario']==1 for c in countries),duplicate_iso3=[k for k,v in collections.Counter(codes).items() if v>1],without_geometry=[{'iso3':c['iso3'],'pais':c['pais']} for c in countries if c['iso3'] not in geocodes],geometry_without_data=sorted(geocodes-set(codes),key=str),missing_dictionary=missing_dictionary,unexpected_numeric=unexpected,long_wide_mismatches=mismatches,zero_count=sum(c[k]==0 for c in countries for k in numeric),null_count=sum(c[k] is None for c in countries for k in numeric),source_replacement_characters=[{'iso3':c['iso3'],'field':k} for c in countries for k,v in c.items() if isinstance(v,str) and chr(65533) in v],examples=[{'iso3':iso,'indicator':key,'value':bycode[iso][key]} for iso,key in checks],notes=['Source strings and numbers preserved; no silent corrections.','Coded GTMI and weighted OECD dimensions use observed ranges because no authoritative fixed bounds are supplied.','Natural Earth boundaries: cartographic representation, not a position on disputed territories.'])
 metadata=dict(references={row['indicador']:row for row in long},dictionary=book['DICIONARIO'],notes=book['LEIA_ME'],regional=book['DPI_REGIONAIS'],long_records=len(long),geography_source='https://github.com/datasets/geo-countries',geography_license='Natural Earth: public domain; geo-countries: ODC PDDL',validation=report)
 def write(name,value):
  (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 for name,value in [('data/countries.json',countries),('data/indicators.json',indicators),('data/metadata.json',metadata),('data/indicators_long.json',long),('data/world.geojson',geo),('validation/validation_report.json',report)]:write(name,value)
 # Script payload permits direct file:// opening without fetch or a server.
 (ROOT/'data/bundle.js').write_text('window.MAPVIEW_DATA='+json.dumps(dict(countries=countries,indicators=indicators,metadata=metadata,geo=geo),ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='source_replacement_characters'},ensure_ascii=True,indent=2));print('Source replacement characters:',len(report['source_replacement_characters']))
if __name__=='__main__':main()
