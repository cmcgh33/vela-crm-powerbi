from pathlib import Path
import json,csv,argparse
parser=argparse.ArgumentParser()
parser.add_argument("--allow-newer-schemas", action="store_true", help="Skip schema versions not vendored locally; still check bindings and data")
args=parser.parse_args()
from urllib.parse import urlparse
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
ROOT=Path(__file__).resolve().parents[1]
SC=ROOT/'tools/schemas'
store={}
for p in SC.rglob('*.json'):
 obj=json.loads(p.read_text());store['https://developer.microsoft.com/json-schemas/'+str(p.relative_to(SC))]=obj
registry=Registry().with_resources((uri,Resource.from_contents(obj,default_specification=DRAFT7)) for uri,obj in store.items())
count=0
for p in (ROOT/'VelaCRM.Report/definition').rglob('*.json'):
 obj=json.loads(p.read_text())
 if obj['$schema'] not in store:
  if not args.allow_newer_schemas: raise ValueError('Schema not vendored: '+obj['$schema']+'; use --allow-newer-schemas for structural/data checks')
  continue
 schema=store[obj['$schema']]
 jsonschema.Draft7Validator(schema,registry=registry).validate(obj);count+=1
model=json.loads((ROOT/'VelaCRM.SemanticModel/model.bim').read_text())['model']
tabs={t['name']:t for t in model['tables']};cols={n:{c['name'] for c in t['columns']} for n,t in tabs.items()}
measures={m['name'] for t in tabs.values() for m in t.get('measures',[])}
for r in model['relationships']:
 assert r['fromColumn'] in cols[r['fromTable']]
 assert r['toColumn'] in cols[r['toTable']]
for p in (ROOT/'VelaCRM.Report/definition/pages').rglob('visual.json'):
 v=json.loads(p.read_text());pos=v['position'];canvas=json.loads((p.parents[2]/'page.json').read_text());assert pos['x']+pos['width']<=canvas['width'] and pos['y']+pos['height']<=canvas['height']
 for role in v['visual'].get('query',{}).get('queryState',{}).values():
  for proj in role['projections']:
   f=proj['field'];typ=next(iter(f));expr=f[typ];table=expr['Expression']['SourceRef']['Entity'];name=expr['Property']
   assert name in (measures if typ=='Measure' else cols[table]),(p,name)
rows=list(csv.DictReader((ROOT/'data/Opportunities.csv').open()))
assert len({r['OpportunityID'] for r in rows})==len(rows)
ids={r['OpportunityID'] for r in rows}
h=list(csv.DictReader((ROOT/'data/Stage_History.csv').open()))
assert all(r['OpportunityID'] in ids for r in h)
assert all(r['EnteredDate']<=r['ExitedDate'] for r in h if r['ExitedDate'])
assert all((r['Status']=='Open') == (not r['CloseDate']) for r in rows)
assert all((r['CreatedDate'] <= r['CloseDate']) for r in rows if r['CloseDate'])
# Typed numeric literals are essential: schema-valid bare numbers can be ignored by Desktop.
def literals(obj):
 if isinstance(obj,dict):
  if 'Literal' in obj:
   value=obj['Literal']['Value']
   import re
   assert not re.fullmatch(r'-?\d+(?:\.\d+)?',value), ('Untyped numeric literal',value)
  for val in obj.values():literals(val)
 elif isinstance(obj,list):
  for val in obj:literals(val)
for p in (ROOT/'VelaCRM.Report/definition').rglob('*.json'):literals(json.loads(p.read_text()))
for table in ['Opportunities','Stages']:
 assert next(c['dataType'] for c in tabs[table]['columns'] if c['name']=='Probability')=='double'
 expr=tabs[table]['partitions'][0]['source']['expression']
 expr='\n'.join(expr) if isinstance(expr,list) else expr
 assert '{"Probability", type number}' in expr
print(f'PASS: {count} report files against Microsoft JSON schemas; field bindings, canvas bounds, IDs, history, and close dates checked.')
