#!/usr/bin/env python3
"""Fail-closed official-source collector (stdlib only).

Respects robots.txt, uses an explicit host allowlist, rate-limits requests,
records retrieval time and original-response SHA-256, and never converts a
missing value into a guessed value. Raw responses can be kept outside the site.
"""
from __future__ import annotations
import argparse, hashlib, json, re, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError, URLError

UA='NFL2-Research/0.1 (public-source audit; no wagering)'
MAX_BYTES=8_000_000

class SafeRedirect(HTTPRedirectHandler):
    def __init__(self,allowed): super().__init__(); self.allowed=allowed
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlsplit(newurl).hostname not in self.allowed: raise ValueError('Redirect outside official allowlist')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.tables=[]; self.table=None; self.row=None; self.cell=None
        self.heading=''; self.heading_tag=None; self.heading_buf=[]; self.text=[]; self.since_table=[]; self.links=[]; self.scripts=[]; self.script_tag=None; self.script_buf=[]; self.title=''; self.title_tag=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'): self.links.append({'href':a['href'],'text':''}); self._link=True
        else: self._link=False
        if tag in ('h1','h2','h3'): self.heading_tag=tag; self.heading_buf=[]
        if tag=='title': self.title_tag=True
        if tag=='script': self.script_tag=a.get('type',''); self.script_buf=[]
        if tag=='table': self.table={'heading':self.heading,'preceding':' '.join(' '.join(self.since_table).split())[-2500:],'rows':[]}; self.since_table=[]
        if tag=='tr' and self.table is not None: self.row={'cells':[],'links':[]}
        if tag in ('td','th') and self.row is not None: self.cell=[]; self.cell_links=[]
    def handle_data(self,data):
        self.text.append(data)
        if self.table is None: self.since_table.append(data)
        if self.heading_tag: self.heading_buf.append(data)
        if self.title_tag: self.title+=data
        if self.script_tag is not None: self.script_buf.append(data)
        if self.cell is not None: self.cell.append(data)
        if getattr(self,'_link',False) and self.links: self.links[-1]['text']+=data
    def handle_endtag(self,tag):
        if tag=='a': self._link=False
        if tag in ('h1','h2','h3') and self.heading_tag: self.heading=' '.join(''.join(self.heading_buf).split()); self.heading_tag=None
        if tag=='title': self.title_tag=False
        if tag=='script' and self.script_tag is not None: self.scripts.append({'type':self.script_tag,'text':''.join(self.script_buf)}); self.script_tag=None
        if tag in ('td','th') and self.cell is not None:
            self.row['cells'].append(' '.join(''.join(self.cell).split())); self.row['links'].extend(self.cell_links); self.cell=None
        if tag=='a' and self.cell is not None and self.links: self.cell_links.append(self.links[-1]['href'])
        if tag=='tr' and self.row is not None: self.table['rows'].append(self.row); self.row=None
        if tag=='table' and self.table is not None: self.tables.append(self.table); self.table=None


def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')


class Collector:
    def __init__(self,out,raw_dir=None,delay=1.1):
        self.out=Path(out); self.out.mkdir(parents=True,exist_ok=True); self.raw_dir=Path(raw_dir) if raw_dir else None
        if self.raw_dir: self.raw_dir.mkdir(parents=True,exist_ok=True)
        self.delay=delay; self.robots={}; self.last_request=0; self.manifest=[]
        registry=json.loads(Path(__file__).with_name('sources.json').read_text()); self.registry=registry
        self.allowed={'www.nfl.com'}|{urlsplit(c['home']).hostname for c in registry['clubs']}; self.opener=build_opener(SafeRedirect(self.allowed))
    def get(self,url):
        host=urlsplit(url).hostname
        if host not in self.allowed: raise ValueError('Host not in official allowlist')
        if host not in self.robots:
            robots_url=f'https://{host}/robots.txt'; rp=RobotFileParser(); rp.set_url(robots_url)
            try:
                with self.opener.open(Request(robots_url,headers={'User-Agent':UA}),timeout=30) as r: raw=r.read(1_000_000)
                rp.parse(raw.decode(errors='replace').splitlines()); self.robots[host]=rp
            except HTTPError as e:
                if e.code in (401,403): raise ValueError(f'robots access denied: {e.code}')
                rp.parse([]); self.robots[host]=rp
        if not self.robots[host].can_fetch(UA,url): raise ValueError('robots.txt disallows this path; not bypassed')
        wait=self.delay-(time.monotonic()-self.last_request)
        if wait>0: time.sleep(wait)
        self.last_request=time.monotonic()
        with self.opener.open(Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/json'}),timeout=45) as r:
            raw=r.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES: raise ValueError('Response exceeds size limit')
            final_url=r.geturl()
        if urlsplit(final_url).hostname not in self.allowed: raise ValueError('Final redirect outside allowlist')
        digest=hashlib.sha256(raw).hexdigest()
        if self.raw_dir:
            name=re.sub(r'[^A-Za-z0-9.-]+','_',urlsplit(url).netloc+urlsplit(url).path).strip('_') or 'root'
            (self.raw_dir/(name+'-'+digest[:12]+'.html')).write_bytes(raw)
        return raw.decode(errors='replace'),digest,final_url
    def fetch(self,url,kind,**meta):
        entry={'url':url,'kind':kind,'retrieved_at':now(),**meta}
        try:
            text,digest,final=getattr(self,'get')(url); entry.update({'status':'retrieved','sha256':digest,'bytes':len(text.encode()),'final_url':final})
            doc=Document(); doc.feed(text); doc.close(); entry['table_count']=len(doc.tables); entry['title']=doc.title.strip()
            self.manifest.append(entry); return text,doc,entry
        except Exception as e:
            entry.update({'status':'failed','error':str(e)}); self.manifest.append(entry); return None,None,entry
    def save(self,name,data): (self.out/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def injuries(doc,entry,clubs):
    rows=[]; names={c['team']:c for c in clubs}
    for table in doc.tables:
        if not table['rows'] or table['rows'][0]['cells'][:5]!=['Player','Position','Injuries','Practice Status','Game Status']: continue
        context=table['preceding']; matches=[]
        for c in clubs:
            nickname=c['team'].split()[-1]
            for label in (c['team'],nickname):
                pos=context.rfind(label)
                if pos>=0: matches.append((pos,c))
        team=max(matches,key=lambda x:x[0])[1] if matches else None
        for row in table['rows'][1:]:
            cells=row['cells']
            if len(cells)<5 or not cells[0]: continue
            rows.append({'team':team['team'] if team else None,'team_abbr':team['abbr'] if team else None,'player':cells[0],'position':cells[1] or None,
                         'injury':cells[2] or None,'practice_status':cells[3] or None,'game_status':cells[4] or None,
                         'player_source_url':urljoin(entry['url'],row['links'][0]) if row['links'] else None,
                         'source_url':entry['url'],'retrieved_at':entry['retrieved_at'],'response_sha256':entry['sha256'],
                         'verified':team is not None,'flag':None if team else 'Team context not explicitly matched; withheld from model'})
    return {'source_url':entry['url'],'retrieved_at':entry['retrieved_at'],'response_sha256':entry['sha256'],'displayed_heading':doc.heading,'rows':rows,'note':'Practice status and game status are separate. A blank is not healthy. Current route week is read from content, not inferred from URL.'}


def depth_chart(doc,entry,club):
    text=' '.join(doc.text).lower(); editorial='club_published_unofficial' if 'unofficial' in text else 'club_published_editorial_status_unspecified'
    rows=[]
    for table in doc.tables:
        side=table['heading'].lower()
        if side not in ('offense','defense','special teams'): continue
        for row in table['rows']:
            cells=row['cells']
            if len(cells)<2 or not cells[0] or cells[0].lower() in ('position','offense','defense','special teams'): continue
            slots=[]
            for rank,cell in enumerate(cells[1:],1):
                players=re.split(r'\s+(?:OR|or)\s+',cell) if cell else []
                slots.append({'depth':rank,'players':[p.strip() for p in players if p.strip()] or None,'raw_cell':cell or None})
            rows.append({'team':club['team'],'team_abbr':club['abbr'],'side':side,'position':cells[0],'slots':slots,
                         'editorial_status':editorial,'confirmed_gameday_lineup':None,'source_url':entry['url'],'retrieved_at':entry['retrieved_at'],'response_sha256':entry['sha256'],
                         'flag':'Club ordering is not actual participation. Missing slots remain null.'})
    return rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='collector-output'); ap.add_argument('--raw-dir'); ap.add_argument('--mode',choices=['probe','full'],default='probe'); ap.add_argument('--delay',type=float,default=1.1); args=ap.parse_args()
    c=Collector(args.out,args.raw_dir,args.delay); clubs=c.registry['clubs']; all_depth=[]; injury_data=None; schedule_pages=[]
    targets=[('injuries',c.registry['league']['injuries_current']),('schedule',c.registry['league']['schedule_week_11']),('results','https://www.nfl.com/schedules/2026/by-week/week-1')]
    selected=clubs if args.mode=='full' else [x for x in clubs if x['abbr'] in {'DAL','BUF','NE','KC'}]
    targets += [('depth',urljoin(x['home'],'/team/depth-chart')) for x in selected]
    if args.mode=='full': targets += [('results',f'https://www.nfl.com/schedules/2026/by-week/week-{w}') for w in range(2,11)]
    for kind,url in targets:
        club=next((x for x in selected if urlsplit(x['home']).hostname==urlsplit(url).hostname),None)
        text,doc,entry=c.fetch(url,kind,team=club['team'] if club else None)
        if doc is None: continue
        if kind=='injuries': injury_data=injuries(doc,entry,clubs); c.save('injuries.json',injury_data)
        elif kind=='depth':
            rows=depth_chart(doc,entry,club); all_depth.extend(rows); c.save('depth-charts.json',{'rows':all_depth,'directory_source':c.registry['directory_source']})
        else:
            schedule_pages.append({'kind':kind,'url':url,'entry':entry,'tables':[t for t in doc.tables],'links':doc.links,'headings':doc.heading,'scripts':doc.scripts,'text':' '.join(' '.join(doc.text).split())})
            c.save('schedule-pages.json',{'pages':schedule_pages})
        print(json.dumps({'url':url,'status':entry['status'],'tables':entry.get('table_count'),'error':entry.get('error')}),flush=True)
    c.save('manifest.json',{'generated_at':now(),'collector_version':'0.1.0','entries':c.manifest,'successful':sum(e['status']=='retrieved' for e in c.manifest),'failed':sum(e['status']=='failed' for e in c.manifest)})
    # Retrieval failures are published as flags, not silently filled. Parser/schema
    # failures must still fail the workflow; network failures trigger stale-data mode.
    if injury_data is None and args.mode=='full': raise SystemExit('Current official injury source unavailable; use last verified snapshot with a stale banner.')
if __name__=='__main__': main()
