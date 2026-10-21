"""Moves word cues ("seg@k") after a segment's wording changes, so every cue
keeps pointing at the same word. Without it a cue silently drifts: one
added symbol ("km²" becoming one word) shifted every later word by one, and
a label meant for "Montana" pointed into the next sentence and never
showed.

    python pipeline/recue.py episodes/<id> <scene.tsx> <seg> "<old text>" [--apply]

The new text is read from episode.json, which must already hold it. Words
are matched by their letters; a cue on a word that no longer exists moves
to the first word that replaced it and is flagged, so it can be checked by
eye. Without --apply it only prints the plan. The scene file and the
episode's sound-effect cues are both rewritten. Cues are found in double
or single quotes ("seg@3", 'seg@3'); a cue built at run time (a template
string) is not found, so write cues as literals.
"""

import difflib
import json
import re
import sys
from pathlib import Path

TAG = re.compile(r"\[[^\]]*\]")


def norm(w):
    return re.sub(r"[^\w²³]", "", w.lower())


def mapping(old, new):
    """{old word index: new word index}, and the old indices whose word
    changed."""
    a, b = [norm(w) for w in old], [norm(w) for w in new]
    out, moved = {}, []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        for k in range(i1, i2):
            if tag == "equal":
                out[k] = j1 + (k - i1)
            else:
                out[k] = min(j1, len(new) - 1)
                moved.append(k)
    return out, moved


def cue_pattern(seg):
    return re.compile(r"""(["'])""" + re.escape(seg) + r"@(\d+)\1")


def rewrite(text, seg, m):
    """Every "seg@k" (or 'seg@k') in `text` with k mapped."""
    return cue_pattern(seg).sub(lambda x: f"{x.group(1)}{seg}@{m.get(int(x.group(2)), int(x.group(2)))}{x.group(1)}", text)


def main():
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    ep_dir, tsx, seg, old_text = sys.argv[1:5]
    apply = "--apply" in sys.argv
    ep_path = Path(ep_dir) / "episode.json"
    ep = json.loads(ep_path.read_text())
    new_text = next(s["text"] for s in ep["segments"] if s["id"] == seg)
    # Audio tags ([curious]) are not caption words, so they hold no index.
    old, new = TAG.sub(" ", old_text).split(), TAG.sub(" ", new_text).split()
    m, moved = mapping(old, new)
    pat = cue_pattern(seg)
    src = Path(tsx).read_text()
    used = sorted({int(k) for _, k in pat.findall(src)} | {int(k) for _, k in pat.findall(ep_path.read_text())})
    for k in used:
        flag = "  <- word changed, check" if k in moved else ""
        j = m.get(k, k)
        print(f"{seg}@{k} {old[k] if k < len(old) else '?'!r} -> {seg}@{j} {new[j] if j < len(new) else '?'!r}{flag}")
    if apply:
        Path(tsx).write_text(rewrite(src, seg, m))
        ep_path.write_text(rewrite(ep_path.read_text(), seg, m))
        print("applied")


if __name__ == "__main__":
    main()
