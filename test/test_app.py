"""The checklist and the cases that broke before, run in a phone-sized browser against a copy of Perry's data.

    pytest -q test/                      # the new page (dist/index.html, built by tools/build.py)
    BUILD=legacy/index.html pytest -q    # the old page, to see which of these it fails
"""
import copy, json, re, sys, pathlib
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from harness import App, load_seed

SEED = load_seed()
TOMORROW = "2026-11-26"   # ST4's paper day in the copied data


def ai_day(d="2026-11-26", paper=True):
    """a Plan-my-day timetable like the ones Perry makes, for a day with no saved plan yet"""
    segs = [
        {"id": "g", "t": 300, "e": 330, "label": "Gurbani", "type": "break", "note": ""},
        {"id": "s1", "t": 330, "e": 480, "label": "Study block", "type": "study", "note": ""},
        {"id": "b1", "t": 480, "e": 495, "label": "Short break, no phone", "type": "break", "note": ""},
        {"id": "s0", "t": 495, "e": 600, "label": "Study block", "type": "study", "note": ""},
        {"id": "n1", "t": 600, "e": 660, "label": "Breakfast and newspaper", "type": "news", "note": ""},
        {"id": "s2", "t": 660, "e": 810, "label": "Study block", "type": "study", "note": ""},
        {"id": "l1", "t": 810, "e": 870, "label": "Lunch, shower, rest", "type": "break", "note": ""},
    ]
    if paper:
        segs.append({"id": "p1", "t": 870, "e": 1050, "label": "ST4 paper", "type": "paper", "note": ""})
    else:
        segs.append({"id": "s4", "t": 870, "e": 1050, "label": "Study block", "type": "study", "note": ""})
    segs += [
        {"id": "b2", "t": 1050, "e": 1140, "label": "Break, phone time", "type": "break", "note": ""},
        {"id": "din", "t": 1140, "e": 1200, "label": "Dinner", "type": "break", "note": ""},
        {"id": "s3", "t": 1200, "e": 1290, "label": "Study block", "type": "study", "note": ""},
    ]
    return {"segs": segs, "lights": 1320, "summary": "Revise, write ST4 at 2:30, light evening.", "at": 1,
            "answers": {"about": [], "push": "normal", "fixed": "", "more": ""}, "prev": None}


def with_day(d, log):
    def edit(seed):
        seed["logs/" + d] = log
    return edit


def tomorrow_app(**kw):
    return App(now=TOMORROW + " " + kw.pop("at", "10:00"),
               edit=with_day(TOMORROW, {"ai": ai_day(), "start": 300, "startHow": "ai", "startAt": 1, "savedAt": 1}), **kw)


def row(app, name):
    return app.page.locator("#day ul.tt li", has=app.page.locator("b", has_text=re.compile("^" + re.escape(name) + "$")))


def brk(app, label):
    return app.page.locator("#day ul.tt li.br", has_text=label)


# ---------- loading ----------

def test_loading_writes_nothing():
    with App() as app:
        app.settle(800)
        assert app.writes() == []
        assert app.errors == []


def test_every_day_and_tab_renders():
    with App() as app:
        prev = app.page.get_by_role("button", name="Previous day")
        while prev.is_enabled():
            prev.click()
        assert "Mon 9 Nov" in app.text("#day h2")
        nxt = app.page.get_by_role("button", name="Next day")
        seen = 1
        while nxt.is_enabled():
            nxt.click(); seen += 1
        assert "Sun 3 Jan" in app.text("#day h2")
        assert seen == 56
        for v in ["log", "tests", "calendar", "law", "jobs", "today"]:
            app.page.click(f"nav.tabs button[data-v={v}]"); app.settle(150)
        assert app.errors == []
        assert app.writes() == []


def test_read_only_view():
    with App(owner=False) as app:
        assert "Read-only" in app.text("#sync")
        assert app.page.locator("#aiChange").count() == 0
        assert app.page.locator("#day li[role=button]").count() == 0
        app.page.locator("#day ul.tt li").nth(2).click()
        assert app.page.locator("#sheetOv").is_hidden()
        assert app.writes() == []


def same_timetables(app_a, app_b):
    """walk every day in both pages and compare what Copy timetable produces"""
    out = []
    for app in (app_a, app_b):
        texts = {}
        prev = app.page.get_by_role("button", name="Previous day")
        while prev.is_enabled():
            prev.click()
        nxt = app.page.get_by_role("button", name="Next day")
        while True:
            d = app.text("#day h2")
            btn = app.page.get_by_role("button", name="Copy timetable")
            if btn.count():
                btn.click(); app.settle(60)
                texts[d] = app.page.evaluate("navigator.clipboard.readText()")
            else:
                texts[d] = None
            if not nxt.is_enabled():
                break
            nxt.click()
        out.append(texts)
    return out


def test_same_timetables_as_the_old_page_for_every_day():
    """Your days come out exactly as before: rule-built, Build-my-day and Plan-my-day days alike."""
    with App(html="legacy/index.html", owner=False) as old, App(html="dist/index.html", owner=False) as new:
        a, b = same_timetables(old, new)
    assert len(a) == 56
    diff = [d for d in a if a[d] != b[d]]
    assert diff == [], diff[:3]
    assert sum(1 for v in a.values() if v) >= 40   # travel, wedding, Delhi and light-Sunday days have no timetable


# ---------- Today: logging ----------

def test_minutes_button_logs_a_block():
    with tomorrow_app() as app:
        r = row(app, "Study block 1")
        r.get_by_role("button", name="Minutes studied in Study block 1").click()
        r.locator("input.mininp").fill("120")
        r.get_by_role("button", name="Save").click(); app.settle()
        b = app.store("logs/" + TOMORROW)["blocks"]["s1"]
        assert b["hours"] == 2 and b["name"] == "Study block 1" and b["t"] == 330
        assert "2h of 2h 30m" in row(app, "Study block 1").inner_text()


def test_tick_and_untick():
    with tomorrow_app() as app:
        row(app, "Study block 3").get_by_role("checkbox").check(); app.settle()
        assert app.store("logs/" + TOMORROW)["blocks"]["s2"]["hours"] == 2.5
        row(app, "Study block 3").get_by_role("checkbox").uncheck(); app.settle()
        assert "s2" not in (app.store("logs/" + TOMORROW).get("blocks") or {})


def test_tap_a_block_to_log_topics():
    with tomorrow_app() as app:
        row(app, "Study block 2").locator(".nm").click()
        assert app.page.locator("#sheetBody h3").inner_text() == "What did you do?"
        first = app.page.locator("#sheetBody ul.todo li input[type=checkbox]").first
        label = app.page.locator("#sheetBody ul.todo li label").first.inner_text()
        first.check()
        app.page.locator("#sheetBody button.primary", has_text="Save").click(); app.settle()
        b = app.store("logs/" + TOMORROW)["blocks"]["s0"]
        assert b["hours"] == 1.75
        assert b["topics"] or b["items"], label
        assert "✓" in row(app, "Study block 2").inner_text()


def test_paper_tick_marks_the_test_written():
    with tomorrow_app(at="17:40") as app:
        row(app, "ST4 paper").get_by_role("checkbox").click()
        assert "Did you write" in app.page.locator("#sheetBody h3").inner_text()
        app.page.locator("#sheetBody button.primary", has_text="Written").click(); app.settle()
        t = app.store("plan/state")["tests"]["ST4"]
        assert t["done"] is True and t["writtenOn"] == TOMORROW
        assert app.store("logs/" + TOMORROW)["blocks"]["p1"]["items"] == ["w-ST4"]


def test_reward_when_the_day_crosses_10_hours():
    with App(now="2026-11-25 22:40") as app:   # 7h 10m done
        app.page.get_by_role("button", name="+ Log other study").click()
        app.page.locator("#sheetBody #lgHrs, #sheetBody input").first.wait_for()
        box = app.page.locator("#sheetBody")
        hrs = box.locator("input[type=number]")
        hrs.first.fill("3")
        if hrs.count() > 1:
            hrs.nth(1).fill("0")
        box.locator("button.primary", has_text="Save").click(); app.settle(600)
        assert app.store("logs/2026-11-25")["blocks"]
        assert not app.page.locator("#sheetOv").is_hidden()   # the reward sheet
        assert app.errors == []


# ---------- Today: changing the plan ----------

def test_change_a_break_on_a_plan_my_day_day_and_undo():
    with tomorrow_app() as app:
        brk(app, "Dinner").click()
        assert app.page.locator("#sheetBody h3").inner_text() == "Change this slot"
        app.page.fill("#slFrom", "19:30"); app.page.fill("#slTo", "20:30")
        app.page.locator("#sheetBody button.primary", has_text="Save").click(); app.settle()
        ai = app.store("logs/" + TOMORROW)["ai"]
        din = [s for s in ai["segs"] if s["id"] == "din"][0]
        assert (din["t"], din["e"]) == (1170, 1230)
        s3 = [s for s in ai["segs"] if s["id"] == "s3"][0]
        assert s3["t"] == 1230                          # the study block after it was trimmed around it
        assert ai["prev"]["segs"][-2]["t"] == 1140
        assert "7:30" in brk(app, "Dinner").inner_text()
        app.page.get_by_role("button", name="Undo last change").click(); app.settle()
        din = [s for s in app.store("logs/" + TOMORROW)["ai"]["segs"] if s["id"] == "din"][0]
        assert din["t"] == 1140


def test_turn_a_break_into_study():
    with tomorrow_app() as app:
        brk(app, "Break, phone time").click()
        app.page.check("#slStudy")
        app.page.locator("#sheetBody button.primary", has_text="Save").click(); app.settle()
        seg = [s for s in app.store("logs/" + TOMORROW)["ai"]["segs"] if s["id"] == "b2"][0]
        assert seg["type"] == "study" and seg["label"] == "Study block"
        assert row(app, "Study block 5").count() == 1


def test_change_a_block_time_from_the_log_sheet():
    with tomorrow_app() as app:
        row(app, "Study block 1").locator(".nm").click()
        app.page.get_by_role("button", name="Change this block's time or name").click()
        app.page.fill("#slFrom", "06:00"); app.page.fill("#slTo", "08:00")
        app.page.locator("#sheetBody button.primary", has_text="Save").click(); app.settle()
        s1 = [s for s in app.store("logs/" + TOMORROW)["ai"]["segs"] if s["id"] == "s1"][0]
        assert (s1["t"], s1["e"]) == (360, 480) and s1["label"] == "Study block"


def test_lights_out_after_midnight():
    with tomorrow_app() as app:
        app.page.locator("#day ul.tt li", has_text="Lights out").click()
        app.page.fill("#slFrom", "00:30")
        app.page.locator("#sheetBody button.primary", has_text="Save").click(); app.settle()
        lg = app.store("logs/" + TOMORROW)
        assert lg["ai"]["lights"] == 1470 and lg.get("lightsAt") is None
        assert "12:30" in app.page.locator("#day ul.tt li", has_text="Lights out").inner_text()


def test_change_box_logs_what_you_did():
    reply = {"lights": "22:00", "summary": "Logged the morning.", "slots": [
        {"id": "g", "start": "05:00", "end": "05:30", "label": "Gurbani", "type": "break"},
        {"id": "s1", "start": "05:30", "end": "08:00", "label": "Study block", "type": "study", "done": True, "studied_min": 120},
        {"id": "b1", "start": "08:00", "end": "08:15", "label": "Short break, no phone", "type": "break"},
        {"id": "s0", "start": "08:15", "end": "10:00", "label": "Study block", "type": "study", "done": True},
        {"id": "n1", "start": "10:00", "end": "11:00", "label": "Breakfast and newspaper", "type": "news"},
        {"id": "s2", "start": "11:00", "end": "13:30", "label": "Study block", "type": "study"},
        {"id": "l1", "start": "13:30", "end": "14:30", "label": "Lunch, shower, rest", "type": "break"},
        {"id": "p1", "start": "14:30", "end": "17:30", "label": "ST4 paper", "type": "paper"},
        {"id": "din", "start": "19:00", "end": "20:00", "label": "Dinner", "type": "break"},
        {"id": "s3", "start": "20:00", "end": "21:30", "label": "Study block", "type": "study"}]}
    with tomorrow_app(replies=[reply]) as app:
        app.page.fill("#aiChange", "studied 5:30 to 7:30 and 8:15 to 10")
        app.page.get_by_role("button", name="Change", exact=True).click(); app.settle(800)
        lg = app.store("logs/" + TOMORROW)
        assert lg["blocks"]["s1"]["hours"] == 2 and lg["blocks"]["s0"]["hours"] == 1.75
        assert lg["ai"]["lights"] == 1320 and lg["ai"]["prev"]
        assert "done" not in json.dumps(lg["ai"]["segs"])
        assert "studied 5:30" in app.prompts()[0]


def test_plan_my_day():
    reply = {"lights": "22:30", "summary": "A normal day.", "slots": [
        {"start": "11:30", "end": "12:00", "label": "Gurbani", "type": "break"},
        {"start": "12:00", "end": "14:00", "label": "Study block", "type": "study"},
        {"start": "14:00", "end": "15:00", "label": "Lunch", "type": "break"},
        {"start": "15:00", "end": "17:30", "label": "Study block", "type": "study"}]}
    with App(now="2026-11-28 11:20", replies=[reply]) as app:
        app.page.fill("#aiWake", "11:30")
        app.page.get_by_role("button", name="Plan my day").click(); app.settle(800)
        lg = app.store("logs/2026-11-28")
        assert lg["start"] == 690 and lg["ai"]["lights"] == 1350
        assert "Starts at 11:30" in app.prompts()[0]
        assert row(app, "Study block 2").count() == 1
        assert "Early" in app.text("#nowline") and "11:30" in app.text("#nowline")


# ---------- tests moving under a saved timetable ----------

def move_test(app, name, to):
    app.page.click("nav.tabs button[data-v=tests]"); app.settle(200)
    ok = app.page.evaluate("""name=>{for(const b of document.querySelectorAll('button')){if(b.textContent!=='Move or skip'||!b.offsetParent)continue;
        let c=b.parentElement;while(c&&c.querySelectorAll('button').length<2&&!c.textContent.includes(name))c=c.parentElement;
        while(c&&!c.textContent.includes(name)&&c.parentElement)c=c.parentElement;
        if(c&&c.textContent.includes(name)&&[...c.querySelectorAll('button')].filter(x=>x.textContent==='Move or skip').length===1){b.click();return true}}return false}""", name)
    assert ok, name
    app.page.fill("#mvDate", to)
    app.page.dispatch_event("#mvDate", "input")
    app.page.click("#mvGo"); app.settle(500)
    app.page.click("nav.tabs button[data-v=today]"); app.settle()


def test_moving_a_test_on_its_own_day_turns_the_paper_into_study():
    with tomorrow_app(at="10:00") as app:
        assert row(app, "ST4 paper").count() == 1
        move_test(app, "ST4 · GS3 topics 11–20", "2026-11-28")
        assert app.store("plan/state")["tests"]["ST4"]["date"] == "2026-11-28"
        assert row(app, "ST4 paper").count() == 0
        assert "paper slot is now study time (ST4 moved to 28 Nov)" in app.text("#day")
        assert "ST4 paper" not in app.page.locator("#day ul.tt").inner_text()
        app.page.wait_for_function("window.__T.mcp.some(c=>c.tool==='update_event'&&c.args.eventId==='bnqcirongrdkmepbl1o0v8r658')", timeout=8000)


def test_a_test_moved_onto_a_planned_day_asks_to_plan_again():
    def edit(seed):
        seed["logs/2026-11-28"] = {"ai": ai_day("2026-11-28", paper=False), "start": 300, "startHow": "ai", "startAt": 1}
    with App(now="2026-11-28 09:00", edit=edit) as app:
        move_test(app, "ST2 · GS2 second half", "2026-11-28")
        assert "ST2 is on this day now, but this timetable has no paper slot." in app.text("#day")
        app.page.locator("#day .banner").get_by_role("button", name="Plan again").click()
        assert app.page.get_by_role("button", name="Plan my day").count() == 1


# ---------- saving: other writers are never overwritten ----------

def test_a_stale_day_copy_does_not_wipe_other_changes():
    with tomorrow_app() as app:
        # the nightly coach (or the SOS chat) changes today's record, and this phone never hears about it
        cur = app.store("logs/" + TOMORROW)
        cur["blocks"] = {"zz": {"name": "Talk & log", "hours": 1, "what": "Polity", "t": None, "e": None}}
        cur["coach"] = "keep me"
        app.ext_silent("logs/" + TOMORROW, cur)
        row(app, "Study block 1").get_by_role("checkbox").check(); app.settle()
        lg = app.store("logs/" + TOMORROW)
        assert lg["coach"] == "keep me"
        assert set(lg["blocks"]) == {"zz", "s1"}


def test_a_stale_plan_copy_does_not_undo_a_test_move():
    with tomorrow_app() as app:
        plan = app.store("plan/state")
        plan["tests"]["ST5"]["date"] = "2026-12-02"           # the Sunday review moved ST5
        plan["tests"]["ST5"]["moves"] = (plan["tests"]["ST5"].get("moves") or []) + [{"from": "2026-12-01", "to": "2026-12-02", "reason": "review", "at": 2}]
        app.ext_silent("plan/state", plan)
        app.page.locator("#day ul.todo li input[type=checkbox]").first.check(); app.settle()
        after = app.store("plan/state")
        assert after["tests"]["ST5"]["date"] == "2026-12-02"
        assert after["topics"] != plan["topics"] or after["tests"] != plan["tests"]


def test_writes_only_the_fields_that_changed():
    with tomorrow_app() as app:
        row(app, "Study block 1").get_by_role("checkbox").check(); app.settle()
        w = [x for x in app.writes() if x["path"] == "logs/" + TOMORROW]
        assert w and all(x["kind"] == "update" for x in w)
        assert set(w[-1]["data"]) <= {"blocks", "realH", "savedAt"}


# ---------- SOS and the coach link ----------

def test_minimum_day():
    with App(now="2026-11-28 15:02") as app:
        app.page.click("#sosBtn"); app.settle()
        app.page.locator("#sosBody button.sos-choice", has_text="Minimum day").click(); app.settle(800)
        lg = app.store("logs/2026-11-28")
        assert [s["id"] for s in lg["ai"]["segs"]][:2] == ["md-g", "md-1"]
        app.page.click("#sosClose")
        if app.page.locator("#sosClose").is_visible():
            app.page.click("#sosClose")
        app.settle()
        assert "Minimum day: Gurbani, two study blocks" in app.text("#day")


def test_coach_link_from_the_sos_app_opens_the_craving_coach():
    with App(hash="#craving-burger-nh-h20-b3-r500-w2") as app:
        app.settle(600)
        body = app.text("#sosBody")
        assert "burger" in body
        assert app.errors == []


def test_overdue_test_alert():
    with App(now="2026-11-28 10:00") as app:
        a = app.text("#alerts")
        assert "ST4 · GS3 topics 11–20 was due Thu 26 Nov" in a and "I wrote it" in a


# ---------- other tabs ----------

def test_log_tab_top3_and_note_save_as_you_type():
    with App(now="2026-11-25 22:40") as app:
        app.page.click("nav.tabs button[data-v=log]"); app.settle(200)
        app.page.fill("#lgTop0", "Finish ST4 topics 17-20")
        app.page.fill("#lgNote", "Good evening block")
        app.settle(2000)
        lg = app.store("logs/2026-11-25")
        assert lg["top3"][0] == "Finish ST4 topics 17-20" and lg["note"] == "Good evening block"
        assert lg["ai"]["segs"]                     # the timetable is untouched
        w = [x for x in app.writes() if x["path"] == "logs/2026-11-25"]
        assert w and set(w[-1]["data"]) <= {"top3", "note", "savedAt"}


def test_weeks_tap_a_day_opens_it():
    with App(now="2026-11-25 22:40") as app:
        app.page.click("nav.tabs button[data-v=calendar]"); app.settle(200)
        app.page.locator("[aria-label^='Fri 20 Nov']").first.click(); app.settle(300)
        assert "Fri 20 Nov" in app.text("#day h2")
        assert app.page.locator("#day ul.tt li").count() > 5   # the Build-my-day timetable he made that day


def test_past_rule_day_logs_through_the_same_screen():
    with App(now="2026-11-25 22:40") as app:
        app.page.click("nav.tabs button[data-v=calendar]"); app.settle(200)
        app.page.locator("[aria-label^='Thu 12 Nov']").first.click(); app.settle(300)
        before = app.store("logs/2026-11-12")
        box = row(app, "Study").get_by_role("checkbox")
        box.uncheck(); app.settle()
        mid = app.store("logs/2026-11-12")
        assert len(mid["blocks"]) == len(before["blocks"]) - 1
        box.check(); app.settle()
        after = app.store("logs/2026-11-12")
        assert len(after["blocks"]) == len(before["blocks"])
        assert after["slots"] == before["slots"] and after["asleep"] == before["asleep"]
        assert "Planned 10h" in app.text("#day")


# ---------- the trial copy ----------

def test_trial_copies_the_backup_into_its_own_database_once():
    root = pathlib.Path(__file__).parent.parent
    seed = (root / "dist/trial/seed.json").read_text()
    with App(html="dist/trial/index.html", seed={}, files={"seed.json": seed}) as app:
        app.page.wait_for_function("window.__T.store.has('plan/state')", timeout=8000); app.settle(800)
        assert "Trial copy" in app.text(".trialbar")
        n = len(json.loads(seed))
        assert len(app.page.evaluate("[...window.__T.store.keys()]")) == n
        assert app.store("logs/2026-11-25")["blocks"]["r1630"]["hours"] == 2.5
        assert "Planned 8h 30m" in app.text("#day")
        assert app.writes()[-1]["path"] == "plan/state"          # written last, so a cut-off copy reruns
        assert len([w for w in app.writes() if w["path"] == "plan/state"]) == 1
