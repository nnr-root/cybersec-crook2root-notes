#!/usr/bin/env bash
cd "$HOME/mnt/cybersec-crook2root-notes" || exit 1
echo "=== 1. RESIDUAL Crook/Operator/Root STRUCTURE IN HEADINGS ==="
n=$(grep -rhE '^#{1,4} .*(Crook|Operator —|Root —|Checkpoint)' --include=*.md . \
      | grep -v '^./docs/' | grep -vi 'root cause\|root-cause\|to-Daemon-to-Root\|Splitting Root\|Authenticated Root\|Two Root Causes\|Common Root Cause' | wc -l)
echo "   heading lines still carrying the vocabulary: $n"
grep -rhE '^#{1,4} .*(Crook|Operator —|Root —|Checkpoint)' --include=*.md . 2>/dev/null \
  | grep -vi 'root cause\|root-cause\|Daemon-to-Root\|Splitting Root\|Authenticated Root' | sort | uniq -c | sort -rn | head

echo
echo "=== 2. RESIDUAL LAB SECTIONS ==="
grep -rlE '^#{2,4} .*(Authorized Lab|Hands-On Lab|Runnable Lab)' --include=*.md . | wc -l

echo
echo "=== 3. LEVEL TAGS REMAINING (should be 0) ==="
grep -rc 'level/crook\|level/operator\|level/root' --include=*.md . 2>/dev/null | grep -v ':0$' | wc -l
echo "--- difficulty tag distribution ---"
grep -rhoE 'difficulty/(info|easy|medium|hard)' --include=*.md . | sort | uniq -c | sort -rn

echo
echo "=== 4. SUMMARY SECTIONS PRESENT ==="
grep -rl '^## Summary' --include=*.md . | wc -l

echo
echo "=== 5. NO NUMBERED TASK HEADINGS (numbering lives in the private site repo) ==="
python3 - <<'PY'
import os,re
SKIP={".git",".obsidian","assets","graphify-out",".claude","docs",".archive"}
bad=[]
tot=0
for dp,dn,fn in os.walk("."):
    dn[:]=[d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".md"): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,".")
        if os.sep not in rel and rel!="Cyber Security.md": continue
        src=open(p,encoding="utf-8").read()
        tot+=1
        n=len(re.findall(r'^#{2,6}\s+Task\s+\d+\s*[—–-]',src,re.M))
        refs=len(re.findall(r'\bTask \d+\b',src))
        if n or refs: bad.append((rel,n,refs))
print(f"   notes scanned: {tot}")
print(f"   notes with a numbered heading or dangling 'Task N' ref: {len(bad)}")
for r,n,q in bad[:8]: print(f"      {r}  headings={n} refs={q}")
PY

echo
echo "=== 6. FRONTMATTER STILL PARSES ==="
python3 - <<'PY'
import os,re,yaml
SKIP={".git",".obsidian","assets","graphify-out",".claude","docs",".archive"}
bad=[];n=0
for dp,dn,fn in os.walk("."):
    dn[:]=[d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".md"): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,".")
        if os.sep not in rel and rel!="Cyber Security.md": continue
        t=open(p,encoding="utf-8").read()
        m=re.match(r'^---\n(.*?)\n---',t,re.S)
        if not m: continue
        n+=1
        try: yaml.safe_load(m.group(1))
        except Exception as e: bad.append((rel,str(e)[:60]))
print(f"   frontmatter blocks parsed: {n}   failures: {len(bad)}")
for r,e in bad[:8]: print("     ",r,e)
PY

echo
echo "=== 7. CODE FENCES STILL BALANCED ==="
python3 docs/scripts/fence-check.py 2>&1 | tail -3

echo
echo "=== 8. PARENT LINK FOOTERS PRESERVED ==="
grep -rl '🔼 Up:' --include=*.md . | wc -l

echo
echo "=== 9. ARCHIVE CONTENTS ==="
ls .archive/ 2>/dev/null
echo "labs archived:        $(ls .archive/labs 2>/dev/null | wc -l)"
echo "checkpoints archived: $(ls .archive/checkpoints 2>/dev/null | wc -l)"
du -sh .archive 2>/dev/null

echo
echo "=== 10. GIT: NOTHING STAGED OR COMMITTED ==="
git log -1 --format='HEAD still at: %h %s' 2>/dev/null
git diff --cached --stat 2>/dev/null | tail -1
echo "modified (unstaged) note count: $(git diff --name-only -- '*.md' 2>/dev/null | wc -l)"
