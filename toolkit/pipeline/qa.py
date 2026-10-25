"""Automated checks on a finished episode. Every check lands in
episodes/<id>/out/qa.json with pass or fail and the measured value. The
contact sheet it writes is for a person or a reviewer to read frame by
frame; passing these checks is necessary, never sufficient.

The checks, and the failure each one exists for:
- spec: 1080x1920, H.264 yuv420p, 23 to 60 fps, AAC 48 kHz, under 300 MB,
  3 s to 3 min (Reels over 3 minutes are not recommended to new viewers);
- loudness within 1 LU of -14 LUFS and true peak at or under -1 dBTP,
  measured on the delivered file, not the mix (the AAC encode adds peaks);
- every script word aligned (a word placed by interpolation is a guess);
- the voice and the picture at the rhythm of the series' reference parts,
  its first approved parts (brand.json `rhythm`, `rhythm.measure`): the
  voice in syllables a second and its shortest pauses, the picture in how
  much of the time it moves, how often and how long it holds still; a part
  passed every other check and two reviews and was still rushed;
- the narrator's tone at the reference parts' (brand.json `voice_tone`,
  `voicestyle.measure`, on the take): pitch, its movement within
  sentences, the words' loudness, brightness and the hook's energy; a take
  slowed by a direction tag kept the pace and was heard at once as a
  different, listless reading;
- no stray sounds or clicks in the narration (`voice_flaws`);
- the transcript matches the script (WER at or under 3 percent; read every
  difference by eye, because one wrong word is under 3 percent);
- every fact in episode.json marked verified, and each one logged in
  verification.md.
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import brand, public_dir
import rhythm
import voicestyle
from voice import TAG, _norm, _pcm16k, whisper_model


def probe(path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    num, den = (int(x) for x in v["avg_frame_rate"].split("/"))
    return {"width": v["width"], "height": v["height"], "vcodec": v["codec_name"], "pix_fmt": v["pix_fmt"],
            "fps": num / den, "acodec": a and a["codec_name"], "arate": a and int(a["sample_rate"]),
            "duration": float(j["format"]["duration"]), "mb": int(j["format"]["size"]) / 1e6}


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))
    return i, tp


def transcribe(path, hotwords=None, model_size=None):
    """`hotwords` names coined words the recogniser cannot spell; they bias
    decoding, so a person still listens to them. The model is medium.en
    unless QA_WHISPER_MODEL or qa.model says otherwise (voice.whisper_model):
    a small model once passed a misread proper noun that a larger one
    caught."""
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size or whisper_model(), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(_pcm16k(path), beam_size=5, hotwords=hotwords)
    return " ".join(s.text.strip() for s in segs)


# The recogniser writes American spelling; a British script is not misread.
SPELLING = {"kilometres": "kilometers", "metres": "meters", "centre": "center", "centres": "centers",
            "litres": "liters", "colour": "color", "colours": "colors", "favourite": "favorite",
            "programme": "program", "travelled": "traveled", "metre": "meter", "kilometre": "kilometer",
            "centred": "centered", "tonnes": "tons", "tonne": "ton", "km": "kilometers",
            "millimetres": "millimeters", "millimetre": "millimeter"}
_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
NUMBERS = {w: str(i) for i, w in enumerate(_ONES)}
for _t, _w in enumerate(_TENS, start=2):
    NUMBERS[_w] = str(_t * 10)
    for _o in range(1, 10):
        NUMBERS[_w + _ONES[_o]] = str(_t * 10 + _o)


def _cmp(w):
    n = _norm(w)
    n = SPELLING.get(n, n)
    return NUMBERS.get(n, n)


def word_errors(script, heard, say=None):
    """Word error rate of what was heard against the script, with the
    differences listed. Units and percentages are read alike on both sides,
    and a compound split differently ("equal-area" heard as "equal area") is
    not an error."""
    import difflib

    heard = re.sub(r"(\d)\s*%", r"\1 percent", heard)
    heard = re.sub(r"(\d)\s*mm\b", r"\1 millimetres", heard)
    heard = re.sub(r"(\d)\s*km\b", r"\1 kilometres", heard)
    heard = re.sub(r"(\d)\s*ft\b", r"\1 feet", heard)
    heard = re.sub(r"(\d)\s*[hH]z\b", r"\1 hertz", heard)
    heard = re.sub(r"(\d+)\.5\b", r"\1 and a half", heard)
    script = re.sub(r"(\d)\s*%", r"\1 percent", script)
    heard = re.sub(r"\bper cent\b", "percent", heard)
    script = re.sub(r"\bper cent\b", "percent", script)
    a = [_cmp(w) for w in TAG.sub(" ", script).split() if _norm(w)]
    b = [_cmp(w) for w in heard.split() if _norm(w)]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    diffs, readings, errors = [], [], 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "replace" and "".join(a[i1:i2]) == "".join(b[j1:j2]):
            continue
        # A word the narrator reads through `say` ("100" as "a hundred",
        # "Kiritimati" as "Kirismass") is heard in its spoken form, spelt as
        # the recogniser spells it: listed as a reading, not an error.
        if op == "replace" and say and _as_said(a[i1:i2], b[j1:j2], say):
            readings.append({"script": " ".join(a[i1:i2]), "heard": " ".join(b[j1:j2])})
            continue
        if op != "equal":
            errors += max(i2 - i1, j2 - j1)
            diffs.append({"script": " ".join(a[i1:i2]), "heard": " ".join(b[j1:j2])})
    if readings:
        diffs.append({"read as `say`": readings})
    return errors / max(1, len(a)), diffs


def _as_said(script_words, heard_words, say):
    """True when every script word here has a `say` reading and the
    words heard sound like those readings (letters 75% alike)."""
    import difflib

    spoken = []
    keys = {_cmp(k): v for k, v in say.items()}
    for w in script_words:
        if w not in keys:
            return False
        spoken += [_cmp(x) for x in keys[w].split() if _norm(x)]
    return difflib.SequenceMatcher(a="".join(spoken), b="".join(heard_words), autojunk=False).ratio() >= 0.75


def contact_sheet(video, times, labels, out_png, cols=4):
    """Frames at the given times, with the safe box drawn on, for reading by
    eye. The red bands are what the platform's interface covers."""
    from io import BytesIO

    safe = brand()["safe"]
    cap = brand()["layout"]["captions"]
    thumbs = []
    for t, label in zip(times, labels):
        png = b""
        for back in (0.0, 0.1, 0.25, 0.5):
            png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t - back):.3f}", "-i", str(video), "-frames:v", "1",
                                  "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
            if png:
                break
        im = Image.open(BytesIO(png)).convert("RGB")
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle([0, 0, 1080, safe["top"]], fill=(255, 0, 0, 40))
        d.rectangle([0, safe["bottom"], 1080, 1920], fill=(255, 0, 0, 40))
        d.rectangle([safe["right"], safe["top"], 1080, safe["bottom"]], fill=(255, 0, 0, 30))
        d.rectangle([safe["railX"], safe["railY"], safe["right"], safe["bottom"]], fill=(255, 0, 0, 30))
        d.rectangle([safe["left"], safe["top"], safe["right"], safe["bottom"]], outline=(0, 255, 136, 255), width=4)
        d.rectangle([200, cap, 880, cap + 100], outline=(0, 200, 255, 255), width=3)
        font = ImageFont.load_default(size=44)
        d.rectangle([0, 1820, 1080, 1920], fill=(0, 0, 0, 200))
        d.text((24, 1840), f"{t:5.2f}s  {label}", fill=(255, 255, 255, 255), font=font)
        thumbs.append(im.resize((540, 960)))
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (540 * cols, 960 * rows), (20, 20, 20))
    for k, im in enumerate(thumbs):
        sheet.paste(im, ((k % cols) * 540, (k // cols) * 960))
    sheet.save(out_png)


def voice_flaws(a, sr, timeline):
    """Sounds in the narration that belong to no word, cuts into sound, and
    clicks. Returns readable lines, empty if the take is clean.

    - A stray sound is a stretch of sound reaching within 40 dB of the
      take's peak, set off by true silence (20 ms or more, 60 dB under the
      peak), that touches no word (each word widened 0.03 s before and
      0.25 s after). A re-voiced ending once kept a "fo" of the next line,
      and a splice once kept the "S" of the "So" it replaced.
    - Every recorded splice must have 30 ms of silence (over 50 dB under the
      peak) on the side kept from the old take, or the cut went into an old
      word (the "T" of a replaced "Tokyo" stayed against the new one).
    - A click is a sample jump over 0.01 inside a pause more than 45 dB
      down; inside speech, sharp jumps are consonants.
    - A hole is a flat stretch of 50 ms or more between two words (10 ms
      levels within 2 dB of each other) that the sound steps down into and
      up out of by over 20 dB, as a fill put into a breath makes (0.1 s at
      -80 dB inside a breath at -25 to -53 dB). A natural pause falls and
      rises gradually, and a consonant's closure is shorter.
    - The take's first and last samples are silence and its last 50 ms
      holds no sound: a take that ended on a cut-off fragment clicked on the
      quiet end card."""
    a = a if a.ndim == 1 else a.mean(axis=1)
    hop = int(0.01 * sr)
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    peak = rms.max() + 1e-12
    words = [(w["start"] - 0.03, w["end"] + 0.25) for w in timeline["words"]]
    out = []
    heard = np.nonzero(rms > peak * 10 ** (-60 / 20))[0]
    for run in np.split(heard, np.nonzero(np.diff(heard) > 2)[0] + 1):
        if not len(run) or rms[run].max() <= peak * 10 ** (-40 / 20):
            continue
        t0, t1 = run[0] * hop / sr, (run[-1] + 1) * hop / sr
        if not any(s < t1 and t0 < e for s, e in words):
            db = 20 * np.log10(rms[run].max() / peak)
            out.append(f"stray sound {t0:.2f} to {t1:.2f} s ({db:.0f} dB from the peak), on no word")
    for x in timeline.get("voice", {}).get("splices", []):
        i = int(x["t"] * sr)
        w = a[i - int(0.035 * sr):i - int(0.005 * sr)] if x["kept"] == "before" else a[i + int(0.005 * sr):i + int(0.035 * sr)]
        level = np.sqrt((w ** 2).mean()) if len(w) else 0.0
        if level > peak * 10 ** (-50 / 20):
            out.append(f"splice at {x['t']:.2f} s cuts into sound on its {x['kept']} side "
                       f"({20 * np.log10(level / peak):.0f} dB from the peak)")
    quiet = rms < peak * 10 ** (-45 / 20)
    quiet = quiet & np.roll(quiet, 1) & np.roll(quiet, -1)
    d = np.abs(np.diff(a[: n * hop]))
    frame = np.arange(len(d)) // hop
    for i in np.nonzero((d > 0.01) & quiet[np.minimum(frame, n - 1)])[0][:20]:
        out.append(f"click at {i / sr:.3f} s (jump {d[i]:.3f} in a pause)")
    db = 20 * np.log10(rms + 1e-9)
    for w0, w1 in zip(timeline["words"], timeline["words"][1:]):
        f, f1 = int(w0["end"] * sr / hop), min(int(w1["start"] * sr / hop), n - 1)
        while f < f1:
            g = f
            while g + 1 < min(f1 + 3, n) and abs(db[g + 1] - db[f]) < 2:
                g += 1
            if g - f >= 4 and f > 0 and g + 1 < n and min(db[f - 1] - db[f], db[g + 1] - db[g]) > 20:
                out.append(f"hole at {f * hop / sr:.2f} s, {(g - f + 1) * 10} ms flat at {db[f]:.0f} dB between "
                           f"{w0['text']!r} and {w1['text']!r}")
            f = g + 1
    if abs(float(a[0])) > 0.002:
        out.append(f"the take starts on sample {a[0]:.4f}, not silence")
    tail = a[-int(0.05 * sr):]
    if abs(float(a[-1])) > 0.002 or float(np.abs(tail).max()) > peak * 10 ** (-50 / 20):
        out.append(f"the take's end is not silent (last sample {a[-1]:.4f})")
    return out


def facts_logged(episode, verification_md):
    """Fact ids from episode.json that verification.md never mentions: a
    fact marked verified with no log row is a claim, not a check."""
    text = Path(verification_md).read_text() if Path(verification_md).exists() else ""
    return [f["id"] for f in episode.get("facts", []) if not re.search(rf"\b{re.escape(f['id'])}\b", text)]


def run(episode, timeline, final_mp4, out_dir, ep_dir):
    import soundfile as sf

    out_dir = Path(out_dir)
    checks = []

    def check(name, ok, value):
        checks.append({"check": name, "pass": bool(ok), "value": value})

    p = probe(final_mp4)
    check("resolution 1080x1920", (p["width"], p["height"]) == (1080, 1920), f"{p['width']}x{p['height']}")
    check("video H.264 yuv420p", p["vcodec"] == "h264" and p["pix_fmt"] == "yuv420p", f"{p['vcodec']} {p['pix_fmt']}")
    check("frame rate 23-60", 23 <= p["fps"] <= 60, round(p["fps"], 3))
    check("audio AAC 48 kHz", p["acodec"] == "aac" and p["arate"] == 48000, f"{p['acodec']} {p['arate']}")
    check("under 300 MB", p["mb"] < 300, round(p["mb"], 2))
    check("length 3 s to 3 min", 3 <= p["duration"] <= 180, round(p["duration"], 2))
    # Every rendered frame delivered: the final file holds as many frames as
    # the muted render beside it (out/video.mp4).
    rendered = Path(final_mp4).with_name("video.mp4")
    if rendered.exists():
        from build import frame_count
        got, want = frame_count(final_mp4)[0], frame_count(rendered)[0]
        check("every rendered frame delivered", got == want, f"{got} of {want}")
    i, tp = loudness(final_mp4)
    check("loudness -14 LUFS +-1", abs(i + 14) <= 1.0, i)
    check("true peak <= -1 dBTP", tp <= -1.0, tp)
    check("every script word aligned", timeline["voice"].get("unmatched_words", 0) == 0, timeline["voice"].get("unmatched_words"))
    m = rhythm.measure(episode, timeline, final_mp4)
    off = rhythm.faults(m)
    check("voice and picture at the reference parts' rhythm", not off, {"faults": off, **m})
    voice_wav = public_dir(episode) / "voice.wav"
    if voice_wav.exists():
        a, sr = sf.read(str(voice_wav), dtype="float32")
        flaws = voice_flaws(a, sr, timeline)
    else:
        flaws = [f"no take at {voice_wav}"]
    check("no stray sounds or clicks in the narration", not flaws, flaws)
    if voice_wav.exists():
        tone = voicestyle.measure(voice_wav, timeline["words"])
        off = voicestyle.faults(tone)
        check("narrator's tone at the reference parts'", not off, {"faults": off, **tone})
    else:
        check("narrator's tone at the reference parts'", False, f"no take at {voice_wav}")
    script = " ".join(s["text"] for s in episode["segments"])
    hotwords = episode.get("qa", {}).get("hotwords")
    heard = transcribe(final_mp4, hotwords, whisper_model(episode))
    say = episode.get("say", {})
    if "british" in say or "american" in say:
        say = say.get(episode.get("voice", {}).get("accent", "british"), {})
    wer, diffs = word_errors(script, heard, say)
    check("narration matches script (WER <= 3%)", wer <= 0.03, {"wer": round(wer, 4), "diffs": diffs})
    unverified = [f["claim"] for f in episode.get("facts", []) if f.get("status") != "verified"]
    check("every on-screen or spoken fact verified", not unverified, unverified)
    missing = facts_logged(episode, Path(ep_dir) / "verification.md")
    check("every fact logged in verification.md", not missing, missing)

    lead = episode.get("audio_lead", 0.0)
    times, labels = [0.0], ["first frame"]
    for sid, s in timeline["segments"].items():
        times.append(min(p["duration"] - 0.05, s["start"] + lead + 0.6))
        labels.append(sid)
    times.append(p["duration"] - 0.05)
    labels.append("last frame")
    contact_sheet(final_mp4, times, labels, out_dir / "contact-sheet.png")

    report = {"episode": episode["id"], "probe": p, "transcript": heard, "hotwords": hotwords, "checks": checks,
              "passed": all(c["pass"] for c in checks)}
    (out_dir / "qa.json").write_text(json.dumps(report, indent=1))
    return report
