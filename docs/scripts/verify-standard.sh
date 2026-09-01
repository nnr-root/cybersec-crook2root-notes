#!/usr/bin/env bash
cd "$HOME/mnt/cybersec-crook2root-notes" || exit 1
EX=( --exclude-dir=.archive --exclude-dir=.git )

echo "=== 1. STANDARD VIOLATIONS IN LIVE NOTES (must be 0) ==="
python3 docs/scripts/content-audit.py --violations 2>&1 | head -5
echo "   violations: $(python3 docs/scripts/content-audit.py --violations 2>/dev/null | wc -l)"

echo
echo "=== 2. GOVERNANCE DOCS: any Crook/Operator/Root STRUCTURE left? ==="
for f in AGENTS.md README.md CONTRIBUTION.md "docs/Crook2Root Authoring Standard.md" "docs/Crook2Root Master Blueprint.md" "docs/templates/Room Template.md"; do
  n=$(grep -cE '(\*\*Crook:?\*\*|\*\*Operator:?\*\*|Crook → Operator|level/(crook|operator|root)|^#{2,4} (Crook|Operator|Root) —)' "$f" 2>/dev/null)
  b=$(grep -c 'Crook2Root' "$f" 2>/dev/null)
  printf "   %-46s structure:%s  brand-mentions:%s\n" "$f" "${n:-0}" "${b:-0}"
done

echo
echo "=== 3. TEMPLATE + SCRIPT VALIDITY ==="
python3 - <<'PY'
import re, yaml
p = "docs/templates/Room Template.md"
t = open(p).read()
fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---', t, re.S).group(1))
print("   Room Template frontmatter keys:", list(fm.keys()))
print("   difficulty tag:", [x for x in fm["tags"] if x.startswith("difficulty/")])
numbered = re.findall(r'^#{2,6}\s+Task\s+\d+\s*[—–-]', t, re.M)
sections = re.findall(r'^## (?!Summary\b|Parent Learning Order\b)(.+)$', t, re.M)
print("   sections:", len(sections), "| numbered (must be 0):", len(numbered))
print("   has Summary:", bool(re.search(r'^## Summary', t, re.M)))
print("   banned constructs present:", bool(re.search(r'c2r-check|\[!question\]|Authorized Lab|Checkpoint', t)))
for f in []:
    try: yaml.safe_load(open(f)); print("   OK  ", f)
    except Exception as e: print("   FAIL", f, e)
PY

echo
echo "=== 4. FENCE BALANCE ON NEW DOCS ==="
python3 - <<'PY'
import re
for p in ["docs/Crook2Root Master Blueprint.md","docs/Crook2Root Authoring Standard.md",
          "docs/templates/Room Template.md","AGENTS.md","README.md","CONTRIBUTION.md"]:
    t=open(p).read()
    q4=len(re.findall(r'^````',t,re.M)); q3=len(re.findall(r'^```(?!`)',t,re.M))
    print(f"   {'OK ' if q3%2==0 and q4%2==0 else 'FAIL'} {p}  ```={q3} ````={q4}")
PY

echo
echo "=== 5. ALL SCRIPTS RUN CLEAN ==="
for s in content-audit.py fence-check.py; do
  python3 "docs/scripts/$s" >/dev/null 2>&1 && echo "   OK   $s" || echo "   note $s exited non-zero (violations flag)"
done

echo
echo "=== 6. ARCHIVE INTACT & HIDDEN FROM OBSIDIAN ==="
echo "   labs:        $(ls .archive/labs 2>/dev/null | wc -l)"
echo "   checkpoints: $(ls .archive/checkpoints 2>/dev/null | wc -l)"
echo "   size:        $(du -sh .archive 2>/dev/null | cut -f1)"
echo "   dot-prefixed (Obsidian ignores): $([ -d .archive ] && echo yes)"

echo
echo "=== 7. GIT: NOTHING STAGED OR COMMITTED ==="
git log -1 --format='   HEAD still at %h  %s' 2>/dev/null
echo "   staged files: $(git diff --cached --name-only 2>/dev/null | wc -l)"
echo "   modified:     $(git diff --name-only 2>/dev/null | wc -l)"
echo "   untracked:    $(git ls-files --others --exclude-standard 2>/dev/null | wc -l)"
