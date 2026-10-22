"""The narrator's tone, measured, and the reference parts it is held to.

The first parts the owner approves are the standard for how the narrator
sounds as well as for how fast they speak. A take can keep the reference
parts' pace and still be heard at once as a different reading: one slowed
by a direction tag at the start of every section was, to the owner, "not
the same tone and style as the earlier parts, above all the first
sentence, which sounds listless". Measured, its pitch sat low, its words'
levels spread wide and its opening line sat under the rest of the take,
while takes without the tag measured inside the reference parts on every
count. So the tone is measured the same way on every take, from the take
(voice.wav) and its word timings:

- pitch: the median (Hz), its spread over the take (10th to 90th
  percentile, in semitones) and its movement within sentences (the mean,
  over sentences, of each sentence's standard deviation, in semitones):
  how lively the intonation is;
- loudness: how much the words vary in level (the standard deviation of
  each word's level, dB);
- brightness: the median spectral centroid of voiced speech (Hz): a
  breathy, low-energy read is darker;
- the hook: the first sentence's pitch movement and its level against the
  whole take's (dB), where a listless opening shows first.

The reference parts are brand.json's `rhythm.reference`, the same parts
that set the pace and the picture's rhythm. `standard` measures their takes
and writes the range (`voice_tone.limits`) back into brand.json; QA reads
it. `voice_tone.tolerance` is how far outside that range a measure may sit
before it counts, and `voice_tone.pitch_hz` the pitch tracker's range,
which must hold the narrator's voice with room either side.

    python pipeline/voicestyle.py standard                     # measure the reference parts
    python pipeline/voicestyle.py report episodes/<id> [voice.wav]

A take other than the committed one (a seed being tried) is reported with
its own timeline.json beside it. Needs librosa (pyin pitch tracking).
"""

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from config import EPISODES, ROOT, brand, public_dir  # noqa: E402
from voice import _pause_kind  # noqa: E402

SR = 16000
HOP = 160  # 10 ms
PITCH_HZ = (60, 320)
# How far outside the reference parts' range a measure may sit before it
# counts (brand.json `voice_tone.tolerance` overrides each): four parts are
# a small sample, and the pitch tracker and the word timings each move a
# reading a little. Set so that the tagged take the owner heard as
# listless fails (its pitch median 2.3 Hz under the reference parts'
# lowest, its words' levels spread 0.3 dB wider than their widest, its
# hook 0.4 dB under the take where theirs sat 0 to 1 dB over it) and takes
# without the tag pass.
TOLERANCE = {"pitch_median_hz": 1.5, "pitch_spread_st": 0.5, "pitch_movement_st": 0.25, "loudness_sd_db": 0.15,
             "brightness_hz": 60.0, "hook_movement_st": 0.5, "hook_level_db": 0.2}
LABELS = {"pitch_median_hz": ("pitch median", "Hz"), "pitch_spread_st": ("pitch spread", "semitones"),
          "pitch_movement_st": ("pitch movement within sentences", "semitones"),
          "loudness_sd_db": ("spread of the words' levels", "dB"), "brightness_hz": ("brightness", "Hz"),
          "hook_movement_st": ("the hook's pitch movement", "semitones"),
          "hook_level_db": ("the hook's level against the take", "dB")}
USAGE = """usage:
  python pipeline/voicestyle.py standard                          measure the reference parts' tone, write the limits
  python pipeline/voicestyle.py report episodes/<id> [voice.wav]   one take against them"""


def sentences(words):
    """The words grouped into sentences: a sentence ends on . ? or ! (past
    any closing quote) or at a section break."""
    out, cur = [], []
    for w, n in zip(words, words[1:] + [None]):
        cur.append(w)
        if n is None or _pause_kind(w, n) in ("sentence", "section"):
            out.append(cur)
            cur = []
    return out


def _db(x):
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))


def measure(wav, words, pitch_hz=None):
    """The tone of one take, from its audio and word timings (seconds)."""
    import librosa

    lo, hi = pitch_hz or brand().get("voice_tone", {}).get("pitch_hz", PITCH_HZ)
    y, sr = sf.read(str(wav), dtype="float32")
    if y.ndim == 2:
        y = y.mean(axis=1)
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    f0, voiced, _ = librosa.pyin(y, fmin=lo, fmax=hi, sr=SR, frame_length=1024, hop_length=HOP)
    t = np.arange(len(f0)) * HOP / SR
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=HOP)[0][: len(f0)]
    cent = librosa.feature.spectral_centroid(y=y, sr=SR, n_fft=1024, hop_length=HOP)[0][: len(f0)]
    ok = voiced & np.isfinite(f0)
    st = 12 * np.log2(np.where(ok, f0, 100.0) / 100.0)

    def span(a, b):
        return (t >= a) & (t < b)

    def movement(ws):
        m = span(ws[0]["start"], ws[-1]["end"]) & ok
        return float(np.std(st[m])) if m.sum() > 10 else None

    sents = sentences(words)
    moves = [x for x in map(movement, sents) if x is not None]
    word_db = [_db(rms[m]) for m in (span(w["start"], w["end"]) for w in words) if m.sum()]
    take_db = _db(rms[span(words[0]["start"], words[-1]["end"])])
    hook = sents[0]
    hook_move = movement(hook)
    return {
        "pitch_median_hz": round(float(np.median(f0[ok])), 1),
        "pitch_spread_st": round(float(np.percentile(st[ok], 90) - np.percentile(st[ok], 10)), 2),
        "pitch_movement_st": round(float(np.mean(moves)), 2),
        "loudness_sd_db": round(float(np.std(word_db)), 2),
        "brightness_hz": round(float(np.median(cent[ok])), 0),
        "hook_movement_st": round(hook_move, 2) if hook_move is not None else None,
        "hook_level_db": round(_db(rms[span(hook[0]["start"], hook[-1]["end"])]) - take_db, 2),
    }


def limits_from(rows):
    """The reference parts' range on every measure, slowest to fastest,
    flattest to liveliest."""
    keys = next(iter(rows.values())).keys()
    return {k: [min(r[k] for r in rows.values()), max(r[k] for r in rows.values())] for k in keys}


def faults(m, limits=None, tolerance=None):
    """Where a take's tone leaves the reference parts' range by more than
    the tolerance, as readable lines; empty when it keeps it."""
    cfg = brand().get("voice_tone", {}) if limits is None or tolerance is None else {}
    lim = limits if limits is not None else cfg.get("limits")
    if not lim:
        return ["no tone standard: list the reference parts in brand.json rhythm.reference and run voicestyle.py standard"]
    tol = dict(TOLERANCE, **(tolerance if tolerance is not None else cfg.get("tolerance", {})))
    out = []
    for k, (lo, hi) in lim.items():
        label, unit = LABELS.get(k, (k, ""))
        if m.get(k) is None:
            out.append(f"{label} could not be measured (too little voiced speech)")
        elif not lo - tol.get(k, 0.0) <= m[k] <= hi + tol.get(k, 0.0):
            out.append(f"{label} {m[k]} {unit}, outside the reference parts' {lo} to {hi} (±{tol.get(k, 0.0)})")
    return out


def _take(episode):
    pub = public_dir(episode)
    return pub / "voice.wav", json.loads((pub / "timeline.json").read_text())["words"]


def standard(path=None):
    """Measures every reference part's take and writes the range into
    brand.json (`voice_tone.limits`), keeping its tolerance and pitch range."""
    import rhythm

    path = Path(path or ROOT / "brand.json")
    b = brand(path)
    ref = b.get("rhythm", {}).get("reference", [])
    if not ref:
        raise SystemExit("no reference parts: list the series' first approved parts in brand.json rhythm.reference")
    tone = b.get("voice_tone", {})
    rows = {}
    for entry in ref:
        ep_id = entry if isinstance(entry, str) else entry["episode"]
        episode = json.loads((EPISODES / ep_id / "episode.json").read_text())
        wav, words = _take(episode)
        if not wav.exists():
            raise SystemExit(f"{ep_id}: no take at {wav}")
        rows[ep_id] = measure(wav, words, tone.get("pitch_hz"))
    lim = limits_from(rows)
    b["voice_tone"] = dict(tone, limits=lim)
    path.write_text(rhythm.dump_brand(b))
    return rows, lim


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["standard"]:
        rows, lim = standard()
        for ep_id, m in rows.items():
            print(f"  {ep_id:28} " + "  ".join(f"{k} {v}" for k, v in m.items()))
        print(json.dumps(lim, indent=1))
    elif len(a) >= 2 and a[0] == "report":
        episode = json.loads((Path(a[1]) / "episode.json").read_text())
        wav, words = _take(episode)
        if len(a) > 2:
            wav = Path(a[2])
            words = json.loads((wav.parent / "timeline.json").read_text())["words"]
        m = measure(wav, words)
        print(json.dumps(m, indent=1))
        print("\n".join(faults(m)) or "within the reference parts")
    else:
        raise SystemExit(USAGE)
