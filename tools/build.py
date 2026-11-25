"""Join src/ chunks (manifest order) into dist/index.html, the single-file page that gets published."""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
names = [n for n in (root / "src/manifest.txt").read_text().split("\n") if n.strip()]
page = "".join((root / "src" / n).read_text(encoding="utf-8") for n in names)
out = root / "dist"; out.mkdir(exist_ok=True)
(out / "index.html").write_text(page, encoding="utf-8")
print("dist/index.html", page.count("\n") + 1, "lines")
if "--same" in sys.argv:
    same = page == (root / "legacy/index.html").read_text(encoding="utf-8")
    print("identical to legacy:", same); sys.exit(0 if same else 1)
