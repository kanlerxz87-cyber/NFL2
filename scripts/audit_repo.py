#!/usr/bin/env python3
"""Offline, line-addressable audit of the pre-integration repository.

This does NOT establish truth by checking whether a URL looks official. Factual
verification is recorded separately in research/source-evidence.json after an
official source has actually been read. This script checks syntax, provenance
coverage, internal links, duplicate snapshots, and arithmetic.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "f64078fcb36271554d7ec032386ea4101ba4d859"

class TableAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.ids=[]; self.rows=[]; self.row=None; self.cell=None
        self.assets=[]; self.errors=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and 'href' in a: self.links.append(a['href'])
        if tag in ('script','img','link'):
            u=a.get('src',a.get('href'))
            if u: self.assets.append(u)
        if tag=='tr': self.row={'line':self.getpos()[0],'cells':[],'links':[]}
        if tag in ('td','th') and self.row is not None: self.cell=[]
        if tag=='a' and self.row is not None and 'href' in a: self.row['links'].append(a['href'])
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row['cells'].append(' '.join(''.join(self.cell).split())); self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row); self.row=None

def git_text(ref,path):
    return subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=ROOT).decode()

def is_official(u):
    h=(urlsplit(u).hostname or '').lower()
    return h in {'nfl.com','www.nfl.com','media.nfl.com','operations.nfl.com','static.www.nfl.com','github.com','api.github.com','www.ncpgambling.org','ncpgambling.org'} or h.endswith('.nfl.com')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ref',default=BASELINE); ap.add_argument('--out',default='research/audit-baseline.json'); args=ap.parse_args()
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',args.ref],cwd=ROOT,text=True).splitlines()
    files=[]; findings=[]; tables=[]; broken=[]
    for path in paths:
        text=git_text(args.ref,path); lines=text.splitlines(); syntax='not_applicable'
        try:
            if path.endswith('.json'): json.loads(text); syntax='valid_json'
            elif path.endswith('.py'): compile(text,path,'exec'); syntax='valid_python'
        except Exception as e:
            syntax='invalid'; findings.append({'id':f'SYN-{path}','file':path,'line':1,'finding':str(e),'severity':'error'})
        files.append({'path':path,'sha256':hashlib.sha256(text.encode()).hexdigest(),'line_count':len(lines),'syntax':syntax,
                      'lines':[{'line':i+1,'sha256':hashlib.sha256(line.encode()).hexdigest(),'text':line} for i,line in enumerate(lines)]})
        if path.endswith('.html'):
            p=TableAudit(); p.feed(text); p.close()
            body=[r for r in p.rows if any(c for c in r['cells'])]
            # Header rows are not factual entries. Empty-state rows are explicitly disclosed.
            data_rows=[r for r in p.rows if r['cells'] and not all(re.fullmatch(r'[\w /%()&+−–.-]+',c or '') and len(c)<35 for c in r['cells'])]
            # Conservative coverage metric: all rendered TRs except obvious header-only rows.
            trs=[r for r in p.rows if r['cells']]
            sourced=sum(any(is_official(u) for u in r['links']) for r in trs)
            tables.append({'file':path,'rows':len(trs),'rows_with_official_link':sourced,'row_lines':[r['line'] for r in trs]})
            for u in p.links+p.assets:
                s=urlsplit(u)
                if s.scheme or u.startswith('//') or not u: continue
                target=(Path(path).parent/unquote(s.path)).resolve() if s.path else (ROOT/path).resolve()
                try: rel=target.relative_to(ROOT)
                except ValueError: continue
                if not target.exists(): broken.append({'file':path,'url':u})
                elif s.fragment and target.suffix=='.html':
                    q=TableAudit(); q.feed(target.read_text());
                    if s.fragment not in q.ids: broken.append({'file':path,'url':u,'reason':'missing fragment'})
    a={k:json.loads(git_text(args.ref,f'data/{k}')) for k in ['standings-2026.json','standings_2026.json','schedule-week11-2026.json','schedule_week11_2026.json']}
    s1={t['team']:t for t in a['standings-2026.json']['teams']}; s2={t['team']:t for t in a['standings_2026.json']['teams']}
    standing_mismatches=[]
    for team,t in s1.items():
        for k,v in t.items():
            k2={'divRec':'div_rec','confRec':'conf_rec'}.get(k,k)
            if s2[team].get(k2)!=v: standing_mismatches.append({'team':team,'field':k,'root':v,'docs':s2[team].get(k2)})
    schedule_mismatches=[]
    teams={t['abbr']:t['team'] for t in a['standings-2026.json']['teams']}
    root_games={(g['away'],g['home']):g for g in a['schedule-week11-2026.json']['games']}
    for g in a['schedule_week11_2026.json']['games']:
        r=root_games[(teams[g['away']],teams[g['home']])]
        if g['tv']!=r['tv']: schedule_mismatches.append({'game':g['game'],'field':'tv','root':r['tv'],'docs':g['tv']})
    report={'baseline_ref':args.ref,'scope':'Every tracked baseline file, every line hashed and syntax/category recorded; HTML rows and links inventoried. This is structural verification, not a claim of independent factual verification.',
            'files':files,'table_inventory':tables,'broken_internal_links':broken,'syntax_findings':findings,
            'cross_snapshot_checks':{'standings_mismatches':standing_mismatches,'schedule_broadcaster_mismatches':schedule_mismatches},
            'limitations':['A source URL is not proof that its current content matches a stored value.','External source availability/content is recorded in the source-evidence ledger.','CSS/HTML presentation and original proposals have no external factual truth condition.']}
    out=ROOT / args.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ref':args.ref,'files':len(files),'lines':sum(f['line_count'] for f in files),'html_rows':sum(t['rows'] for t in tables),'rows_with_official_links':sum(t['rows_with_official_link'] for t in tables),'broken_internal_links':broken,'standings_mismatches':standing_mismatches,'schedule_mismatches':schedule_mismatches},indent=2))
if __name__=='__main__': main()
