#!/usr/bin/env python3
"""
token.py — SnarkGirl World Cup tournament token (the portable "save file").

A SnarkGirl World Cup is played by REAL PEOPLE, one match (PR review) at a time,
spread across many tickets and PRs and across many work sessions. There is no
server and no committed standings file. Instead, the whole tournament state
travels as a short, signed, append-only TOKEN that gets pasted into the
ticket/PR comment at the end of each match. The next person loads that token to
continue.

    SGWC1.<base64url(payload)>.<hmac>

The payload carries the standings, awards, golden boot, season info, AND the
chain metadata that makes the ledger tamper-EVIDENT:

    seq        the match number (1, 2, 3, ...) — strictly increments by one
    prevHash   hash of the PREVIOUS token — the cryptographic back-link
    prevRef    URL of the previous match's comment — the human-walkable back-link
    lastMatch  a compact record of the match this token closed (fixture/score/result)

Anti-cheat, honestly: with no server this is a DETERRENT, not a guarantee.
Anyone who knows the signing secret can forge a token. The point is that
(a) editing the standings breaks the HMAC, and (b) the seq + prevHash + prevRef
chain makes a hidden or dropped match obvious — `audit` walks the chain and
flags any gap or broken link. Teams who want real protection set a private
SGWC_SECRET so outsiders can't re-sign a forgery.

Verbs:
    encode   state.json standings  ->  a new token (the new chain head)
    decode   a token  ->  load its standings into state.json (resume / fork)
    verify   a token  ->  is the signature intact? (tamper check)
    audit    a file of tokens (one per line)  ->  walk the whole chain for gaps

Secret resolution order (first hit wins):
    --secret  >  env SGWC_SECRET  >  built-in public default
"""

import argparse
import base64
import datetime
import hashlib
import hmac
import json
import os
import sys

VERSION = "SGWC1"
PAYLOAD_V = 1
# Public default — makes tokens tamper-EVIDENT out of the box. Teams that want
# tamper-RESISTANCE export a private SGWC_SECRET that outsiders don't know.
DEFAULT_SECRET = "snarkgirl-world-cup-public-v1"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg):
    print(f"token.py: {msg}", file=sys.stderr)
    sys.exit(1)


def get_secret(args):
    return args.secret or os.environ.get("SGWC_SECRET") or DEFAULT_SECRET


def canonical(obj):
    """Stable JSON: sorted keys, no whitespace — the bytes the HMAC signs."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def b64u_encode(s):
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("ascii").rstrip("=")


def b64u_decode(s):
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad).decode("utf-8")


def sign(secret, body):
    return hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()


def build_token(secret, payload):
    body = VERSION + "." + b64u_encode(canonical(payload))
    return body + "." + sign(secret, body)


def token_hash(token):
    """The hash a FOLLOWING token records as its prevHash."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def parse_token(token):
    token = token.strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != VERSION:
        die(f"not a {VERSION} token (expected '{VERSION}.<payload>.<sig>').")
    ver, body64, sig = parts
    try:
        payload = json.loads(b64u_decode(body64))
    except Exception as e:
        die(f"corrupt token payload — could not decode ({e}).")
    return payload, sig, f"{ver}.{body64}"


def check_sig(secret, body, sig):
    return hmac.compare_digest(sign(secret, body), sig)


# ----------------------------------------------------------------------------
# state.json helpers (encode/decode read & write the local season state)
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


def standings_from_state(state):
    """Pull just the tournament-wide slices a token needs to carry."""
    return {
        "season": state.get("season", {}),
        "table": state.get("table", []),
        "goldenBoot": state.get("goldenBoot", []),
        "awards": state.get("awards", {}),
        "champion": state.get("champion"),
    }


def last_match_from_state(state):
    m = state.get("match") or {}
    if not m:
        return None
    return {
        "fixture": m.get("fixture"),
        "home": (m.get("home") or {}).get("name"),
        "away": (m.get("away") or {}).get("name"),
        "score": m.get("score", {}),
        "result": m.get("result"),
        "cleanSheet": m.get("cleanSheet"),
    }


# ----------------------------------------------------------------------------
# Verbs
# ----------------------------------------------------------------------------

def cmd_encode(args, secret):
    state = load_state(args)
    resumed = state.get("resumedFrom") or {}
    seq = args.seq if args.seq is not None else (resumed.get("seq", 0) + 1)
    prev_hash = args.prev_hash if args.prev_hash is not None else resumed.get("hash")
    prev_ref = args.prev_ref if args.prev_ref is not None else resumed.get("ref")

    payload = {
        "v": PAYLOAD_V,
        "seq": seq,
        "prevHash": prev_hash,
        "prevRef": prev_ref,
        "createdAt": now_iso(),
        "lastMatch": last_match_from_state(state),
    }
    payload.update(standings_from_state(state))

    token = build_token(secret, payload)
    this_hash = token_hash(token)

    # Record the new head locally so the page can render the ledger and so a
    # follow-up encode in the same session chains correctly.
    state["chain"] = {
        "seq": seq,
        "prevHash": prev_hash,
        "prevRef": prev_ref,
        "thisHash": this_hash,
        "createdAt": payload["createdAt"],
        "token": token,
    }
    write_state(args, state)

    if args.quiet:
        print(token)
        return
    print(f"# SnarkGirl World Cup — match #{seq} token (chain head)")
    print(f"# thisHash={this_hash}  prevHash={prev_hash or '-'}  prevRef={prev_ref or '-'}")
    print(token)
    print(f"\n# Store this HEAD in team memory:")
    print(f"#   World Cup HEAD: seq={seq}, hash={this_hash}, comment=<URL of the comment you post this token in>")


def cmd_decode(args, secret):
    payload, sig, body = parse_token(args.token)
    ok = check_sig(secret, body, sig)
    if not ok and not args.force:
        die("SIGNATURE INVALID — this token was edited or signed with a different "
            "secret. Refusing to load. Re-run with --force only if you trust it.")
    if not ok:
        print("token.py: WARNING — signature invalid, loading anyway (--force).", file=sys.stderr)

    state = load_state(args)
    for k in ("season", "table", "goldenBoot", "awards", "champion"):
        if k in payload:
            state[k] = payload[k]
    state["resumedFrom"] = {
        "seq": payload.get("seq", 0),
        "hash": token_hash(args.token),
        "ref": args.ref,  # URL where THIS token lives — becomes next match's prevRef
        "signatureOk": ok,
    }
    write_state(args, state)
    print(f"resumed tournament at match #{payload.get('seq', 0)} "
          f"({len(payload.get('table', []))} teams) — signature {'OK' if ok else 'INVALID'}")
    if not args.ref:
        print("token.py: note — no --ref given; pass the comment URL so the next "
              "match can back-link to it.", file=sys.stderr)


def cmd_verify(args, secret):
    payload, sig, body = parse_token(args.token)
    ok = check_sig(secret, body, sig)
    print(f"version    : {VERSION}")
    print(f"seq        : {payload.get('seq')}")
    print(f"prevHash   : {payload.get('prevHash') or '-'}")
    print(f"prevRef    : {payload.get('prevRef') or '-'}")
    print(f"thisHash   : {token_hash(args.token)}")
    print(f"teams      : {len(payload.get('table', []))}")
    lm = payload.get("lastMatch") or {}
    if lm:
        sc = lm.get("score", {})
        print(f"lastMatch  : {lm.get('fixture','?')} "
              f"{sc.get('home','?')}-{sc.get('away','?')} ({lm.get('result','?')})")
    print(f"signature  : {'OK ✅' if ok else 'INVALID ❌ (tampered or wrong secret)'}")
    sys.exit(0 if ok else 2)


def cmd_audit(args, secret):
    raw = []
    with open(args.file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                raw.append(line)
    if not raw:
        die(f"no tokens found in {args.file} (one token per line).")

    parsed = []
    for t in raw:
        payload, sig, body = parse_token(t)
        parsed.append({
            "token": t, "payload": payload,
            "sigOk": check_sig(secret, body, sig),
            "hash": token_hash(t),
            "seq": payload.get("seq", 0),
            "prevHash": payload.get("prevHash"),
            "prevRef": payload.get("prevRef"),
        })
    parsed.sort(key=lambda r: r["seq"])

    print(f"=== SnarkGirl World Cup — chain audit ({len(parsed)} tokens) ===")
    problems = 0
    expected_seq = 1
    prev = None
    for r in parsed:
        flags = []
        if not r["sigOk"]:
            flags.append("BAD-SIGNATURE")
        if r["seq"] != expected_seq:
            flags.append(f"SEQ-GAP(expected {expected_seq}, got {r['seq']})")
        if prev is not None:
            if r["prevHash"] != prev["hash"]:
                flags.append("BROKEN-BACKLINK(prevHash≠previous thisHash)")
            if not r["prevRef"]:
                flags.append("MISSING-PREVREF")
        elif r["seq"] == 1 and r["prevHash"]:
            flags.append("GENESIS-HAS-PREVHASH")
        status = "OK" if not flags else " / ".join(flags)
        if flags:
            problems += 1
        lm = r["payload"].get("lastMatch") or {}
        print(f"  #{r['seq']:>2}  {r['hash']}  {('← ' + r['prevRef']) if r['prevRef'] else '(genesis)'}")
        print(f"       {lm.get('fixture','?')}  ->  {status}")
        expected_seq = r["seq"] + 1
        prev = r

    print("=" * 50)
    if problems:
        print(f"⚠️  {problems} problem(s) found — the ledger has been tampered with "
              f"or a match is missing.")
        sys.exit(2)
    print("✅ chain intact — every match links to the last, signatures valid, no gaps.")


def build_parser():
    p = argparse.ArgumentParser(description="SnarkGirl World Cup tournament token tool.")
    p.add_argument("--dir", default=".", help="season directory with state.json (encode/decode)")
    p.add_argument("--secret", default=None, help="HMAC secret (else env SGWC_SECRET, else public default)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("encode", help="state.json standings -> a new chain-head token")
    sp.add_argument("--seq", type=int, default=None, help="override match number (else resumedFrom.seq+1)")
    sp.add_argument("--prev-hash", default=None, help="override prevHash (else from resumedFrom)")
    sp.add_argument("--prev-ref", default=None, help="override prevRef comment URL (else from resumedFrom)")
    sp.add_argument("--quiet", action="store_true", help="print ONLY the token (for piping)")
    sp.set_defaults(func=cmd_encode)

    sp = sub.add_parser("decode", help="load a token's standings into state.json (resume/fork)")
    sp.add_argument("token")
    sp.add_argument("--ref", default=None, help="URL of the comment this token came from")
    sp.add_argument("--force", action="store_true", help="load even if the signature is invalid")
    sp.set_defaults(func=cmd_decode)

    sp = sub.add_parser("verify", help="check a token's signature and print its header")
    sp.add_argument("token")
    sp.set_defaults(func=cmd_verify)

    sp = sub.add_parser("audit", help="walk a file of tokens (one per line) for chain gaps/forgery")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_audit)

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
