"""Build the private trial copy: dist/trial/index.html + dist/trial/seed.json.

The trial is the rebuilt page with three differences: a TRIAL strip at the top, its own device storage key,
and, on first open, it copies the backup into its own (separate) database. It never declares Google Calendar,
so test moves there can't touch the real calendar events.
"""
import json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent.parent
subprocess.run([sys.executable, "-I", str(root / "tools/build.py")], check=True, stdout=subprocess.DEVNULL)
page = (root / "dist/index.html").read_text(encoding="utf-8")

def rep(a, b):
    global page
    assert page.count(a) == 1, a
    page = page.replace(a, b)

rep("<title>Mains Run to 3 Jan</title>", "<title>Mains Run · trial</title>")
rep('const LS="mains-run-v2";', 'const LS="mains-run-trial";')
rep("</style></head><body>", ".trialbar{position:sticky;top:0;z-index:50;background:var(--margin,#8a2b2b);color:#fff;font:600 13px/1.35 system-ui,sans-serif;"
    "padding:7px 14px;text-align:center}</style></head><body><div class=\"trialbar\" role=\"note\">Trial copy of Mains Run. Your real page and data "
    "aren't touched, and Google Calendar is off here.</div>")
rep("db=d;", "db=d;await trialSeed(d);")
rep("async function boot(){", '''/* trial only: the first open copies the backup into this page's own database; plan/state goes last, so an
   interrupted copy simply runs again next time */
async function trialSeed(d){try{const s=await d.doc("plan/state").get();if(s&&s.exists)return;
  sync("Copying your data into the trial…");const r=await fetch("seed.json");if(!r.ok)return;const all=await r.json();
  for(const x of all.filter(x=>x.path!=="plan/state"))await d.doc(x.path).set(x.data);
  const p=all.find(x=>x.path==="plan/state");if(p)await d.doc(p.path).set(p.data)}catch(e){sync("Couldn't copy your data into the trial ("+(e&&e.code||e&&e.message||"error")+").")}}
async function boot(){''')
out = root / "dist/trial"; out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(page, encoding="utf-8")
seed = []
for f in sorted((root / "backup/2026-11-25").glob("*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line); seed.append({"path": f"{f.stem}/{r['id']}", "data": r["data"]})
(out / "seed.json").write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")
print("dist/trial:", len(seed), "records")
