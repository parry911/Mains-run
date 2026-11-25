# Rebuild progress (keep updated; survives chat compaction)

Decisions (Perry, 25 Nov 2026): hidden features (Re-plan, Change box, Build my day UI) stay OUT; one-day trial page before switch; private repo parry911/Mains-run.
Plan doc: https://claude.ai/artifact/NuJ8GqKe3wQ814HoLfkYMu

## Legacy capture (legacy/parts -> legacy/index.html)
Live page version 1795624616-3cfc, 2551 lines. Parts are copied from reads at mixed versions, then patched by legacy/apply_edits.py:
- p01 1-300 @3cfc, p02 301-379 @3cfc, p03 380-639 @5e8d (needs li edit), p04 640-969 @4fb1 (needs dayPlan edit), p05 970-1299 @4fb1 (needs aiSegs/aiContext/cleanPlan edits)
- p06-p09 done. legacy/assemble.py re-applies edits_A/B/C.json (each must match once) -> legacy/index.html = live 3cfc: 2551 lines, 253,369 bytes, both scripts parse. DONE 25 Nov 22:45 IST.

## Status, 25 Nov ~23:15 IST
- src/ split; tools/build.py -> dist/index.html (2,470 lines). 27 tests in test/test_app.py pass on dist; 10 fail on legacy
  (7 = features that never existed on Plan-my-day days, 3 = the stale-copy overwrite bugs).
- Same-timetable check: legacy vs new Copy-timetable text identical for all 56 days (read-only mode).
- Trial artifact: slug 01741787-5ba7-4bb8-bf61-39b8163715b4, https://claude.ai/artifact/1BQnAuAmJyUSNoUKNfzcdy
  (contract 0.2.99, db/dictation/sample/user, NO mcp so no calendar). First open copies dist/trial/seed.json (24 records,
  backup incl. the 22:30 coach writes) into its own db, plan/state last.
- TODO after Perry opens the trial: db_list the trial to confirm 24 records, then republish without seed.json (remove).
- Switch (step 4): publish dist/index.html onto d0f18cb9-e778-4b34-aaeb-18c53ea168ca with publish_files (keep contract 0.2.96,
  outside guests -> may need shared_live per refusal), quiet time, not near 22:30. Old version = 1795629511-837b (restore; = 3cfc + edits_D).

## Behaviour changes in the rebuild (all tested)
- One shared step (finishDay) after every timetable source; one timetable screen (timetableView) for every day.
- Plan-my-day days: tap a row to log topics/time (openBlockLog) or change a slot (written into ai.segs, Undo works);
  lights out editable (after-midnight handled); paper tick opens "Did you write?" and marks the test written;
  "+ Log other study"; logged blocks no longer in the plan are listed.
- Field-level saves (DOCS/diffOps/applyOps/saveDoc in 29-writes): fresh get, apply this page's changes, update touched fields.
- Food/journal/study/coach-memory writes keep fields they don't know.
- SOS button hidden while a sheet is open (it covered Save).
- Removed unreachable code: dayLine, openBuild, openReplan, setStart, idealText, asleepDraft, defaultAsleep, idealStart.

## Next
1. test/ harness: stub window.claude (db with get/set/update/onSnapshot, user.isOwner, sample, mcp, dictation=null) seeded from backup/; Playwright at 393x852 with clock fixed.
2. src/: split legacy into modules + tools/build.py that concatenates them back; first prove build(src) == legacy byte-for-byte.
3. Rebuild changes (keep look and words): drop hidden UI (dayLine, openReplan, openBuild, SOS food()), keep buildCustom for old custom days; one pipeline for every timetable; field-level saves; log-with-topics on Plan-my-day rows.
4. Tests for checklist + old-bug cases; trial artifact (calendar sync OFF, data copied); switch after Perry's OK.

## Coaches (25 Nov 23:27 IST)
- Nightly coach (trig_01V8mZsUjCR8yYtmPsXdDPS9) and Sunday review (trig_0136ApBajYzfefQ5heLbS2Ap) now also log hours
  into logs/<date>.blocks (slot id from ai.segs, or "x<ms>" Other study), clear realH like the page does, ask on mismatches,
  and note "Page issue: <date>: ..." in coach/memory notes; the Sunday review lists the week's page issues.
- Until the switch, the old page's whole-doc saves can overwrite a coach-added block if a stale copy is open (Perry told).
- 25 Nov 23:30: live page edited (edits_D): in-page chats count hours like the page (realH, else all blocks except nostudy;
  newspaper counts). Live version now 1795629511-837b; legacy/assemble.py reproduces it. Sunday review told newspaper counts.
  Trial republished 1795629609-ea82.
