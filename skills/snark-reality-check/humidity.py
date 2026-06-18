import os, re, sys, hashlib

root = sys.argv[1]
listfile = sys.argv[2]
N = 6  # duplicate blocks are >= 6 consecutive matching lines

with open(listfile, encoding='utf-8-sig') as f:
    rels = [l.strip() for l in f if l.strip()]

def normalize(line):
    s = line.strip()
    if not s:
        return None
    # drop comment-only and xml-doc lines (comments aren't code)
    if s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
        return None
    # drop brace-only / trivial structural lines
    if s in ('{', '}', '});', '};', ')', '({', '(', ');'):
        return None
    # collapse internal whitespace; lowercase (ignoreIdentifierCase default true)
    s = re.sub(r'\s+', ' ', s).lower()
    return s

# Build per-file normalized lines (with original index for marking)
files = []
total_sig = 0
for rel in rels:
    p = os.path.join(root, rel.replace('/', os.sep))
    if not os.path.isfile(p):
        continue
    with open(p, encoding='utf-8-sig', errors='replace') as fh:
        raw = fh.readlines()
    norm = []
    for ln in raw:
        n = normalize(ln)
        norm.append(n)
    sig_idx = [i for i, n in enumerate(norm) if n is not None]
    total_sig += len(sig_idx)
    files.append((rel, norm, sig_idx))

# Collect all N-length windows over significant lines (per file), hash them.
# A window is the concatenation of N consecutive *significant* normalized lines.
window_map = {}   # hash -> list of (file_idx, [orig_indices])
for fi, (rel, norm, sig_idx) in enumerate(files):
    for w in range(0, len(sig_idx) - N + 1):
        idxs = sig_idx[w:w+N]
        text = '\n'.join(norm[i] for i in idxs)
        h = hashlib.md5(text.encode()).hexdigest()
        window_map.setdefault(h, []).append((fi, idxs))

# A window is duplicated if its hash appears >= 2 times (anywhere, incl. same file elsewhere).
wet = [set() for _ in files]
for h, occ in window_map.items():
    if len(occ) >= 2:
        for fi, idxs in occ:
            for i in idxs:
                wet[fi].add(i)

wet_total = sum(len(s) for s in wet)
humidity = 100.0 * wet_total / total_sig if total_sig else 0.0
print(f"files analyzed      : {len(files)}")
print(f"significant LOC     : {total_sig}")
print(f"duplicated (wet) LOC: {wet_total}")
print(f"HUMIDITY            : {humidity:.1f}%")

# Top offenders
pair = sorted(((len(wet[fi]), files[fi][0]) for fi in range(len(files))), reverse=True)
print("---- wettest files ----")
for c, rel in pair[:8]:
    if c:
        print(f"{c:4}  {rel.split('/')[-1]}")
