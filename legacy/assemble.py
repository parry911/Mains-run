"""Rebuild the live Mains Run page (version 1795629511-837b (D: chats count hours like the page)) from the copied parts.

Parts were copied from reads taken at different versions; the edits that came after each read
are re-applied here, exactly as they were sent to the artifact. Every edit must match exactly
once, which also checks the copied text around it.
"""
import json, pathlib, sys

here = pathlib.Path(__file__).parent
parts = sorted((here / "parts").glob("p0*.html"))
page = "".join(p.read_text(encoding="utf-8") for p in parts)

for name in ["edits_A.json", "edits_B.json", "edits_C.json", "edits_D.json"]:
    for i, e in enumerate(json.loads((here / name).read_text(encoding="utf-8"))):
        n = page.count(e["old_text"])
        if n != 1:
            sys.exit(f"{name} edit {i}: old_text found {n} times")
        page = page.replace(e["old_text"], e["new_text"])

(here / "index.html").write_text(page, encoding="utf-8")
print("lines:", page.count("\n") + 1, "bytes:", len(page.encode("utf-8")))
