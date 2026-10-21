"""Starts a new episode or release from the templates, so every one has the
same files from the first minute and nothing is left to memory.

    python pipeline/scaffold.py episode <NN-slug> ["<title>"]
    python pipeline/scaffold.py release <NN-reel-slug> <episode id>

`episode` writes episodes/<NN-slug>/ with episode.json, music-plan.json,
research.md, verification.md and picture-audit.md, each with its
placeholders, writes the scene file studio/src/episodes/Ep<NN>.tsx, and
prints the two lines that register it in studio/src/episodes/index.ts and
studio/src/Root.tsx. `release` writes releases/to-post/<release>/ with
release.json and post.md. Neither overwrites a file that exists.
"""

import json
import re
import sys
from pathlib import Path

from config import EPISODES, STUDIO, TEMPLATES, WAITING


def _fill(text, values):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def _write(dst, text):
    if dst.exists():
        print("kept", dst)
        return
    dst.write_text(text)
    print("wrote", dst)


def episode(ep_id, title="<the question>"):
    m = re.fullmatch(r"(\d{2})-[a-z0-9-]+", ep_id)
    if not m:
        raise SystemExit("an episode id is two digits, a hyphen and a slug: 07-shipping-containers")
    values = {"ID": ep_id, "TITLE": title, "COMPOSITION": f"Ep{m.group(1)}"}
    out = EPISODES / ep_id
    out.mkdir(parents=True, exist_ok=True)
    for src in sorted((TEMPLATES / "episode").iterdir()):
        text = _fill(src.read_text(), values)
        if src.name == "episode.json":
            spec = json.loads(text)
            spec["number"] = int(m.group(1))
            text = json.dumps(spec, indent=2, ensure_ascii=False) + "\n"
        _write(out / src.name, text)
    comp = values["COMPOSITION"]
    n = int(m.group(1))
    scene = _fill((TEMPLATES / "scene" / "EpNN.tsx").read_text(),
                  dict(values, COMPONENT=comp, NUMBER=str(n), NEXT=str(n + 1)))
    _write(SCENES / f"{comp}.tsx", scene)
    print(f"""
Register it:
  studio/src/episodes/index.ts:  import {{ {comp} }} from "./{comp}";   and add {comp} to EPISODES
  studio/src/Root.tsx:           import {{ {comp} }} from "./episodes/{comp}";   and
                                 <Composition id="{comp}" component={{{comp}}} {{...EP}}
                                   defaultProps={{{{ id: "{ep_id}", lead: 0.3, tail: 1.4, qa: false }}}} calculateMetadata={{episodeMetadata}} />
and its cover in COVERS there. The composition has a length once build.py episodes/{ep_id} voice has run.""")
    return out


SCENES = STUDIO / "src" / "episodes"


def release(name, ep_id):
    m = re.fullmatch(r"(\d{2})-reel-[a-z0-9-]+", name)
    if not m:
        raise SystemExit("a release name is two digits, 'reel' and a slug: 09-reel-shipping-containers")
    nn = re.match(r"\d{2}", ep_id)
    values = {"RELEASE": name, "EPISODE": ep_id, "NN": nn.group(0) if nn else "NN"}
    out = WAITING / name
    out.mkdir(parents=True, exist_ok=True)
    for src in sorted((TEMPLATES / "release").iterdir()):
        _write(out / src.name, _fill(src.read_text(), values))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("episode", "release"):
        raise SystemExit(__doc__)
    {"episode": episode, "release": release}[sys.argv[1]](*sys.argv[2:])
