# Rebuild progress (keep updated; survives chat compaction)

Decisions (Perry, 25 Nov 2026): hidden features (Re-plan, Change box, Build my day UI) stay OUT; one-day trial page before switch; private repo parry911/Mains-run.
Plan doc: https://claude.ai/artifact/NuJ8GqKe3wQ814HoLfkYMu

## Legacy capture (legacy/parts -> legacy/index.html)
Live page version 1795624616-3cfc, 2551 lines. Parts are copied from reads at mixed versions, then patched by legacy/apply_edits.py:
- p01 1-300 @3cfc, p02 301-379 @3cfc, p03 380-639 @5e8d (needs li edit), p04 640-969 @4fb1 (needs dayPlan edit), p05 970-1299 @4fb1 (needs aiSegs/aiContext/cleanPlan edits)
- p06-p09 done. legacy/assemble.py re-applies edits_A/B/C.json (each must match once) -> legacy/index.html = live 3cfc: 2551 lines, 253,369 bytes, both scripts parse. DONE 25 Nov 22:45 IST.

## Next
1. test/ harness: stub window.claude (db with get/set/update/onSnapshot, user.isOwner, sample, mcp, dictation=null) seeded from backup/; Playwright at 393x852 with clock fixed.
2. src/: split legacy into modules + tools/build.py that concatenates them back; first prove build(src) == legacy byte-for-byte.
3. Rebuild changes (keep look and words): drop hidden UI (dayLine, openReplan, openBuild, SOS food()), keep buildCustom for old custom days; one pipeline for every timetable; field-level saves; log-with-topics on Plan-my-day rows.
4. Tests for checklist + old-bug cases; trial artifact (calendar sync OFF, data copied); switch after Perry's OK.
