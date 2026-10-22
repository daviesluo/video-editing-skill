#!/bin/sh
# Copyright 2026 Zheng Luo (Davies Luo). Licensed under the Apache
# License 2.0, whose text is the LICENSE file in this package. Keep this
# notice when you copy the script.
#
# Self-test for the skill package: its layout, its hygiene and its toolkit.
#
#   sh bin/selftest.sh
#
# 1. The package: the two pointers are identical, carry SKILL.md's own
#    front matter and name SKILL.md; every stage reference SKILL.md names
#    exists and every one that exists is named; every relative link in the
#    documents resolves.
# 2. Hygiene: no e-mail address, session id, key, model identifier or
#    commit trailer anywhere in the package; the owner's name only in the
#    author credit ("Copyright 2026 Zheng Luo (Davies Luo)", on every file
#    that carries the licence line, and CITATION.cff's author entry) and
#    in the repository's own URL; and, outside those two, none of the
#    strings in a private deny-list, if one is given
#    (VIDEO_SKILL_DENYLIST=<file>, or bin/denylist.local, which is
#    gitignored), one string per line, so a fork can guard its own names
#    without publishing them.
# 3. The toolkit builds: every Python file compiles, every JSON file
#    parses, every Node script parses, and the studio type-checks when its
#    packages are installed (cd toolkit/studio && npm ci).
# 4. The pipeline's pure functions (bin/selftest_pipeline.py), on signals
#    and texts whose right answer is known by construction. Needs numpy,
#    soundfile and Pillow (toolkit/requirements.txt); the narrator's tone
#    cases need librosa too, and are reported as skipped without it.
# 5. The studio's pure modules (bin/selftest_studio.ts): caption pages and
#    word cues. Needs Node 22.18 or newer, nothing installed.
#
# A step whose tools are missing is reported as skipped, never as passed.
# The case counts are printed by the run itself, which is the only place
# worth trusting them from. Exits non-zero on any failure. Writes nothing
# outside a temporary directory it removes.

set -u
PYTHONDONTWRITEBYTECODE=1; export PYTHONDONTWRITEBYTECODE
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
T=$(mktemp -d) || exit 1
trap 'rm -rf "$T"' EXIT INT TERM
pass=0; fail=0; skip=0
ok()   { pass=$((pass+1)); echo "  ok   $1"; }
bad()  { fail=$((fail+1)); echo "  FAIL $1"; }
skp()  { skip=$((skip+1)); echo "  skip $1"; }

# The files of the package: tracked or not yet tracked, never ignored ones
# (node_modules, .venv, renders), so the run means the same before and
# after a commit. Outside a git work tree, every file but those.
cd "$ROOT"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files --cached --others --exclude-standard > "$T/files"
else
  find . -type f ! -path '*/node_modules/*' ! -path '*/.venv/*' ! -path './.git/*' ! -path '*/out/*' \
    | sed 's|^\./||' > "$T/files"
fi
grep -v -E '\.(png|jpg|jpeg|woff2|mp4|wav|mp3)$' "$T/files" | while read -r f; do [ -f "$f" ] && echo "$f"; done > "$T/text"

echo "1. the package"
FM() { awk 'NR==1 && $0=="---" {f=1; print; next} f {print} f && $0=="---" {exit}' "$1"; }
FM SKILL.md > "$T/fm"
if grep -q '^name: video-editing$' "$T/fm" && grep -q '^description: ' "$T/fm"; then ok "SKILL.md has front matter with its name and description"
else bad "SKILL.md's front matter has no name or description"; fi
A=.claude/skills/video-editing/SKILL.md; B=.agents/skills/video-editing/SKILL.md
if [ -f "$A" ] && [ -f "$B" ] && cmp -s "$A" "$B"; then ok "the two pointers exist and are identical"
else bad "the pointers are missing or differ: $A, $B"; fi
drift=0
for p in "$A" "$B"; do FM "$p" | cmp -s - "$T/fm" || drift=$((drift+1)); done
# A tool lists the skill by what the POINTER says, so a description edited
# in SKILL.md alone would leave both tools describing the old skill.
if [ "$drift" = 0 ]; then ok "each pointer carries SKILL.md's own front matter"
else bad "$drift pointer(s) describe a skill that has moved on"; fi
miss=0
for p in "$A" "$B"; do
  grep -q 'This file is a POINTER' "$p" && grep -q '\.\./\.\./\.\./SKILL\.md' "$p" || miss=$((miss+1))
done
if [ "$miss" = 0 ]; then ok "each pointer says it is one and names ../../../SKILL.md"
else bad "$miss pointer(s) do not name the file they point at"; fi
named=$(grep -o 'references/[0-9][0-9]-[a-z-]*\.md' SKILL.md | sort -u)
missing=""; for r in $named; do [ -f "$r" ] || missing="$missing $r"; done
if [ -z "$missing" ] && [ -n "$named" ]; then ok "every stage reference SKILL.md names exists ($(echo "$named" | wc -l | tr -d ' '))"
else bad "SKILL.md names references that do not exist:$missing"; fi
orphans=""; for r in references/*.md; do echo "$named" | grep -qx "$r" || orphans="$orphans $r"; done
if [ -z "$orphans" ]; then ok "every reference file is named in SKILL.md"
else bad "references not named in SKILL.md:$orphans"; fi
broken=""
for d in $(grep -E '\.md$' "$T/text" | grep -v '^toolkit/node_modules'); do
  dir=$(dirname "$d")
  for l in $(grep -o '](\([^)#: ]*\))' "$d" | sed 's/^](//; s/)$//'); do
    case "$l" in http*|mailto*|'') continue;; esac
    [ -e "$dir/$l" ] || broken="$broken $d:$l"
  done
done
if [ -z "$broken" ]; then ok "every relative link in the documents resolves"
else bad "broken links:$broken"; fi

echo "2. hygiene: nothing personal or secret in the package"
scan() { # label, extended regex (written so it cannot match itself)
  hits=$(while read -r f; do grep -n -I -E -i -- "$2" "$f" 2>/dev/null | sed "s|^|$f:|"; done < "$T/text" | head -5)
  if [ -z "$hits" ]; then ok "no $1"; else bad "$1 found: $hits"; fi
}
scan "e-mail address" '[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}'
scan "session id" 'session_[0-9a-z]{16,}'
scan "key or token" '(sk|xi)[_-][a-z0-9]{24,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key["'"'"' ]*[:=] *["'"'"']?[a-z0-9]{24,}'
scan "model identifier" 'claude-[a-z]+-[0-9]|\bo[p]us\b|\bs[o]nnet\b|\bh[a]iku\b|\bgpt-[0-9]|\bgemini-[0-9]'
scan "commit trailer" 'co-[a]uthored-by|claude-[s]ession'
# The author's credit and the repository's own URL are the only personal
# strings the package may carry; they are removed before the deny-list is
# matched, and any other trace of the owner fails. The patterns are
# split so that they cannot match this file.
CREDIT='Copyright 2026 Zh''eng Luo \(Dav''ies Luo\)'
REPO='https://github\.com/dav''iesluo/video-editing-skill'
strip() { sed -E "s#$CREDIT##g; s#$REPO##g; /^ *(family-names: Luo|given-names: Zheng|alias: Dav[i]es Luo)$/d" "$1"; }
hits=$(while read -r f; do strip "$f" | grep -n -I -i 'dav[i]esluo' | sed "s|^|$f:|"; done < "$T/text" | head -5)
if [ -z "$hits" ]; then ok "the owner appears only in the credit line and the repository URL"
else bad "an owner string outside the credit: $hits"; fi
missing=""
for f in NOTICE SKILL.md README.md LICENSE .claude/skills/video-editing/SKILL.md .agents/skills/video-editing/SKILL.md; do
  grep -q 'Zh''eng Luo (Dav''ies Luo)' "$f" || missing="$missing $f"
done
if [ -z "$missing" ]; then ok "the author credit is on every file that carries the licence line"
else bad "no author credit in:$missing"; fi
DENY=${VIDEO_SKILL_DENYLIST:-$HERE/denylist.local}
if [ -f "$DENY" ]; then
  grep -v -E '^[[:space:]]*(#|$)' "$DENY" > "$T/deny"
  n=$(wc -l < "$T/deny" | tr -d ' ')
  hits=$(while read -r f; do strip "$f" | grep -n -I -i -F -f "$T/deny" | sed "s|^|$f:|"; done < "$T/text" | head -5)
  if [ -z "$hits" ]; then ok "none of the $n strings in the private deny-list, outside the credit"
  else bad "a deny-listed string is in the package: $hits"; fi
else
  ok "no private deny-list given, the generic patterns above apply"
fi

echo "3. the toolkit builds"
PY=${PYTHON:-}
[ -n "$PY" ] || { [ -x toolkit/.venv/bin/python ] && PY=toolkit/.venv/bin/python; } || true
[ -n "$PY" ] || PY=python3
pyfiles=$(grep -E '\.py$' "$T/text")
nbad=0; for f in $pyfiles; do "$PY" -c "import ast,sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])" "$f" 2>/dev/null || { nbad=$((nbad+1)); echo "    $f"; }; done
if [ "$nbad" = 0 ]; then ok "all $(echo "$pyfiles" | wc -w | tr -d ' ') Python files compile"
else bad "$nbad Python file(s) do not compile"; fi
jsonfiles=$(grep -E '\.json$' "$T/text")
nbad=0; for f in $jsonfiles; do "$PY" -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null || { nbad=$((nbad+1)); echo "    $f"; }; done
if [ "$nbad" = 0 ]; then ok "all $(echo "$jsonfiles" | wc -w | tr -d ' ') JSON files parse"
else bad "$nbad JSON file(s) do not parse"; fi
NODE_OK=0
if command -v node >/dev/null 2>&1 && node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a>22||(a===22&&b>=18)?0:1)'; then NODE_OK=1; fi
if command -v node >/dev/null 2>&1; then
  nbad=0; for f in $(grep -E '\.mjs$' "$T/text"); do node --check "$f" 2>/dev/null || { nbad=$((nbad+1)); echo "    $f"; }; done
  if [ "$nbad" = 0 ]; then ok "every Node script parses"; else bad "$nbad Node script(s) do not parse"; fi
else skp "Node scripts not parsed: no node on this machine"; fi
if [ -x toolkit/studio/node_modules/.bin/tsc ]; then
  if (cd toolkit/studio && node_modules/.bin/tsc --noEmit -p . > "$T/tsc" 2>&1); then ok "the studio type-checks (tsc --noEmit)"
  else bad "the studio does not type-check: $(head -3 "$T/tsc" | tr '\n' ' ')"; fi
else skp "the studio was not type-checked: run npm ci in toolkit/studio first"; fi
if [ "$NODE_OK" = 1 ]; then
  if (cd toolkit/studio && node --experimental-strip-types --no-warnings scripts/caption-pages.ts 00-example > "$T/pages" 2>&1) \
     && grep -q '^== 00-example: [0-9]* pages' "$T/pages" && ! grep -q 'one word after an unfinished page' "$T/pages"; then
    ok "the example's caption pages list, none flagged ($(sed -n 's/^== 00-example: \([0-9]*\) pages/\1/p' "$T/pages") pages)"
  else bad "the example's caption pages: $(head -3 "$T/pages" | tr '\n' ' ')"; fi
else skp "caption pages not listed: Node 22.18 or newer needed"; fi

echo "4. the pipeline's pure functions"
if "$PY" -c 'import numpy, soundfile, PIL' 2>/dev/null; then
  "$PY" "$HERE/selftest_pipeline.py" > "$T/py" 2>&1
  grep -E '^  (ok|FAIL|skip) |^[a-z].*:' "$T/py" | grep -v '^PY '
  p=$(sed -n 's/^PY \([0-9]*\) \([0-9]*\) \([0-9]*\)$/\1/p' "$T/py"); f=$(sed -n 's/^PY \([0-9]*\) \([0-9]*\) \([0-9]*\)$/\2/p' "$T/py")
  s=$(sed -n 's/^PY \([0-9]*\) \([0-9]*\) \([0-9]*\)$/\3/p' "$T/py")
  if [ -z "$p" ]; then bad "the pipeline tests did not finish: $(tail -3 "$T/py" | tr '\n' ' ')"
  else pass=$((pass+p)); fail=$((fail+f)); skip=$((skip+s)); fi
else
  skp "pipeline tests: $PY lacks numpy, soundfile or Pillow (pip install -r toolkit/requirements.txt, or set PYTHON)"
fi

echo "5. the studio's pure modules"
if [ "$NODE_OK" = 1 ]; then
  node --experimental-strip-types --no-warnings "$HERE/selftest_studio.ts" > "$T/ts" 2>&1
  grep -v '^TS ' "$T/ts"
  p=$(sed -n 's/^TS \([0-9]*\) \([0-9]*\)$/\1/p' "$T/ts"); f=$(sed -n 's/^TS \([0-9]*\) \([0-9]*\)$/\2/p' "$T/ts")
  if [ -z "$p" ]; then bad "the studio tests did not finish"; else pass=$((pass+p)); fail=$((fail+f)); fi
else
  skp "studio tests: Node 22.18 or newer needed"
fi

echo
echo "$((pass+fail)) cases: $pass passed, $fail failed, $skip skipped"
[ "$fail" = 0 ]
