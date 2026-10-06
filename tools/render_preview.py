"""Render a design preview from the same fictional data; not a Desktop screenshot."""
from pathlib import Path
import csv,json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data/Opportunities.csv').open()));reps={r['RepID']:r for r in csv.DictReader((ROOT/'data/Sales_Reps.csv').open())}
e=json.loads((ROOT/'docs/expected-results.json').read_text())
navy='#ECF0FF';purple='#A875FF';teal='#26D9EA';muted='#A1ACCA';bg='#070A18';pink='#F85BA5';surface='#11152A';edge='#272C4A'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(16,10),dpi=180,facecolor=bg)
ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1440);ax.set_ylim(900,0);ax.axis('off')
def panel(x,y,w,h,c=surface,r=12):ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=c,edgecolor=edge if c==surface else '#7757FF',linewidth=.8))
def text(x,y,s,size=11,c=navy,weight='normal'):ax.text(x,y,s,fontsize=size,color=c,weight=weight,va='top')
panel(24,20,190,62,'#171034');text(40,38,'VELA / CRM',17,teal,'bold');text(232,28,'Executive overview',26,navy,'bold');text(1130,30,'CARLA McGHEE',11,navy,'bold');text(1130,52,'Portfolio project 02',10,muted)
for x,label in [(24,'Region'),(251,'Sales rep'),(478,'Segment'),(705,'Industry'),(932,'Year'),(1159,'Quarter')]:
 panel(x,98,215,66);text(x+14,110,label,9,muted);text(x+14,132,'All',11);text(x+186,132,'⌄',11,muted)
text(24,182,'Date filters apply to closed sales and targets. Open pipeline shows the 30 Sep 2026 snapshot.',10,muted)
metrics=[('WON ACV',f'${e["won_acv"]/1e6:.2f}M',teal),('OPEN PIPELINE',f'${e["open_pipeline_acv"]/1e6:.2f}M',purple),('WIN RATE',f'{e["win_rate"]:.1%}',teal),('TARGET ATTAINMENT',f'{e["won_acv"]/e["target_acv"]:.1%}',pink)]
for i,(label,val,c) in enumerate(metrics):
 x=24+i*352;panel(x,226,336,112);ax.plot([x+20,x+80],[226,226],color=c,lw=2);text(x+20,245,label,10,muted,'bold');text(x+20,274,val,30,c,'bold')
def chart_axes(x,y,w,h,title):
 panel(x,y,w,h);text(x+20,y+16,title,12,navy,'bold')
 return fig.add_axes([(x+62)/1440,1-(y+h-36)/900,(w-92)/1440,(h-85)/900],facecolor=surface)
months=[f'{y}-{m:02d}' for y in [2025,2026] for m in range(1,13) if f'{y}-{m:02d}'<='2026-09']
trend=collections.defaultdict(float)
for r in rows:
 if r['Status']=='Won':trend[r['CloseDate'][:7]]+=float(r['ACV'])
a=chart_axes(24,356,688,286,'Won ACV by close month');ys=[trend[m]/1e6 for m in months];a.plot(range(len(months)),ys,color=purple,lw=12,alpha=.06);a.plot(range(len(months)),ys,color=purple,lw=7,alpha=.12);a.plot(range(len(months)),ys,color=purple,lw=2.8);a.fill_between(range(len(months)),ys,color=purple,alpha=.09);a.set_xticks([0,4,8,12,16,20],['Jan 25','May 25','Sep 25','Jan 26','May 26','Sep 26']);a.set_ylabel('USD millions',color=muted,fontsize=9);a.grid(axis='y',color=edge,alpha=.8);a.tick_params(labelsize=9,colors=muted);a.spines[['left','bottom']].set_visible(False)
stagevals={i:sum(float(r['ACV']) for r in rows if r['Status']=='Open' and int(r['StageID'])==i)/1e6 for i in range(1,6)}
a=chart_axes(728,356,688,286,'Current open pipeline by stage');a.barh(['Qualified','Discovery','Demo','Proposal','Negotiation'],list(stagevals.values()),color=[teal,'#4785FF','#7757FF',purple,pink],height=.58);a.invert_yaxis();a.set_xlabel('USD millions',color=muted,fontsize=9);a.tick_params(labelsize=9,colors=muted);a.grid(axis='x',color=edge,alpha=.8);a.spines[['left','bottom']].set_visible(False)
for x,title,key,labels in [(24,'Won ACV by region','region',['West','Central','East']),(490,'Won ACV by lead source','source',['Partner','Inbound','Outbound','Event'])]:
 a=chart_axes(x,660,450,150,title)
 vals=[sum(float(r['ACV']) for r in rows if r['Status']=='Won' and (reps[r['RepID']]['Region'] if key=='region' else r['LeadSource'])==l)/1e6 for l in labels]
 a.barh(labels,vals,color=teal if key=='region' else purple,height=.56);a.invert_yaxis();a.tick_params(labelsize=8,colors=muted);a.spines[['left','bottom']].set_visible(False);a.grid(axis='x',color=edge,alpha=.8)
panel(956,660,460,150);text(978,680,'AT RISK PIPELINE ACV',10,muted,'bold');text(978,708,f'${e["at_risk_pipeline_acv"]/1e6:.2f}M',30,'#FFBD59','bold');text(978,759,f'{e["at_risk_deals"]} deals need attention',10,muted)
text(24,843,'FICTIONAL DATA  •  USD annual contract value  •  Design preview; Desktop rendering pending',10,muted)
p=ROOT/'design/executive-preview.png';p.parent.mkdir(exist_ok=True);fig.savefig(p,dpi=180,facecolor=bg);print(p)
