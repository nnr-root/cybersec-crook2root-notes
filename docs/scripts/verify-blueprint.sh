#!/usr/bin/env bash
cd "$HOME/mnt/cybersec-crook2root-notes" || exit 1
echo "=== 1. AUDIT SCRIPT RE-RUN (embed fix) ==="
python3 docs/scripts/content-audit.py 2>&1 | tail -10
echo
echo "=== 2. CODE FENCE BALANCE ==="
python3 - <<'PY'
import re
for p in ["docs/Crook2Root Master Blueprint.md","docs/templates/Room Template.md"]:
    t=open(p).read()
    # count fences at line start, longest-first so ```` isn't double-counted
    q4=len(re.findall(r'^````',t,re.M)); q3=len(re.findall(r'^```(?!`)',t,re.M))
    m=len(re.findall(r'^```mermaid',t,re.M))
    ok = (q4%2==0) and (q3%2==0)
    print(f"{'OK ' if ok else 'FAIL'} {p}: ```={q3} ````={q4} mermaid={m}")
PY
echo
echo "=== 3. YAML VALIDITY ==="
python3 - <<'PY'
import yaml
for p in []:
    try: yaml.safe_load(open(p)); print("OK  ",p)
    except Exception as e: print("FAIL",p,e)
PY
echo
echo "=== 4. ROOM TEMPLATE FRONTMATTER PARSES AS YAML ==="
python3 - <<'PY'
import yaml,re
t=open("docs/templates/Room Template.md").read()
fm=re.match(r'^---\n(.*?)\n---',t,re.S).group(1)
d=yaml.safe_load(fm)
print("top-level keys:",list(d.keys()))
r=d["room"]
print("room.id:",r["id"],"| rank:",r["rank"],"| status:",r["status"])
print("paths:",r["paths"])
print("prereqs:",r["prereqs"])
PY
echo
echo "=== 5. c2r-check COMMENTS ARE VALID + INVISIBLE ==="
python3 - <<'PY'
import re,yaml
t=open("docs/templates/Room Template.md").read()
ch=re.findall(r'<!-- c2r-check:\s*(\{.*?\})\s*-->',t)
print("c2r-check blocks found:",len(ch))
for c in ch:
    try:
        d=yaml.safe_load(c); print("  OK ",d.get("id"),"type=",d.get("type"),"pts=",d.get("points"))
    except Exception as e: print("  FAIL",c,e)
q=len(re.findall(r'> \[!question\]',t))
s=len(re.findall(r'> > \[!success\]-',t))
h=len(re.findall(r'> > \[!tip\]-',t))
print(f"[!question]={q}  collapsed [!success]-={s}  hint rungs={h}")
PY
echo
echo "=== 6. NO LATERAL WIKILINKS INTRODUCED IN TEMPLATE ==="
grep -o '\[\[[^]]*\]\]' "docs/templates/Room Template.md" | sort -u
echo
echo "=== 7. PARENT LEARNING ORDER LINE IS PLAIN TEXT ==="
grep -A1 '^## Parent Learning Order' "docs/templates/Room Template.md" | tail -1
echo
echo "=== 8. FILES IN PLACE ==="
ls -la docs/ docs/templates/ docs/scripts/ 2>/dev/null | grep -v '^total\|^d.*\s\.\.$'
echo
echo "=== 9. GIT STATUS (must be untouched / unstaged) ==="
git status --porcelain | head -20
