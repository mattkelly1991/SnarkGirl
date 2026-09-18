#!/usr/bin/env python3
"""
settings.py — SnarkGirl's persistent settings store.

One tiny stdlib CLI so SnarkGirl can REMEMBER things you tell her across
sessions, repos, and machines-that-share-a-home-dir. Every skill that has a
tunable reads it from here instead of asking again.

Storage:
    {SNARKGIRL_HOME or ~/.snarkgirl}/settings.json

The file is plain JSON so a human can read or hand-edit it. Writes are atomic
(tmp + replace) so a crash mid-write never leaves a half file.

Every setting is declared in SCHEMA below with its allowed values and default.
Unknown keys and out-of-range values are rejected — that's the whole point of
a registry: the persona can't "remember" garbage.

Examples:
    python settings.py get divergence
    python settings.py set divergence high
    python settings.py reset divergence
    python settings.py list
    python settings.py list --json
    python settings.py describe divergence
    python settings.py path
"""

import argparse
import json
import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# Registry — add new settings here. A setting is:
#   type:    "enum" | "bool" | "int" | "string"
#   values:  allowed values (enum only)
#   default: value used when nothing is stored
#   help:    one-line human description shown by `describe` / `list`
# ---------------------------------------------------------------------------
SCHEMA = {
    "divergence": {
        "type": "enum",
        "values": ["off", "low", "medium", "high"],
        "default": "off",
        "help": (
            "How hard SnarkGirl diverges before converging on open-ended problems "
            "(design, naming, architecture, fuzzy bugs). off = never auto-run; "
            "low = 3 frames x 4 ideas, explicit asks only; medium = 5 x 6, "
            "auto-runs on clearly open-ended high-stakes questions; "
            "high = 7 x 8, auto-runs on anything with more than one good answer."
        ),
    },
}

TRUE_WORDS = {"1", "true", "yes", "on", "y"}
FALSE_WORDS = {"0", "false", "no", "off", "n"}


def settings_dir():
    return os.environ.get("SNARKGIRL_HOME") or os.path.join(os.path.expanduser("~"), ".snarkgirl")


def settings_path():
    return os.path.join(settings_dir(), "settings.json")


def load():
    path = settings_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        die(f"settings file is unreadable ({e}). Fix or delete: {path}")
    if not isinstance(data, dict):
        die(f"settings file is not a JSON object: {path}")
    return data


def save(data):
    d = settings_dir()
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="settings.", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, settings_path())
    except OSError:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def require_key(key):
    if key not in SCHEMA:
        known = ", ".join(sorted(SCHEMA))
        die(f"unknown setting '{key}'. Known settings: {known}")
    return SCHEMA[key]


def coerce(key, raw):
    """Validate + normalize a raw CLI string into the stored value."""
    spec = require_key(key)
    t = spec["type"]
    if t == "enum":
        v = str(raw).strip().lower()
        if v not in spec["values"]:
            die(f"'{raw}' is not valid for {key}. Allowed: {', '.join(spec['values'])}")
        return v
    if t == "bool":
        v = str(raw).strip().lower()
        if v in TRUE_WORDS:
            return True
        if v in FALSE_WORDS:
            return False
        die(f"'{raw}' is not a boolean for {key}. Use on/off, true/false, yes/no")
    if t == "int":
        try:
            v = int(str(raw).strip())
        except ValueError:
            die(f"'{raw}' is not an integer for {key}")
        lo, hi = spec.get("min"), spec.get("max")
        if lo is not None and v < lo:
            die(f"{key} must be >= {lo}")
        if hi is not None and v > hi:
            die(f"{key} must be <= {hi}")
        return v
    return str(raw)


def effective(data, key):
    """Stored value if present and still valid, else the schema default."""
    spec = require_key(key)
    if key in data:
        v = data[key]
        if spec["type"] != "enum" or v in spec["values"]:
            return v, True
    return spec["default"], False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_get(args):
    data = load()
    value, _ = effective(data, args.key)
    print(value if not isinstance(value, bool) else str(value).lower())


def cmd_set(args):
    data = load()
    value = coerce(args.key, args.value)
    previous, _ = effective(data, args.key)
    data[args.key] = value
    save(data)
    print(f"{args.key}: {previous} -> {value}")


def cmd_reset(args):
    data = load()
    if args.key == "all":
        data = {}
        save(data)
        print("all settings reset to defaults")
        return
    spec = require_key(args.key)
    data.pop(args.key, None)
    save(data)
    print(f"{args.key}: reset to default ({spec['default']})")


def cmd_list(args):
    data = load()
    rows = []
    for key in sorted(SCHEMA):
        value, is_set = effective(data, key)
        rows.append({"key": key, "value": value, "default": SCHEMA[key]["default"], "set": is_set})
    if args.json:
        print(json.dumps({r["key"]: r["value"] for r in rows}, indent=2))
        return
    width = max(len(r["key"]) for r in rows)
    for r in rows:
        marker = "" if r["set"] else "  (default)"
        print(f"{r['key']:<{width}}  {r['value']}{marker}")


def cmd_describe(args):
    spec = require_key(args.key)
    data = load()
    value, is_set = effective(data, args.key)
    print(f"{args.key}")
    print(f"  type:    {spec['type']}")
    if spec["type"] == "enum":
        print(f"  values:  {', '.join(spec['values'])}")
    print(f"  default: {spec['default']}")
    print(f"  current: {value}{'' if is_set else ' (default)'}")
    print(f"  help:    {spec['help']}")


def cmd_path(_args):
    print(settings_path())


def build_parser():
    p = argparse.ArgumentParser(prog="settings.py", description="SnarkGirl persistent settings")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("get", help="print the effective value of a setting")
    g.add_argument("key")
    g.set_defaults(func=cmd_get)

    s = sub.add_parser("set", help="store a value for a setting")
    s.add_argument("key")
    s.add_argument("value")
    s.set_defaults(func=cmd_set)

    r = sub.add_parser("reset", help="remove a stored value (or 'all')")
    r.add_argument("key")
    r.set_defaults(func=cmd_reset)

    l = sub.add_parser("list", help="show every known setting and its effective value")
    l.add_argument("--json", action="store_true", help="emit a JSON object instead of a table")
    l.set_defaults(func=cmd_list)

    d = sub.add_parser("describe", help="show a setting's type, allowed values, default, and help")
    d.add_argument("key")
    d.set_defaults(func=cmd_describe)

    pa = sub.add_parser("path", help="print the settings file location")
    pa.set_defaults(func=cmd_path)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
