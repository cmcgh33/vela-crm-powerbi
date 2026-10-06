"""Preview source-to-outcome graphics from the same synthetic rows. Not a Desktop screenshot."""
from pathlib import Path
import csv,json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,PathPatch
from matplotlib.path import Path as MPath
from matplotlib.colors import to_rgb
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data/Opportunities.csv').open()));e=json.loads((ROOT/'docs/expected-results.json').read_text())
bg='#070A18';surface='#11152A';edge='#272C4A';fg='#ECF0FF';muted='#A1ACCA';cyan='#26D9EA';pink='#F85BA5';violet='#A875FF'
plt.rcParams.update({'font.family':'DejaVu Sans'})
fig=plt.figure(figsize=(16,10),dpi=180,facecolor=bg);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1440);ax.set_ylim(900,0);ax.axis('off')
def panel(x,y,w,h):ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=12',facecolor=surface,edgecolor=edge))
def text(x,y,s,size=11,c=fg,bold=False):ax.text(x,y,s,fontsize=size,color=c,weight='bold' if bold else 'normal',va='top')
panel(24,20,190,62);text(40,37,'VELA / CRM',17,cyan,True);text(232,28,'Pipeline intelligence',26,fg,True);text(1130,30,'CARLA McGHEE',11,fg,True);text(1130,52,'Portfolio project 02',10,muted)
for x,label,w in [(24,'Region',215),(251,'Sales rep',215),(478,'Segment',215),(705,'Industry',215),(932,'Creation month',440)]:panel(x,98,w,76);text(x+14,110,label,10,muted);text(x+14,135,'All',11)
text(24,184,'Flows and funnel use the selected creation cohort. Pipeline cards show the 30 Sep 2026 snapshot.',10,muted)
for i,(label,v,c) in enumerate([('OPEN PIPELINE',f'${e["open_pipeline_acv"]/1e6:.2f}M',violet),('WEIGHTED PIPELINE',f'${e["weighted_pipeline_acv"]/1e6:.2f}M',cyan),('AT RISK DEALS',str(e['at_risk_deals']),'#FFBD59'),('OVERDUE DEALS',str(e['overdue_deals']),pink)]):
 x=24+i*352;panel(x,226,336,112);text(x+20,244,label,10,muted,True);text(x+20,276,v,28,c,True)
panel(24,356,884,292);text(44,372,'Lead source → outcome',15,fg,True);text(44,399,'Creation cohort · link width represents deal count',9,muted)
f=fig.add_axes([44/1440,1-630/900,844/1440,205/900],facecolor=surface);f.set_xlim(0,1000);f.set_ylim(340,0);f.axis('off')
sources=['Partner','Inbound','Outbound','Event'];outcomes=['Won','Lost','Open'];sc=[cyan,'#4785FF',violet,pink];oc=[cyan,pink,'#FFBD59'];n=collections.Counter((r['LeadSource'],r['Status']) for r in rows);total=len(rows);scale=200/total
source_n=[sum(n[s,o] for o in outcomes) for s in sources];out_n=[sum(n[s,o] for s in sources) for o in outcomes];st=[24+i*24+sum(source_n[:i])*scale for i in range(4)];ot=[35+j*35+sum(out_n[:j])*scale for j in range(3)]
for i,s in enumerate(sources):
 for j,o in enumerate(outcomes):
  count=n[s,o];sy=st[i]+(sum(n[s,x] for x in outcomes[:j])+count/2)*scale;dy=ot[j]+(sum(n[x,o] for x in sources[:i])+count/2)*scale
  verts=[(192,sy),(415,sy),(585,dy),(808,dy)];path=MPath(verts,[MPath.MOVETO,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4]);col=tuple((a+b)/2 for a,b in zip(to_rgb(sc[i]),to_rgb(oc[j])));f.add_patch(PathPatch(path,fill=False,color=col,lw=count*scale*.45,alpha=.6))
for i,s in enumerate(sources):
 f.add_patch(FancyBboxPatch((14,st[i]),178,source_n[i]*scale,boxstyle='round,pad=0,rounding_size=7',facecolor=sc[i],edgecolor='none'));f.text(27,st[i]+18,f'{s} · {source_n[i]}',color=bg,fontsize=9,weight='bold')
for j,o in enumerate(outcomes):
 f.add_patch(FancyBboxPatch((808,ot[j]),178,out_n[j]*scale,boxstyle='round,pad=0,rounding_size=7',facecolor=oc[j],edgecolor='none'));f.text(822,ot[j]+18,f'{o} · {out_n[j]}',color=bg,fontsize=9,weight='bold')
panel(924,356,492,292);text(944,372,'Stage reach',15,fg,True);text(944,399,'Distinct deals · creation cohort',9,muted)
history=list(csv.DictReader((ROOT/'data/Stage_History.csv').open()));counts=[len({r['OpportunityID'] for r in history if int(r['StageID'])==i}) for i in range(1,6)]
for i,(name,count,c) in enumerate(zip(['Qualified','Discovery','Demo','Proposal','Negotiation'],counts,[cyan,'#4785FF','#7757FF',violet,pink])):
 width=300*count/counts[0];x=1170-width/2;y=432+i*38
 ax.add_patch(FancyBboxPatch((x,y),width,27,boxstyle='round,pad=0,rounding_size=4',facecolor=c,edgecolor='none'));text(945,y+5,name,9,muted);text(1360,y+4,str(count),10,fg,True)
panel(24,666,1392,144);text(44,681,'Attention queue',12,fg,True)
text(44,708,'ACCOUNT / OPPORTUNITY',9,cyan,True);text(730,708,'ATTENTION REASON',9,cyan,True);text(1110,708,'EXPECTED CLOSE',9,cyan,True);text(1280,708,'ACTIVITY AGE',9,cyan,True)
flagged=[r for r in rows if r['IsAtRisk']=='1'][:3]
for i,r in enumerate(flagged):
 y=733+i*22;text(44,y,r['OpportunityName'],9);text(730,y,r['AttentionReason'],9,'#FFBD59');text(1110,y,r['ExpectedCloseDate'],9);text(1280,y,r['DaysSinceActivity']+' days',9)
text(24,843,'FICTIONAL DATA  •  Design preview from CRM data; new native visuals require Desktop verification',10,muted)
out=ROOT/'design/pipeline-preview.png';fig.savefig(out,dpi=180,facecolor=bg);print(out)
