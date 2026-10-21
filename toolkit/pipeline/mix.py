"""Audio mix: voice, cue-timed sound effects and a ducked music bed, then
loudness normalisation to the delivery target (-14 LUFS integrated, true
peak under -1 dBTP on the delivered AAC file).

Levels, and why:
- the voice is levelled to -16 LUFS before the mix;
- the bed sits 8 LU under the voice where nobody speaks and is ducked 7 dB
  under speech from the word alignment, with 250-400 Hz and 1.5-4 kHz
  dipped while the voice runs, which puts it about 15-16 LU under the voice
  while it speaks (broadcast practice keeps commentary at least 10 LU over
  music, and listeners prefer more);
- effects sit under the voice, never over it;
- the mix is limited 3 dB under full scale before linear loudnorm, because
  a punchy voice cannot otherwise reach -14 LUFS under the peak ceiling and
  linear normalisation settles a dB or two low.
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from config import SFX_LIB
from sfx import LIBRARY, RATE, bed

VOICE_LUFS = -16.0
# TP leaves 1 dB for the AAC encode, which adds inter-sample peaks: a punchy
# voice mixed to -1.0 here measured -0.2 dBTP in the delivered MP4.
TARGET = {"I": -14.0, "TP": -2.0, "LRA": 11.0}
BED_OPEN_LUFS = VOICE_LUFS - 8.0
BED_CHAIN = "highpass=f=110:p=2,lowpass=f=14500,acompressor=threshold=0.03:ratio=2:attack=200:release=1200:knee=4"
BED_DUCK_DB = -7.0


def _db(x):
    return 10 ** (x / 20)


def _measure(src):
    """Integrated loudness of a file, LUFS."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    return float(json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S).group(0))["input_i"])


def _ffmpeg_loudnorm(src, dst, target, extra_filters=""):
    """Two-pass EBU R128 normalisation with ffmpeg's loudnorm, linear."""
    pre = f"{extra_filters}," if extra_filters else ""
    first = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af",
         f"{pre}loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", first, re.S).group(0))
    second = (f"{pre}loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}"
              f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", second, "-ar", str(RATE), str(dst)], check=True)


def recorded(name, args, k):
    """The k-th use of an effect in an episode: a take from sfx-lib/
    (cycling, so a repeat is never the same sample twice running), matched
    in loudness to the synthesised effect the cue's gain was set for, and
    cut to its `dur`. Falls back to the synthesised effect when no take
    exists."""
    synth = LIBRARY[name](**args) if name in LIBRARY else None
    takes = sorted(SFX_LIB.glob(f"{name}-*.wav"))
    if not takes:
        if synth is None:
            raise SystemExit(f"no effect {name!r}: neither a take in {SFX_LIB} nor a synthesised one")
        return synth
    x, _ = sf.read(takes[k % len(takes)], dtype="float32")
    if "dur" in args:
        x = x[: int(args["dur"] * RATE)].copy()
        fade = min(len(x), int(0.06 * RATE))
        x[-fade:] *= np.linspace(1, 0, fade) ** 2
    if synth is not None:
        x *= _peak_rms(synth) / (_peak_rms(x) + 1e-9)
    return x * min(1.0, 0.9 / (np.abs(x).max() + 1e-9))


def _peak_rms(x, win=0.05):
    """Loudest 50 ms of a clip: how loud a short effect sounds."""
    w = max(1, int(win * RATE))
    p = np.convolve(x.astype(np.float64) ** 2, np.ones(w) / w, mode="valid") if len(x) >= w else [np.mean(x ** 2)]
    return float(np.sqrt(np.max(p)))


def cue_time(timeline, cue):
    """`cue` is "segment" (its first word), "segment@k" (its k-th word, from
    0) or "segment$" (its last word's end). A cue past its own segment is a
    stale word number left by a wording change, and is refused."""
    m = re.fullmatch(r"([\w-]+)(?:@(\d+)|(\$))?", cue)
    if not m:
        raise ValueError(f"bad cue {cue!r}")
    if m.group(1) not in timeline["segments"]:
        raise ValueError(f"cue {cue!r}: no segment {m.group(1)!r}")
    seg = timeline["segments"][m.group(1)]
    if m.group(3):
        return seg["end"]
    k = int(m.group(2) or 0)
    if seg["first"] + k > seg["last"]:
        raise ValueError(f"cue {cue!r} is past the end of its segment ({seg['last'] - seg['first'] + 1} words)")
    return timeline["words"][seg["first"] + k]["start"]


def sfx_problems(episode, timeline, takes=None):
    """What a listener would hear as a template rather than a designed
    track: the same effect twice within a second when only one take of it
    exists (the identical sample, back to back), and effects packed denser
    than one every 1.5 s across the episode. `takes` maps an effect name to
    its number of takes (default: what sfx-lib holds)."""
    cues = []
    for c in episode.get("sfx", []):
        cues.append((cue_time(timeline, c["cue"]) + c.get("offset", 0.0), c["name"]))
    cues.sort()
    if takes is None:
        takes = {}
        for p in SFX_LIB.glob("*-*.wav"):
            n = p.stem.rsplit("-", 1)[0]
            takes[n] = takes.get(n, 0) + 1
    out = []
    last = {}
    for t, name in cues:
        if name in last and t - last[name] < 1.0 and takes.get(name, 0) < 2:
            out.append(f"{name} twice within {t - last[name]:.2f} s at {t:.2f} s with one take: the same sample back to back")
        last[name] = t
    if cues and timeline["duration"] / len(cues) < 1.5:
        out.append(f"{len(cues)} effects in {timeline['duration']:.0f} s, one every {timeline['duration'] / len(cues):.2f} s: "
                   "use them on cuts, reveals and the payoff only")
    return out


def speech_mask(timeline, lead, n):
    """1 while the narrator speaks, 0 otherwise: word spans from the
    alignment, with pauses under 0.5 s bridged so the bed does not pump."""
    m = np.zeros(n, np.float32)
    words = timeline["words"]
    i = 0
    while i < len(words):
        a, b = words[i]["start"], words[i]["end"]
        while i + 1 < len(words) and words[i + 1]["start"] - b < 0.5:
            i += 1
            b = words[i]["end"]
        m[int((a + lead) * RATE):int((b + lead) * RATE)] = 1
        i += 1
    return m


def _ramp_envelope(mask, down=0.25, ahead=0.08, release=0.75):
    """Duck amount 0..1 from a speech mask: falls over `down` seconds,
    finishing `ahead` seconds before each onset, and recovers over
    `release` seconds after speech ends, so the return is not heard in a
    short pause."""
    n = len(mask)
    ctl = 1000
    step = RATE // ctl
    m = mask[::step]
    shift = int(ahead * ctl)
    early = np.concatenate([m[shift:], np.zeros(shift, np.float32)])
    env = np.zeros(len(m), np.float32)
    up, rel = 1.0 / (down * ctl), 1.0 / (release * ctl)
    v = 0.0
    for i, t in enumerate(early):
        v = min(t, v + up) if t > v else max(t, v - rel)
        env[i] = v
    return np.interp(np.arange(n), np.arange(len(m)) * step, env).astype(np.float32)


def composed_bed(path, timeline, lead, n, work, cfg):
    """The episode's composed bed (pipeline/music.py), placed with the voice:
    cleaned and gently levelled (BED_CHAIN) so sections step rather than
    jump, set to its open level, ducked under speech, and with 250-400 Hz
    and 1.5-4 kHz dipped while the voice runs. The last `end_fade_s`
    seconds fade to silence: 0.3 s by default, 1.0 s for a bed composed to
    hold its final chord past the end of the video (`tail_s` in the plan)."""
    clean = work / "music-clean.wav"
    dipped = work / "music-dipped.wav"
    base = BED_CHAIN
    # A bed composed for a slightly shorter narration (a line re-voiced
    # after the music was made) is slowed, pitch kept, to the video's
    # length; up to 5 percent is inaudible on sparse acoustic material.
    # More than that needs a new composition.
    have = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout)
    need = (n - int(lead * RATE)) / RATE
    if have < need:
        tempo = have / need
        if tempo < 0.95:
            raise SystemExit(f"music is {have:.2f} s for {need:.2f} s of video: retime the plan and compose a new bed")
        base = f"rubberband=tempo={tempo:.5f}," + base
        print(f"music: {have:.2f} s slowed to {need:.2f} s (tempo {tempo:.4f})")
    for dst, extra in ((clean, ""), (dipped, ",equalizer=f=320:t=q:w=1.2:g=-3,equalizer=f=2500:t=q:w=1.0:g=-4")):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", base + extra, "-ac", "1", "-ar", str(RATE),
                        "-c:a", "pcm_f32le", str(dst)], check=True)
    gain = _db(BED_OPEN_LUFS + cfg.get("trim_db", 0.0) - _measure(clean))
    a, _ = sf.read(clean, dtype="float32")
    b, _ = sf.read(dipped, dtype="float32")
    off = int(lead * RATE)
    track = np.zeros(n, np.float32)
    dtrack = np.zeros(n, np.float32)
    k = min(len(a), n - off)
    track[off:off + k] = a[:k]
    dtrack[off:off + k] = b[:k]
    fade = int(cfg.get("end_fade_s", 0.3) * RATE)
    ramp = np.linspace(1, 0, fade, dtype=np.float32)
    track[n - fade:] *= ramp
    dtrack[n - fade:] *= ramp
    env = _ramp_envelope(speech_mask(timeline, lead, n))
    mixed = track * (1 - env) + dtrack * env
    return (mixed * gain * _db(BED_DUCK_DB * env)).astype(np.float32)


def build(episode, timeline, voice_wav, out_wav, work):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    public_dir = Path(voice_wav).parent
    voice_norm = work / "voice-16.wav"
    _ffmpeg_loudnorm(voice_wav, voice_norm, {"I": VOICE_LUFS, "TP": -2.0, "LRA": 11.0})
    voice, _ = sf.read(voice_norm, dtype="float32")
    # The take's own ends are faded over 10 ms, so it never starts or stops
    # on a sample away from zero: a take that ended at 0.006 became a click
    # on the quiet end card once the loudness gain was applied.
    edge = min(int(0.01 * RATE), len(voice) // 2)
    voice[:edge] *= np.linspace(0, 1, edge, dtype=np.float32)
    voice[len(voice) - edge:] *= np.linspace(1, 0, edge, dtype=np.float32)
    lead = episode.get("audio_lead", 0.0)
    tail = episode.get("tail", 1.2)
    n = int((timeline["duration"] + lead + tail) * RATE)
    voice_track = np.zeros(n, np.float32)
    off = int(lead * RATE)
    voice_track[off:off + len(voice)] = voice[: n - off]

    for p in sfx_problems(episode, timeline):
        print("sfx:", p)
    fx = np.zeros(n, np.float32)
    seen = {}
    for c in episode.get("sfx", []):
        k = seen[c["name"]] = seen.get(c["name"], -1) + 1
        clip = recorded(c["name"], c.get("args", {}), k)
        t = cue_time(timeline, c["cue"]) + lead + c.get("offset", 0.0)
        i = max(0, int(t * RATE))
        j = min(n, i + len(clip))
        fx[i:j] += clip[: j - i] * _db(c.get("gain_db", -12.0))

    music_cfg = episode.get("music", {})
    music = np.zeros(n, np.float32)
    if music_cfg.get("file"):
        music = composed_bed(public_dir / music_cfg["file"], timeline, lead, n, work, music_cfg)
    elif music_cfg.get("enabled", True):
        # The synthesised fallback bed, for pipeline tests: ducked by the
        # voice's own envelope.
        music = bed(n / RATE, **music_cfg.get("args", {})) * _db(music_cfg.get("gain_db", -20.0))
        env = np.convolve(np.abs(voice_track), np.ones(int(0.25 * RATE)) / int(0.25 * RATE), mode="same")
        duck = 1.0 - np.clip(env / (env.max() + 1e-9) * 2.5, 0, 1) * (1 - _db(music_cfg.get("duck_db", -8.0)))
        music *= duck.astype(np.float32)

    mix = voice_track + fx + music
    sf.write(work / "music-bed.wav", music, RATE, subtype="FLOAT")
    raw = work / "mix-raw.wav"
    sf.write(raw, mix, RATE, subtype="FLOAT")
    first = _measure(raw)
    limit = f"volume={TARGET['I'] - first:.2f}dB,alimiter=limit={_db(-3.0):.4f}:attack=3:release=60:level=false"
    _ffmpeg_loudnorm(raw, out_wav, TARGET, extra_filters=limit)
    return {"duration": n / RATE, "lead": lead}
