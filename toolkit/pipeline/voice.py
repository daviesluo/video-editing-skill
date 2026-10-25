"""Narration: synthesis, word alignment, re-voicing and the episode timeline.

The script's own words drive the captions and the visual cues, so whatever
produced the audio, its timings are mapped back onto the script word by
word.

Providers:
  elevenlabs  the production voice, one request per episode to
              /with-timestamps, which also returns character timings.
              VOICE_REALIGN=1 keeps the existing take and recovers word
              timings with faster-whisper instead.
  kokoro      pipeline tests only (`VOICE_PROVIDER=kokoro`); never ships.

Entry points: `make` (a whole take), `realign` (re-time a committed take by
forced alignment), `replace_words` (re-voice one changed phrase and splice
it into the approved take), `add_line` (append a line), `measure_span`
(numbers for choosing among several seeds), `pace_measure` and
`pace_report` (the narration's pace in syllables a second, against the
series' reference parts), `pace` (lengthen a take's short pauses, in
silence, to the reference parts' typical pauses).
"""

import base64
import difflib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from config import EPISODES, ROOT, brand, readings

RATE = 48000
TAG = re.compile(r"\[[^\]]*\]")
API = "https://api.elevenlabs.io/v1"
PUNCT = ".,:;?!"


def eleven():
    """Base URL and headers for ElevenLabs: a direct key from the
    environment or the project's .env (gitignored), or else a relay that
    holds the key server-side (ELEVENLABS_PROXY_URL and a token). A key
    never goes in the repository or in chat."""
    env = dict(os.environ)
    dotenv = ROOT / ".env"
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep and not line.startswith("#"):
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if env.get("ELEVENLABS_API_KEY"):
        return API, {"xi-api-key": env["ELEVENLABS_API_KEY"]}
    if env.get("ELEVENLABS_PROXY_URL") and env.get("ELEVENLABS_PROXY_TOKEN"):
        return env["ELEVENLABS_PROXY_URL"].rstrip("/") + "/v1", {"x-proxy-token": env["ELEVENLABS_PROXY_TOKEN"]}
    raise SystemExit("No ElevenLabs access: set ELEVENLABS_API_KEY in the environment or .env (see .env.example)")


def _core(w):
    """A script word without its trailing punctuation, and that punctuation."""
    core = w.rstrip(PUNCT)
    return core, w[len(core):]


def spoken_text(segments, say=None):
    """The text sent to the voice: audio tags kept, segments joined. `say`
    maps a script word ("2,688") to how the narrator reads it ("two thousand
    six hundred and eighty-eight"); captions keep the script's form."""
    say = say or {}
    out = []
    for s in segments:
        for w in s["text"].split():
            core, trail = _core(w)
            out.append(say[core] + trail if core in say else w)
    return " ".join(out)


def script_words(segments):
    """Caption words with their segment ids; audio tags removed."""
    out = []
    for s in segments:
        for w in TAG.sub(" ", s["text"]).split():
            out.append({"text": w, "seg": s["id"]})
    return out


def _norm(w):
    return re.sub(r"[^0-9a-z]", "", w.lower().replace("’", "'"))


def to_wav48(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(RATE), "-c:a", "pcm_s16le", str(dst)],
                   check=True)


def lufs(a, sr):
    """Integrated loudness (EBU R128) of a mono or stereo array."""
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        sf.write(f.name, a, sr)
        err = subprocess.run(["ffmpeg", "-nostats", "-i", f.name, "-af", "ebur128", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def synth_elevenlabs(text, cfg, wav_path, previous_text=None, next_text=None, seed=None):
    """One request returns the audio and per-character timings of the text as
    sent, so no separate alignment call is needed. `previous_text` and
    `next_text` give the model the narration around this text, so an added
    or replaced line continues the delivery instead of starting afresh."""
    import requests

    api, auth = eleven()
    body = {
        "text": text,
        "model_id": cfg.get("model", "eleven_v4"),
        "voice_settings": {
            "stability": cfg.get("stability", 0.5),
            "similarity_boost": cfg.get("similarity_boost", 0.75),
        },
        "apply_text_normalization": "auto",
        "language_code": cfg.get("language", "en"),
    }
    seed = cfg.get("seed") if seed is None else seed
    if seed is not None:
        body["seed"] = int(seed)
    if previous_text:
        body["previous_text"] = previous_text
    if next_text:
        body["next_text"] = next_text
    r = requests.post(f"{api}/text-to-speech/{cfg['voice_id']}/with-timestamps",
                      params={"output_format": cfg.get("format", "mp3_44100_192")},
                      headers={**auth, "Content-Type": "application/json"}, json=body, timeout=300)
    if not r.ok:
        raise SystemExit(f"ElevenLabs {r.status_code}: {r.text[:400]}")
    j = r.json()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(base64.b64decode(j["audio_base64"]))
        tmp.flush()
        to_wav48(tmp.name, wav_path)
    return words_from_chars(j["alignment"]), r.headers.get("x-character-count")


def words_from_chars(al):
    """Character timings to whitespace-separated words with start and end."""
    tokens, cur = [], None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                tokens.append(cur)
            cur = None
        elif cur is None:
            cur = {"text": ch, "start": a, "end": b}
        else:
            cur["text"] += ch
            cur["end"] = b
    if cur:
        tokens.append(cur)
    return [t for t in tokens if not TAG.fullmatch(t["text"])]


def _pcm16k(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def whisper_model(episode=None):
    """The recogniser used for every check of what the voice says: medium.en
    by default, because a small model once passed a misread proper noun that
    a larger one caught. QA_WHISPER_MODEL (e.g. large-v3) or episode.json's
    qa.model overrides it where the machine can hold a larger one."""
    return (episode or {}).get("qa", {}).get("model") or os.environ.get("QA_WHISPER_MODEL", "medium.en")


def align_whisper(wav_path):
    """Word timings recovered from finished audio, for a take whose own
    timings were lost. Less exact than forced alignment. faster-whisper is
    given decoded samples: its own file decoding fails on some systems."""
    from faster_whisper import WhisperModel

    model = WhisperModel(whisper_model(), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(_pcm16k(wav_path), beam_size=5, word_timestamps=True)
    return [{"text": w.word.strip(), "start": w.start, "end": w.end} for s in segs for w in s.words]


def synth_kokoro(text, cfg, wav_path):
    """A local voice for pipeline tests only: it never ships."""
    from kokoro import KPipeline

    voice = cfg.get("kokoro_voice", "af_heart")
    pipe = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
    chunks, tokens, offset = [], [], 0.0
    for r in pipe(TAG.sub(" ", text), voice=voice, speed=cfg.get("speed", 1.0)):
        a = r.audio.numpy()
        for tk in r.tokens or []:
            if tk.start_ts is None or not tk.text.strip():
                continue
            tokens.append({"text": tk.text, "start": offset + tk.start_ts, "end": offset + tk.end_ts})
        chunks.append(a)
        offset += len(a) / 24000
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, np.concatenate(chunks), 24000)
        to_wav48(tmp.name, wav_path)
    return tokens


def align_forced(wav_path, text):
    """Word timings from forced alignment of the finished audio against the
    text as spoken. Synthesis timings run 150 to 250 ms late on words after
    a pause, where forced alignment lands within about 85 ms of the voiced
    onset, so every shipped timeline is re-timed with it."""
    import requests

    api, auth = eleven()
    with open(wav_path, "rb") as f:
        r = requests.post(f"{api}/forced-alignment", headers=auth, files={"file": ("voice.wav", f, "audio/wav")},
                          data={"text": text}, timeout=300)
    if not r.ok:
        raise SystemExit(f"ElevenLabs forced alignment {r.status_code}: {r.text[:400]}")
    return [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in r.json()["words"] if w["text"].strip()]


def realign(episode, public_dir):
    """Re-times the committed narration's words by forced alignment, keeping
    the audio; writes timeline.json and returns the shift of each word's
    start against the timeline it replaces, or None when the number of
    words changed. Splice records, caption keeps and the lead and tail are
    kept."""
    public_dir = Path(public_dir)
    say = readings(episode)
    wav = public_dir / "voice.wav"
    old = json.loads((public_dir / "timeline.json").read_text())
    tokens = align_forced(wav, spoken_text(episode["segments"], say))
    mapped, missing = map_to_script(script_words(episode["segments"]), tokens, say)
    a, sr = sf.read(wav, dtype="float32")
    fricative_onsets(mapped, a, sr, say)
    timeline = build_timeline(mapped, wav)
    timeline["voice"] = dict(old["voice"], alignment="forced", unmatched_words=missing)
    for k in ("keep", "split", "lead", "tail"):
        if k in old:
            timeline[k] = old[k]
    (public_dir / "timeline.json").write_text(json.dumps(timeline, indent=1, ensure_ascii=False))
    # The shift per word means something only when the words are the same
    # words: after a wording change the counts differ.
    if len(mapped) != len(old["words"]):
        return None
    return [round(n["start"] - o["start"], 3) for n, o in zip(mapped, old["words"])]


def hiss_db(a, sr):
    """Energy from 4 to 10 kHz in 10 ms frames, dB: where an s, f or z is."""
    if a.ndim == 2:
        a = a.mean(axis=1)
    n = int(0.01 * sr)
    frames = a[: len(a) // n * n].reshape(-1, n)
    spec = np.abs(np.fft.rfft(frames * np.hanning(n), axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    return 10 * np.log10(spec[:, (f > 4000) & (f < 10000)].sum(axis=1) + 1e-12)


def fricative_onsets(words, a, sr, say=None, pause=0.15, reach=0.3, closure=0.08):
    """Forced alignment puts a word that starts with a hiss after a pause at
    the next sound instead ("Spain" started at its "p", 0.2 s after its
    "S"), so its caption lights late. Such a word's start moves back over
    the hiss, through at most `closure` s of a stop's silence, to where the
    4 to 10 kHz energy first rises within 30 dB of the take's loudest hiss.
    A word is judged by how it is read ("65%" reads "sixty-five"), and a
    hiss that runs on unbroken from a word ending in a hiss or a burst
    ("straight south") is that word's and is left alone. Edits `words` in
    place and returns the indices it moved."""
    say = say or {}

    def read(w):
        return say.get(_core(w["text"])[0], w["text"])

    hi = hiss_db(a, sr)
    floor = hi.max() - 30
    moved = []
    for i, (prev, w) in enumerate(zip(words, words[1:]), start=1):
        if not re.match(r"[sfzSFZ]", read(w)) or w["start"] - prev["end"] < pause:
            continue
        k = min(int(w["start"] / 0.01), len(hi) - 1)
        lo = max(int((prev["end"] + 0.02) / 0.01), int((w["start"] - reach) / 0.01))
        j = k - 1
        while j >= lo and k - j <= closure / 0.01 and hi[j] < floor:
            j -= 1
        first = None
        while j >= lo and hi[j] >= floor:
            first = j
            j -= 1
        if first is not None and re.search(r"[tszfxkp]$", _core(prev["text"])[0].lower()) and first <= lo:
            continue
        if first is not None and k - first >= 3:
            w["start"] = round(first * 0.01, 3)
            moved.append(i)
    return moved


def map_to_script(words, tokens, say=None):
    """Give every script word a start and end from the timed tokens.

    Tokens are matched to script words on normalised text; punctuation-only
    tokens are dropped first. Words with no match are placed by interpolating
    between their matched neighbours, and the count is returned so a poor
    alignment fails QA instead of passing silently."""
    say = say or {}
    toks = [t for t in tokens if _norm(t["text"])]
    # Each script word as the words actually spoken, so a spelled-out number
    # matches its tokens and they time the one caption word.
    spoken = []
    for i, w in enumerate(words):
        core, _ = _core(w["text"])
        for f in (say[core] if core in say else w["text"]).split():
            if _norm(f):
                spoken.append((_norm(f), i))
    a = [x[0] for x in spoken]
    b = [_norm(t["text"]) for t in toks]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    timed = [None] * len(words)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            t = toks[blk.b + k]
            i = spoken[blk.a + k][1]
            timed[i] = (t["start"], t["end"]) if timed[i] is None else (min(timed[i][0], t["start"]), max(timed[i][1], t["end"]))
    missing = sum(1 for x in timed if x is None)
    idx = [i for i, x in enumerate(timed) if x is not None]
    if not idx:
        raise SystemExit("alignment matched no words")
    for i, x in enumerate(timed):
        if x is not None:
            continue
        prev = max((j for j in idx if j < i), default=None)
        nxt = min((j for j in idx if j > i), default=None)
        s = timed[prev][1] if prev is not None else timed[nxt][0]
        e = timed[nxt][0] if nxt is not None else timed[prev][1] + 0.3
        span = [k for k in range(len(words)) if (prev is None or k > prev) and (nxt is None or k < nxt)]
        step = (e - s) / max(1, len(span))
        pos = span.index(i)
        timed[i] = (s + pos * step, s + (pos + 1) * step)
    out = [dict(w, start=round(t[0], 3), end=round(t[1], 3)) for w, t in zip(words, timed)]
    return out, missing


def build_timeline(words, wav_path):
    info = sf.info(str(wav_path))
    segs = {}
    for i, w in enumerate(words):
        s = segs.setdefault(w["seg"], {"start": w["start"], "end": w["end"], "first": i, "last": i})
        s["end"] = w["end"]
        s["last"] = i
    return {"duration": round(info.frames / info.samplerate, 3), "words": words, "segments": segs}


def speech_span(line, sr):
    """Start and end, in seconds, of the speech in a synthesised line.

    The synthesis timings can run past the last word into trailing silence,
    so the span comes from the sound: 10 ms frames within 40 dB of the peak,
    with 40 ms kept before and 120 ms of release after. A short burst (under
    0.2 s) left alone after a pause of 0.2 s or more is dropped: given the
    next line as context, the model can start voicing it, and a re-voiced
    ending once kept the "fo" of the "Follow" that came next."""
    mono = line if line.ndim == 1 else line.mean(axis=1)
    hop = int(0.01 * sr)
    rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, mode="same"))[::hop]
    loud = np.nonzero(rms > rms.max() * 10 ** (-40 / 20))[0]
    runs = np.split(loud, np.nonzero(np.diff(loud) > 20)[0] + 1)
    while len(runs) > 1 and len(runs[-1]) < 20:
        runs.pop()
    t0 = max(0.0, runs[0][0] * hop / sr - 0.04)
    t1 = min(len(line) / sr, runs[-1][-1] * hop / sr + 0.12)
    return t0, t1


def silence_near(a, sr, t, step):
    """The nearest point to `t`, searching backward (step -1) or forward
    (step 1), at the middle of 30 ms of true silence (every 10 ms frame over
    55 dB under the take's peak). Forced alignment can place a word's start
    up to about 0.1 s after its sound begins (an "S", a "T"), so a cut at
    the aligned time keeps part of the removed word: a hiss of a replaced
    "So", the "T" of a replaced "Tokyo"."""
    mono = a if a.ndim == 1 else a.mean(axis=1)
    hop = int(0.01 * sr)
    n = len(mono) // hop
    rms = np.sqrt((mono[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    quiet = rms < rms.max() * 10 ** (-55 / 20)
    f = int(t * sr) // hop
    while 1 <= f < n - 1:
        if quiet[f - 1] and quiet[f] and quiet[f + 1]:
            return (f + 0.5) * hop / sr
        f += step
    raise SystemExit(f"no silence near {t:.2f} s to cut at")


def record_splices(tl, at, moved_after=None, shift=0.0, replaced=None):
    """Notes splice points in a timeline's voice record, which `realign`
    keeps, as {"t": seconds in the take, "kept": "before" or "after"}: the
    side that came from the old take, which `qa.voice_flaws` checks is
    silent. Points inside the span just replaced belong to audio that is
    gone and are dropped (a stale record inside a new line failed QA);
    points after `moved_after` move by `shift`. Returns the timeline."""
    old = tl["voice"].get("splices", [])
    if replaced is not None:
        old = [x for x in old if not (replaced[0] < x["t"] < replaced[1])]
    if moved_after is not None:
        old = [dict(x, t=round(x["t"] + shift, 3)) if x["t"] > moved_after else x for x in old]
    new = [{"t": round(t, 3), "kept": side} for t, side in at]
    tl["voice"]["splices"] = sorted(old + new, key=lambda x: x["t"])
    return tl


def _write_splices(public_dir, *args, **kw):
    p = Path(public_dir) / "timeline.json"
    p.write_text(json.dumps(record_splices(json.loads(p.read_text()), *args, **kw), indent=1))


def add_line(episode, public_dir, seg, pause=0.4, seed=None):
    """Appends one new segment to a finished narration without touching the
    approved audio before it: the line is synthesised alone (with the
    narration so far as context), trimmed to its sound, matched in loudness
    to the segment before it, placed `pause` seconds after the last word,
    and its words are added to the timeline. `seg` is {"id", "text"} and
    must already be the last segment of episode.json. Run `realign` after."""
    public_dir = Path(public_dir)
    cfg = episode["voice"]
    say = readings(episode)
    assert episode["segments"][-1]["id"] == seg["id"]
    before = [s for s in episode["segments"] if s["id"] != seg["id"]]
    tl = json.loads((public_dir / "timeline.json").read_text())
    if any(w["seg"] == seg["id"] for w in tl["words"]):
        raise SystemExit(f"{seg['id']} is already in the timeline")
    wav = public_dir / "voice.wav"
    base, sr = sf.read(wav, dtype="float32")
    with tempfile.TemporaryDirectory() as tmp:
        line_wav = Path(tmp) / "line.wav"
        tokens, _ = synth_elevenlabs(spoken_text([seg], say), cfg, line_wav, previous_text=spoken_text(before, say), seed=seed)
        line, lsr = sf.read(line_wav, dtype="float32")
    assert lsr == sr, (lsr, sr)
    t0, t1 = speech_span(line, sr)
    line = line[int(t0 * sr):int(t1 * sr)]
    seg_t = tl["segments"][before[-1]["id"]]
    ref = base[int(seg_t["start"] * sr):int(seg_t["end"] * sr)]
    line = line * float(10 ** (np.clip(lufs(ref, sr) - lufs(line, sr), -8, 8) / 20))
    off = tl["words"][-1]["end"] + pause
    cut = int(off * sr)
    head = base[:cut].copy()
    fade = int(0.03 * sr)
    ramp = np.linspace(1, 0, fade, dtype=np.float32)
    head[-fade:] *= ramp[:, None] if head.ndim == 2 else ramp
    if len(head) < cut:
        head = np.concatenate([head, np.zeros((cut - len(head),) + head.shape[1:], np.float32)])
    line[: int(0.015 * sr)] *= np.linspace(0, 1, int(0.015 * sr), dtype=np.float32)
    sf.write(wav, np.concatenate([head, line]), sr)
    _write_splices(public_dir, [(off, "before")])
    tl = json.loads((public_dir / "timeline.json").read_text())
    shifted = [{"text": t["text"], "start": t["start"] - t0 + off, "end": t["end"] - t0 + off} for t in tokens]
    mapped, missing = map_to_script(script_words([seg]), shifted, say)
    timeline = build_timeline(tl["words"] + mapped, wav)
    timeline["voice"] = dict(tl["voice"], added_line=seg["id"], unmatched_words=tl["voice"].get("unmatched_words", 0) + missing)
    (public_dir / "timeline.json").write_text(json.dumps(timeline, indent=1))
    return timeline


def replace_words(episode, public_dir, seg_id, first, last, gap=0.5, seed=None):
    """Re-voices one changed phrase inside a finished narration and keeps
    the rest of the approved take: words `first` to `last` (indices within
    segment `seg_id` of the committed timeline) are cut out, and the
    segment's new wording from that word on, which episode.json must
    already hold, is synthesised alone with the narration before and after
    it as context, trimmed to its sound, matched in loudness to the segment
    and spliced in with 15 ms ramps. Cuts are made only in true silence.
    Any extra length comes out of the pause after it, down to `gap` seconds
    before the next word, so the rest of the episode moves as little as
    possible. Replace whole sentences from a pause: a start inside connected
    speech is refused, because the nearest silence can be words earlier and
    the cut would silently drop them. The caller then re-times the take
    with `realign`. Returns the shift of the words after the splice."""
    public_dir = Path(public_dir)
    cfg = episode["voice"]
    say = readings(episode)
    tl = json.loads((public_dir / "timeline.json").read_text())
    s = tl["segments"][seg_id]
    i0, i1 = s["first"] + first, s["first"] + last
    old_words = tl["words"]
    segs = episode["segments"]
    k = next(n for n, x in enumerate(segs) if x["id"] == seg_id)
    new_seg_words = segs[k]["text"].split()
    new_text = " ".join(new_seg_words[first:])
    before_text = spoken_text(segs[:k], say) + " " + " ".join(new_seg_words[:first])
    after_text = spoken_text(segs[k + 1:], say)
    wav = public_dir / "voice.wav"
    base, sr = sf.read(wav, dtype="float32")
    cut_a = 0.0 if i0 == 0 else silence_near(base, sr, old_words[i0]["start"] - 0.03, -1)
    if old_words[i0]["start"] - cut_a > 0.35:
        raise ValueError(f"no pause before word {first} of {seg_id!r}: the cut would start "
                         f"{old_words[i0]['start'] - cut_a:.2f} s early; replace from an earlier word")
    with tempfile.TemporaryDirectory() as tmp:
        line_wav = Path(tmp) / "line.wav"
        synth_elevenlabs(spoken_text([{"id": seg_id, "text": new_text}], say), cfg, line_wav,
                         previous_text=before_text.strip(), next_text=after_text, seed=seed)
        line, lsr = sf.read(line_wav, dtype="float32")
    assert lsr == sr, (lsr, sr)
    t0, t1 = speech_span(line, sr)
    line = line[int(t0 * sr):int(t1 * sr)]
    ref = base[int(s["start"] * sr):int(s["end"] * sr)]
    line = line * float(10 ** (np.clip(lufs(ref, sr) - lufs(line, sr), -8, 8) / 20))
    nxt = old_words[i1 + 1]["start"] if i1 + 1 < len(old_words) else None
    cut_b = silence_near(base, sr, old_words[i1]["end"] + 0.08, 1)
    resume = cut_b if nxt is None else max(cut_b, min(nxt - gap, silence_near(base, sr, nxt - 0.03, -1)))
    fade = int(0.015 * sr)
    head = base[:int(cut_a * sr)].copy()
    tail = base[int(resume * sr):].copy()
    ramp = np.linspace(0, 1, fade, dtype=np.float32)
    if head.ndim == 2:
        ramp = ramp[:, None]
    if len(head) >= fade:
        head[-fade:] *= ramp[::-1]
    line[:fade] *= ramp
    line[-fade:] *= ramp[::-1]
    tail[:fade] *= ramp
    sf.write(wav, np.concatenate([head, line, tail]), sr)
    shift = cut_a + len(line) / sr - resume
    _write_splices(public_dir, [(cut_a, "before"), (cut_a + len(line) / sr, "after")], moved_after=cut_a, shift=shift,
                   replaced=(cut_a, resume))
    return round(shift, 3)


def pitch_track(a, sr, hop=0.01, win=0.04, fmin=60.0, fmax=400.0):
    """Fundamental frequency per `hop` seconds by autocorrelation, NaN where
    the frame is unvoiced (too quiet or no clear period). Enough to tell a
    line that falls at its end (a statement, or one question asked whole)
    from one that rises (a second question tacked on)."""
    mono = a if a.ndim == 1 else a.mean(axis=1)
    n, h = int(win * sr), int(hop * sr)
    lo, hi = int(sr / fmax), int(sr / fmin)
    peak = np.abs(mono).max() + 1e-12
    out = []
    for i in range(0, len(mono) - n, h):
        x = mono[i:i + n] - mono[i:i + n].mean()
        if np.sqrt(np.mean(x ** 2)) < peak * 0.02:
            out.append(np.nan)
            continue
        ac = np.correlate(x, x, mode="full")[n - 1:]
        lag = lo + int(np.argmax(ac[lo:hi]))
        out.append(sr / lag if ac[lag] > 0.3 * ac[0] else np.nan)
    return np.array(out)


def measure_span(wav, t0, t1, transcribe=True):
    """Numbers for choosing among several seeds of one line: its length,
    its pitch at the start and the end of its voiced part, the slope over
    its last 0.4 s (negative falls), and what a recogniser hears. Keep the
    take whose transcript reads as written (one question, not two), whose
    length suits the cut and whose pitch does what the sentence needs."""
    a, sr = sf.read(str(wav), dtype="float32")
    seg = a[int(t0 * sr):int(t1 * sr)]
    f0 = pitch_track(seg, sr)
    voiced = np.nonzero(~np.isnan(f0))[0]
    rep = {"seconds": round(t1 - t0, 2)}
    if len(voiced):
        rep["f0_start"] = round(float(np.nanmedian(f0[voiced[:10]])), 1)
        rep["f0_end"] = round(float(np.nanmedian(f0[voiced[-10:]])), 1)
        tail = voiced[voiced >= voiced[-1] - 40]
        if len(tail) >= 3:
            rep["end_slope_hz_per_s"] = round(float(np.polyfit(tail * 0.01, f0[tail], 1)[0]), 1)
    if transcribe:
        from faster_whisper import WhisperModel

        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            sf.write(f.name, seg, sr)
            model = WhisperModel(whisper_model(), device="cpu", compute_type="int8")
            segs, _ = model.transcribe(_pcm16k(f.name), beam_size=5)
            rep["heard"] = " ".join(s.text.strip() for s in segs)
    return rep


def make(episode, public_dir, seed=None):
    """Synthesise and align one episode; writes voice.wav and timeline.json.
    One request for the whole narration keeps its prosody whole."""
    public_dir = Path(public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)
    cfg = episode["voice"]
    provider = os.environ.get("VOICE_PROVIDER") or cfg.get("provider", "elevenlabs")
    say = readings(episode)
    text = spoken_text(episode["segments"], say)
    wav = public_dir / "voice.wav"
    words = script_words(episode["segments"])
    if provider == "elevenlabs" and os.environ.get("VOICE_REALIGN"):
        tokens = align_whisper(wav)
        meta = {"provider": "elevenlabs", "model": cfg.get("model", "eleven_v4"), "voice_id": cfg["voice_id"], "alignment": "whisper"}
    elif provider == "elevenlabs":
        tokens, chars = synth_elevenlabs(text, cfg, wav, seed=seed)
        meta = {"provider": "elevenlabs", "model": cfg.get("model", "eleven_v4"), "voice_id": cfg["voice_id"],
                "seed": seed if seed is not None else cfg.get("seed"), "characters": chars, "alignment": "synthesis"}
    elif provider == "kokoro":
        tokens = synth_kokoro(text, cfg, wav)
        meta = {"provider": "kokoro", "voice": cfg.get("kokoro_voice", "af_heart")}
    else:
        raise SystemExit(f"unknown voice provider {provider}")
    mapped, missing = map_to_script(words, tokens, say)
    timeline = build_timeline(mapped, wav)
    timeline["voice"] = dict(meta, unmatched_words=missing)
    (public_dir / "timeline.json").write_text(json.dumps(timeline, indent=1))
    return timeline


CLOSERS = "\"'”’)]"


def _end_mark(text):
    """The punctuation a word ends on, past any closing quote or bracket."""
    t = text.rstrip(CLOSERS)
    return t[-1] if t and t[-1] in PUNCT else ""


def _pause_kind(w, n):
    """What the pause between two words is: a section break (a new
    segment), a sentence end, a comma's pause, or none."""
    if w.get("seg") != n.get("seg"):
        return "section"
    mark = _end_mark(w["text"])
    if not mark:
        return None
    return "sentence" if mark in ".?!" else "comma"


def _syllables(word):
    """Syllables in an English word, by vowel groups with the usual
    corrections (a silent final "e", "-ed" after anything but t or d):
    not a dictionary count, but the same count for every episode, which
    is what comparing one take with another needs."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    if w.endswith("ed") and not w.endswith(("ted", "ded")) and n > 1:
        n -= 1
    return max(n, 1)


def spoken_syllables(text, say=None):
    """Syllables in one script word as the narrator reads it: a number or
    symbol through `say`, looked up as `spoken_text` looks it up ("65%"
    read "sixty-five percent" is five)."""
    core, _ = _core(text)
    return sum(_syllables(x) for x in re.split(r"[\s\-]+", (say or {}).get(core, core)))


# A gap between words longer than this is a pause, not speech.
PAUSE = 0.125
# Two forced alignments of the same words place their ends a few
# hundredths of a second apart, which moves the rate within speech by up to
# about 0.05 syllables a second: a take that close to the reference range
# is not faster or slower than it by anything the measure can tell.
SPEECH_NOISE = 0.05


def pace_measure(words, say=None):
    """The narration's pace, as the series is judged on it. Syllables a
    second over the whole narration (`syllables_per_s`, first word's start
    to last word's end) and within speech (`speech_syllables_per_s`, every
    pause over 0.125 s taken out), the shortest and the median sentence
    pause and section break, in seconds; and words a second, for planning
    a script's length. Syllables, not words, are the measure: a script of
    short words ("Dig straight down into the Earth") reads fast in words
    and not in syllables. Numbers count as read, through `say`."""
    span = words[-1]["end"] - words[0]["start"]
    syl = sum(spoken_syllables(w["text"], say) for w in words)
    gaps = {"sentence": [], "section": []}
    silent = 0.0
    for w, n in zip(words, words[1:]):
        gap = n["start"] - w["end"]
        # Over 0.125 s, not 0.12: forced alignment places words in 20 ms
        # steps, and gaps of exactly 0.12 s fell either side of a 0.12 line
        # by float rounding, moving one take's speech rate by 0.1 syllables
        # a second between two readings of the same timings.
        if gap > PAUSE:
            silent += gap
        kind = _pause_kind(w, n)
        if kind in gaps:
            gaps[kind].append(gap)

    def low(k):
        return round(min(gaps[k]), 2) if gaps[k] else None

    def mid(k):
        return round(float(np.median(gaps[k])), 2) if gaps[k] else None

    return {"words": len(words), "syllables": syl, "seconds": round(span, 2),
            "words_per_s": round(len(words) / span, 2),
            "syllables_per_s": round(syl / span, 2),
            "speech_syllables_per_s": round(syl / (span - silent), 2),
            "sentence_pause": low("sentence"), "sentence_pause_median": mid("sentence"),
            "section_pause": low("section"), "section_pause_median": mid("section")}


def pace_faults(m, limits=None):
    """Where a pace measure leaves the reference parts' range (brand.json
    `rhythm.limits`, written by `rhythm.py standard`), as readable lines;
    empty when it keeps it. The rate within speech may sit SPEECH_NOISE
    outside the range, the most two alignments of the same words differ
    by. A limit that is not set is not checked."""
    lim = limits or brand()["rhythm"]["limits"]
    out = []
    for key, label, noise in (("speech_syllables_per_s", "syllables/s within speech", SPEECH_NOISE),
                              ("syllables_per_s", "syllables/s overall", 0.0)):
        if key in lim:
            lo, hi = lim[key]
            if not lo - noise <= m[key] <= hi + noise:
                out.append(f"{m[key]} {label}, outside the reference parts' {lo} to {hi}"
                           + (f" (±{noise}, the alignment's own noise)" if noise else ""))
    for key, label in (("sentence_pause", "a sentence pause"), ("section_pause", "a section break")):
        floor = lim.get(key + "_min")
        if floor is not None and m[key] is not None and m[key] < floor:
            out.append(f"{label} of {m[key]} s, under the reference parts' shortest, {floor} s")
    return out


def pace_report(ep_dir):
    """This episode's pace beside every other episode that has a timeline,
    the reference parts (brand.json `rhythm.reference`) marked, so a take
    is judged against the series, not only against the limits. Only a real
    take is a reference: synthetic timings are marked."""
    from config import public_dir

    ref = {r if isinstance(r, str) else r["episode"] for r in brand().get("rhythm", {}).get("reference", [])}
    rows = []
    for d in sorted(EPISODES.glob("*/episode.json")):
        ep = json.loads(d.read_text())
        tl = public_dir(ep) / "timeline.json"
        if tl.exists():
            t = json.loads(tl.read_text())
            rows.append((d.parent.name, pace_measure(t["words"], readings(ep)), d.parent.resolve() == Path(ep_dir).resolve(),
                         t.get("voice", {}).get("provider", "")))
    for name, m, this, provider in rows:
        print(f"{'>' if this else ' '} {name:28} {m['speech_syllables_per_s']:5.2f} syl/s in speech  "
              f"{m['syllables_per_s']:5.2f} overall  {m['words_per_s']:5.2f} words/s  "
              f"sentence pause {m['sentence_pause']} s (median {m['sentence_pause_median']})  "
              f"section {m['section_pause']} s (median {m['section_pause_median']})"
              + ("  reference" if name in ref else "")
              + ("  (synthetic timings, not a reference)" if provider in ("synthetic", "kokoro") else ""))
    return rows


def pace_plan(words, tempo=1.0, sentence=0.5, section=0.6, comma=0.1):
    """The silences `pace` inserts, as (time in the slowed take, seconds):
    one at the middle of each pause that is short of its target after the
    slow-down (a sentence end to `sentence`, a section break to
    `section`, a comma's pause of 0.12 s or more by `comma`)."""
    k = 1 / tempo
    inserts = []
    for w, n in zip(words, words[1:]):
        gap = (n["start"] - w["end"]) * k
        kind = _pause_kind(w, n)
        if kind == "section":
            want = section
        elif kind == "sentence":
            want = sentence
        elif kind == "comma" and gap >= 0.12:
            want = gap + comma
        else:
            continue
        if want > gap + 0.01:
            inserts.append(((w["end"] + (n["start"] - w["end"]) / 2) * k, want - gap))
    return inserts


def paced_time(t, tempo, inserts):
    """Where a moment of the original take lands after `pace`: stretched by
    the slow-down, then moved by every silence inserted before it."""
    s = t / tempo
    return round(s + sum(e for at, e in inserts if at < s), 3)


def pace(public_dir, tempo=1.0, sentence=None, section=None, comma=0.1):
    """Brings a take to the series' rhythm by its pauses alone: each pause
    lengthened in its own silence (`pace_plan`), faded over 5 ms either
    side, so no word is touched or stretched. What goes in is noise at
    the level of the pause's quietest 20 ms (the take's room tone, about
    -88 dB; never over -80 dB, since a comma's short pause may hold the
    word's tail), not digital zero: zeros made the pitch tracker drop most
    of the voiced frames of a short sentence after a lengthened pause, and
    a tone gate read 4.35 semitones of movement against 4.56 for the same
    words (a pitch-kept slow-down was
    heard as unnatural; speed comes from choosing the take). A sentence end
    and a section break are brought up to the reference parts' typical
    pauses (brand.json `rhythm.pauses`, written by `rhythm.py standard`)
    unless `sentence` and `section` are given. The word timings, the
    segments' times, the take's length and its splice records move with the
    silence put in before them, so the words need no re-alignment: a forced
    alignment of a paced take placed the same words' ends differently and
    read the rate within speech 0.05 to 0.07 syllables a second faster with
    no word changed. The caller re-makes the music, since every later
    segment now starts later. Returns the new length in seconds."""
    # The words are never slowed: a 4 percent pitch-kept slow-down was heard
    # at once as unnatural. `tempo` stays for the planner's arithmetic only.
    if tempo != 1.0:
        raise SystemExit("the voice is never slowed in post; choose a slower take and lengthen its pauses")
    typical = brand().get("rhythm", {}).get("pauses", {})
    sentence = sentence if sentence is not None else typical.get("sentence", 0.5)
    section = section if section is not None else typical.get("section", 0.6)
    public_dir = Path(public_dir)
    wav = public_dir / "voice.wav"
    tl = json.loads((public_dir / "timeline.json").read_text())
    a, sr = sf.read(wav, dtype="float32")
    inserts = pace_plan(tl["words"], tempo, sentence, section, comma)
    fade = int(0.005 * sr)

    def ramp(n, up):
        r = np.linspace(0, 1, n, dtype=np.float32) if up else np.linspace(1, 0, n, dtype=np.float32)
        return r[:, None] if a.ndim == 2 else r

    win = int(0.02 * sr)
    rng = np.random.default_rng(0)
    ends = [w["end"] / tempo for w in tl["words"]]
    starts = [w["start"] / tempo for w in tl["words"]]

    def room(t):
        g0 = max([e for e in ends if e <= t], default=t)
        g1 = min([b for b in starts if b >= t], default=t)
        g = a[int(g0 * sr):int(g1 * sr)]
        levels = [float(np.sqrt(np.mean(g[j:j + win] ** 2))) for j in range(0, len(g) - win + 1, win // 2)]
        return min(levels + [10 ** (-80 / 20)])

    out, last = [], 0
    for t, extra in inserts:
        i = int(t * sr)
        seg = a[last:i].copy()
        if len(seg) > fade:
            seg[-fade:] *= ramp(fade, False)
        out += [seg, (rng.standard_normal((int(extra * sr),) + a.shape[1:]) * room(t)).astype(np.float32)]
        a[i:i + fade] *= ramp(len(a[i:i + fade]), True)
        last = i
    out.append(a[last:])
    sf.write(wav, np.concatenate(out), sr)
    moved = lambda t: paced_time(t, tempo, inserts)  # noqa: E731
    tl["voice"]["splices"] = [dict(x, t=moved(x["t"])) for x in tl["voice"].get("splices", [])]
    for w in tl["words"]:
        w["start"], w["end"] = moved(w["start"]), moved(w["end"])
    for seg in tl.get("segments", {}).values():
        seg["start"], seg["end"] = moved(seg["start"]), moved(seg["end"])
    tl["duration"] = round(sum(len(x) for x in out) / sr, 3)
    tl["voice"]["paced"] = {"tempo": tempo, "sentence": sentence, "section": section, "comma": comma}
    (public_dir / "timeline.json").write_text(json.dumps(tl, indent=1))
    return round(sum(len(x) for x in out) / sr, 3)


USAGE = """usage:
  python pipeline/voice.py measure  <voice.wav> <start s> <end s>
  python pipeline/voice.py replace  episodes/<id> <seg> <first> <last> [seed]
  python pipeline/voice.py add-line episodes/<id> <seg> [seed]
  python pipeline/voice.py pace-report episodes/<id>
  python pipeline/voice.py pace     episodes/<id>
Then run build.py <ep> realign after replace or add-line; after pace the word timings are moved, not re-aligned,
and the music is re-made. Copy voice.wav and timeline.json aside
first when trying several seeds. Other steps run through pipeline/build.py."""


def _episode(ep_dir):
    from config import public_dir

    ep = json.loads((Path(ep_dir) / "episode.json").read_text())
    return ep, public_dir(ep)


if __name__ == "__main__":
    import sys

    a = sys.argv[1:]
    if len(a) >= 4 and a[0] == "measure":
        print(json.dumps(measure_span(a[1], float(a[2]), float(a[3])), indent=1))
    elif len(a) >= 5 and a[0] == "replace":
        ep, pub = _episode(a[1])
        seed = int(a[5]) if len(a) > 5 else None
        print("shift", replace_words(ep, pub, a[2], int(a[3]), int(a[4]), seed=seed), "s; now run build.py <ep> realign")
    elif len(a) >= 3 and a[0] == "add-line":
        ep, pub = _episode(a[1])
        seg = next(s for s in ep["segments"] if s["id"] == a[2])
        add_line(ep, pub, seg, seed=int(a[3]) if len(a) > 3 else None)
        print("added", a[2], "; now run build.py <ep> realign")
    elif len(a) >= 2 and a[0] == "pace-report":
        pace_report(a[1])
    elif len(a) >= 2 and a[0] == "pace":
        ep, pub = _episode(a[1])
        before = pace_measure(json.loads((pub / "timeline.json").read_text())["words"], readings(ep))
        print("before", before)
        print("length", pace(pub), "s, the word timings moved with the silence; now pace-report and re-make the music")
    else:
        raise SystemExit(USAGE)
