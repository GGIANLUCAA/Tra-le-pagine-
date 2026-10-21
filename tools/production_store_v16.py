"""Restore a checkpoint only from this repository's V16 workflow; never execute archive content."""
import argparse
import json
import os
import urllib.request
import urllib.error
import zipfile
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from production_runner_v16 import restore

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def api(route):
    repo=os.environ['GITHUB_REPOSITORY']
    req=urllib.request.Request('https://api.github.com/repos/'+repo+route,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    return json.load(urllib.request.urlopen(req,timeout=60))

def recover(workspace):
    try:runs=api('/actions/workflows/production-runner-v16.yml/runs?branch=main&status=completed&per_page=50')['workflow_runs']
    except urllib.error.HTTPError as exc:
        if exc.code==404:return False
        raise
    for run in runs:
        artifacts=api('/actions/runs/'+str(run['id'])+'/artifacts?per_page=100')['artifacts']
        candidates=[a for a in artifacts if not a.get('expired') and a['name']=='production-workspace-v16-'+str(run['id'])]
        if not candidates:continue
        artifact=candidates[0]
        req=urllib.request.Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/actions/artifacts/'+str(artifact['id'])+'/zip',headers={'Authorization':'Bearer '+os.environ['GH_TOKEN']})
        opener=urllib.request.build_opener(NoRedirect)
        try:
            response=opener.open(req,timeout=60)
        except urllib.error.HTTPError as exc:
            if exc.code not in (301,302,303,307,308):raise
            location=exc.headers['Location']
            if not location.startswith('https://'):raise ValueError('Redirect artifact non HTTPS')
            # Do not forward the GitHub token to the signed storage URL.
            response=urllib.request.urlopen(location,timeout=180)
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/'artifact.zip'
            with response,archive.open('wb') as target:
                total=0
                while chunk:=response.read(1024*1024):
                    total+=len(chunk)
                    if total>4_000_000_000:raise ValueError('Checkpoint oltre il limite di trasferimento')
                    target.write(chunk)
            with zipfile.ZipFile(archive) as z:
                member=z.getinfo('workspace-v16.tar')
                if member.file_size>6_000_000_000:raise ValueError('Checkpoint troppo grande')
                target=Path(temp)/'workspace.tar'
                with z.open(member) as src,target.open('wb') as dst:
                    import shutil;shutil.copyfileobj(src,dst)
            restore(target,workspace)
        print('Checkpoint ripristinato dal workflow V16, run '+str(run['id']))
        return True
    print('Nessun checkpoint V16 recuperabile: usare lo stato persistente senza rigenerare master mancanti.')
    return False

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',default='output/production-v16');a=p.parse_args();recover(a.workspace)
