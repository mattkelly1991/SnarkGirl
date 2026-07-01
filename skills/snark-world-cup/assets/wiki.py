#!/usr/bin/env python3
"""
wiki.py — SnarkGirl World Cup, stored in the repo Wiki as signed pages.

A GitHub Wiki is its own git repo (github.com/{owner}/{repo}.wiki.git), so the
whole tournament lives there as human-readable Markdown that anyone can browse:

    Home                      an index of every season, linking to each
    Season-{slug}             a season's standings + Golden Boot + awards + match log
    Season-{slug}-Match-{N}   one readable report per PR reviewed (fixture, timeline)

Every page ends with a signed footer:

    <!-- SGWC-SIG v1 | seq=7 | page=home | sig=<hmac-sha256 of everything above> -->

The HMAC signs the ENTIRE body above the footer — the readable table AND the
embedded machine-readable LEDGER block. So editing a win from 3 to 4 in the
GitHub wiki editor changes the signed body, and `verify` reports INVALID. You
can't re-sign a forgery without the secret.

Anti-cheat, honestly: this is a BARRIER, not a vault. With the built-in public
default secret it's tamper-EVIDENT (someone who reads this file's default could
re-sign). Teams who want a real barrier export a private SGWC_SECRET that
outsiders don't know — then a hand-edit simply cannot be re-signed.

Verbs (operate on a locally cloned wiki working directory):
    render-season  state.json standings  ->  {wiki}/Season-{slug}.md   (signed)
    render-match   state.json match       ->  {wiki}/Season-{slug}-Match-{N}.md (signed)
    render-index   scan all Season pages  ->  {wiki}/Home.md (signed landing page)
    verify         one .md file           ->  is the signature intact? (exit 0/2)
    verify-all     a wiki directory       ->  verify every signed page
    load-season    {wiki}/Season-*.md     ->  load standings into state.json (resume)

Page hierarchy:  Home (index of seasons)  ->  Season-{slug}  ->  Season-{slug}-Match-{N}

Secret resolution (first hit wins):  --secret  >  env SGWC_SECRET  >  public default
"""

import argparse
import datetime
import hashlib
import hmac
import json
import os
import re
import sys

VERSION = "SGWC-WIKI1"
LEDGER_V = 1
# Public default — tamper-EVIDENT out of the box. Export a private SGWC_SECRET
# for a real barrier that outsiders can't re-sign.
DEFAULT_SECRET = "snarkgirl-world-cup-public-v1"

SIG_RE = re.compile(r'^<!--\s*SGWC-SIG\s+v1\s*\|.*?-->\s*$', re.MULTILINE)
SIG_FIELD_RE = re.compile(r'sig=([0-9a-f]{64})')
LEDGER_RE = re.compile(r'<!--\s*SGWC-LEDGER\s+v1\s*\n(.*?)\n-->', re.DOTALL)

EVENT_ICON = {
    "goal": "⚽", "owngoal": "😬", "shot": "🎯", "save": "🧤", "chance": "🅾️",
    "foul": "🚩", "yellow": "🟨", "red": "🟥", "sub": "🔁", "kickoff": "🟢",
    "whistle": "🔔",
}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg):
    print(f"wiki.py: {msg}", file=sys.stderr)
    sys.exit(1)


def get_secret(args):
    return args.secret or os.environ.get("SGWC_SECRET") or DEFAULT_SECRET


def canonical(obj):
    """Stable JSON: sorted keys, no whitespace — round-trips through the LEDGER block."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign(secret, body):
    return hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()


def check_sig(secret, body, sig):
    return hmac.compare_digest(sign(secret, body), sig)


def normalize(body):
    """The exact bytes the HMAC signs — tolerant of editor CRLF / trailing-space churn."""
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in body.split("\n")]
    return "\n".join(lines).rstrip() + "\n"


def sign_page(secret, body, seq, page):
    nb = normalize(body)
    footer = f"<!-- SGWC-SIG v1 | seq={seq} | page={page} | sig={sign(secret, nb)} -->\n"
    return nb + footer


def split_footer(text):
    """Return (body_before_footer, sig_or_None). Body is everything above the SIG line."""
    m = SIG_RE.search(text)
    if not m:
        return text, None
    sig_m = SIG_FIELD_RE.search(m.group(0))
    return text[:m.start()], (sig_m.group(1) if sig_m else None)


def verify_text(secret, text):
    """None = unsigned, True = intact, False = tampered/wrong secret."""
    body, sig = split_footer(text)
    if sig is None:
        return None
    return check_sig(secret, normalize(body), sig)


# ----------------------------------------------------------------------------
# state.json helpers
# ----------------------------------------------------------------------------

def state_path(args):
    return os.path.join(args.dir, "state.json")


def load_state(args):
    p = state_path(args)
    if not os.path.exists(p):
        die(f"no state.json in '{args.dir}'.")
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_state(args, state):
    state["updatedAt"] = now_iso()
    tmp = state_path(args) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_path(args))


def read_page(path):
    if not os.path.exists(path):
        die(f"no such page: {path}")
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_page(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------

def fmt_gd(gd):
    return f"+{gd}" if gd > 0 else str(gd)


def slugify(name):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(name or "season")).strip("-")
    return s or "season"


def season_slug(state):
    return slugify((state.get("season") or {}).get("name") or "season")


def season_page(slug):
    return f"Season-{slug}"


def match_page(slug, seq):
    return f"Season-{slug}-Match-{seq}"


def render_season_body(state):
    season = state.get("season", {}) or {}
    table = state.get("table", []) or []
    boot = state.get("goldenBoot", []) or []
    awards = state.get("awards", {}) or {}
    champ = state.get("champion") or {}
    fixtures = state.get("fixtures", []) or []
    slug = season_slug(state)

    name = season.get("name", "Season")
    stage = season.get("stage", "group")
    L = []
    L.append(f"# 🏆 SnarkGirl World Cup — {name}")
    L.append("")
    L.append(f"_Stage: **{stage}** · updated {now_iso()}_ · [← all seasons](Home)")
    L.append("")
    if champ.get("team"):
        L.append(f"> 🏆 **Champions: {champ['team']}** — {champ.get('blurb', '')}".rstrip())
        L.append("")

    L.append("## Standings")
    L.append("")
    L.append("| # | Club | P | W | D | L | GF | GA | GD | CS | Pts | Form |")
    L.append("|--:|------|--:|--:|--:|--:|--:|--:|--:|--:|--:|------|")
    for i, r in enumerate(table, 1):
        form = "".join(r.get("form", []))
        L.append(
            f"| {i} | {r.get('team','?')} | {r.get('P',0)} | {r.get('W',0)} | "
            f"{r.get('D',0)} | {r.get('L',0)} | {r.get('GF',0)} | {r.get('GA',0)} | "
            f"{fmt_gd(r.get('GD',0))} | {r.get('CS',0)} | **{r.get('Pts',0)}** | {form} |"
        )
    L.append("")

    if boot:
        L.append("## 🥇 Golden Boot — criticals caught")
        L.append("")
        L.append("| Reviewer | Criticals |")
        L.append("|----------|--:|")
        for r in boot:
            L.append(f"| {r.get('reviewer','?')} | {r.get('criticals',0)} |")
        L.append("")

    if awards:
        L.append("## 🏅 Awards")
        L.append("")
        labels = [
            ("goldenBall", "⚽ Golden Ball (MVP)"), ("goldenBoot", "🥇 Golden Boot"),
            ("goldenGlove", "🧤 Golden Glove"), ("bestYoung", "🌟 Best Young Player"),
            ("woodenSpoon", "🥄 Wooden Spoon"),
        ]
        for key, label in labels:
            if awards.get(key):
                L.append(f"- **{label}:** {awards[key]}")
        L.append("")

    L.append("## 📋 Match Log")
    L.append("")
    if fixtures:
        for i, fx in enumerate(fixtures, 1):
            sc = fx.get("score", {}) or {}
            L.append(
                f"- [Match {i} — {fx.get('home','?')} {sc.get('home','?')}"
                f"–{sc.get('away','?')} {fx.get('away','?')}]({match_page(slug, i)})"
            )
    else:
        L.append("_No matches played yet._")
    L.append("")

    ledger = {
        "v": LEDGER_V,
        "kind": "season",
        "slug": slug,
        "season": season,
        "table": table,
        "goldenBoot": boot,
        "awards": awards,
        "champion": state.get("champion"),
        "fixtures": fixtures,
    }
    L.append(f"<!-- SGWC-LEDGER v1\n{canonical(ledger)}\n-->")
    L.append("")
    return "\n".join(L)


def render_match_body(state, seq):
    m = state.get("match", {}) or {}
    home = m.get("home", {}) or {}
    away = m.get("away", {}) or {}
    score = m.get("score", {}) or {}
    fixture = m.get("fixture", f"{home.get('name','Home')} vs {away.get('name','Away')}")
    result = (m.get("result") or "?").upper()
    hs, as_ = score.get("home", 0), score.get("away", 0)
    slug = season_slug(state)
    season_name = (state.get("season") or {}).get("name", "Season")

    L = []
    L.append(f"# ⚽ Match {seq} — {fixture}")
    L.append("")
    L.append(f"**{home.get('name','Home')} {hs}–{as_} {away.get('name','Away')}** · "
             f"{result} · {m.get('stage','')}".rstrip(" ·"))
    L.append("")
    cs = "denied" if not m.get("cleanSheet") else "kept 🧤"
    L.append(f"🎖️ POTM: **{m.get('potm','—')}** · Clean sheet: {cs}")
    if m.get("verdict"):
        L.append("")
        L.append(f"> {m['verdict']}")
    L.append("")

    events = m.get("events", []) or []
    if events:
        L.append("## Timeline")
        L.append("")
        L.append("| Min | | Event |")
        L.append("|--:|:-:|-------|")
        for ev in events:
            icon = EVENT_ICON.get(ev.get("type", ""), "•")
            minute = ev.get("minute", "")
            text = (ev.get("text", "") or "").replace("|", "\\|")
            L.append(f"| {minute}' | {icon} | {text} |")
        L.append("")

    L.append(f"[← {season_name} standings]({season_page(slug)}) · [all seasons](Home)")
    L.append("")
    return "\n".join(L)


def render_index_body(seasons):
    """seasons: list of dicts {name, slug, stage, champion, leader, matches, finished}."""
    L = []
    L.append("# 🏆 SnarkGirl World Cup")
    L.append("")
    L.append(f"_The tournament ledger — signed & tamper-evident · updated {now_iso()}_")
    L.append("")
    L.append("## Seasons")
    L.append("")
    if seasons:
        L.append("| Season | Stage | Leader / Champion | Matches |")
        L.append("|--------|-------|-------------------|--:|")
        for s in seasons:
            crown = f"🏆 {s['champion']}" if s.get("champion") else (s.get("leader") or "—")
            L.append(f"| [{s['name']}]({season_page(s['slug'])}) | {s.get('stage','')} "
                     f"| {crown} | {s.get('matches', 0)} |")
    else:
        L.append("_No seasons yet. Say “SnarkGirl, kickoff” to start one._")
    L.append("")

    ledger = {"v": LEDGER_V, "kind": "index",
              "seasons": [{"name": s["name"], "slug": s["slug"]} for s in seasons]}
    L.append(f"<!-- SGWC-LEDGER v1\n{canonical(ledger)}\n-->")
    L.append("")
    return "\n".join(L)


def scan_seasons(secret, wiki):
    """Find every signed Season page, verify it, and pull a summary for the index."""
    seasons = []
    for fn in sorted(os.listdir(wiki)):
        if not (fn.startswith("Season-") and fn.endswith(".md")) or "-Match-" in fn:
            continue
        text = read_page(os.path.join(wiki, fn))
        m = LEDGER_RE.search(text)
        if not m:
            continue
        try:
            led = json.loads(m.group(1))
        except Exception:
            continue
        season = led.get("season", {}) or {}
        table = led.get("table", []) or []
        champ = (led.get("champion") or {}).get("team")
        seasons.append({
            "name": season.get("name", fn[7:-3]),
            "slug": led.get("slug", slugify(season.get("name", fn[7:-3]))),
            "stage": season.get("stage", ""),
            "champion": champ,
            "leader": (table[0].get("team") if table else None),
            "matches": len(led.get("fixtures", []) or []),
            "sigOk": verify_text(secret, text),
        })
    seasons.sort(key=lambda s: [int(t) if t.isdigit() else t.lower()
                                for t in re.split(r"(\d+)", s["name"]) if t])
    return seasons


# ----------------------------------------------------------------------------
# Verbs
# ----------------------------------------------------------------------------

def cmd_render_season(args, secret):
    state = load_state(args)
    seq = args.seq if args.seq is not None else len(state.get("fixtures", []) or [])
    slug = season_slug(state)
    body = render_season_body(state)
    page = sign_page(secret, body, seq, "season")
    out = args.out or os.path.join(args.wiki, f"{season_page(slug)}.md")
    write_page(out, page)
    print(f"wrote {out} — signed (season={slug}, seq={seq}, {len(state.get('table', []))} clubs)")


def cmd_render_match(args, secret):
    state = load_state(args)
    seq = args.seq if args.seq is not None else len(state.get("fixtures", []) or []) or 1
    slug = season_slug(state)
    body = render_match_body(state, seq)
    page = sign_page(secret, body, seq, "match")
    out = args.out or os.path.join(args.wiki, f"{match_page(slug, seq)}.md")
    write_page(out, page)
    print(f"wrote {out} — signed (season={slug}, match #{seq})")


def cmd_render_index(args, secret):
    seasons = scan_seasons(secret, args.wiki)
    body = render_index_body(seasons)
    page = sign_page(secret, body, len(seasons), "index")
    out = args.out or os.path.join(args.wiki, "Home.md")
    write_page(out, page)
    tampered = [s["name"] for s in seasons if s.get("sigOk") is False]
    note = f" — ⚠️ tampered: {', '.join(tampered)}" if tampered else ""
    print(f"wrote {out} — signed index of {len(seasons)} season(s){note}")


def cmd_verify(args, secret):
    text = read_page(args.file)
    res = verify_text(secret, text)
    if res is None:
        print(f"{args.file}: no signature (unsigned page)")
        sys.exit(3)
    print(f"{args.file}: signature {'OK ✅' if res else 'INVALID ❌ (edited or wrong secret)'}")
    sys.exit(0 if res else 2)


def cmd_verify_all(args, secret):
    bad = 0
    signed = 0
    for fn in sorted(os.listdir(args.wiki)):
        if not fn.endswith(".md"):
            continue
        text = read_page(os.path.join(args.wiki, fn))
        res = verify_text(secret, text)
        if res is None:
            print(f"  {fn:<28} — unsigned (skipped)")
            continue
        signed += 1
        if res:
            print(f"  {fn:<28} — OK ✅")
        else:
            print(f"  {fn:<28} — INVALID ❌")
            bad += 1
    print("-" * 44)
    if bad:
        print(f"⚠️  {bad} of {signed} signed page(s) tampered with — someone edited the wiki by hand.")
        sys.exit(2)
    print(f"✅ all {signed} signed page(s) intact.")


def cmd_load_season(args, secret):
    text = read_page(args.file)
    res = verify_text(secret, text)
    if res is None:
        die(f"{args.file} has no SGWC-SIG footer — not a SnarkGirl wiki page.")
    if not res and not args.force:
        die("SIGNATURE INVALID — the season page was edited by hand or signed with a "
            "different secret. Refusing to load. Re-run with --force only if you trust it.")
    if not res:
        print("wiki.py: WARNING — signature invalid, loading anyway (--force).", file=sys.stderr)

    m = LEDGER_RE.search(text)
    if not m:
        die("no SGWC-LEDGER block found — cannot recover standings.")
    try:
        ledger = json.loads(m.group(1))
    except Exception as e:
        die(f"corrupt LEDGER block ({e}).")
    if ledger.get("kind") == "index":
        die("that's the Home index page — pass a Season-*.md page to resume standings.")

    state = load_state(args)
    for k in ("season", "table", "goldenBoot", "awards", "champion", "fixtures"):
        if k in ledger:
            state[k] = ledger[k]
    state["resumedFrom"] = {
        "source": "wiki",
        "page": os.path.basename(args.file),
        "signatureOk": res,
        "loadedAt": now_iso(),
    }
    write_state(args, state)
    print(f"resumed season '{(ledger.get('season') or {}).get('name','?')}' "
          f"({len(ledger.get('table', []))} clubs, "
          f"{len(ledger.get('fixtures', []))} matches) — signature {'OK' if res else 'INVALID'}")


def build_parser():
    p = argparse.ArgumentParser(description="SnarkGirl World Cup — signed wiki pages.")
    p.add_argument("--dir", default=".", help="season directory with state.json")
    p.add_argument("--wiki", default=".", help="local clone of the repo wiki")
    p.add_argument("--secret", default=None, help="HMAC secret (else env SGWC_SECRET, else public default)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("render-season", help="write a signed Season standings page")
    sp.add_argument("--seq", type=int, default=None, help="match number (else = matches played)")
    sp.add_argument("--out", default=None, help="output path (else {wiki}/Season-{slug}.md)")
    sp.set_defaults(func=cmd_render_season)

    sp = sub.add_parser("render-match", help="write a signed per-match report page")
    sp.add_argument("--seq", type=int, default=None, help="match number (else = matches played)")
    sp.add_argument("--out", default=None, help="output path (else {wiki}/Season-{slug}-Match-{seq}.md)")
    sp.set_defaults(func=cmd_render_match)

    sp = sub.add_parser("render-index", help="rebuild the signed Home index from all Season pages")
    sp.add_argument("--out", default=None, help="output path (else {wiki}/Home.md)")
    sp.set_defaults(func=cmd_render_index)

    sp = sub.add_parser("verify", help="check one page's signature")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_verify)

    sp = sub.add_parser("verify-all", help="verify every signed page in the wiki")
    sp.set_defaults(func=cmd_verify_all)

    sp = sub.add_parser("load-season", help="load a Season page's standings into state.json")
    sp.add_argument("file")
    sp.add_argument("--force", action="store_true", help="load even if the signature is invalid")
    sp.set_defaults(func=cmd_load_season)

    return p


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args()
    args.func(args, get_secret(args))


if __name__ == "__main__":
    main()
