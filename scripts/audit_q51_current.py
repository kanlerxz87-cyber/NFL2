#!/usr/bin/env python3
"""Current-tree structural audit: every tracked file hashed and line-counted;
JSON/CSV/Python/JS syntax checked; every HTML table row and internal link inventoried.
This is NOT a claim that a URL prefix proves factual agreement. Factual evidence
is recorded separately in research/q51/source-evidence.json and current-review.json.
"""
from __future__ import annotations
import csv, hashlib, io, json, subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research'/'q51'/'current-audit.json'
NFL_HOSTS={'nfl.com','www.nfl.com','media.nfl.com','operations.nfl.com','static.www.nfl.com','nextgenstats.nfl.com'}
CLUB_HOSTS={urlsplit(c['home']).hostname for c in json.loads((ROOT/'collectors'/'q51'/'sources.json').read_text())['clubs']}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.links=[]; self.assets=[]; self.ids=[]; self.rows=[]; self.row=None; self.in_body=False; self.tables=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag in ('script','img','link'):
            u=a.get('src') or a.get('href')
            if u: self.assets.append(u)
        if tag=='table': self.tables+=1
        if tag=='tbody': self.in_body=True
        if tag=='tr' and self.in_body: self.row={'line':self.getpos()[0],'links':[]}
        if tag=='a' and self.row is not None and a.get('href'): self.row['links'].append(a['href'])
    def handle_endtag(self,tag):
        if tag=='tbody': self.in_body=False
        if tag=='tr' and self.row is not None: self.rows.append(self.row); self.row=None

def official(u):
    h=(urlsplit(u).hostname or '').lower()
    return h in NFL_HOSTS or h in CLUB_HOSTS or h.endswith('.nfl.com')

def main():
    paths=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    files=[]; errors=[]; pages={}; broken=[]; zero_source=[]
    for rel in paths:
        p=ROOT/rel; data=p.read_bytes(); text=None; syntax='binary_or_not_applicable'
        try: text=data.decode('utf-8')
        except UnicodeDecodeError: pass
        item={'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'line_count':len(data.splitlines()),'syntax':syntax}
        if text is not None:
            try:
                if rel.endswith('.json'): json.loads(text); syntax='valid_json'
                elif rel.endswith('.py'): compile(text,rel,'exec'); syntax='valid_python'
                elif rel.endswith('.csv'):
                    delim='|' if text.splitlines()[0].count('|')>text.splitlines()[0].count(',') else ','
                    rows=list(csv.reader(io.StringIO(text),delimiter=delim)); width=len(rows[0]) if rows else 0
                    if any(len(r)!=width for r in rows): raise ValueError('ragged CSV rows')
                    syntax='valid_csv'; item['csv_rows']=max(0,len(rows)-1)
                elif rel.endswith('.js'):
                    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
                    if r.returncode: raise ValueError(r.stderr.strip())
                    syntax='valid_js'
            except Exception as e: syntax='invalid'; errors.append({'file':rel,'error':str(e)})
            item['syntax']=syntax
            if rel.endswith('.html'):
                q=Page(); q.feed(text); q.close(); pages[rel]=q
                sourced=sum(any(official(u) for u in r['links']) for r in q.rows)
                item.update({'tables':q.tables,'tbody_rows':len(q.rows),'rows_with_official_nfl_or_club_link':sourced})
                if q.rows and sourced==0: zero_source.append(rel)
        files.append(item)
    for rel,q in pages.items():
        for u in q.links+q.assets:
            s=urlsplit(u)
            if s.scheme or u.startswith('//') or not u: continue
            target=(ROOT/rel).parent/unquote(s.path) if s.path else ROOT/rel
            target=target.resolve()
            if not target.exists(): broken.append({'file':rel,'url':u}); continue
            if s.fragment and target.suffix=='.html':
                t=pages.get(str(target.relative_to(ROOT)))
                if t is None:
                    t=Page(); t.feed(target.read_text()); t.close()
                if s.fragment not in t.ids: broken.append({'file':rel,'url':u,'reason':'missing fragment'})
    report={'ref':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'scope':'Every tracked file hashed and line-counted; text syntax parsed; HTML rows/links inventoried. Structural only, not independent factual verification of every cell.',
            'files':files,'syntax_errors':errors,'broken_internal_links':broken,'zero_official_source_html_pages':zero_source,
            'totals':{'files':len(files),'lines':sum(f['line_count'] for f in files),'html_pages':len(pages),
                      'tbody_rows':sum(f.get('tbody_rows',0) for f in files),
                      'rows_with_official_nfl_or_club_link':sum(f.get('rows_with_official_nfl_or_club_link',0) for f in files)},
            'limitations':['Official-domain coverage is not factual agreement.','Internal design/proposal rows may cite the canonical repository rather than an NFL fact.','Vendored raw data is hashed and parsed, not re-transcribed from the league in this script.']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['totals']|{'syntax_errors':len(errors),'broken_internal_links':len(broken),'zero_source_pages':len(zero_source)},indent=2))
    if errors or broken: raise SystemExit(1)

if __name__=='__main__': main()
