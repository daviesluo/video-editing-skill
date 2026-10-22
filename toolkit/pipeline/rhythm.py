"""The series' rhythm, measured, and the reference parts it is held to.

The first parts the owner approves are the standard for how fast the
narrator speaks and how busy the picture is; every later part is measured
the same way and kept inside their range. Two measures:

- the voice (`voice.pace_measure`, on the timeline): syllables a second
  within speech and over the whole narration, and the shortest pause at a
  sentence end and at a section break;
- the picture (`picture`, on the delivered video): how much of the time the
  picture band (between the headline and the captions) is moving, how many
  separate movements there are per 10 seconds, and how long it holds still
  between them.

The reference parts are listed in brand.json (`rhythm.reference`), each as
an episode id, whose video is then episodes/<id>/out/final.mp4, or as
{"episode": "<id>", "video": "<path from the project root>"} for a part
whose delivered file lives elsewhere (a release folder). `standard`
measures them and writes the limits (`rhythm.limits`) and the typical
pauses (`rhythm.pauses`, which `voice.pace` lengthens short pauses to) back
into brand.json; QA and `build.py render` read them from there.

    python pipeline/rhythm.py standard                  # re-measure the reference parts
    python pipeline/rhythm.py report episodes/<id> [video.mp4]

A part that felt rushed beside its four reference parts measured 5.22
syllables a second in speech against 4.86 to 5.19, its picture moving 29
percent of the time against at most 18, 2.81 movements per 10 s against at
most 1.89, and a median hold of 0.8 s against at least 2.27: every measure
outside, where words a second had not shown it.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402
from config import EPISODES, ROOT, brand, public_dir, readings  # noqa: E402

# The picture band, as fractions of the frame's height: below the headline
# and above the captions, where the picture itself is (brand.json
# `rhythm.band` overrides it).
BAND = (0.33, 0.72)
# A frame-to-frame change of the band's mean grey level (0 to 255, at
# 108x192, smoothed over five frames) above this counts as movement: a
# camera move, a shape travelling, a fill or a line drawing.
MOVING = 0.6
# Movements and holds shorter than this are flicker, not rhythm.
SHORTEST = 0.2
SIZE = (108, 192)
USAGE = """usage:
  python pipeline/rhythm.py standard                    measure the reference parts, write the limits
  python pipeline/rhythm.py report episodes/<id> [video]   one part against them"""


def frames(video):
    """The delivered video's frames, grey, at 108x192, as one array."""
    w, h = SIZE
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def motion(f, fps, band=BAND):
    """Movement in the picture band of grey frames `f` (frames x height x
    width): the share of the time it moves, separate movements per 10 s,
    and the median movement and hold between movements, in seconds."""
    h = f.shape[1]
    f = f[:, int(h * band[0]):int(h * band[1]), :].astype(np.float32)
    d = np.convolve(np.abs(np.diff(f, axis=0)).mean(axis=(1, 2)), np.ones(5) / 5, mode="same")
    moving = d > MOVING
    # A change shorter than SHORTEST (a dot appearing, the last frame of a
    # label's fade) is not a movement anyone sees: it counts as still, so it
    # neither adds a movement nor splits the hold it falls in. Counted apart,
    # one-frame blips cut a part's long holds in two and its median hold
    # read 1.55 s where the eye saw 1.7 s.
    start = 0
    for i in range(1, len(moving) + 1):
        if i == len(moving) or moving[i] != moving[start]:
            if moving[start] and (i - start) / fps < SHORTEST:
                moving[start:i] = False
            start = i
    runs, holds, start = [], [], 0
    for i in range(1, len(moving) + 1):
        if i == len(moving) or moving[i] != moving[start]:
            (runs if moving[start] else holds).append((i - start) / fps)
            start = i
    holds = [x for x in holds if x >= SHORTEST]
    seconds = len(d) / fps
    return {"moving_share": round(sum(runs) / seconds, 3), "moves_per_10s": round(len(runs) / seconds * 10, 2),
            "median_move_s": round(float(np.median(runs)), 2) if runs else 0.0,
            "median_hold_s": round(float(np.median(holds)), 2) if holds else round(seconds, 2)}


def picture(video):
    """Movement in the picture band of a delivered video."""
    b = brand()
    return motion(frames(video), b["frame"]["fps"], tuple(b.get("rhythm", {}).get("band", BAND)))


def measure(episode, timeline, video):
    """The voice and the picture of one part, measured the same way as the
    reference parts."""
    return {"voice": voice.pace_measure(timeline["words"], readings(episode)), "picture": picture(video)}


def limits_from(rows):
    """The range of the reference parts' measures: the voice's rates
    between their slowest and fastest, its pauses no shorter than their
    shortest, the picture no busier than their busiest; and their typical
    pauses (the median of each part's median)."""
    def col(group, key):
        return [r[group][key] for r in rows.values() if r[group].get(key) is not None]

    def span(key):
        v = col("voice", key)
        return [min(v), max(v)]

    def median(key):
        v = col("voice", key)
        return round(float(np.median(v)), 2) if v else None

    lim = {"speech_syllables_per_s": span("speech_syllables_per_s"), "syllables_per_s": span("syllables_per_s"),
           "sentence_pause_min": min(col("voice", "sentence_pause")),
           "moving_share_max": max(col("picture", "moving_share")), "moves_per_10s_max": max(col("picture", "moves_per_10s")),
           "median_hold_s_min": min(col("picture", "median_hold_s"))}
    if col("voice", "section_pause"):
        lim["section_pause_min"] = min(col("voice", "section_pause"))
    pauses = {k: median(f"{k}_pause_median") for k in ("sentence", "section") if median(f"{k}_pause_median") is not None}
    return lim, pauses


def _compact(v):
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{json.dumps(k)}: {_compact(x)}" for k, x in v.items()) + " }" if v else "{}"
    if isinstance(v, list):
        return "[" + ", ".join(_compact(x) for x in v) + "]"
    return json.dumps(v, ensure_ascii=False)


def dump_brand(b):
    """brand.json as the project writes it: one line per entry, a long
    object over one line per key, so `standard` changes only what it
    measured."""
    rows = []
    for k, v in b.items():
        one = _compact(v)
        if isinstance(v, dict) and len(one) > 110:
            inner = ",\n".join(f"    {json.dumps(k2)}: {_compact(v2)}" for k2, v2 in v.items())
            rows.append(f"  {json.dumps(k)}: {{\n{inner}\n  }}")
        else:
            rows.append(f"  {json.dumps(k)}: {one}")
    return "{\n" + ",\n".join(rows) + "\n}\n"


def _reference(entry):
    if isinstance(entry, str):
        return entry, None
    return entry["episode"], entry.get("video")


def standard(path=None):
    """Measures every reference part from its timeline and delivered video
    and writes the limits and typical pauses back into brand.json."""
    path = Path(path or ROOT / "brand.json")
    b = brand(path)
    ref = b.get("rhythm", {}).get("reference", [])
    if not ref:
        raise SystemExit("no reference parts: list the series' first approved parts in brand.json rhythm.reference")
    rows = {}
    for entry in ref:
        ep_id, video = _reference(entry)
        episode = json.loads((EPISODES / ep_id / "episode.json").read_text())
        tl = json.loads((public_dir(episode) / "timeline.json").read_text())
        video = ROOT / video if video else EPISODES / ep_id / "out" / "final.mp4"
        if not video.exists():
            raise SystemExit(f"{ep_id}: no delivered video at {video}")
        rows[ep_id] = measure(episode, tl, video)
    lim, pauses = limits_from(rows)
    b["rhythm"] = dict(b.get("rhythm", {}), reference=ref, limits=lim, pauses=pauses)
    path.write_text(dump_brand(b))
    return rows, lim, pauses


def picture_faults(p, lim):
    out = []
    if "moving_share_max" in lim and p["moving_share"] > lim["moving_share_max"]:
        out.append(f"picture moving {p['moving_share']:.0%} of the time, over the reference parts' {lim['moving_share_max']:.0%}")
    if "moves_per_10s_max" in lim and p["moves_per_10s"] > lim["moves_per_10s_max"]:
        out.append(f"{p['moves_per_10s']} movements per 10 s, over the reference parts' {lim['moves_per_10s_max']}")
    if "median_hold_s_min" in lim and p["median_hold_s"] < lim["median_hold_s_min"]:
        out.append(f"a median hold of {p['median_hold_s']} s between movements, under the reference parts' {lim['median_hold_s_min']} s")
    return out


def faults(m, limits=None):
    """Where a part's voice or picture leaves the reference parts' range, as
    readable lines; empty when both keep it."""
    lim = limits or brand()["rhythm"]["limits"]
    return voice.pace_faults(m["voice"], lim) + picture_faults(m["picture"], lim)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["standard"]:
        rows, lim, pauses = standard()
        for ep_id, m in rows.items():
            v, p = m["voice"], m["picture"]
            print(f"  {ep_id:28} {v['speech_syllables_per_s']:5.2f} syl/s in speech  {v['syllables_per_s']:5.2f} overall  "
                  f"sentence pause {v['sentence_pause']} s  picture moving {p['moving_share']:.0%}  "
                  f"{p['moves_per_10s']} moves/10 s  median hold {p['median_hold_s']} s")
        print(json.dumps({"limits": lim, "pauses": pauses}, indent=1))
    elif len(a) >= 2 and a[0] == "report":
        ep_dir = Path(a[1])
        episode = json.loads((ep_dir / "episode.json").read_text())
        tl = json.loads((public_dir(episode) / "timeline.json").read_text())
        m = measure(episode, tl, Path(a[2]) if len(a) > 2 else ep_dir / "out" / "final.mp4")
        print(json.dumps(m, indent=1))
        print("\n".join(faults(m)) or "within the reference parts")
    else:
        raise SystemExit(USAGE)
