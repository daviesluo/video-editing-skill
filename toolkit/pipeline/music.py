"""Music beds composed per episode with Eleven Music, and the checks a take
must pass before it is used.

    python pipeline/music.py make   episodes/<id> <seed> [model]
    python pipeline/music.py check  episodes/<id> <take.mp3>
    python pipeline/music.py use    episodes/<id> <take.mp3>
    python pipeline/music.py retime episodes/<id> <segment id> [...]

`make` sends episodes/<id>/music-plan.json, a composition plan whose chunk
boundaries sit on the narration's segment starts, and writes the take to
episodes/<id>/out/music/. `check` measures it after the mixer's own
clean-up and levelling, which is what the viewer hears. `use` copies a take
that passed to studio/public/episodes/<id>/music.mp3 (committed) and
records model, seed, song id and licence in episode.json. `retime` puts the
chunk boundaries back on the segment starts after a new take of the voice.

Make two or more seeds, check each, and use the best that passes: takes of
one plan differ a lot, and the checks below each come from a take that
sounded wrong once (a hole under the hook, a jump at a seam, a chord cut
off under the last word, a hummed vocal).
"""

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from config import brand, public_dir

FORMAT = "mp3_44100_128"
# The plan's own keys, which the API does not take.
LOCAL_KEYS = ("tail_s",)


def _load(path, sr=44100):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32), sr


def make(ep_dir, seed, model="music_v2_5"):
    import requests

    from voice import eleven

    ep_dir = Path(ep_dir)
    plan = json.loads((ep_dir / "music-plan.json").read_text())
    for k in LOCAL_KEYS:
        plan.pop(k, None)
    base, headers = eleven()
    r = requests.post(f"{base}/music", params={"output_format": FORMAT}, headers=headers, timeout=600,
                      json={"composition_plan": plan, "model_id": model, "seed": int(seed)})
    if r.status_code != 200:
        raise SystemExit(f"music: HTTP {r.status_code}: {r.text[:400]}")
    out = ep_dir / "out" / "music"
    out.mkdir(parents=True, exist_ok=True)
    take = out / f"take-{model}-{seed}.mp3"
    take.write_bytes(r.content)
    meta = {"model": model, "seed": int(seed), "format": FORMAT, "song_id": r.headers.get("song-id"),
            "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    take.with_suffix(".json").write_text(json.dumps(meta, indent=1))
    print(take, len(r.content), "bytes")
    return take


def hole_db(x, sr, skip_end_s=4.0):
    """How far the quietest 3 s of the bed's body falls under its median
    level, dB (negative). 1 s windows every 0.5 s, smoothed over 3 s; the
    first window and the ending are left out. A take that sat near silence
    for 3 s under a hook and then came in at once scored -13.9; the check
    fails anything under -10."""
    sec = int(sr)
    starts = range(0, max(1, len(x) - sec), sec // 2)
    rms = np.array([np.sqrt(np.mean(x[i:i + sec] ** 2) + 1e-12) for i in starts])
    db = 20 * np.log10(rms)
    if len(db) < 8:
        return 0.0
    win = np.convolve(db, np.ones(6) / 6, mode="valid")
    body = win[1:max(2, len(win) - int(2 * skip_end_s))]
    return round(float(body.min() - np.median(body)), 1)


def hold_db(x, sr, t0, t1):
    """The bed's level from t0 to t1 (the last words and the end card)
    against the median of the whole take, dB. A bed that stops on the last
    word leaves the end card in near silence: 15 dB or more under the
    median, where a held final chord stays within a few dB."""
    sec = int(0.25 * sr)
    rms = lambda a, b: 20 * np.log10(np.sqrt(np.mean(x[a:b] ** 2) + 1e-12))
    whole = [rms(i, i + sec) for i in range(0, len(x) - sec, sec)]
    span = [rms(i, i + sec) for i in range(int(t0 * sr), max(int(t0 * sr) + 1, int(t1 * sr) - sec), sec)]
    if not span:
        return 0.0
    return round(float(min(span) - np.median(whole)), 1)


def check(ep_dir, take):
    """Measures a take against the plan and the rules below. Returns the
    report, with "passed"."""
    from mix import BED_CHAIN

    ep_dir = Path(ep_dir)
    episode = json.loads((ep_dir / "episode.json").read_text())
    raw_take = take
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(take), "-af", BED_CHAIN, "-ac", "1", "-c:a", "pcm_f32le", tmp.name],
                   check=True)
    take = tmp.name
    plan = json.loads((ep_dir / "music-plan.json").read_text())
    x, sr = _load(take)
    want = sum(c["duration_ms"] for c in plan["chunks"]) / 1000
    dur = len(x) / sr
    rep = {"duration": round(dur, 2), "planned": want}

    err = subprocess.run(["ffmpeg", "-nostats", "-i", str(take), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    rep["lufs"] = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    rep["lra"] = float(re.findall(r"LRA:\s+([\d.]+) LU", err)[-1])

    # The share of energy in the 1-4 kHz speech-clarity band, and note
    # onsets per second: a bed that competes with the voice fails both.
    n, hop = 4096, 1024
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    rep["clarity_band_db"] = round(float(10 * np.log10(spec[:, (f >= 1000) & (f < 4000)].sum() / spec.sum())), 1)
    mag = np.sqrt(spec)
    flux = np.maximum(mag[1:] - mag[:-1], 0).sum(axis=1)
    flux /= flux.max() + 1e-9
    thr = np.median(flux) + 0.08
    onsets = sum(1 for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] > flux[i + 1])
    rep["onsets_per_s"] = round(onsets / dur, 2)

    # Jumps at chunk seams, as a listener hears them: short-term loudness
    # (3 s) over the 3 s after each seam against the 3 s before it.
    log = subprocess.run(["ffmpeg", "-nostats", "-v", "verbose", "-i", str(take), "-af", "ebur128=framelog=verbose", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [(float(a), float(b)) for a, b in re.findall(r"t:\s*([\d.]+)\s+TARGET.*?S:\s*(-?[\d.]+)", log)]
    ts = np.array([a for a, _ in st])
    sv = np.array([b for _, b in st])
    short = lambda t: float(sv[np.argmin(np.abs(ts - t))])
    seams, t = [], 0.0
    for c in plan["chunks"][:-1]:
        t += c["duration_ms"] / 1000
        seams.append(round(short(t + 3.0) - short(t), 1))
    rep["seam_jumps_lu"] = seams
    # The very end decays, with no click.
    last = x[-int(1.5 * sr):]
    q = [np.sqrt(np.mean(s ** 2) + 1e-12) for s in np.array_split(last, 6)]
    rep["tail_db"] = [round(float(20 * np.log10(v)), 1) for v in q]
    rep["end_click"] = round(float(20 * np.log10(np.abs(x[-64:]).max() + 1e-9)), 1)
    rep["hole_db"] = hole_db(x, sr)
    # Under the last words and the end card: the bed must still sound.
    tl_path = public_dir(episode) / "timeline.json"
    if tl_path.exists():
        tl = json.loads(tl_path.read_text())
        end_card = tl["duration"] + episode.get("tail", 1.2) - episode.get("music", {}).get("end_fade_s", 0.3)
        rep["hold_db"] = hold_db(x, sr, max(0.0, tl["duration"] - 1.0), min(dur, end_card))

    # Vocals: speech detection on the take; an instrumental bed has none.
    from faster_whisper import WhisperModel

    # Speech detection only: the small model is enough to hear a hum or a
    # sung line, and it is fast.
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    x16, _ = _load(raw_take, 16000)
    segs, _ = model.transcribe(x16, vad_filter=True, language="en")
    words = [s.text.strip() for s in segs if s.no_speech_prob < 0.5 and s.avg_logprob > -0.8]
    rep["voice_detected"] = words

    rules = {
        "length within 0.6 s of the plan": abs(dur - want) < 0.6,
        "loudness range at most 9 LU": rep["lra"] <= 9,
        "1-4 kHz share at most -20 dB": rep["clarity_band_db"] <= -20,
        "at most 4 onsets per second": rep["onsets_per_s"] <= 4,
        "no seam jumps over 4 LU": max(map(abs, seams), default=0) <= 4,
        "the last 1.5 s decays by over 6 dB": rep["tail_db"][-1] < rep["tail_db"][0] - 6,
        "no click at the end": rep["end_click"] < -30,
        "no hole in the body (over -10 dB)": rep["hole_db"] > -10,
        "holds under the end card (over -12 dB)": rep.get("hold_db", 0.0) > -12,
        "no voice detected": not words,
    }
    rep["failed"] = [k for k, ok in rules.items() if not ok]
    rep["passed"] = not rep["failed"]
    os.unlink(tmp.name)
    return rep


def use(ep_dir, take):
    ep_dir = Path(ep_dir)
    episode = json.loads((ep_dir / "episode.json").read_text())
    public = public_dir(episode)
    public.mkdir(parents=True, exist_ok=True)
    shutil.copy(take, public / "music.mp3")
    meta = json.loads(Path(take).with_suffix(".json").read_text())
    music = episode.get("music", {})
    for k in ("args", "gain_db", "duck_db", "enabled"):
        music.pop(k, None)
    music.update({"file": "music.mp3", "plan": "music-plan.json", **meta, "licence": brand()["music"]["licence"]})
    episode["music"] = music
    (ep_dir / "episode.json").write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n")
    print("installed", public / "music.mp3")


def chunk_edges(timeline, starts, tail_s=1.5):
    """Chunk boundaries for a plan: chunk i starts where segment starts[i]
    starts (the first at 0), and the last ends `tail_s` after the
    narration. A `tail_s` of 3 to 4 s lets the bed hold its final chord
    under the end card instead of decaying there."""
    return [0.0] + [timeline["segments"][s]["start"] for s in starts[1:]] + [timeline["duration"] + tail_s]


def retime(ep_dir, *starts):
    ep_dir = Path(ep_dir)
    episode = json.loads((ep_dir / "episode.json").read_text())
    plan_path = ep_dir / "music-plan.json"
    plan = json.loads(plan_path.read_text())
    if len(starts) != len(plan["chunks"]):
        raise SystemExit(f"{len(plan['chunks'])} chunks need {len(plan['chunks'])} segment ids, got {len(starts)}")
    tl = json.loads((public_dir(episode) / "timeline.json").read_text())
    edges = chunk_edges(tl, starts, plan.get("tail_s", 1.5))
    for chunk, a, b in zip(plan["chunks"], edges, edges[1:]):
        chunk["duration_ms"] = int(round((b - a) * 100)) * 10
    plan_path.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
    print("chunks:", [(c.get("text"), c["duration_ms"]) for c in plan["chunks"]])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, ep = sys.argv[1], sys.argv[2]
    if cmd == "make":
        make(ep, *sys.argv[3:])
    elif cmd == "check":
        print(json.dumps(check(ep, sys.argv[3]), indent=1))
    elif cmd == "use":
        use(ep, sys.argv[3])
    elif cmd == "retime":
        retime(ep, *sys.argv[3:])
    else:
        raise SystemExit(__doc__)
