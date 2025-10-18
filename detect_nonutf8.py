import subprocess
import sys

try:
    files = subprocess.check_output(["git", "ls-files"]).decode().splitlines()
except Exception as e:
    print(f"ERROR: cannot run git ls-files: {e}", file=sys.stderr)
    sys.exit(2)

bad = []
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fh:
            fh.read()
    except Exception as e:
        bad.append((f, repr(e)))

if not bad:
    print("All git-tracked files are UTF-8 decodable.")
else:
    for f, e in bad:
        print(f"BAD: {f} -> {e}")
    print(f"Total bad: {len(bad)}")
