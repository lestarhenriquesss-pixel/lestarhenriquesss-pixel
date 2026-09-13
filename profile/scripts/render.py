from __future__ import annotations
from datetime import date, timedelta
from html import escape
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from model import daily_series, validate_collaboration

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/profile'
DATA=ROOT/'profile/data'
FONT='Segoe UI,Arial,Helvetica,sans-serif'
MONO='Consolas,Menlo,monospace'
PALETTES={
 'dark':{'bg':'#090F1C','panel':'#101A2C','inset':'#0C1424','border':'#263850','text':'#ECF4FF','muted':'#A4B5CE','sub':'#70849E','blue':'#509AFF','cyan':'#5DE8E5','amber':'#FFC278','grid':'#263950'},
 'light':{'bg':'#F8FAFF','panel':'#FFFFFF','inset':'#EDF3FC','border':'#D1DCEE','text':'#142740','muted':'#4D627D','sub':'#586D88','blue':'#2563C7','cyan':'#087F8C','amber':'#965407','grid':'#D8E2F1'}
}
ICONS=json.loads((DATA/'icons.json').read_text())
CSS='''
@keyframes orbit{to{transform:rotate(360deg)}}
@keyframes breath{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes trace{to{stroke-dashoffset:-1700}}
@keyframes grow{0%,100%{opacity:.72}35%,75%{opacity:1}}
@keyframes rise{0%{transform:translateY(6px);opacity:1}100%{transform:translateY(0);opacity:1}}
@keyframes draw{0%{stroke-dashoffset:1400}30%,100%{stroke-dashoffset:0}}
@keyframes terminal{0%,4%{clip-path:inset(0 100% 0 0)}40%,96%{clip-path:inset(0 0 0 0)}100%{clip-path:inset(0 100% 0 0)}}
@keyframes cursor{0%,48%{opacity:1}49%,100%{opacity:0}}
@keyframes typingA{0%,2%{opacity:1;clip-path:inset(0 100% 0 0)}12%,43%{opacity:1;clip-path:inset(0 0 0 0)}49%{opacity:1;clip-path:inset(0 100% 0 0)}50%,100%{opacity:0}}
@keyframes typingB{0%,49%{opacity:0;clip-path:inset(0 100% 0 0)}50%{opacity:1;clip-path:inset(0 100% 0 0)}62%,93%{opacity:1;clip-path:inset(0 0 0 0)}99%{opacity:1;clip-path:inset(0 100% 0 0)}100%{opacity:0}}
.orbit{animation:orbit 28s linear infinite}.breath{animation:breath 5s ease-in-out infinite}
.trace{stroke-dasharray:180 1520;animation:trace 10s linear infinite}
.grow{animation:grow 14s ease-in-out infinite}.rise{animation:rise 1.2s ease-out both}
.draw{stroke-dasharray:1400;animation:draw 12s ease-in-out infinite}
.terminal{animation:terminal 16s steps(65,end) infinite}
.cursor{animation:cursor 1.1s steps(1,end) infinite}
.typing-a{animation:typingA 14s steps(48,end) infinite}
.typing-b{opacity:0;animation:typingB 14s steps(48,end) infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.motion{display:none!important}.typing-a{opacity:1!important;clip-path:none!important}.typing-b{display:none!important}.terminal{clip-path:none!important}}
'''

def t(x,y,s,size=18,color='#ECF4FF',weight=400,anchor='start',mono=False,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{MONO if mono else FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>'
def rect(x,y,w,h,fill,stroke='none',rx=16,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'
def line(x,y,x2,y2,col,width=1,extra=''):
    return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{width}" {extra}/>'
def circ(x,y,r,fill,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {extra}/>'
def icon(name,x,y,size,color):
    if name.startswith('text:'):
        return t(x+size/2,y+size*.76,name[5:],size*.66,color,750,'middle',True)
    i=ICONS[name]
    paths=''.join(f'<path d="{p}" fill="{color}"/>' for p in i['paths'])
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{i["viewBox"]}">{paths}</svg>'
def svg(w,h,title,body,defs='',extra_css=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><defs>{defs}</defs><style>{CSS}{extra_css}</style>{body}</svg>'
def frame(w,h,c):
    return rect(1,1,w-2,h-2,c['bg'],c['border'],20)
def write(name,content):
    OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_text(content,encoding='utf-8')
def format_date(s):return date.fromisoformat(s[:10]).strftime('%d/%m/%Y')

def hero(mobile=False):
    w,h=(500,426) if mobile else (1000,350)
    c=PALETTES['dark'];s=frame(w,h,c)
    defs='<linearGradient id="hero-grad" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#090F1C"/><stop offset=".68" stop-color="#0C1B32"/><stop offset="1" stop-color="#123A67"/></linearGradient><radialGradient id="hero-glow"><stop stop-color="#2C87EF" stop-opacity=".22"/><stop offset="1" stop-color="#2C87EF" stop-opacity="0"/></radialGradient>'
    s+=rect(2,2,w-4,h-4,'url(#hero-grad)',rx=20)
    for x in range(20,w,36):s+=line(x,18,x,h-18,'#83ACDA',extra='opacity=".045"')
    for y in range(18,h,36):s+=line(20,y,w-20,y,'#83ACDA',extra='opacity=".045"')
    cx,cy=(413,195) if mobile else (806,174)
    s+=circ(cx,cy,180,'url(#hero-glow)')
    art=''
    for r in [64,105,143]:art+=circ(cx,cy,r,'none',f'stroke="#5799DB" stroke-opacity=".20" stroke-width="1"')
    art+=f'<g class="orbit" style="transform-origin:{cx}px {cy}px">'
    for r,a,col in [(64,-.6,c['amber']),(105,2.2,c['cyan']),(143,4.3,c['blue'])]:
        art+=circ(round(cx+r*math.cos(a),2),round(cy+r*math.sin(a),2),4,col)
    art+='</g>'
    for xx,yy,txt,col in [(cx-89,cy-80,'SQL',c['cyan']),(cx+42,cy-12,'PY',c['blue']),(cx-38,cy+79,'BI',c['amber'])]:
        art+=line(cx,cy,xx+27,yy,col,1,'opacity=".25"')
        art+=rect(xx,yy-21,59,42,c['panel'],c['border'],11)+t(xx+29.5,yy+5,txt,16,col,700,'middle',True)
    art+=circ(cx,cy,25,'#122744',f'stroke="{c["blue"]}"')+icon('diagram-project',cx-12,cy-12,24,c['cyan'])
    s+=f'<g opacity="{.28 if mobile else 1}">{art}</g>'
    x=30 if mobile else 42
    s+=line(x,35,x+31,35,c['amber'],3)
    s+=t(x+43,40,'DADOS / ANÁLISE / DESENVOLVIMENTO',11 if mobile else 13,c['muted'],500,mono=True)
    s+=t(x,124 if mobile else 120,'Lestar',64 if mobile else 68,c['text'],750)
    s+=t(x,190,'Henriques',60 if mobile else 68,c['text'],750)
    s+=t(x,229,'Engenharia de Dados & Business Intelligence',17 if mobile else 19,c['muted'])

    if mobile:
        s+=f'<g class="typing-a">{t(x,275,"Dashboards | ETL / ELT",18,c["cyan"],600,mono=True)}{t(x,302,"Automação",18,c["cyan"],600,mono=True)}</g>'
        s+=f'<g class="typing-b">{t(x,275,"Python | SQL | Power BI",18,c["cyan"],600,mono=True)}{t(x,302,"Dados com visão de negócio",16,c["cyan"],600,mono=True)}</g>'
        s+=line(x,329,w-30,329,c['border'])
        s+=t(x,363,'Decisões mais inteligentes',19,c['text'],600)+t(x,390,'começam com dados.',19,c['text'],600)
    else:
        s+=f'<g class="typing-a">{t(x,270,"Dashboards | ETL / ELT | Automação",20,c["cyan"],600,mono=True)}</g>'
        s+=f'<g class="typing-b">{t(x,270,"Python | SQL | Power BI | TypeScript",20,c["cyan"],600,mono=True)}</g>'
        s+=line(x,294,w-42,294,c['border'])+t(x,325,'Decisões mais inteligentes começam com dados.',19,c['text'],600)
        s+=t(956,325,'LESTAR / DATA',12,c['sub'],500,'end',True)
    return svg(w,h,'Lestar Henriques — Engenharia de Dados e Business Intelligence',s,defs)


def terminal(mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,335) if mobile else (1000,240)
    s=frame(w,h,c)+rect(2,2,w-4,40,c['panel'],rx=18)+line(2,43,w-2,43,c['border'])
    for i,col in enumerate([c['amber'],c['cyan'],c['blue']]):s+=circ(25+i*18,22,4,col)
    s+=t(92,27,'lestar@dados: ~/sobre-mim',12,c['muted'],mono=True)
    s+=t(28,80,'$ whoami',16,c['cyan'],600,mono=True)
    content=t(28,112,'Lestar Henriques',21,c['text'],600,mono=True)
    content+=t(28,144 if mobile else 145,'Dados + análise + desenvolvimento',18,c['muted'],mono=True)
    s+=f'<g class="terminal">{content}</g>'
    s+=t(28,193,'$ propósito',16,c['cyan'],600,mono=True)
    if mobile:
        s+=t(28,229,'Dados confiáveis. Indicadores claros.',18,c['text'])
        s+=t(28,260,'Tecnologia aplicada à rotina.',18,c['text'])
        s+=rect(28,285,9,18,c['amber'],rx=1,extra='class="cursor"')
    else:
        s+=t(180,194,'Dados confiáveis. Indicadores claros. Rotinas automatizadas.',19,c['text'])
        s+=rect(909,179,9,18,c['amber'],rx=1,extra='class="cursor"')
        s+=line(705,69,705,152,c['border'])
        s+=t(738,89,'DA ORIGEM À DECISÃO',11,c['sub'],600,mono=True)
        for i,ico in enumerate(['database','gears','chart-column']):
            xx=743+i*82
            s+=rect(xx,105,40,38,c['inset'],c['border'],9)+icon(ico,xx+10,114,20,c['cyan'] if i!=2 else c['amber'])
            if i<2:s+=line(xx+45,124,xx+77,124,c['blue'],2,'class="breath"')
    return svg(w,h,'Apresentação em terminal: conecto dados, análise e desenvolvimento.',s)

STACKS=[
 ('Engenharia & BI','Integração, indicadores e visualização.','cyan',[
  ('database','SQL','#5DBBFA'),('python','Python','#F8CC58'),('chart-column','Power BI','#F2C811'),('table','Excel','#56C08D'),('gears','Power Query','#56C08D'),('chart-column','Looker','#7CACFF')]),
 ('Back-end & integrações','APIs, regras de negócio e persistência.','blue',[
  ('java','Java','#F19654'),('leaf','Spring','#78C443'),('bolt','FastAPI','#59CDB4'),('code','APIs','#64D3ED'),('database','PostgreSQL','#76ADCE'),('database','MySQL','#EAA767')]),
 ('Aplicações & interfaces','Experiências úteis para quem utiliza os dados.','blue',[
  ('text:TS','TypeScript','#519EFF'),('js','JavaScript','#F4DC58'),('react','React','#64D9F5'),('figma','Figma','#D595FF'),('code','HTML / CSS','#F59E75')]),
 ('Plataforma & automação','Ambiente, versionamento e processos.','cyan',[
  ('docker','Docker','#47B0F5'),('google','GCP','#7CACFF'),('git-alt','Git','#F8856A'),('github','GitHub','#D7E5F8'),('server','Redis','#FF8689'),('google','Workspace','#77C798')])
]

def stack_card(index,c,x=0,y=0,mobile=False):
    title,desc,accent,items=STACKS[index];color=c[accent];w,h=490,(342 if mobile else 240)
    s=rect(1,1,w-2,h-2,c['bg'],c['border'],18)
    s+=rect(1,1,w-2,h-2,'none',color,18,'stroke-width="1.3" class="trace" opacity=".55"')
    s+=t(24,38,title,24,c['text'],650)+t(24,64,desc,14,c['muted'])
    for j,(ico,label,col) in enumerate(items):
        xx=(40+(j%3)*148) if mobile else 26+j*74
        yy=89+(j//3)*107 if mobile else 89
        s+=rect(xx,yy,64,67,c['panel'],c['border'],14)
        s+=icon(ico,xx+16,yy+16,32,col if c is PALETTES['dark'] else (c['blue'] if ico=='github' else col))
        s+=t(xx+32,yy+89,label,14 if mobile else 11.5,c['text'],600,'middle')
    s+=line(24,h-38,466,h-38,c['border'])
    s+=t(24,h-15,['ANÁLISE / CONTEXTO','SERVIÇOS / INTEGRAÇÃO','INTERFACES / EXPERIÊNCIA','PROCESSOS / COLABORAÇÃO'][index],10.5,c['sub'],500,mono=True)
    s+=circ(465,h-19,3,color,'class="breath"')
    return f'<g transform="translate({x},{y})">{s}</g>'

def stack(mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,1416) if mobile else (1000,500)
    s=''
    for i in range(4):
        x,y=(5,i*358) if mobile else ((i%2)*510,(i//2)*260)
        s+=stack_card(i,c,x,y,mobile)
    return svg(w,h,'Tecnologias organizadas em Engenharia e BI, Back-end, Interfaces e Plataforma.',s)


def radar_card(axes,title,subtitle,foot,c,color,kind,x=0,y=0):
    w,h=490,464;cx,cy,r=245,238,116
    s=frame(w,h,c)+t(24,38,title,24,c['text'],650)+t(24,63,subtitle,13,c['muted'])
    count=len(axes)
    def pts(radius,values=None):
        return ' '.join(f'{radius*(values[i]/100 if values else 1)*math.sin(2*math.pi*i/count):.2f},{-radius*(values[i]/100 if values else 1)*math.cos(2*math.pi*i/count):.2f}' for i in range(count))
    grid=''
    for q in [.25,.5,.75,1]:grid+=f'<polygon points="{pts(r*q)}" fill="none" stroke="{c["grid"]}" stroke-width="1"/>'
    for i in range(count):
        a=2*math.pi*i/count;grid+=line(0,0,r*math.sin(a),-r*math.cos(a),c['grid'])
    grid+=f'<g class="orbit" style="animation-duration:18s"><path d="M0,0 L0,-116 A116,116 0 0,1 80,-84 Z" fill="{color}" opacity=".07"/></g>'
    vals=[a['value'] for a in axes]
    grid+=f'<g class="grow"><polygon points="{pts(r,vals)}" fill="{color}" fill-opacity=".13" stroke="{color}" stroke-width="2.3" stroke-linejoin="round"/>'
    for i,v in enumerate(vals):
        a=2*math.pi*i/count;grid+=circ(r*v/100*math.sin(a),-r*v/100*math.cos(a),3.3,color)
    grid+='</g>'
    s+=f'<g transform="translate({cx},{cy})">{grid}</g>'
    for i,axis in enumerate(axes):
        a=2*math.pi*i/count;xx=cx+144*math.sin(a);yy=cy-144*math.cos(a)
        anchor='middle' if abs(math.sin(a))<.1 else ('start' if math.sin(a)>0 else 'end')
        if kind=='languages':
            s+=t(round(xx,2),round(yy,2),axis['label'],15,c['text'],600,anchor)
            val=f'{axis["value"]:g}'.replace('.',',')+' pts'
            s+=t(round(xx,2),round(yy+18,2),val,12.5,c['muted'],400,anchor)
        else:s+=t(round(xx,2),round(yy+4,2),axis['label'],15,c['text'],600,anchor)
    s+=line(24,410,466,410,c['border'])+t(24,434,foot,12,c['muted'])
    return f'<g transform="translate({x},{y})">{s}</g>'

def radars(skills,langs,mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,948) if mobile else (1000,464)
    s=radar_card(skills['axes'],'Mapa de atuação','Áreas de foco e aplicação profissional.','Ênfase declarada · não é nota de proficiência.',c,c['cyan'],'skills',5 if mobile else 0,0)
    s+=radar_card(langs['axes'],'Linguagens no código','Intensidade relativa nos repositórios analisados.','Índice relativo · curva 0,4 · não é percentual.',c,c['blue'],'languages',5 if mobile else 510,484 if mobile else 0)
    return svg(w,h,'Radar técnico: mapa de atuação e índices relativos de linguagens.',s)


def collaboration(data,mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,383) if mobile else (1000,245)
    s=frame(w,h,c)+t(28,36,'COLABORAÇÃO / FORA DA CONTA PESSOAL',11.5 if mobile else 13,c['cyan'],600,mono=True)
    items=[(data['proposed'],'PRs propostos','Propostas de alteração'),(data['merged'],'PRs incorporados','Mudanças integradas'),(data['repositories'],'Repositórios externos','Participação em equipes')]
    if mobile:
        for i,(value,label,sub) in enumerate(items):
            yy=62+i*87
            s+=rect(22,yy,456,76,c['panel'],c['border'],13)
            s+=t(46,yy+53,f'{value:02}',41,c['text'],700,extra='class="rise"')
            s+=t(135,yy+30,label,18,c['text'],650)+t(135,yy+53,sub,13,c['muted'])
        s+=t(28,353,'Snapshot autorizado · '+format_date(data['verified_at']),12,c['muted'])
    else:
        for i,(value,label,sub) in enumerate(items):
            xx=26+i*322
            s+=rect(xx,60,302,132,c['panel'],c['border'],14)
            s+=t(xx+20,119,f'{value:02}',48,c['text'],700,extra=f'class="rise" style="animation-delay:{i*.13}s"')
            s+=t(xx+103,101,label,16,c['text'],600)+t(xx+103,126,sub,12,c['muted'])
            s+=line(xx+20,164,xx+282,164,c['border'],3)
            s+=line(xx+20,164,xx+20+262*([1,data['merged']/max(1,data['proposed']),1][i]),164,c['cyan'] if i==1 else c['blue'],3,'class="breath"')
        s+=t(28,223,'Contagens agregadas · histórico acessível até '+format_date(data['verified_at']),12,c['muted'])
        s+=t(w-28,223,'Sem expor projetos privados',12,c['sub'],400,'end')
    return svg(w,h,f'Colaboração externa: {data["proposed"]} PRs propostos, {data["merged"]} incorporados, {data["repositories"]} repositórios.',s)


def history(data,mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,264) if mobile else (1000,284)
    end=date.fromisoformat(data['verified_at']);start=end-timedelta(days=90)
    days=daily_series(data['days'],start.isoformat(),end.isoformat())
    bins=[sum(d['count'] for d in days[i:i+7]) for i in range(0,91,7)]
    s=frame(w,h,c)+t(26,37,'Ritmo de colaboração',22,c['text'],650)
    s+=t(26,60,'PRs propostos por semana · últimos 91 dias',12,c['muted'])
    left,right,top,bottom=44,w-33,88,h-58
    maximum=max(max(bins),1)
    for i in range(maximum+1):
        yy=bottom-(bottom-top)*i/maximum
        s+=line(left,yy,right,yy,c['grid'],extra='stroke-dasharray="3 6"')
        s+=t(left-12,yy+4,i,11,c['sub'],anchor='end')
    coords=[(left+i*(right-left)/(len(bins)-1),bottom-v*(bottom-top)/maximum) for i,v in enumerate(bins)]
    points=' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)
    area=f'{left},{bottom} '+points+f' {right},{bottom}'
    s+=f'<polygon points="{area}" fill="{c["blue"]}" opacity=".09"/>'
    s+=f'<polyline points="{points}" fill="none" stroke="{c["blue"]}" stroke-width="2.5" stroke-linejoin="round" class="draw"/>'
    for (x,y),v in zip(coords,bins):
        if v:s+=circ(x,y,4,c['cyan'])+t(x,y-10,v,12,c['text'],600,'middle')
    for i in [0,4,8,12]:
        d=start+timedelta(days=i*7)
        s+=t(coords[i][0],bottom+25,d.strftime('%d/%m'),11,c['sub'],anchor='middle')
    s+=t(26,h-15,'Recorte de PRs externos; não representa todos os commits.',11,c['muted'])
    return svg(w,h,'Histórico semanal de pull requests externos, não de todos os commits.',s)


def calendar(data,mobile=False,theme='dark'):
    c=PALETTES[theme];w,h=(500,560) if mobile else (1000,320)
    s=frame(w,h,c)+t(27,38,'Mapa de colaboração',22,c['text'],650)
    s+=t(27,63,'Um bloco por dia · altura = PRs propostos',12,c['muted'])
    end=date.fromisoformat(data['verified_at']);start=end-timedelta(days=90)
    days=daily_series(data['days'],start.isoformat(),end.isoformat())

    ox,oy=(142,117) if mobile else (192,109)
    step=19 if mobile else 22
    for col in range(13):
        for row in range(7):
            d=days[col*7+row];n=d['count'];z=n*12
            x=ox+(col-row)*step;y=oy+(col+row)*step*.42
            topcol=c['cyan'] if n else c['panel'];side=c['blue'] if n else c['border']
            p=f'M{x},{y-z} l{step-2},{-(step-2)*.42} l{step-2},{(step-2)*.42} l{-step+2},{(step-2)*.42} Z'
            s+=f'<path d="{p}" fill="{topcol}" stroke="{c["border"]}" stroke-width=".6"><title>{d["date"]}: {n} PRs</title></path>'
            if n:
                s+=f'<path d="M{x},{y-z} l{step-2},{(step-2)*.42} v{z} l{-step+2},{-(step-2)*.42} Z" fill="{side}" opacity=".75"/>'
                s+=f'<path d="M{x+step-2},{y-z+(step-2)*.42} l{step-2},{-(step-2)*.42} v{z} l{-step+2},{(step-2)*.42} Z" fill="{side}" opacity=".45"/>'
    sx,sy=(70,355) if mobile else (700,108)
    if not mobile:s+=line(658,86,658,272,c['border'])
    s+=t(sx,sy-20,'TRILHA / SNAKE',11,c['cyan'],600,mono=True)
    cell=18 if mobile else 17;gap=4
    route=[]
    for row in range(7):
        for col in range(13):
            xx=sx+col*(cell+gap);yy=sy+row*(cell+gap)
            n=days[col*7+row]['count']
            fill=c['blue'] if n==1 else (c['cyan'] if n>1 else c['panel'])
            s+=rect(xx,yy,cell,cell,fill,c['border'],3)
        cols=range(13) if row%2==0 else range(12,-1,-1)
        route.extend([(sx+col*(cell+gap)+cell/2,sy+row*(cell+gap)+cell/2) for col in cols])
    key='@keyframes snake{'+''.join(f'{i*100/(len(route)-1):.4f}%{{transform:translate({x:.2f}px,{y:.2f}px)}}' for i,(x,y) in enumerate(route))+'}'
    for i in range(6):
        s+=f'<g class="motion" style="animation:snake 24s linear infinite;animation-delay:{-i*.22}s;opacity:{.24+i*.12}">{circ(0,0,cell*.39,c["amber"] if i==5 else c["cyan"])}</g>'
    labely=sy+7*(cell+gap)+20
    s+=t(sx,labely,'Movimento decorativo sobre dados reais.',10.5,c['muted'])
    s+=t(27,h-18,format_date(start.isoformat())+' a '+format_date(end.isoformat())+' · dias em UTC',11,c['muted'])
    return svg(w,h,'Calendário isométrico e snake com dados agregados de pull requests externos.',s,extra_css=key)


def footer(mobile=False):
    c=PALETTES['dark'];w,h=(500,144) if mobile else (1000,125)
    s=frame(w,h,c);xs=[45,180,315,450] if mobile else [80,360,640,920]
    yy=48 if mobile else 54
    s+=line(xs[0],yy,xs[-1],yy,c['border'],2)
    s+=line(xs[0],yy,xs[-1],yy,c['cyan'],2,'class="trace"')
    for x,label,col in zip(xs,['DADOS','CONTEXTO','DECISÃO','RESULTADO'],[c['blue'],c['cyan'],c['cyan'],c['amber']]):
        s+=circ(x,yy,7,c['bg'],f'stroke="{col}" stroke-width="2"')+circ(x,yy,3,col,'class="breath"')
        s+=t(x,yy+34,label,11,col,600,'middle',True)
    s+=t(w/2,h-16,'Lestar Henriques · Engenharia de Dados & BI',11,c['muted'],anchor='middle')
    return svg(w,h,'Dados, contexto, decisão, resultado.',s)


def links():
    for name,label,ico,color in [('portfolio','Portfólio','arrow-up-right-from-square','#FFC278'),('linkedin','LinkedIn','text:in','#7EBAFF'),('email','Contato','envelope','#68DDD9')]:
        s=rect(1,1,158,40,'#111C2E','#304762',11)+icon(ico,17,12,18,color)+t(44,27,label,15,'#E8F2FF',600)
        write(f'link-{name}.svg',svg(160,42,label,s))


def static_svg(content):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root=ET.fromstring(content)
    for parent in list(root.iter()):
        for node in list(parent):
            if node.tag.endswith('style') or set(node.get('class','').split()) & {'motion','typing-b'}:
                parent.remove(node)
    for node in root.iter():
        if 'style' in node.attrib:
            value=re.sub(r'animation[^;]*(;|$)','',node.attrib['style'])
            if value:node.attrib['style']=value
            else:node.attrib.pop('style')
    return ET.tostring(root,encoding='unicode')


def main():
    skills=json.loads((DATA/'skills.json').read_text());langs=json.loads((DATA/'languages.json').read_text());collab=json.loads((DATA/'collaboration.json').read_text())
    validate_collaboration(collab)
    for mobile in [False,True]:
        suffix='-mobile' if mobile else ''
        write('hero'+suffix+'.svg',hero(mobile));write('footer'+suffix+'.svg',footer(mobile))
        for theme in PALETTES:
            for name,fn in [('terminal',lambda:terminal(mobile,theme)),('stack',lambda:stack(mobile,theme)),('radars',lambda:radars(skills,langs,mobile,theme)),('collaboration',lambda:collaboration(collab,mobile,theme)),('history',lambda:history(collab,mobile,theme)),('calendar',lambda:calendar(collab,mobile,theme))]:
                write(f'{name}{suffix}-{theme}.svg',fn())
    links()
    for path in list(OUT.glob('*.svg')):
        if not path.stem.endswith('-static'):
            write(path.stem+'-static.svg',static_svg(path.read_text()))
    print('Recursos SVG renderizados:',len(list(OUT.glob('*.svg'))))
if __name__=='__main__':main()
