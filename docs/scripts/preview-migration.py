#!/usr/bin/env python3
"""Preview the migration on a single note without writing anything."""
import sys, os, importlib.util, difflib

rel = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NOTE")

spec = importlib.util.spec_from_file_location("mig", "docs/scripts/migrate-structure.py")
mig = importlib.util.module_from_spec(spec)
sys.argv = ["preview"]          # keep the module's __main__ guard from running
spec.loader.exec_module(mig)
src = open(rel, encoding="utf-8").read()
out, stats, archived = mig.migrate(src, rel)

print(f"### {rel}")
print(f"### stats: {dict(stats)}")
print(f"### archived: { {k: len(v) for k, v in archived.items()} }\n")
print("### ---------- HEADING STRUCTURE AFTER ----------")
for l in out.split("\n"):
    if l.startswith("#") or l.startswith("You should now be able to:"):
        print("   " + l)
print()
print("### ---------- FRONTMATTER AFTER ----------")
print("\n".join(out.split("\n")[:14]))
print()
print("### ---------- SUMMARY SECTION AFTER ----------")
body = out.split("## Summary", 1)
if len(body) > 1:
    print("## Summary" + body[1][:900])
else:
    print("(no Summary section produced)")
