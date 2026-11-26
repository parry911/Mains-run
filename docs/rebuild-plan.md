# Mains Run rebuild: what it was and the plan (from the Claude doc, 25 Nov 2026)

Kept here so nothing about the rebuild lives in Claude except the page itself.

## In short
- Same link, same database. Every log, test move, topic tick, food entry and coach note stays where it is.
- Every feature stays, looking the same; behaviour changes are bug fixes.
- The nightly coach and the Sunday review keep working, because the data keeps the same shape.
- The old version stays in the page's history and can be restored in one step.

## The system (checklist the new page had to pass)
- Top: date, next test countdown, days to prelims; ring 1 (today vs planned), ring 2 (average since 9 Nov vs 10 h, 7-day trend); Now line; alerts (overdue test, prep that won't fit, GS1 days before Delhi).
- Today: day arrows, Today button, Copy timetable; thought for the day; fixes for today's paper; Plan my day (questions, AI timetable) with change box, Undo last change, Plan again; older rule-built and Build-my-day days still drawn; edit slot time/name, break to study, lights out; log a block (topics, items, time, not study), "Written?" on the paper, + Log other study; minutes and tick per block; real hours; To do list; rewards at 10/11/12 h.
- Dropped, as Perry decided: Build my day, Standard day, start/fell-asleep controls, Change options, Re-plan.
- Log: start time, logged blocks, unlogged banner, day total, top 3 and note, copy summary, Mon–Sat hours, 10-hour days, last 7 days.
- Tests: GS1 runway, 14 tests with state, move or skip with reasons, written/uploaded/marks/fix, topic progress and drops, Google Calendar follows moves.
- Weeks: calendar 9 Nov–3 Jan, this week. Law: 45-topic pipeline. More: how it works, Learning speed, jobs, day rules, numbers.
- SOS: Can't study, craving coach, Urge hit, Minimum day, Talk & log; chats log food, journal, study, stories, notes; mic; opened from the SOS app's coach button.
- Underneath: syncs across devices, works offline on the device, read-only for others.

## Data (shapes must not change)
| Record | Holds | Written by | Read by |
| --- | --- | --- | --- |
| plan/state | tests and moves, written/uploaded/marks/fixes, topics, drops, Law, jobs, day overrides, rules, gcal ids | page, nightly coach, Sunday review | page, coaches |
| logs/<date> | wake/sleep, blocks, saved timetables (ai, custom), slots, lost/light, stop, realH, top3, note | page, SOS chats, coaches (hours, from 26 Nov) | page, coaches |
| study/<date> | Talk & log sessions | chats, coaches | page (Learning speed), coaches |
| journal/<date> | coach notes on the day | chats, coaches | page, coaches |
| food/<date> | SOS app log, card alerts, food sent in chat | nightly coach, chats | page, coaches |
| coach/memory | stories told, notes, "Page issue:" notes | page, coaches | page, coaches |

## What went wrong, and the fix
1. Three timetable sources with a pecking order; most controls reached only one. Fix: one shared step (finishDay) and one timetable screen (timetableView).
2. Features hidden by accident. Fix: removed the dead code; Plan-my-day rows got topics/time logging.
3. Whole-record saves overwrote newer changes. Fix: field-level saves onto a fresh read (29-writes).
4. One 2,550-line file patched blind. Fix: src/ split, build script, Playwright tests on a copy of real data.

## Rollout
Backup → build and test on a copy → trial page (25–26 Nov) → switch onto the same link (26 Nov, 08:40 IST, version 1795662653-677a; previous 1795629511-837b) → trial and this doc deleted from Claude at Perry's request.

## Decisions (25 Nov)
1. Hidden features: leave them out. 2. Trial page: yes. 3. Code: private GitHub repo parry911/Mains-run.
