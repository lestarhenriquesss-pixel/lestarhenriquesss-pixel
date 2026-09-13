from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from model import aggregate_prs, language_axes, save_validated, validate_collaboration

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'profile/data'
API='https://api.github.com'


def request(path: str, token: str=''):
    headers={'Accept':'application/vnd.github+json','User-Agent':'Lestar-Profile-Assets',
             'X-GitHub-Api-Version':'2022-11-28'}
    if token:headers['Authorization']='Bearer '+token
    req=urllib.request.Request(API+path,headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=20) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            if error.code>=500 and attempt<2:time.sleep(2**attempt);continue

            raise RuntimeError('Consulta GitHub indisponível (HTTP '+str(error.code)+')') from None
        except (urllib.error.URLError,TimeoutError):
            if attempt<2:time.sleep(2**attempt);continue
            raise RuntimeError('Consulta GitHub indisponível (conexão)') from None
    raise RuntimeError('Não foi possível concluir a consulta')


def refresh_languages(config: dict, today: str):
    token=os.environ.get('GITHUB_TOKEN','')
    totals: Counter[str]=Counter()
    user=config['username']
    for name in config['public_repositories']:
        path='/repos/'+urllib.parse.quote(user,safe='')+'/'+urllib.parse.quote(name,safe='')
        info=request(path,token)
        if info.get('private') or info.get('fork'):
            raise RuntimeError('O conjunto de repositórios públicos mudou; revisar o escopo antes de atualizar')
        values=request(path+'/languages',token)
        if not isinstance(values,dict):raise RuntimeError('Resposta de linguagens inválida')
        for lang,value in values.items():
            if type(value) is not int or value<0:raise RuntimeError('Contagem inválida')
            if lang not in config['excluded_languages']:totals[lang]+=value
    curve=config.get('curve',0.4)
    axes=language_axes(dict(totals),curve)
    out={'mode':'public_bytes','verified_at':today,'generated_at':today,'curve':curve,
         'source':'GitHub REST API /repos/{owner}/{repo}/languages',
         'scope':'Repositórios públicos selecionados em profile/data/config.json; sem forks.',
         'bytes':dict(totals),'axes':axes,
         'note':'Índice relativo em curva explícita; share contém porcentagem real, mas não é a escala do radar.'}
    save_validated(DATA/'languages.json',out,lambda x:language_axes(x['bytes'],x['curve']))


def refresh_collaboration(config: dict,today: str):
    enabled=os.environ.get('REFRESH_AUTHORIZED_AGGREGATES','').lower()=='true'
    if not enabled:
        print('Agregado autorizado preservado: atualização privada não ativada.');return
    token=os.environ.get('METRICS_TOKEN','')
    if not token:raise RuntimeError('METRICS_TOKEN não configurado; agregado preservado')
    user=config['username']
    if request('/user',token).get('login','').lower()!=user.lower():
        raise RuntimeError('A credencial não corresponde ao perfil; agregado preservado')
    query='is:pr author:'+user+' -user:'+user
    items=[];page=1;total=None
    while True:
        path='/search/issues?'+urllib.parse.urlencode({'q':query,'per_page':100,'page':page,'sort':'created','order':'asc'})
        result=request(path,token)
        if result.get('incomplete_results') or result.get('total_count',0)>1000:
            raise RuntimeError('Busca incompleta; agregado preservado')
        if total is None:total=result['total_count']
        if result['total_count']!=total:raise RuntimeError('Busca alterada durante a paginação; tentar novamente')
        batch=result['items'];items.extend(batch)
        if len(items)>=total:break
        if not batch:raise RuntimeError('Paginação incompleta; agregado preservado')
        page+=1
    if len(items)!=total:raise RuntimeError('Busca inconsistente; agregado preservado')
    out=aggregate_prs(items,today)
    del items
    old=json.loads((DATA/'collaboration.json').read_text())
    if any(out[k]<old[k] for k in ('proposed','merged','repositories')):
        raise RuntimeError('Possível redução de escopo; validar manualmente antes de substituir o agregado')
    save_validated(DATA/'collaboration.json',out,validate_collaboration)


def main():
    config=json.loads((DATA/'config.json').read_text())
    today=datetime.now(timezone.utc).date().isoformat()
    failures=0
    for label,fn in [('Linguagens públicas',refresh_languages),('Colaboração agregada',refresh_collaboration)]:
        try:fn(config,today);print(label+': etapa concluída.')
        except Exception as exc:
            failures+=1

            message=str(exc) if type(exc) is RuntimeError else type(exc).__name__
            print(label+': último snapshot mantido. '+message,file=sys.stderr)
    print('Atualização finalizada; etapas sem nova coleta:',failures)

if __name__=='__main__':main()
