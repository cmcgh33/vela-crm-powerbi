"""Rebuild the portable Power BI portfolio project with deterministic fictional data."""
from pathlib import Path
import random, json, csv, base64, uuid, statistics, shutil
from datetime import date,timedelta
ROOT=Path(__file__).resolve().parents[1]
R=random.Random(3387)
SNAP=date(2026,9,30)
NAVY='#ECF0FF'; VIOLET='#A875FF'; TEAL='#26D9EA'; WHITE='#11152A'; MUTED='#A1ACCA'; BG='#070A18'; PINK='#F85BA5'; EDGE='#272C4A'
def write(path,obj):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def csvwrite(name,rows):
 p=ROOT/'data'/f'{name}.csv';p.parent.mkdir(exist_ok=True)
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
reps=[{'RepID':i+1,'RepName':n,'Region':['West','Central','East'][i//4]} for i,n in enumerate(['Avery Brooks','Jordan Ellis','Morgan Reed','Cameron Hayes','Taylor James','Riley Carter','Skyler Quinn','Parker Lane','Alex Rivera','Drew Bennett','Sam Monroe','Casey Wells'])]
accounts=[{'AccountID':i+1,'AccountName':f'{["Northstar","Juniper","Meridian","Cobalt","Beacon","Summit"][i%6]} {i+1:03d}','Industry':R.choice(['Healthcare','Technology','Manufacturing','Professional services','Retail']),'Segment':R.choices(['SMB','Mid-market','Enterprise'],[.35,.45,.2])[0]} for i in range(180)]
stages=[{'StageID':i+1,'StageName':n,'StageOrder':i+1,'Probability':p} for i,(n,p) in enumerate([('Qualified',.15),('Discovery',.3),('Demo',.5),('Proposal',.7),('Negotiation',.85),('Closed won',1),('Closed lost',0)])]
opps=[];history=[];activities=[]
for i in range(1400):
 created=date(2025,1,1)+timedelta(days=R.randrange((SNAP-date(2025,1,1)).days+1))
 rep=R.choice(reps);acct=R.choice(accounts);product=R.choice(['CRM Pro','CRM Enterprise','Service Suite']);amount=round(R.uniform(4000,22000)*{'SMB':1,'Mid-market':3,'Enterprise':8}[acct['Segment']],-2)
 skill=.04*(rep['RepID']%4); win=R.random()<.43+skill
 loss_stage=R.choices([1,2,3,4,5],[.15,.23,.23,.24,.15])[0]
 terminal=5 if win else loss_stage
 t=created;entered=[];closed=None
 for stage in range(1,terminal+1):
  if t>SNAP:break
  exitdate=t+timedelta(days=R.randint(5,27)+(15 if acct['Segment']=='Enterprise' else 0))
  entered.append((stage,t,exitdate if exitdate<=SNAP else None))
  if exitdate>SNAP:break
  t=exitdate
  if stage==terminal:closed=t
 status=('Won' if win else 'Lost') if closed else 'Open'
 current=(6 if win else 7) if closed else entered[-1][0]
 last=closed or entered[-1][1]
 expected=closed or (created+timedelta(days=R.randint(60,180)))
 activitydate=max(created,SNAP-timedelta(days=R.randint(0,45))) if status=='Open' else closed-timedelta(days=R.randint(0,4))
 age=(SNAP-entered[-1][1]).days if status=='Open' else 0
 follow=(SNAP-activitydate).days if status=='Open' else 0
 overdue=status=='Open' and expected<SNAP
 alert='Close date overdue' if overdue else ('No activity 14+ days' if status=='Open' and follow>=14 else ('Stage age 30+ days' if status=='Open' and age>=30 else 'On track'))
 opp={'OpportunityID':i+1,'OpportunityName':f'{acct["AccountName"]} • {product}','AccountID':acct['AccountID'],'RepID':rep['RepID'],'StageID':current,'CreatedDate':created.isoformat(),'CloseDate':closed.isoformat() if closed else None,'ExpectedCloseDate':expected.isoformat(),'Status':status,'ACV':int(amount),'Probability':stages[current-1]['Probability'],'LeadSource':R.choice(['Partner','Inbound','Outbound','Event']),'Product':product,'DaysInStage':age,'DaysSinceActivity':follow,'AttentionReason':alert,'IsAtRisk':int(status=='Open' and alert!='On track'),'IsOverdue':int(overdue),'SalesCycleDays':(closed-created).days if closed else None}
 opps.append(opp)
 for stage,entry,exitdate in entered:
  history.append({'HistoryID':len(history)+1,'OpportunityID':i+1,'StageID':stage,'EnteredDate':entry.isoformat(),'ExitedDate':exitdate.isoformat() if exitdate else None,'DaysInStage':((exitdate or SNAP)-entry).days})
 activities.append({'ActivityID':i+1,'OpportunityID':i+1,'ActivityDate':activitydate.isoformat(),'ActivityType':R.choice(['Call','Email','Meeting']),'Outcome':R.choice(['Follow-up scheduled','Proposal discussed','Stakeholders engaged'])})
dates=[];d=date(2025,1,1)
while d<=date(2026,12,31):
 dates.append({'Date':d.isoformat(),'Year':d.year,'Quarter':f'Q{(d.month-1)//3+1}','Month':d.strftime('%b'),'MonthYear':d.strftime('%b %Y'),'YearMonth':d.year*100+d.month,'MonthStart':d.replace(day=1).isoformat()});d+=timedelta(days=1)
targets=[{'TargetID':len(reps)*((y-2025)*12+m-1)+r['RepID'],'RepID':r['RepID'],'MonthDate':date(y,m,1).isoformat(),'TargetACV':(65000+5000*(r['RepID']%4))*(1.1 if y==2026 else 1)} for y in [2025,2026] for m in range(1,13) for r in reps]
tables={'Accounts':accounts,'Sales Reps':reps,'Stages':stages,'Opportunities':opps,'Stage History':history,'Activities':activities,'Date':dates,'Targets':targets}
for n,rows in tables.items():csvwrite(n.replace(' ','_'),rows)
# Measures: Date is a closed-sales period. Pipeline deliberately ignores this date filter.
measures={
'Won ACV':('CALCULATE(SUM(Opportunities[ACV]), Opportunities[Status] = "Won")','$#,0;($#,0);$0'),
'Won Deals':('CALCULATE(COUNTROWS(Opportunities), Opportunities[Status] = "Won")','#,0'),
'Lost Deals':('CALCULATE(COUNTROWS(Opportunities), Opportunities[Status] = "Lost")','#,0'),
'Closed Deals':('[Won Deals] + [Lost Deals]','#,0'),
'Win Rate':('DIVIDE([Won Deals], [Closed Deals])','0.0%'),
'Average Won ACV':('DIVIDE([Won ACV], [Won Deals])','$#,0'),
'Average Sales Cycle':('CALCULATE(AVERAGE(Opportunities[SalesCycleDays]), Opportunities[Status] = "Won")','0.0" days"'),
'Open Pipeline ACV':('CALCULATE(SUM(Opportunities[ACV]), REMOVEFILTERS(\'Date\'), Opportunities[Status] = "Open")','$#,0'),
'Weighted Pipeline ACV':('CALCULATE(SUMX(Opportunities, Opportunities[ACV] * Opportunities[Probability]), REMOVEFILTERS(\'Date\'), Opportunities[Status] = "Open")','$#,0'),
'Open Deals':('CALCULATE(COUNTROWS(Opportunities), REMOVEFILTERS(\'Date\'), Opportunities[Status] = "Open")','#,0'),
'At Risk Pipeline ACV':('CALCULATE([Open Pipeline ACV], Opportunities[IsAtRisk] = 1)','$#,0'),
'At Risk Deals':('CALCULATE([Open Deals], Opportunities[IsAtRisk] = 1)','#,0'),
'Overdue Deals':('CALCULATE([Open Deals], Opportunities[IsOverdue] = 1)','#,0'),
'Target ACV':('IF(ISCROSSFILTERED(Accounts) || ISFILTERED(Opportunities[LeadSource]) || ISFILTERED(Opportunities[Product]) || ISCROSSFILTERED(Stages), BLANK(), CALCULATE(SUM(Targets[TargetACV]), KEEPFILTERS(\'Date\'[Date] <= DATE(2026, 9, 30))))','$#,0'),
'Target Attainment':('DIVIDE([Won ACV], [Target ACV])','0.0%'),
'Won ACV Prior Year':('CALCULATE([Won ACV], DATEADD(\'Date\'[Date], -1, YEAR))','$#,0'),
'Won ACV YoY':('DIVIDE([Won ACV] - [Won ACV Prior Year], [Won ACV Prior Year])','0.0%'),
'Pipeline Risk Share':('DIVIDE([At Risk Pipeline ACV], [Open Pipeline ACV])','0.0%'),
'Average Current Stage Age':('CALCULATE(AVERAGE(Opportunities[DaysInStage]), REMOVEFILTERS(\'Date\'), Opportunities[Status] = "Open")','0.0" days"'),
'Accounts in Context':('DISTINCTCOUNT(Opportunities[AccountID])','#,0'),
'Snapshot Label':('"Pipeline snapshot · 30 Sep 2026"',''),
'Stage Reached Deals':('VAR Cohort = CALCULATETABLE(VALUES(Opportunities[OpportunityID]), CROSSFILTER(\'Date\'[Date], Opportunities[CloseDate], NONE), USERELATIONSHIP(\'Date\'[Date], Opportunities[CreatedDate]), REMOVEFILTERS(Stages)) RETURN CALCULATE(DISTINCTCOUNT(\'Stage History\'[OpportunityID]), TREATAS(Cohort, \'Stage History\'[OpportunityID]))','#,0'),
'Cohort Qualified Deals':('CALCULATE([Stage Reached Deals], REMOVEFILTERS(Stages), Stages[StageID] = 1)','#,0'),
'Stage Reach Rate':('DIVIDE([Stage Reached Deals], [Cohort Qualified Deals])','0.0%'),
'Average Completed Stage Days':('VAR Cohort = CALCULATETABLE(VALUES(Opportunities[OpportunityID]), CROSSFILTER(\'Date\'[Date], Opportunities[CloseDate], NONE), USERELATIONSHIP(\'Date\'[Date], Opportunities[CreatedDate]), REMOVEFILTERS(Stages)) RETURN CALCULATE(AVERAGE(\'Stage History\'[DaysInStage]), TREATAS(Cohort, \'Stage History\'[OpportunityID]), \'Stage History\'[ExitedDate] <> BLANK())','0.0" days"'),
'Last Activity Date':('MAX(Activities[ActivityDate])','dd mmm yyyy'),
'Attention Deal ACV':('CALCULATE(SUM(Opportunities[ACV]), REMOVEFILTERS(\'Date\'), Opportunities[Status] = "Open", Opportunities[IsAtRisk] = 1)','$#,0'),
}
# Graphics use the same model and respond to slicers.
tables['Risk Bands']=[{'RiskID':0,'RiskLabel':'On track'},{'RiskID':1,'RiskLabel':'Needs attention'}]
csvwrite('Risk_Bands', tables['Risk Bands'])
measures.update({
 'Cohort Deals':('CALCULATE(COUNTROWS(Opportunities), CROSSFILTER(\'Date\'[Date], Opportunities[CloseDate], NONE), USERELATIONSHIP(\'Date\'[Date], Opportunities[CreatedDate]), REMOVEFILTERS(Stages))','#,0'),
 'Gauge Minimum':('0','0%'),
 'Gauge Maximum':('MAX(1.5, [Target Attainment] * 1.15)','0%'),
 'Gauge Target':('1','0%'),
 'Pipeline by Risk Band':('VAR Flag = SELECTEDVALUE(\'Risk Bands\'[RiskID]) RETURN IF(NOT ISBLANK(Flag), CALCULATE([Open Pipeline ACV], Opportunities[IsAtRisk] = Flag))','$#,0'),
})
measures['Source Outcome Flow SVG']=('VAR Sources = DATATABLE("SourceName", STRING, "I", INTEGER, "C", STRING, {{"Partner",0,"#26D9EA"},{"Inbound",1,"#4785FF"},{"Outbound",2,"#A875FF"},{"Event",3,"#F85BA5"}})\nVAR Outcomes = DATATABLE("Outcome", STRING, "J", INTEGER, "D", STRING, {{"Won",0,"#26D9EA"},{"Lost",1,"#F85BA5"},{"Open",2,"#FFBD59"}})\nVAR Total = [Cohort Deals]\nVAR Scale = DIVIDE(200, Total, 0)\nVAR Links = CONCATENATEX(Sources,\n VAR S = [SourceName] VAR SI = [I] VAR SC = [C]\n RETURN CONCATENATEX(Outcomes,\n  VAR O = [Outcome] VAR OI = [J] VAR OC = [D]\n  VAR N = CALCULATE([Cohort Deals], Opportunities[LeadSource] = S, Opportunities[Status] = O)\n  VAR PriorS = SUMX(FILTER(Outcomes, [J] < OI), VAR PO = [Outcome] RETURN CALCULATE([Cohort Deals], Opportunities[LeadSource] = S, Opportunities[Status] = PO))\n  VAR PriorO = SUMX(FILTER(Sources, [I] < SI), VAR PS = [SourceName] RETURN CALCULATE([Cohort Deals], Opportunities[LeadSource] = PS, Opportunities[Status] = O))\n  VAR SY = 24 + SI * 24 + SUMX(FILTER(Sources, [I] < SI), VAR PS = [SourceName] RETURN CALCULATE([Cohort Deals], Opportunities[LeadSource] = PS)) * Scale + (PriorS + N / 2) * Scale\n  VAR DY = 35 + OI * 35 + SUMX(FILTER(Outcomes, [J] < OI), VAR PO = [Outcome] RETURN CALCULATE([Cohort Deals], Opportunities[Status] = PO)) * Scale + (PriorO + N / 2) * Scale\n  VAR W = N * Scale\n  RETURN IF(N > 0, "<defs><linearGradient id=\'g" & SI & OI & "\'><stop stop-color=\'" & SC & "\'/><stop offset=\'1\' stop-color=\'" & OC & "\'/></linearGradient></defs><path d=\'M 192 " & FORMAT(SY,"0.00","en-US") & " C 415 " & FORMAT(SY,"0.00","en-US") & " 585 " & FORMAT(DY,"0.00","en-US") & " 808 " & FORMAT(DY,"0.00","en-US") & "\' fill=\'none\' stroke=\'url(#g" & SI & OI & ")\' stroke-opacity=\'0.58\' stroke-width=\'" & FORMAT(W,"0.00","en-US") & "\'/>", ""), ""), "")\nVAR LeftNodes = CONCATENATEX(Sources,\n VAR S = [SourceName] VAR SI = [I] VAR SC = [C]\n VAR N = CALCULATE([Cohort Deals], Opportunities[LeadSource] = S)\n VAR Y = 24 + SI * 24 + SUMX(FILTER(Sources, [I] < SI), VAR PS = [SourceName] RETURN CALCULATE([Cohort Deals], Opportunities[LeadSource] = PS)) * Scale\n RETURN IF(N > 0, "<rect x=\'14\' y=\'" & Y & "\' width=\'178\' height=\'" & FORMAT(N*Scale,"0.00","en-US") & "\' rx=\'8\' fill=\'" & SC & "\'/><text x=\'28\' y=\'" & (Y+19) & "\' font-size=\'14\' font-weight=\'600\' fill=\'#070A18\'>" & S & " · " & FORMAT(N,"#,0") & "</text>", ""), "")\nVAR RightNodes = CONCATENATEX(Outcomes,\n VAR O = [Outcome] VAR OI = [J] VAR OC = [D]\n VAR N = CALCULATE([Cohort Deals], Opportunities[Status] = O)\n VAR Y = 35 + OI * 35 + SUMX(FILTER(Outcomes, [J] < OI), VAR PO = [Outcome] RETURN CALCULATE([Cohort Deals], Opportunities[Status] = PO)) * Scale\n RETURN IF(N > 0, "<rect x=\'808\' y=\'" & Y & "\' width=\'178\' height=\'" & FORMAT(N*Scale,"0.00","en-US") & "\' rx=\'8\' fill=\'" & OC & "\'/><text x=\'822\' y=\'" & (Y+19) & "\' font-size=\'14\' font-weight=\'600\' fill=\'#070A18\'>" & O & " · " & FORMAT(N,"#,0") & "</text>", ""), "")\nVAR Svg = "<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'1000\' height=\'340\' viewBox=\'0 0 1000 340\'><rect width=\'1000\' height=\'340\' fill=\'#11152A\'/><g font-family=\'Segoe UI\'>" & Links & LeftNodes & RightNodes & "</g></svg>"\nRETURN IF(Total > 0, "data:image/svg+xml;utf8," & SUBSTITUTE(Svg,"#","%23"))','')
modeltables=[]
for name,rows in tables.items():
 cols=[];types=[]
 for col in rows[0]:
  val=next((r[col] for r in rows if r[col] is not None),None)
  isdate=col.endswith('Date') or col in ['Date','MonthStart']
  typ='dateTime' if isdate else 'int64' if isinstance(val,int) else 'double' if isinstance(val,float) else 'string'
  c={'name':col,'dataType':typ,'sourceColumn':col,'summarizeBy':'none'}
  if isdate:c['formatString']='dd mmm yyyy'
  if col.endswith('ID'):c['isHidden']=True
  if name=='Stages' and col=='StageName':c['sortByColumn']='StageOrder'
  if name=='Date' and col=='MonthYear':c['sortByColumn']='YearMonth'
  cols.append(c);types.append('{"'+col+'", '+{'dateTime':'type date','int64':'Int64.Type','double':'type number','string':'type text'}[typ]+'}')
 encoded=base64.b64encode(json.dumps(rows,separators=(',',':')).encode()).decode()
 expr=['let',f'    Source = Table.FromRecords(Json.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64))),','    Typed = Table.TransformColumnTypes(Source, {'+', '.join(types)+'}, "en-US")','in','    Typed']
 tab={'name':name,'columns':cols,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':expr}}]}
 if name=='Opportunities':tab['measures']=[{'name':n,'expression':e,'formatString':fmt,'displayFolder':'Pipeline snapshot' if 'Pipeline' in n or n in ['Open Deals','At Risk Deals','Overdue Deals','Average Current Stage Age','Snapshot Label'] else 'Sales performance','description':n+'; see docs/metric-definitions.md for date and denominator rules.'} for n,(e,fmt) in measures.items()]
 if name=='Opportunities':
  next(m for m in tab['measures'] if m['name']=='Source Outcome Flow SVG')['dataCategory']='ImageUrl'
 if name=='Date':
  tab['dataCategory']='Time';tab['columns'][0]['isKey']=True
 modeltables.append(tab)
rels=[]
def rel(ft,fc,tt,tc,active=True):
 rels.append({'name':str(uuid.uuid5(uuid.NAMESPACE_DNS,ft+fc+tt+tc)),'fromTable':ft,'fromColumn':fc,'toTable':tt,'toColumn':tc,'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection','isActive':active})
for args in [('Opportunities','AccountID','Accounts','AccountID'),('Opportunities','RepID','Sales Reps','RepID'),('Opportunities','StageID','Stages','StageID'),('Opportunities','CloseDate','Date','Date'),('Stage History','OpportunityID','Opportunities','OpportunityID'),('Stage History','StageID','Stages','StageID'),('Activities','OpportunityID','Opportunities','OpportunityID'),('Targets','RepID','Sales Reps','RepID'),('Targets','MonthDate','Date','Date')]:rel(*args)
rel('Opportunities','CreatedDate','Date','Date',False)
# Avoid ambiguous Stage->Opportunity->History alongside Stage->History; history relationship to Opportunity inactive.
next(r for r in rels if r['fromTable']=='Stage History' and r['toTable']=='Opportunities')['isActive']=False
# Account/rep context for history carried explicitly in stage measure (Cohort).
write('VelaCRM.SemanticModel/model.bim',{'name':'Vela CRM','compatibilityLevel':1567,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-US','tables':modeltables,'relationships':rels,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(list(tables))}]}})
write('VelaCRM.SemanticModel/definition.pbism',{'version':'1.0','settings':{}})
write('VelaCRM.pbip',{'version':'1.0','artifacts':[{'report':{'path':'VelaCRM.Report'}}],'settings':{'enableAutoRecovery':True}})
write('VelaCRM.Report/definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../VelaCRM.SemanticModel'}}})
BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
write('VelaCRM.Report/definition/version.json',{'$schema':BASE+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
write('VelaCRM.Report/definition/report.json',{'$schema':BASE+'report/2.0.0/schema.json','themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':'5.55','type':'SharedResources'},'customTheme':{'name':'VelaTheme','reportVersionAtImport':'5.55','type':'RegisteredResources'}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'VelaTheme','path':'VelaTheme.json','type':'CustomTheme'},{'name':'OmbreBackground','path':'OmbreBackground.png','type':'Image'}]}],'settings':{'useEnhancedTooltips':True,'defaultFilterActionIsDataFilter':True,'exportDataMode':'AllowSummarized'}})
theme={'name':'VelaTheme','dataColors':[VIOLET,TEAL,'#4785FF','#FFBD59',PINK,'#7757FF'],'background':WHITE,'foreground':NAVY,'tableAccent':VIOLET,'textClasses':{'title':{'fontFace':'Segoe UI Semibold','fontSize':13,'color':NAVY},'label':{'fontFace':'Segoe UI','fontSize':11,'color':MUTED},'callout':{'fontFace':'Segoe UI Semibold','fontSize':28,'color':NAVY}},'visualStyles':{'*':{'*':{'background':[{'show':True,'color':{'solid':{'color':WHITE}},'transparency':0}],'border':[{'show':True,'color':{'solid':{'color':EDGE}},'radius':12}],'title':[{'show':True,'fontColor':{'solid':{'color':NAVY}},'fontSize':13}]}},'page':{'*':{'background':[{'color':{'solid':{'color':BG}},'transparency':0}]}}}}
theme['visualStyles']['*']['*'].update({'categoryAxis':[{'labelColor':{'solid':{'color':MUTED}},'titleColor':{'solid':{'color':MUTED}},'gridlineColor':{'solid':{'color':EDGE}}}], 'valueAxis':[{'labelColor':{'solid':{'color':MUTED}},'titleColor':{'solid':{'color':MUTED}},'gridlineColor':{'solid':{'color':EDGE}}}], 'legend':[{'labelColor':{'solid':{'color':MUTED}}}], 'visualTooltip':[{'background':{'solid':{'color':'#171D36'}},'titleFontColor':{'solid':{'color':NAVY}},'valueFontColor':{'solid':{'color':NAVY}}}]})
theme['visualStyles']['tableEx']={'*':{'columnHeaders':[{'fontColor':{'solid':{'color':TEAL}},'backColor':{'solid':{'color':'#171D36'}}}], 'values':[{'fontColor':{'solid':{'color':NAVY}},'backColor':{'solid':{'color':WHITE}},'fontSize':10}], 'grid':[{'gridVertical':False,'gridHorizontal':True,'gridHorizontalColor':{'solid':{'color':EDGE}}}]}}
theme['visualStyles']['slicer']={'*':{'items':[{'fontColor':{'solid':{'color':NAVY}},'background':{'solid':{'color':WHITE}}}], 'header':[{'fontColor':{'solid':{'color':MUTED}}}]}}
write('VelaCRM.Report/StaticResources/RegisteredResources/VelaTheme.json',theme);write('design/VelaTheme.json',theme)
def lit(v):
 value=("'"+v.replace("'","''")+"'") if isinstance(v,str) else str(v).lower() if isinstance(v,bool) else str(v)+'D'
 return {'expr':{'Literal':{'Value':value}}}
def longlit(v):return {'expr':{'Literal':{'Value':str(v)+'L'}}}
def color(v):return {'solid':{'color':lit(v)}}
def field(t,n,m=False):return {('Measure' if m else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':n}}
def proj(t,n,m=False):return {'field':field(t,n,m),'queryRef':t+'.'+n,'nativeQueryRef':n,'displayName':{'RepName':'Sales rep','AccountName':'Account','OpportunityName':'Opportunity','AttentionReason':'Attention reason','ExpectedCloseDate':'Expected close','DaysSinceActivity':'Activity age (days)'}.get(n,n)}
shutil.rmtree(ROOT/'VelaCRM.Report/definition/pages',ignore_errors=True)
visualcount=0
pages=['overview','pipeline','performance','accounts']
names=['Executive overview','Pipeline intelligence','Sales performance','Account detail']
write('VelaCRM.Report/definition/pages/pages.json',{'$schema':BASE+'pagesMetadata/1.0.0/schema.json','pageOrder':pages,'activePageName':'overview'})
def visual(page,kind,title,x,y,w,h,roles=None,objects=None,dark=False):
 global visualcount
 visualcount+=1;name=f'v{visualcount:04d}'
 v={'visualType':kind,'drillFilterOtherVisuals':True,'visualContainerObjects':{'title':[{'properties':{'show':lit(bool(title)),'text':lit(title),'fontColor':color(NAVY),'fontSize':lit(13),'bold':lit(True)}}],'background':[{'properties':{'show':lit(True),'color':color('#171034' if dark else WHITE),'transparency':lit(0)}}],'border':[{'properties':{'show':lit(True),'color':color('#7757FF' if dark else EDGE),'radius':lit(12)}}],'general':[{'properties':{'altText':lit(title or 'Report navigation and context')}}]}}
 if roles:v['query']={'queryState':{k:{'projections':[proj(*f) for f in fs]} for k,fs in roles.items()}}
 if objects:v['objects']=objects
 v['visualContainerObjects']['padding']=[{'properties':{k:lit(8) for k in ['top','bottom','left','right']}}]
 v['visualContainerObjects']['subTitle']=[{'properties':{'show':lit(False)}}]
 if kind=='tableEx':
  v['visualContainerObjects']['stylePreset']=[{'properties':{'name':lit('None')}}]
  v.setdefault('objects',{}).setdefault('values',[{'properties':{}}])[0]['properties'].update({'fontColorPrimary':color(NAVY),'fontColorSecondary':color(NAVY),'backColorPrimary':color(WHITE),'backColorSecondary':color('#151B32'),'fontSize':lit(10)})
  v['objects'].setdefault('columnHeaders',[{'properties':{}}])[0]['properties'].setdefault('autoSizeColumnWidth',lit(True))
  v['objects']['columnHeaders'][0]['properties'].setdefault('columnAdjustment',lit('growToFit'))
 if kind=='tableEx':v['objects'].setdefault('grid',[{'properties':{}}])[0]['properties'].setdefault('rowPadding',lit(2))
 if roles and kind in ['barChart','funnel','donutChart'] and 'Category' in roles:
  ct,cn,_=roles['Category'][0]
  palette=({'Qualified':TEAL,'Discovery':'#4785FF','Demo':'#7757FF','Proposal':VIOLET,'Negotiation':PINK,'Closed won':TEAL,'Closed lost':PINK} if ct=='Stages' else {'On track':TEAL,'Needs attention':'#FFBD59'} if ct=='Risk Bands' else {})
  if palette:
   entries=[]
   for label,c in palette.items():
    comparison={'ComparisonKind':0,'Left':field(ct,cn),'Right':{'Literal':{'Value':"'"+label+"'"}}}
    entries.append({'properties':{'fill':color(c)},'selector':{'data':[{'scopeId':{'Comparison':comparison}}]}})
   v.setdefault('objects',{})['dataPoint']=entries
 if kind=='funnel':
  v.setdefault('objects',{})['labels']=[{'properties':{'labelDisplayUnits':lit(0),'labelPrecision':longlit(0),'color':color(NAVY)}}]
 if kind=='gauge':
  v.setdefault('objects',{})['calloutValue']=[{'properties':{'color':color(NAVY),'fontSize':lit(28),'labelPrecision':longlit(1),'labelDisplayUnits':lit(0)}}]
 write(f'VelaCRM.Report/definition/pages/{page}/visuals/{name}/visual.json',{'$schema':BASE+'visualContainer/2.1.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':visualcount,'tabOrder':visualcount},'visual':v})
 return name
def text(page,s,x,y,w,h,size=12,fg=MUTED,dark=False):
 name=visual(page,'textbox','',x,y,w,max(h,44),objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':s,'textStyle':{'fontFamily':'Segoe UI','fontSize':f'{min(size,22)}pt','color':fg}}]}]}}]},dark=dark)
 path=ROOT/f'VelaCRM.Report/definition/pages/{page}/visuals/{name}/visual.json'
 obj=json.loads(path.read_text());obj['visual']['visualContainerObjects']['padding']=[{'properties':{k:lit(0) for k in ['top','bottom','left','right']}}]
 write(str(path.relative_to(ROOT)),obj)
 return name
def card(page,n,x,y,w=276,accent=VIOLET):
 visual(page,'card',n,x,y,w,112,{'Values':[('Opportunities',n,True)]},{'labels':[{'properties':{'color':color(accent),'fontSize':lit(27),'labelDisplayUnits':lit(1000000 if 'Pipeline ACV' in n or n=='Won ACV' else 0),'labelPrecision':longlit(2 if 'ACV' in n else 1 if n in ['Win Rate','Target Attainment'] else 0)}}],'categoryLabels':[{'properties':{'show':lit(False)}}]})
 path=ROOT/f'VelaCRM.Report/definition/pages/{page}/visuals/v{visualcount:04d}/visual.json'
 obj=json.loads(path.read_text());obj['visual']['visualContainerObjects']['border'][0]['properties']['color']=color(accent)
 write(str(path.relative_to(ROOT)),obj)
def chart(page,kind,title,x,y,w,h,cat,val,extra=None):
 roles={'Category':[cat],'Y':[('Opportunities',val,True)]}
 if extra:roles.update(extra)
 name=visual(page,kind,title,x,y,w,h,roles,{'categoryAxis':[{'properties':{'showAxisTitle':lit(False),'fontSize':lit(10),'labelColor':color(MUTED)}}],'valueAxis':[{'properties':{'showAxisTitle':lit(False),'fontSize':lit(10),'labelColor':color(MUTED)}}],'dataPoint':[{'properties':{'defaultColor':color(TEAL if cat[0]=='Sales Reps' else PINK if cat[1]=='LeadSource' else VIOLET)}}]})
 path=ROOT/f'VelaCRM.Report/definition/pages/{page}/visuals/{name}/visual.json'
 obj=json.loads(path.read_text());ordered=cat[0] in ['Date','Stages'];sortfield=field(*cat) if ordered else field('Opportunities',val,True)
 obj['visual']['query']['sortDefinition']={'sort':[{'field':sortfield,'direction':'Ascending' if ordered else 'Descending'}],'isDefaultSort':False}
 write(str(path.relative_to(ROOT)),obj)
def slicer(page,t,n,x,y,w=215):
 label={'RepName':'Sales rep','MonthYear':'Creation month','AccountName':'Account'}.get(n,n)
 visual(page,'slicer','',x,y,w,76,{'Values':[(t,n,False)]},{'data':[{'properties':{'mode':lit('Dropdown')}}],'header':[{'properties':{'show':lit(True),'text':lit(label),'fontColor':color(MUTED),'textSize':lit(10)}}],'items':[{'properties':{'fontColor':color(NAVY),'textSize':lit(11)}}]})
for p,n in zip(pages,names):
 write(f'VelaCRM.Report/definition/pages/{p}/page.json',{'$schema':BASE+'page/2.0.0/schema.json','name':p,'displayName':n,'displayOption':'FitToWidth' if p=='performance' else 'FitToPage','width':1440,'height':1020 if p=='performance' else 900,'objects':{'background':[{'properties':{'color':color(BG),'transparency':lit(0),'image':{'image':{'name':lit('OmbreBackground.png'),'url':{'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':'OmbreBackground'}}},'scaling':lit('Fit')}}}}]}})
 text(p,'VELA  /  CRM',24,20,190,62,19,TEAL,True)
 text(p,n,232,20,780,62,24,NAVY)
 text(p,'CARLA McGHEE\nPortfolio project 02',1130,20,286,62,11,MUTED)
 # Desktop page tabs are the native navigation; this header explicitly marks date scope.
 text(p,'FICTIONAL DATA  •  USD annual contract value  •  Pipeline snapshot: 30 Sep 2026',24,960 if p=='performance' else 835,1392,40,11,MUTED)
 slicer(p,'Sales Reps','Region',24,98)
 slicer(p,'Sales Reps','RepName',251,98)
 slicer(p,'Accounts','Segment',478,98)
 slicer(p,'Accounts','Industry',705,98)
 if p in ['overview','performance']:slicer(p,'Date','Year',932,98);slicer(p,'Date','Quarter',1159,98)
 elif p=='pipeline':slicer(p,'Date','MonthYear',932,98,440)
 else:slicer(p,'Accounts','AccountName',932,98,440)
# Overview
p='overview'
text(p,'Date filters apply to closed sales and targets. Open pipeline cards always show the fixed snapshot.',24,176,1392,36,11)
for i,n in enumerate(['Won ACV','Open Pipeline ACV','Win Rate','Average Sales Cycle']):card(p,n,24+i*352,226,336,TEAL if i in [0,2] else PINK if i==3 else VIOLET)
chart(p,'lineChart','Won ACV · closed-sales momentum',24,356,884,274,('Date','MonthYear',False),'Won ACV')
visual(p,'gauge','Target attainment · 100% quota marker',924,356,492,274,{'Y':[('Opportunities','Target Attainment',True)],'MinValue':[('Opportunities','Gauge Minimum',True)],'MaxValue':[('Opportunities','Gauge Maximum',True)],'TargetValue':[('Opportunities','Gauge Target',True)]},{'dataPoint':[{'properties':{'fill':color(PINK),'target':color(TEAL)}}],'labels':[{'properties':{'color':color(NAVY),'labelPrecision':longlit(1)}}]})
chart(p,'barChart','Open pipeline · current stage',24,648,884,176,('Stages','StageName',False),'Open Pipeline ACV')
visual(p,'donutChart','Pipeline risk · snapshot ACV',924,648,492,176,{'Category':[('Risk Bands','RiskLabel',False)],'Y':[('Opportunities','Pipeline by Risk Band',True)]},{'legend':[{'properties':{'show':lit(True),'position':lit('Right'),'labelColor':color(MUTED),'fontSize':lit(10)}}]})
# Pipeline
p='pipeline'
text(p,'Month selection defines the creation cohort in the stage-reach chart. Pipeline and attention metrics use the snapshot.',24,176,1392,36,11)
for i,n in enumerate(['Open Pipeline ACV','Weighted Pipeline ACV','At Risk Deals','Overdue Deals']):card(p,n,24+i*352,226,336,'#FFBD59' if i>1 else VIOLET)
visual(p,'tableEx','Lead source → outcome · creation cohort · link width = deal count',24,356,884,292,{'Values':[('Opportunities','Source Outcome Flow SVG',True)]},{'grid':[{'properties':{'imageHeight':lit(240),'imageWidth':lit(820),'rowPadding':lit(0),'gridHorizontal':lit(False),'gridVertical':lit(False)}}],'columnHeaders':[{'properties':{'fontColor':color(WHITE),'backColor':color(WHITE),'fontSize':lit(8),'autoSizeColumnWidth':lit(False),'columnAdjustment':lit('fixedWidth')}}],'columnWidth':[{'properties':{'value':lit(840)},'selector':{'metadata':'Opportunities.Source Outcome Flow SVG'}}],'total':[{'properties':{'totals':lit(False)}}]})
chart(p,'funnel','Stage reach · creation cohort',924,356,492,292,('Stages','StageName',False),'Stage Reached Deals')
visual(p,'tableEx','Attention queue · select a deal to inspect',24,650,1392,160,{'Values':[('Opportunities','OpportunityName',False),('Accounts','AccountName',False),('Sales Reps','RepName',False),('Opportunities','AttentionReason',False),('Opportunities','ExpectedCloseDate',False),('Opportunities','DaysSinceActivity',False),('Opportunities','Attention Deal ACV',True)]})
# Performance
p='performance'
text(p,'Closed sales use actual close date. Targets are monthly: use Year and Quarter filters for comparable periods.',24,176,1392,36,11)
for i,n in enumerate(['Won ACV','Won Deals','Average Won ACV','Average Sales Cycle']):card(p,n,24+i*352,226,336,TEAL if i==3 else VIOLET)
visual(p,'scatterChart','Rep performance · bubble size = open pipeline',24,356,688,292,{'Category':[('Sales Reps','RepName',False)],'X':[('Opportunities','Won ACV',True)],'Y':[('Opportunities','Win Rate',True)],'Size':[('Opportunities','Open Pipeline ACV',True)],'Tooltips':[('Opportunities','Won Deals',True),('Opportunities','Average Sales Cycle',True)]},{'categoryAxis':[{'properties':{'showAxisTitle':lit(True),'axisTitle':lit('Won ACV'),'labelColor':color(MUTED)}}],'valueAxis':[{'properties':{'showAxisTitle':lit(True),'axisTitle':lit('Win rate'),'labelColor':color(MUTED)}}]})
chart(p,'clusteredColumnChart','Won ACV and target by close month',728,356,688,292,('Date','MonthYear',False),'Won ACV',{'Y':[('Opportunities','Won ACV',True),('Opportunities','Target ACV',True)]})
visual(p,'tableEx','Rep scorecard · closed-period performance',24,666,1392,270,{'Values':[('Sales Reps','RepName',False),('Opportunities','Won ACV',True),('Opportunities','Target ACV',True),('Opportunities','Target Attainment',True),('Opportunities','Win Rate',True),('Opportunities','Average Sales Cycle',True)]})
# Accounts
p='accounts'
text(p,'Choose an account above. This page shows all closed history and the fixed snapshot of open opportunities.',24,176,1392,36,11)
for i,n in enumerate(['Won ACV','Open Pipeline ACV','Won Deals','At Risk Deals']):card(p,n,24+i*352,226,336,'#FFBD59' if i==3 else VIOLET)
chart(p,'barChart','Won ACV by product',24,356,688,244,('Opportunities','Product',False),'Won ACV')
chart(p,'barChart','Open pipeline by stage',728,356,688,244,('Stages','StageName',False),'Open Pipeline ACV')
visual(p,'tableEx','Opportunity detail',24,618,1392,192,{'Values':[('Opportunities','OpportunityName',False),('Opportunities','Status',False),('Stages','StageName',False),('Opportunities','ExpectedCloseDate',False),('Opportunities','AttentionReason',False),('Opportunities','Last Activity Date',True)]})
# Account drill-through carries the account only, avoiding an inherited closed-date filter.
accountpath=ROOT/'VelaCRM.Report/definition/pages/accounts/page.json'
accountpage=json.loads(accountpath.read_text())
accountpage['type']='Drillthrough'
accountpage['filterConfig']={'filters':[{'name':'AccountDrillFilter','field':field('Accounts','AccountName'),'type':'Categorical','howCreated':'Drillthrough'}]}
accountpage['pageBinding']={'name':'AccountDetailBinding','type':'Drillthrough','acceptsFilterContext':'None','parameters':[{'name':'AccountParameter','boundFilter':'AccountDrillFilter','fieldExpr':field('Accounts','AccountName')}]}
write('VelaCRM.Report/definition/pages/accounts/page.json',accountpage)
# Expected results independently computed for UAT.
won=[o for o in opps if o['Status']=='Won'];lost=[o for o in opps if o['Status']=='Lost'];opened=[o for o in opps if o['Status']=='Open']
expected={'snapshot':SNAP.isoformat(),'opportunities':len(opps),'accounts':len(accounts),'history_rows':len(history),'won_acv':sum(o['ACV'] for o in won),'won_deals':len(won),'lost_deals':len(lost),'win_rate':len(won)/(len(won)+len(lost)),'open_deals':len(opened),'open_pipeline_acv':sum(o['ACV'] for o in opened),'weighted_pipeline_acv':round(sum(o['ACV']*o['Probability'] for o in opened),2),'at_risk_deals':sum(o['IsAtRisk'] for o in opened),'at_risk_pipeline_acv':sum(o['ACV'] for o in opened if o['IsAtRisk']),'overdue_deals':sum(o['IsOverdue'] for o in opened),'target_acv':sum(t['TargetACV'] for t in targets if t['MonthDate']<=SNAP.isoformat()),'average_sales_cycle':statistics.mean(o['SalesCycleDays'] for o in won)}
write('docs/expected-results.json',expected)
(ROOT/'docs/measures.dax').write_text('\n\n'.join(f'{n} =\n{e}' for n,(e,fmt) in measures.items())+'\n')
print(json.dumps(expected,indent=2));print('Native visuals:',visualcount)
