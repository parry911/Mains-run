# Mains Run (private)

Source, tests and data backups for Perry's "Mains Run to 3 Jan" Claude artifact
(https://claude.ai/artifact/SoUNgwpovKoWycJGTuXkBB, slug d0f18cb9-e778-4b34-aaeb-18c53ea168ca).
The page itself stays a Claude artifact; this repo only holds its code and backups. Keep it private:
the coach briefs contain personal details.

- `backup/<date>/` — every database record, one JSON line per document (id, version, data).
- `legacy/` — the page as it was before the rebuild (baseline for comparison).
- `src/` — the rebuilt page, published to the artifact from files.
- `test/` — local harness (stub Claude: db, sample, user, mcp) and phone-size Playwright checks.
- `REBUILD.md` — plan, decisions and progress.
