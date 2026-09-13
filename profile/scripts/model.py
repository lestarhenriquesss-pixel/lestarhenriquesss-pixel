from __future__ import annotations
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import json
import os
import tempfile
from typing import Any, Callable


def date_value(value: str) -> date:
    return date.fromisoformat(value[:10])


def validate_collaboration(data: dict[str, Any]) -> None:
    for key in ('proposed','merged','repositories'):
        if type(data.get(key)) is not int or data[key]<0:
            raise ValueError(f'Contagem inválida: {key}')
    if data['merged']>data['proposed'] or data['repositories']>data['proposed']:
        raise ValueError('Totais inconsistentes')
    end=date_value(data['verified_at'])
    for day,n in data['days'].items():
        if date_value(day)>end or type(n) is not int or n<0:
            raise ValueError('Data ou contagem inválida')
    if sum(data['days'].values())!=data['proposed']:
        raise ValueError('O calendário de PRs não corresponde ao total')


def aggregate_prs(items: list[dict[str, Any]], verified_at: str) -> dict[str, Any]:
    days: Counter[str]=Counter()
    repositories=set()
    merged=0
    for item in items:
        day=date_value(item['created_at']).isoformat()
        days[day]+=1
        repositories.add(item['repository_url'])
        merged+=bool(item.get('pull_request',{}).get('merged_at'))
    out={'proposed':len(items),'merged':int(merged),'repositories':len(repositories),
         'days':dict(sorted(days.items())), 'verified_at':verified_at,
         'scope':'PRs de autoria própria fora da conta pessoal, no acesso autorizado; UTC.',
         'mode':'authorized_snapshot'}
    validate_collaboration(out)
    return out


def save_validated(path: Path, data: Any, validator: Callable[[Any],None]) -> None:
    validator(data)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False) as f:
            temp=f.name
            json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
        os.replace(temp,path)
    finally:
        if temp and os.path.exists(temp):os.unlink(temp)


def language_axes(raw: dict[str,int], curve: float=0.4, limit: int=6) -> list[dict[str,Any]]:
    if not raw or any(type(n) is not int or n<0 for n in raw.values()) or sum(raw.values())<=0:
        raise ValueError('Distribuição de linguagens vazia ou inválida')
    if not 0<curve<=1:raise ValueError('Curva fora do intervalo')
    total=sum(raw.values());largest=max(raw.values())
    return [{'label':name,'value':round(100*(n/largest)**curve,2),
             'share':round(100*n/total,2)}
            for name,n in sorted(raw.items(),key=lambda x:(-x[1],x[0]))[:limit]]


def daily_series(values: dict[str,int], start: str, end: str) -> list[dict[str,Any]]:
    first,last=date_value(start),date_value(end)
    if first>last:raise ValueError('Intervalo invertido')
    for key,n in values.items():
        if date_value(key)>last or type(n) is not int or n<0:
            raise ValueError('Dia fora do intervalo ou contagem inválida')
    return [{'date':(first+timedelta(days=i)).isoformat(),
             'count':values.get((first+timedelta(days=i)).isoformat(),0)}
            for i in range((last-first).days+1)]


def calendar_stats(days: list[dict[str,Any]]) -> dict[str,int]:
    longest=run=0
    for d in days:
        run=run+1 if d['count']>0 else 0;longest=max(run,longest)
    current=0
    eligible=days[:-1] if days and days[-1]['count']==0 else days
    for d in reversed(eligible):
        if not d['count']:break
        current+=1
    return {'total':sum(d['count'] for d in days),'active_days':sum(d['count']>0 for d in days),
            'current_streak':current,'longest_streak':longest}
