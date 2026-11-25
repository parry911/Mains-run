"""One-time: cut legacy/index.html into src/ chunks at its own section markers.
build.py joins them back in manifest order; the first build must equal legacy byte for byte."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
lines = (root / "legacy/index.html").read_text(encoding="utf-8").split("\n")
mark = re.compile(r"^\s*/\* -{5,} (.*?) -{5,} \*/")
cuts = [(0, "head")]
for i, l in enumerate(lines):
    m = mark.match(l)
    if m: cuts.append((i, m.group(1)))
    elif l in ("<style>", "<script>") and i > 0: cuts.append((i, l.strip("<>") + "-start"))
    elif l.startswith("</script>"): cuts.append((i, "script-end"))
cuts = sorted(set(cuts))
src = root / "src"; src.mkdir(exist_ok=True)
names = []
for n, (start, title) in enumerate(cuts):
    end = cuts[n + 1][0] if n + 1 < len(cuts) else len(lines)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
    name = f"{n:02d}-{slug}.part"
    chunk = lines[start:end]
    (src / name).write_text("\n".join(chunk) + ("\n" if end < len(lines) else ""), encoding="utf-8")
    names.append(name)
(src / "manifest.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
print(len(names), "chunks")
