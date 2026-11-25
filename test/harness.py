"""Open a Mains Run build in a phone-sized Chromium with a stubbed window.claude and a copy of real data.

    with App("dist/index.html", now="2026-11-25 22:30") as app:
        app.page.click(...); app.writes(); app.shot("today")
"""
import datetime as dt, json, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKUP = ROOT / "backup" / "2026-11-25"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def load_seed(folder=BACKUP):
    seed = {}
    for f in sorted(pathlib.Path(folder).glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                seed[f"{f.stem}/{r['id']}"] = r["data"]
    return seed


class App:
    def __init__(self, html="dist/index.html", now="2026-11-25 22:30", seed=None, edit=None, size=(393, 852), replies=None):
        self.html = (ROOT / html).read_text(encoding="utf-8")
        self.now = dt.datetime.strptime(now, "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        self.seed = load_seed() if seed is None else seed
        if edit: edit(self.seed)
        self.size, self.replies, self.errors = size, replies or [], []

    def __enter__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch()
        self.ctx = self.browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}, device_scale_factor=2)
        self.ctx.route("**/*", lambda r: r.fulfill(body=self.html, content_type="text/html")
                       if r.request.url.startswith("http://app.local/") else r.abort())
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("console", lambda m: m.type == "error" and self.errors.append(m.text))
        self.page.clock.set_fixed_time(self.now)
        self.page.add_init_script("window.__SEED=" + json.dumps(self.seed) + ";")
        self.page.add_init_script(path=str(ROOT / "test" / "stub.js"))
        self.page.goto("http://app.local/")
        self.page.evaluate("r=>{window.__T.sampleReplies.push(...r)}", self.replies)
        self.page.wait_for_function("document.getElementById('sync') && !/Connecting/.test(document.getElementById('sync').textContent)", timeout=15000)
        self.page.wait_for_timeout(300)
        return self

    def __exit__(self, *a):
        self.browser.close(); self.pw.stop()

    # helpers
    def writes(self, path=None):
        w = self.page.evaluate("window.__T.writes")
        return [x for x in w if path is None or x["path"] == path]

    def store(self, path):
        return self.page.evaluate("p=>{const v=window.__T.store.get(p);return v===undefined?null:JSON.parse(JSON.stringify(v))}", path)

    def ext(self, path, data, merge=False):
        self.page.evaluate("([p,d,m])=>window.__T.ext(p,d,m)", [path, data, merge]); self.page.wait_for_timeout(100)

    def reply(self, *r):
        self.page.evaluate("r=>{window.__T.sampleReplies.push(...r)}", list(r))

    def prompts(self):
        return self.page.evaluate("window.__T.prompts")

    def text(self, sel="body"):
        return self.page.inner_text(sel)

    def shot(self, name, full=False):
        out = ROOT / "test" / "shots"; out.mkdir(exist_ok=True)
        self.page.screenshot(path=str(out / f"{name}.png"), full_page=full)
        return out / f"{name}.png"
