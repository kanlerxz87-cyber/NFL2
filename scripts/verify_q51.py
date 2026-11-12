#!/usr/bin/env python3
"""Strict Q51 publication gate: row sources, blanks, links, JSON, determinism, safety."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'q51'
ALLOWED={'nfl.com','www.nfl.com','media.nfl.com','operations.nfl.com','static.www.nfl.com','nextgenstats.nfl.com','www.ncpgambling.org','ncpgambling.org','www.weather.gov','api.weather.gov','github.com'}
CLUBS={urlsplit(c['home']).hostname for c in json.loads((ROOT/'collectors/q51/sources.json').read_text())['clubs']}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.links=[]; self.assets=[]; self.rows=[]; self.row=None; self.body=False; self.ids=[]; self.blanks=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag in ('script','link','img'):
            u=a.get('src') or a.get('href')
            if u: self.assets.append(u)
        if tag=='tbody': self.body=True
        if tag=='tr' and self.body: self.row=[]
        if tag=='a' and self.row is not None and a.get('href'): self.row.append(a['href'])
        if tag=='td' and a.get('class')=='blank': self.blanks+=1
    def handle_endtag(self,tag):
        if tag=='tbody': self.body=False
        if tag=='tr' and self.row is not None: self.rows.append(self.row); self.row=None

def allowed(u):
    s=urlsplit(u); h=(s.hostname or '').lower()
    if h in ALLOWED or h in CLUBS or h.endswith('.nfl.com'): return True
    return h=='github.com' and s.path.startswith('/kanlerxz87-cyber/NFL2')

def digest():
    return {str(p.relative_to(Q)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Q.rglob('*')) if p.is_file()}

def main():
    errors=[]; pages=sorted(Q.glob('*.html')); rows=0; sourced=0; blanks=0
    for p in pages:
        q=P(); q.feed(p.read_text()); q.close(); rows+=len(q.rows); blanks+=q.blanks
        for i,r in enumerate(q.rows,1):
            if any(allowed(u) for u in r): sourced+=1
            else: errors.append(f'{p.name}: tbody row {i} lacks official/canonical source')
        for u in q.links+q.assets:
            s=urlsplit(u)
            if s.scheme or u.startswith('//') or not u: continue
            target=(p.parent/unquote(s.path)).resolve() if s.path else p
            if not target.exists(): errors.append(f'{p.name}: broken link {u}')
            elif s.fragment and target.suffix=='.html':
                t=P(); t.feed(target.read_text()); t.close()
                if s.fragment not in t.ids: errors.append(f'{p.name}: missing fragment {u}')
    for p in (Q/'data').glob('*.json'):
        try: json.loads(p.read_text())
        except Exception as e: errors.append(f'{p.name}: invalid JSON {e}')
    lines=json.loads((Q/'data/lines.json').read_text()); board=json.loads((Q/'data/leaderboard.json').read_text()); gates=json.loads((Q/'data/gates.json').read_text())
    if lines.get('real_money_enabled') is not False: errors.append('lines: real money must be disabled')
    if lines.get('status')!='research_lines_generated_unvalidated': errors.append('lines: unexpected validation status')
    if any(v for b in board['boards'].values() for v in b): errors.append('leaderboard: invented eligible entries')
    if gates.get('eligible') or gates.get('real_money_enabled') is not False: errors.append('gates: fail-closed policy violated')
    before=digest(); subprocess.run([sys.executable,'-m','engine.q51.build_site'],cwd=ROOT,check=True,capture_output=True)
    if digest()!=before: errors.append('Q51 rebuild is not deterministic')
    print(json.dumps({'pages':len(pages),'tbody_rows':rows,'rows_with_official_or_canonical_source':sourced,'explicit_blank_cells':blanks,'errors':errors},indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
