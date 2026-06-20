#!/usr/bin/env python3
"""
gm.py — SnarkGirl Battle Royale Game Master helper.

A tiny, friction-free CLI so the Game Master can update the live arena ONE
event at a time instead of rewriting the whole state.json in a big batch at
the end of a turn. Every verb does the same safe cycle:

    load state.json  ->  mutate one thing  ->  stamp updatedAt
    ->  atomic write (tmp + replace)  ->  append snapshot to history.jsonl

That means a single observation ("FlashFury found a bug", "the cannon fires for
HaikuHavoc", "two tributes square up") is literally one short command, so the
page updates live, event by event, the way a spectator broadcast should.

Run it from inside the arena directory (where state.json lives), or point at
one with --dir.

Examples:
    python gm.py find flash-fury critical src/auth.ts:42 "Token never expires" --fix "Add TTL check"
    python gm.py invalid haiku-havoc --reason "hallucinated race condition"
    python gm.py hurt mini-menace 3 --reason hunger --epitaph "Ran out of ridge to camp."
    python gm.py fight flash-fury rhyme-reaper
    python gm.py endfight flash-fury rhyme-reaper --stake 4
    python gm.py move codex-crusher feed-flats
    python gm.py zone config-flats closing
    python gm.py announce "The storm comes for Config Flats. Three remain. 💅"
    python gm.py phase finished
"""

import argparse
import datetime
import json
import os
import sys

SEVERITY_BOUNTY = {"critical": 3, "important": 2, "nitpick": 1}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def state_path(args):
    return os.path.join(args.dir, "state.json")


def history_path(args):
    return os.path.join(args.dir, "history.jsonl")


def load_state(args):
    with open(state_path(args), "r", encoding="utf-8-sig") as f:
        return json.load(f)


def find_tribute(state, tid):
    for c in state.get("contestants", []):
        if c.get("id") == tid:
            return c
    die(f"no contestant with id '{tid}'. Known ids: "
        + ", ".join(c.get("id", "?") for c in state.get("contestants", [])))


def find_zone(state, zid):
    for z in state.get("zones", []):
        if z.get("id") == zid:
            return z
    die(f"no zone with id '{zid}'. Known ids: "
        + ", ".join(z.get("id", "?") for z in state.get("zones", [])))


def add_feed(state, ftype, text):
    """Append a factual feed entry, stamped with the current turn."""
    state.setdefault("feed", []).append(
        {"turn": state.get("turn", 0), "type": ftype, "text": text}
    )


def die(msg):
    print(f"gm.py: {msg}", file=sys.stderr)
    sys.exit(1)


def kill_tribute(state, c, cause, epitaph):
    """Flip a tribute to dead and fire the cannon. Never leave anyone at 0 alive."""
    c["status"] = "dead"
    c["rations"] = 0
    c["action"] = "roaming"
    c["opponent"] = None
    c["causeOfDeath"] = cause or f"perished in {c.get('zone', 'the arena')}"
    c["epitaph"] = epitaph or ""
    add_feed(state, "kill",
             f"💀 {c.get('name', c['id'])} — {c['causeOfDeath']}"
             + (f' | "{epitaph}"' if epitaph else ""))


def commit(args, state):
    """Atomic write of the whole state, then append the snapshot to history."""
    state["updatedAt"] = now_iso()
    tmp = state_path(args) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_path(args))
    # History powers the shareable replay — append the same snapshot, one per line.
    try:
        with open(history_path(args), "a", encoding="utf-8") as f:
            f.write(json.dumps(state, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"gm.py: warning — could not append history: {e}", file=sys.stderr)


# ----------------------------------------------------------------------------
# Verbs
# ----------------------------------------------------------------------------

def cmd_find(args, state):
    c = find_tribute(state, args.tribute)
    if c.get("status") == "dead":
        die(f"{args.tribute} is dead and cannot find anything.")
    sev = args.severity.lower()
    if sev not in SEVERITY_BOUNTY:
        die(f"severity must be one of {list(SEVERITY_BOUNTY)}")
    bounty = SEVERITY_BOUNTY[sev]
    findings = state.setdefault("findings", [])
    fid = args.id or f"f{len(findings) + 1}"
    file_part, _, line_part = args.location.partition(":")
    findings.append({
        "id": fid,
        "severity": sev,
        "title": args.title,
        "file": file_part,
        "line": int(line_part) if line_part.isdigit() else line_part or None,
        "foundBy": c.get("name", c["id"]),
        "turn": state.get("turn", 0),
        "contested": False,
        "status": "validated",
        "fix": args.fix,
        "fellBecause": None,
    })
    c["rations"] = c.get("rations", 0) + bounty
    c["finds"] = c.get("finds", 0) + 1
    c["action"] = "feasting"
    icon = {"critical": "🚨", "important": "⚠️", "nitpick": "💅"}[sev]
    add_feed(state, "find",
             f"{icon} {c.get('name', c['id'])} found {sev.upper()} in "
             f"`{args.location}` — +{bounty} 🍖 — \"{args.title}\"")
    print(f"{c.get('name', c['id'])} +{bounty}🍖 (now {c['rations']}🍖) — finding {fid}")


def cmd_invalid(args, state):
    c = find_tribute(state, args.tribute)
    c["rations"] = c.get("rations", 0) - 1
    reason = f" — {args.reason}" if args.reason else ""
    add_feed(state, "info",
             f"❌ {c.get('name', c['id'])}'s claim was INVALID — −1 🍖{reason}")
    if c["rations"] <= 0 and c.get("status") != "dead":
        kill_tribute(state, c, args.cause or f"starved on a lie in {c.get('zone', 'the arena')}", args.epitaph)
        print(f"{c.get('name', c['id'])} −1🍖 and DIED on a bad claim.")
    else:
        print(f"{c.get('name', c['id'])} −1🍖 (now {c['rations']}🍖) — invalid claim.")


def cmd_reward(args, state):
    c = find_tribute(state, args.tribute)
    c["rations"] = c.get("rations", 0) + args.amount
    if args.reason:
        add_feed(state, "info", f"🍖 {c.get('name', c['id'])} +{args.amount} 🍖 — {args.reason}")
    print(f"{c.get('name', c['id'])} +{args.amount}🍖 (now {c['rations']}🍖)")


def cmd_hurt(args, state):
    c = find_tribute(state, args.tribute)
    c["rations"] = c.get("rations", 0) - args.amount
    reason = f" — {args.reason}" if args.reason else ""
    if c["rations"] <= 0 and c.get("status") != "dead":
        cause = args.cause or f"starved in {c.get('zone', 'the arena')}"
        kill_tribute(state, c, cause, args.epitaph)
        print(f"{c.get('name', c['id'])} −{args.amount}🍖 and DIED.{reason}")
    else:
        add_feed(state, "storm" if args.reason == "storm" else "info",
                 f"🩸 {c.get('name', c['id'])} −{args.amount} 🍖{reason} (now {c['rations']}🍖)")
        print(f"{c.get('name', c['id'])} −{args.amount}🍖 (now {c['rations']}🍖){reason}")


def cmd_kill(args, state):
    c = find_tribute(state, args.tribute)
    kill_tribute(state, c, args.cause, args.epitaph)
    print(f"💀 {c.get('name', c['id'])} is dead — {c['causeOfDeath']}")


def cmd_move(args, state):
    c = find_tribute(state, args.tribute)
    if c.get("status") == "dead":
        die("the dead don't relocate — leave them where they fell.")
    find_zone(state, args.zone)  # validate
    old = c.get("zone")
    c["zone"] = args.zone
    c["action"] = "roaming"
    add_feed(state, "move",
             f"🥾 {c.get('name', c['id'])} relocated to {args.zone}")
    print(f"{c.get('name', c['id'])} moved {old} → {args.zone}")


def cmd_fight(args, state):
    a = find_tribute(state, args.a)
    b = find_tribute(state, args.b)
    if a.get("zone") != b.get("zone"):
        die(f"{args.a} ({a.get('zone')}) and {args.b} ({b.get('zone')}) "
            "aren't in the same zone — they can't skirmish.")
    for x, y in ((a, b), (b, a)):
        x["action"] = "fighting"
        x["opponent"] = y["id"]
    add_feed(state, "skirmish",
             f"⚔️ {a.get('name', a['id'])} and {b.get('name', b['id'])} "
             f"square up in {a.get('zone')}"
             + (f" over {args.over}" if args.over else ""))
    print(f"⚔️ {a.get('name', a['id'])} vs {b.get('name', b['id'])} — fight on.")


def cmd_endfight(args, state):
    w = find_tribute(state, args.winner)
    l = find_tribute(state, args.loser)
    stake = args.stake if args.stake is not None else min(2, l.get("rations", 0))
    stake = min(stake, l.get("rations", 0))
    l["rations"] = l.get("rations", 0) - stake
    w["rations"] = w.get("rations", 0) + (0 if args.no_transfer else stake)
    w["action"] = "roaming"
    w["opponent"] = None
    if args.finding:
        for fnd in state.get("findings", []):
            if fnd.get("id") == args.finding:
                fnd["foundBy"] = w.get("name", w["id"])
    if l["rations"] <= 0 and l.get("status") != "dead":
        w["kills"] = w.get("kills", 0) + 1
        kill_tribute(state, l, args.cause or f"slain by {w.get('name', w['id'])} in {l.get('zone', 'the arena')}", args.epitaph)
        add_feed(state, "skirmish",
                 f"⚔️ {w.get('name', w['id'])} DEFEATED {l.get('name', l['id'])} "
                 f"— took {stake} 🍖 and the kill")
        print(f"⚔️ {w.get('name', w['id'])} won and KILLED {l.get('name', l['id'])} (+{stake}🍖, +1 kill)")
    else:
        l["action"] = "roaming"
        l["opponent"] = None
        add_feed(state, "skirmish",
                 f"⚔️ {w.get('name', w['id'])} bested {l.get('name', l['id'])} "
                 f"— took {stake} 🍖. {l.get('name', l['id'])} limps off.")
        print(f"⚔️ {w.get('name', w['id'])} won (+{stake}🍖). "
              f"{l.get('name', l['id'])} survives at {l['rations']}🍖")


def cmd_feast(args, state):
    c = find_tribute(state, args.tribute)
    c["action"] = "feasting"
    print(f"{c.get('name', c['id'])} is feasting.")


def cmd_roam(args, state):
    c = find_tribute(state, args.tribute)
    c["action"] = "roaming"
    c["opponent"] = None
    print(f"{c.get('name', c['id'])} is roaming.")


def cmd_zone(args, state):
    z = find_zone(state, args.zone)
    if args.status not in ("safe", "closing", "closed"):
        die("status must be safe | closing | closed")
    z["status"] = args.status
    if args.status in ("closing", "closed"):
        verb = "is CLOSING" if args.status == "closing" else "has CLOSED"
        add_feed(state, "storm", f"🌀 {z.get('name', z['id'])} {verb} — the storm rolls in")
    print(f"zone {args.zone} → {args.status}")


def cmd_feed(args, state):
    add_feed(state, args.type, args.text)
    print(f"feed[{args.type}]: {args.text}")


def cmd_announce(args, state):
    state.setdefault("announcements", []).append(
        {"turn": state.get("turn", 0), "text": args.text})
    print(f"announce: {args.text}")


def cmd_commentary(args, state):
    state["commentary"] = args.text
    print(f"commentary set.")


def cmd_turn(args, state):
    state["turn"] = args.n
    print(f"turn → {args.n}")


def cmd_phase(args, state):
    if args.phase not in ("lobby", "live", "finished"):
        die("phase must be lobby | live | finished")
    state["phase"] = args.phase
    print(f"phase → {args.phase}")


def cmd_set(args, state):
    """Patch one contestant's scalar fields directly (escape hatch)."""
    c = find_tribute(state, args.tribute)
    for pair in args.kv:
        k, _, v = pair.partition("=")
        if v.lstrip("-").isdigit():
            v = int(v)
        c[k] = v
    print(f"{c.get('name', c['id'])} patched: {', '.join(args.kv)}")


def build_parser():
    p = argparse.ArgumentParser(description="SnarkGirl Battle Royale GM helper — one event, one command.")
    p.add_argument("--dir", default=".", help="arena directory containing state.json (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("find", help="validate a finding: pay rations, feast, log it")
    sp.add_argument("tribute")
    sp.add_argument("severity", help="critical | important | nitpick")
    sp.add_argument("location", help="file:line")
    sp.add_argument("title")
    sp.add_argument("--fix", default=None)
    sp.add_argument("--id", default=None)
    sp.set_defaults(func=cmd_find)

    sp = sub.add_parser("invalid", help="reject a claim: −1 ration (auto-death at 0)")
    sp.add_argument("tribute")
    sp.add_argument("--reason", default=None)
    sp.add_argument("--cause", default=None)
    sp.add_argument("--epitaph", default=None)
    sp.set_defaults(func=cmd_invalid)

    sp = sub.add_parser("reward", help="add rations to a tribute")
    sp.add_argument("tribute")
    sp.add_argument("amount", type=int)
    sp.add_argument("--reason", default=None)
    sp.set_defaults(func=cmd_reward)

    sp = sub.add_parser("hurt", help="subtract rations (hunger/storm/etc; auto-death at 0)")
    sp.add_argument("tribute")
    sp.add_argument("amount", type=int)
    sp.add_argument("--reason", default=None, help="e.g. hunger, storm")
    sp.add_argument("--cause", default=None)
    sp.add_argument("--epitaph", default=None)
    sp.set_defaults(func=cmd_hurt)

    sp = sub.add_parser("kill", help="mark a tribute dead and fire the cannon")
    sp.add_argument("tribute")
    sp.add_argument("--cause", default=None)
    sp.add_argument("--epitaph", default=None)
    sp.set_defaults(func=cmd_kill)

    sp = sub.add_parser("move", help="relocate a living tribute to a zone")
    sp.add_argument("tribute")
    sp.add_argument("zone")
    sp.set_defaults(func=cmd_move)

    sp = sub.add_parser("fight", help="start a skirmish (both square up)")
    sp.add_argument("a")
    sp.add_argument("b")
    sp.add_argument("--over", default=None, help="what they're fighting over")
    sp.set_defaults(func=cmd_fight)

    sp = sub.add_parser("endfight", help="resolve a skirmish: winner takes stake (auto-death at 0)")
    sp.add_argument("winner")
    sp.add_argument("loser")
    sp.add_argument("--stake", type=int, default=None, help="rations transferred (default 2)")
    sp.add_argument("--finding", default=None, help="finding id whose ownership transfers to winner")
    sp.add_argument("--no-transfer", action="store_true", help="loser pays the stake but winner doesn't gain it")
    sp.add_argument("--cause", default=None)
    sp.add_argument("--epitaph", default=None)
    sp.set_defaults(func=cmd_endfight)

    sp = sub.add_parser("feast", help="set a tribute to feasting")
    sp.add_argument("tribute")
    sp.set_defaults(func=cmd_feast)

    sp = sub.add_parser("roam", help="set a tribute back to roaming")
    sp.add_argument("tribute")
    sp.set_defaults(func=cmd_roam)

    sp = sub.add_parser("zone", help="set a zone's status (fires storm feed on close)")
    sp.add_argument("zone")
    sp.add_argument("status", help="safe | closing | closed")
    sp.set_defaults(func=cmd_zone)

    sp = sub.add_parser("feed", help="append an arbitrary feed entry")
    sp.add_argument("type", help="kill | skirmish | find | move | storm | info")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_feed)

    sp = sub.add_parser("announce", help="append a Game Master announcement (SnarkGirl's voice)")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_announce)

    sp = sub.add_parser("commentary", help="set the current turn's one-liner commentary")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_commentary)

    sp = sub.add_parser("turn", help="set the turn number")
    sp.add_argument("n", type=int)
    sp.set_defaults(func=cmd_turn)

    sp = sub.add_parser("phase", help="set the phase (lobby | live | finished)")
    sp.add_argument("phase")
    sp.set_defaults(func=cmd_phase)

    sp = sub.add_parser("set", help="escape hatch: patch a contestant's scalar fields (key=value ...)")
    sp.add_argument("tribute")
    sp.add_argument("kv", nargs="+", help="one or more key=value pairs")
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
