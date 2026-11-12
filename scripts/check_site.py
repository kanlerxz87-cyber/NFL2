import json,glob,os,re
files=sorted(glob.glob('site/data/*.json'))
for f in files:
    try:
        d=json.load(open(f)); print(f"OK   {f:34s} {os.path.getsize(f):>7d} bytes")
    except Exception as e: print(f"FAIL {f}: {e}")
# nav/page consistency
pages=set(os.path.basename(p) for p in glob.glob('site/*.html'))
js=set(os.path.basename(p) for p in glob.glob('site/pages/*.js'))
print("\npages:", len(pages), "page scripts:", len(js))
for p in sorted(pages):
    if p=='index.html': continue
    key=p.replace('.html','')
    if f"{key}.js" not in js: print("  MISSING SCRIPT:", key)
print("\njs modules:", sorted(js))
