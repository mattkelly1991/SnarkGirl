#!/usr/bin/env python3
"""
gm.py — SnarkGirl World Cup match-day helper.

A tiny, friction-free CLI so the commentator can drive the live pitch ONE
event at a time instead of rewriting the whole state.json by hand. Every verb
does the same safe cycle:

    load state.json  ->  mutate one thing  ->  stamp updatedAt
    ->  atomic write (tmp + replace)  ->  append snapshot to history.jsonl

That means a single moment ("GOAL for the PR", "straight red — secret committed",
"the keeper tips it over", "full time, advance the table") is literally one short
command, so the page updates live, kick by kick, the way a broadcast should. The
appended history.jsonl is what powers the whole-season replay.

The page renders four phases, and gm.py drives the transitions between them:
    lobby  ->  match (the animated pitch)  ->  tournament (table/bracket)
    ->  match  ->  tournament  ->  ...  ->  finished (the trophy + awards)

Run it from inside the season directory (where state.json lives), or point at
one with --dir.

Examples:
    python gm.py goal home --player "Copilot" --minute 23 --finding f1 --text "Clean try/catch wrapping — lovely finish"
    python gm.py goal away --minute 41 --finding f2 --text "Unhandled promise rejection in checkout()"
    python gm.py red away --player "config.ts" --minute 58 --reason "hardcoded API key committed"
    python gm.py save away --keeper "feat/checkout GK" --minute 66 --text "Tipped the disputed null-deref over the bar"
    python gm.py minute 90
    python gm.py fulltime --result loss --potm "Copilot" --verdict "Back to the locker room."
    python gm.py record "Kelly's Coders FC" "feat/checkout-refactor" 2 3 --away-ephemeral
    python gm.py phase tournament
    python gm.py announce "Two lovely props, then THREE criticals. feat/checkout runs riot."
    python gm.py phase finished
"""

import argparse
import datetime
import json
import os
import sys

SIDE_NAMES = {"home": "the club", "away": "the PR"}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def state_path(args):
    return os.path.join(args.dir, "state.json")


def history_path(args):
    return os.path.join(args.dir, "history.jsonl")


def load_state(args):
    with open(state_path(args), "r", encoding="utf-8-sig") as f:
        return json.load(f)


def die(msg):
    print(f"gm.py: {msg}", file=sys.stderr)
    sys.exit(1)


def match(state):
    m = state.get("match")
    if not m:
        die("no active match in state.json — write the kickoff match block first, "
            "then drive it with gm.py.")
    return m


def cur_minute(state, override):
    if override is not None:
        match(state)["minute"] = override
        return override
    return match(state).get("minute", 0)


def add_event(state, etype, side, text, player=None, finding=None, minute=None):
    m = match(state)
    ev = {
        "minute": minute if minute is not None else m.get("minute", 0),
        "type": etype,
        "side": side,
        "text": text,
    }
    if player:
        ev["player"] = player
    if finding:
        ev["finding"] = finding
    m.setdefault("events", []).append(ev)
    return ev


def other(side):
    return "away" if side == "home" else "home"


def card_player(state, side, player, color):
    if not player:
        return
    team = match(state).get(side, {})
    for p in team.get("players", []):
        if p.get("name") == player or p.get("id") == player:
            p["card"] = color
            return


def commit(args, state):
    state["updatedAt"] = now_iso()
    tmp = state_path(args) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_path(args))
    try:
        with open(history_path(args), "a", encoding="utf-8") as f:
            f.write(json.dumps(state, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"gm.py: warning — could not append history: {e}", file=sys.stderr)


# ----------------------------------------------------------------------------
# Match-event verbs
# ----------------------------------------------------------------------------

def cmd_goal(args, state):
    m = match(state)
    minute = cur_minute(state, args.minute)
    score = m.setdefault("score", {"home": 0, "away": 0})
    score[args.side] = score.get(args.side, 0) + 1
    m["ball"] = {"x": 0.98 if args.side == "home" else 0.02, "y": 0.5, "owner": None}
    who = f"{args.player} — " if args.player else ""
    text = args.text or f"GOAL for {SIDE_NAMES[args.side]}"
    add_event(state, "goal", args.side, f"{who}{text}", args.player, args.finding, minute)
    print(f"GOAL {SIDE_NAMES[args.side]} ({minute}') — "
          f"{score.get('home',0)}-{score.get('away',0)}")


def cmd_owngoal(args, state):
    m = match(state)
    minute = cur_minute(state, args.minute)
    benef = other(args.side)
    score = m.setdefault("score", {"home": 0, "away": 0})
    score[benef] = score.get(benef, 0) + 1
    m["ball"] = {"x": 0.98 if benef == "home" else 0.02, "y": 0.5, "owner": None}
    who = f"{args.player} " if args.player else ""
    text = args.text or "breaks the build / reverts progress"
    add_event(state, "owngoal", args.side,
              f"OWN GOAL — {who}{text}", args.player, args.finding, minute)
    print(f"OWN GOAL by {SIDE_NAMES[args.side]} ({minute}') — "
          f"{score.get('home',0)}-{score.get('away',0)}")


def cmd_shot(args, state):
    minute = cur_minute(state, args.minute)
    who = f"{args.player} — " if args.player else ""
    text = args.text or "shot on target (important issue)"
    add_event(state, "shot", args.side, f"{who}{text}", args.player, args.finding, minute)
    print(f"Shot on target — {SIDE_NAMES[args.side]} ({minute}')")


def cmd_save(args, state):
    minute = cur_minute(state, args.minute)
    who = f"{args.keeper} — " if args.keeper else ""
    text = args.text or "the keeper denies it (disputed finding waved away)"
    add_event(state, "save", args.side, f"{who}{text}", args.keeper, args.finding, minute)
    print(f"SAVE — {SIDE_NAMES[args.side]} ({minute}')")


def cmd_chance(args, state):
    minute = cur_minute(state, args.minute)
    who = f"{args.player} — " if args.player else ""
    add_event(state, "chance", args.side, f"{who}{args.text or 'half-chance, nothing comes of it'}",
              args.player, args.finding, minute)
    print(f"chance for {SIDE_NAMES[args.side]} ({minute}')")


def cmd_foul(args, state):
    minute = cur_minute(state, args.minute)
    who = f"{args.player} " if args.player else ""
    add_event(state, "foul", args.side, f"{who}{args.text or 'commits a foul'}",
              args.player, None, minute)
    print(f"Foul — {SIDE_NAMES[args.side]} ({minute}')")


def cmd_yellow(args, state):
    minute = cur_minute(state, args.minute)
    card_player(state, args.side, args.player, "yellow")
    who = f"{args.player} " if args.player else ""
    reason = f" — {args.reason}" if args.reason else ""
    add_event(state, "yellow", args.side, f"{who}booked{reason}", args.player, args.finding, minute)
    print(f"Yellow — {who}({SIDE_NAMES[args.side]}, {minute}')")


def cmd_red(args, state):
    m = match(state)
    minute = cur_minute(state, args.minute)
    card_player(state, args.side, args.player, "red")
    m["redCard"] = {"side": args.side, "player": args.player, "reason": args.reason, "minute": minute}
    who = f"{args.player} " if args.player else ""
    reason = f" — {args.reason}" if args.reason else ""
    add_event(state, "red", args.side, f"STRAIGHT RED — {who}off you go{reason}",
              args.player, args.finding, minute)
    print(f"RED — {who}({SIDE_NAMES[args.side]}, {minute}') — down to 10")


def cmd_sub(args, state):
    minute = cur_minute(state, args.minute)
    add_event(state, "sub", args.side,
              f"{args.off or '?'} off, {args.on or '?'} on" + (f" — {args.text}" if args.text else ""),
              args.on, None, minute)
    print(f"Sub — {SIDE_NAMES[args.side]} ({minute}')")


def cmd_ball(args, state):
    m = match(state)
    m["ball"] = {"x": args.x, "y": args.y, "owner": args.owner}
    print(f"ball -> ({args.x:.2f}, {args.y:.2f})"
          + (f" held by {args.owner}" if args.owner else ""))


def cmd_minute(args, state):
    match(state)["minute"] = args.n
    print(f"minute -> {args.n}'")


def cmd_whistle(args, state):
    minute = cur_minute(state, args.minute)
    add_event(state, "whistle", args.side or "home", args.text or "the whistle goes",
              None, None, minute)
    print(f"{args.text or 'whistle'} ({minute}')")


def cmd_kickoff(args, state):
    m = match(state)
    m["status"] = "live"
    m["minute"] = 0
    m["ball"] = {"x": 0.5, "y": 0.5, "owner": None}
    state["phase"] = "match"
    add_event(state, "kickoff", "home", args.text or "We're underway!", None, None, 0)
    print(f"KICK OFF — {m.get('fixture', 'match')}")


def cmd_fulltime(args, state):
    m = match(state)
    m["status"] = "fulltime"
    m["minute"] = max(m.get("minute", 90), 90)
    score = m.get("score", {"home": 0, "away": 0})
    hs, as_ = score.get("home", 0), score.get("away", 0)
    if args.result:
        result = args.result
    elif hs > as_:
        result = "win"
    elif hs == as_:
        result = "draw"
    else:
        result = "loss"
    m["result"] = result
    m["cleanSheet"] = (as_ == 0) if args.cleansheet is None else bool(args.cleansheet)
    if args.potm:
        m["potm"] = args.potm
    if args.verdict:
        m["verdict"] = args.verdict
    if args.report:
        m["report"] = args.report
    add_event(state, "whistle", "home",
              f"FULL TIME — {m.get('fixture','')} {hs}-{as_} ({result.upper()})",
              None, None, m["minute"])
    print(f"FULL TIME — {hs}-{as_} -> {result.upper()}"
          + (" clean sheet" if m["cleanSheet"] else ""))


# ----------------------------------------------------------------------------
# Tournament verbs
# ----------------------------------------------------------------------------

def blank_row(team):
    return {"team": team, "P": 0, "W": 0, "D": 0, "L": 0,
            "GF": 0, "GA": 0, "GD": 0, "CS": 0, "Pts": 0, "form": []}


def table_row(state, team):
    table = state.setdefault("table", [])
    for r in table:
        if r.get("team") == team:
            return r
    row = blank_row(team)
    table.append(row)
    return row


def recompute_sort(state):
    pts = state.get("config", {}).get("points", {"win": 3, "draw": 1, "loss": 0})
    for r in state.get("table", []):
        r["GD"] = r.get("GF", 0) - r.get("GA", 0)
        r["Pts"] = r.get("W", 0) * pts.get("win", 3) + r.get("D", 0) * pts.get("draw", 1) \
            + r.get("L", 0) * pts.get("loss", 0)
    state["table"] = sorted(
        state.get("table", []),
        key=lambda r: (r.get("Pts", 0), r.get("GD", 0), r.get("GF", 0)),
        reverse=True)


def cmd_record(args, state):
    hs, as_ = args.home_score, args.away_score
    ephemeral = getattr(args, "away_ephemeral", False)
    home = table_row(state, args.home)
    away = None if ephemeral else table_row(state, args.away)
    home["P"] += 1
    home["GF"] += hs
    home["GA"] += as_
    if as_ == 0:
        home["CS"] += 1
    if away is not None:
        away["P"] += 1
        away["GF"] += as_
        away["GA"] += hs
        if hs == 0:
            away["CS"] += 1
    if hs > as_:
        home["W"] += 1
        home["form"].append("W")
        if away is not None:
            away["L"] += 1
            away["form"].append("L")
    elif hs < as_:
        home["L"] += 1
        home["form"].append("L")
        if away is not None:
            away["W"] += 1
            away["form"].append("W")
    else:
        home["D"] += 1
        home["form"].append("D")
        if away is not None:
            away["D"] += 1
            away["form"].append("D")
    state.setdefault("fixtures", []).append(
        {"home": args.home, "away": args.away, "score": {"home": hs, "away": as_},
         "played": True})
    recompute_sort(state)
    print(f"recorded {args.home} {hs}-{as_} {args.away} — table updated ({len(state['table'])} teams)")


def cmd_boot(args, state):
    boot = state.setdefault("goldenBoot", [])
    for r in boot:
        if r.get("reviewer") == args.reviewer:
            r["criticals"] = r.get("criticals", 0) + args.n
            break
    else:
        boot.append({"reviewer": args.reviewer, "criticals": args.n})
    state["goldenBoot"] = sorted(boot, key=lambda r: r.get("criticals", 0), reverse=True)
    tally = next(r["criticals"] for r in state["goldenBoot"] if r["reviewer"] == args.reviewer)
    print(f"Golden Boot: {args.reviewer} -> {tally} criticals")


def cmd_award(args, state):
    state.setdefault("awards", {})[args.key] = args.value
    print(f"award {args.key} -> {args.value}")


def cmd_champion(args, state):
    state["champion"] = {"team": args.team}
    if args.text:
        state["champion"]["blurb"] = args.text
    print(f"champion -> {args.team}")


def cmd_finalcommentary(args, state):
    state["finalCommentary"] = args.text
    print("final commentary set.")


# ----------------------------------------------------------------------------
# Narration / bookkeeping verbs
# ----------------------------------------------------------------------------

def cmd_commentary(args, state):
    state["commentary"] = args.text
    print("commentary set.")


def cmd_announce(args, state):
    state.setdefault("announcements", []).append(
        {"stage": (state.get("season") or {}).get("stage", ""), "text": args.text})
    print(f"announce: {args.text}")


def cmd_phase(args, state):
    if args.phase not in ("lobby", "match", "tournament", "finished"):
        die("phase must be lobby | match | tournament | finished")
    state["phase"] = args.phase
    print(f"phase -> {args.phase}")


def cmd_stage(args, state):
    s = state.setdefault("season", {})
    if args.stage:
        s["stage"] = args.stage
    if args.round is not None:
        s["round"] = args.round
    if args.name:
        s["name"] = args.name
    print(f"season -> {s}")


def cmd_set(args, state):
    target = state
    key = args.key
    if key.startswith("match."):
        target = match(state)
        key = key[len("match."):]
    v = args.value
    if v.lstrip("-").isdigit():
        v = int(v)
    target[key] = v
    print(f"set {args.key} = {args.value}")


def build_parser():
    p = argparse.ArgumentParser(description="SnarkGirl World Cup GM helper — one moment, one command.")
    p.add_argument("--dir", default=".", help="season directory containing state.json (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def side_arg(sp):
        sp.add_argument("side", choices=["home", "away"], help="home = the author's club, away = the PR")

    sp = sub.add_parser("kickoff", help="start the active match (phase -> match, clock 0)")
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_kickoff)

    sp = sub.add_parser("goal", help="a goal: props=home, critical=away")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--finding", default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_goal)

    sp = sub.add_parser("owngoal", help="own goal (build break / revert) — counts for the other side")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--finding", default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_owngoal)

    sp = sub.add_parser("shot", help="shot on target (important issue)")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--finding", default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_shot)

    sp = sub.add_parser("save", help="a save (disputed/VAR finding waved away)")
    side_arg(sp)
    sp.add_argument("--keeper", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--finding", default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_save)

    sp = sub.add_parser("chance", help="a half-chance / build-up moment (color)")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--finding", default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_chance)

    sp = sub.add_parser("foul", help="a foul (color)")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_foul)

    sp = sub.add_parser("yellow", help="yellow card (repeated bad pattern / smell)")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--reason", default=None)
    sp.add_argument("--finding", default=None)
    sp.set_defaults(func=cmd_yellow)

    sp = sub.add_parser("red", help="straight red — code unit (secret/security) or agent (bad finding); offender down to 10, no auto-loss")
    side_arg(sp)
    sp.add_argument("--player", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--reason", default=None)
    sp.add_argument("--finding", default=None)
    sp.set_defaults(func=cmd_red)

    sp = sub.add_parser("sub", help="a substitution (color)")
    side_arg(sp)
    sp.add_argument("--off", default=None)
    sp.add_argument("--on", default=None)
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_sub)

    sp = sub.add_parser("ball", help="move the ball (x,y in 0..1; x-> attacks the away goal)")
    sp.add_argument("x", type=float)
    sp.add_argument("y", type=float)
    sp.add_argument("--owner", default=None, help="player id holding it (optional)")
    sp.set_defaults(func=cmd_ball)

    sp = sub.add_parser("minute", help="set the match clock")
    sp.add_argument("n", type=int)
    sp.set_defaults(func=cmd_minute)

    sp = sub.add_parser("whistle", help="a whistle / narration beat in the event ticker")
    sp.add_argument("--side", default=None, choices=["home", "away"])
    sp.add_argument("--minute", type=int, default=None)
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_whistle)

    sp = sub.add_parser("fulltime", help="close the match; derive/lock the result")
    sp.add_argument("--result", default=None, choices=["win", "draw", "loss"])
    sp.add_argument("--potm", default=None, help="Player of the Match")
    sp.add_argument("--cleansheet", type=int, default=None, help="1/0 to force; default derives from score")
    sp.add_argument("--verdict", default=None)
    sp.add_argument("--report", default=None)
    sp.set_defaults(func=cmd_fulltime)

    sp = sub.add_parser("record", help="record a finished fixture and recompute the table")
    sp.add_argument("home")
    sp.add_argument("away")
    sp.add_argument("home_score", type=int)
    sp.add_argument("away_score", type=int)
    sp.add_argument("--away-ephemeral", action="store_true",
                    help="away is a one-off opponent (the PR/branch) — don't add it to the league table")
    sp.set_defaults(func=cmd_record)

    sp = sub.add_parser("boot", help="add to a reviewer's Golden Boot tally (criticals)")
    sp.add_argument("reviewer")
    sp.add_argument("n", type=int)
    sp.set_defaults(func=cmd_boot)

    sp = sub.add_parser("award", help="set an end-of-season award (key value)")
    sp.add_argument("key", help="goldenBoot | goldenGlove | goldenBall | bestYoung | woodenSpoon")
    sp.add_argument("value")
    sp.set_defaults(func=cmd_award)

    sp = sub.add_parser("champion", help="crown the champion")
    sp.add_argument("team")
    sp.add_argument("--text", default=None)
    sp.set_defaults(func=cmd_champion)

    sp = sub.add_parser("finalcommentary", help="set SnarkGirl's closing commentary (finished screen)")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_finalcommentary)

    sp = sub.add_parser("commentary", help="set the live one-liner (header)")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_commentary)

    sp = sub.add_parser("announce", help="append a SnarkGirl announcement (bottom bar)")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_announce)

    sp = sub.add_parser("phase", help="set the page phase (lobby | match | tournament | finished)")
    sp.add_argument("phase")
    sp.set_defaults(func=cmd_phase)

    sp = sub.add_parser("stage", help="set season stage/round/name")
    sp.add_argument("--stage", default=None, help="group | knockout | final")
    sp.add_argument("--round", type=int, default=None)
    sp.add_argument("--name", default=None)
    sp.set_defaults(func=cmd_stage)

    sp = sub.add_parser("set", help="escape hatch: patch a scalar (key value ; prefix match. for match fields)")
    sp.add_argument("key")
    sp.add_argument("value")
    sp.set_defaults(func=cmd_set)

    return p


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass  # older Python or non-reconfigurable stream — best effort
    args = build_parser().parse_args()
    if not os.path.exists(state_path(args)):
        die(f"no state.json in '{args.dir}'. Write the initial lobby state first, "
            "then drive it with gm.py.")
    state = load_state(args)
    args.func(args, state)
    commit(args, state)


if __name__ == "__main__":
    main()
