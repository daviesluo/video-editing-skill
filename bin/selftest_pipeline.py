# Copyright 2026 Zheng Luo (Davies Luo). Licensed under the Apache
# License 2.0, whose text is the LICENSE file in this package.
#
# Unit tests for the pipeline's pure functions, on signals and texts whose
# right answer is known by construction: a hiss placed at 1.00 s must be
# found at 1.00 s, a cover drawn off centre must fail the balance rule, a
# straight apostrophe must be refused. Run by bin/selftest.sh, which counts
# the "ok" and "FAIL" lines; it can also run alone:
#
#   python bin/selftest_pipeline.py
#
# Needs numpy, soundfile and Pillow (toolkit/requirements.txt), and librosa
# for the narrator's tone, whose cases are reported as skipped without it.
# No network, no ffmpeg, no API key. Writes only inside a temporary
# directory.

import json
import math
import re
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit" / "pipeline"))

import build  # noqa: E402
import config  # noqa: E402
import covercheck  # noqa: E402
import mix  # noqa: E402
import music  # noqa: E402
import publish  # noqa: E402
import qa  # noqa: E402
import recue  # noqa: E402
import rhythm  # noqa: E402
import scaffold  # noqa: E402
import voice  # noqa: E402
import voicestyle  # noqa: E402

SR = 48000
RNG = np.random.default_rng(7)
passed = failed = skipped = 0
try:
    import librosa  # noqa: F401
    LIBROSA = True
except ImportError:
    LIBROSA = False


def skip(label, why):
    global skipped
    skipped += 1
    print(f"  skip {label}: {why}")


def case(label, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  ok   {label}")
    except Exception as e:  # noqa: BLE001
        failed += 1
        msg = str(e) or e.__class__.__name__
        print(f"  FAIL {label}: {msg}")
        if not isinstance(e, AssertionError):
            traceback.print_exc(limit=2)


def tone(dur, f=150.0, amp=0.3):
    t = np.arange(int(dur * SR)) / SR
    env = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 0.5
    return (amp * np.sin(2 * np.pi * f * t) * env).astype(np.float32)


def hiss(dur, amp=0.2):
    """White noise high-passed above 4 kHz: an s, f or z."""
    x = RNG.standard_normal(int(dur * SR))
    spec = np.fft.rfft(x)
    spec[np.fft.rfftfreq(len(x), 1 / SR) < 4000] = 0
    y = np.fft.irfft(spec, len(x))
    return (amp * y / np.abs(y).max()).astype(np.float32)


def place(a, t, clip):
    i = int(t * SR)
    a[i:i + len(clip)] += clip[: len(a) - i]


# ---------------------------------------------------------------- voice
print("voice: script readings, alignment mapping and re-voicing guards")


def t_spoken():
    segs = [{"id": "a", "text": "It is 2,688 kilometres."}, {"id": "b", "text": "[curious] Why 87%?"}]
    say = {"2,688": "two thousand six hundred and eighty-eight", "87%": "eighty-seven per cent"}
    got = voice.spoken_text(segs, say)
    assert got == "It is two thousand six hundred and eighty-eight kilometres. [curious] Why eighty-seven per cent?", got
    words = voice.script_words(segs)
    assert [w["text"] for w in words] == ["It", "is", "2,688", "kilometres.", "Why", "87%?"], words


case("spoken text carries the readings, captions keep the script and drop audio tags", t_spoken)


def t_accent():
    ep = {"voice": {"accent": "american"}, "say": {"british": {"2001": "two thousand and one"}, "american": {"2001": "two thousand one"}}}
    assert config.readings(ep) == {"2001": "two thousand one"}
    ep["voice"]["accent"] = "british"
    assert config.readings(ep) == {"2001": "two thousand and one"}


case("readings follow the narrator's accent", t_accent)


def t_map():
    words = [{"text": "About", "seg": "a"}, {"text": "2,688", "seg": "a"}, {"text": "km.", "seg": "a"}]
    say = {"2,688": "two thousand six hundred and eighty-eight"}
    toks = [{"text": t, "start": i * 0.2, "end": i * 0.2 + 0.15} for i, t in
            enumerate("About two thousand six hundred and eighty-eight km .".split())]
    out, missing = voice.map_to_script(words, toks, say)
    assert missing == 0, missing
    assert out[1]["start"] == 0.2 and out[1]["end"] == round(6 * 0.2 + 0.15, 3), out[1]
    assert out[2]["start"] == 1.4, out[2]


case("a spelled-out number's tokens time its one caption word", t_map)


def t_map_missing():
    words = [{"text": w, "seg": "a"} for w in "one two three".split()]
    toks = [{"text": "one", "start": 0.0, "end": 0.2}, {"text": "three", "start": 1.0, "end": 1.2}]
    out, missing = voice.map_to_script(words, toks)
    assert missing == 1
    assert 0.2 <= out[1]["start"] < out[1]["end"] <= 1.0, out[1]


case("an unmatched word is placed between its neighbours and counted", t_map_missing)


def take_with_hiss(prev_text, prev_end, hiss_from, word_at):
    a = np.zeros(int(2.0 * SR), np.float32)
    place(a, 0.2, tone(prev_end - 0.2))
    place(a, hiss_from, hiss(word_at - hiss_from))
    place(a, word_at, tone(0.35))
    words = [{"text": prev_text, "seg": "a", "start": 0.2, "end": prev_end}, {"text": "So", "seg": "a", "start": word_at, "end": word_at + 0.35}]
    return a, words


def t_fricative():
    a, words = take_with_hiss("away,", 0.5, 1.00, 1.15)
    moved = voice.fricative_onsets(words, a, SR)
    assert moved == [1], moved
    assert abs(words[1]["start"] - 1.00) <= 0.02, words[1]["start"]


case("a word starting with a hiss after a pause starts at its hiss, not its vowel", t_fricative)


def t_fricative_runon():
    a, words = take_with_hiss("straight", 0.95, 0.95, 1.15)
    voice.fricative_onsets(words, a, SR)
    assert words[1]["start"] == 1.15, words[1]["start"]


case("a hiss running on from a word that ends in a burst stays with that word", t_fricative_runon)


def t_fricative_reading():
    a, words = take_with_hiss("away,", 0.5, 1.00, 1.15)
    words[1]["text"] = "65%"
    w2 = [dict(w) for w in words]
    voice.fricative_onsets(words, a, SR)
    assert words[1]["start"] == 1.15, "judged by the written digits, it must stay"
    voice.fricative_onsets(w2, a, SR, say={"65%": "sixty-five per cent"})
    assert abs(w2[1]["start"] - 1.00) <= 0.02, w2[1]["start"]


case("a word is judged by how it is read: 65% reads sixty-five", t_fricative_reading)


def t_speech_span():
    line = np.zeros(int(1.6 * SR), np.float32)
    place(line, 0.1, tone(0.7))
    place(line, 1.2, tone(0.1, f=220))
    t0, t1 = voice.speech_span(line, SR)
    assert t0 < 0.12 and 0.8 < t1 < 1.0, (t0, t1)


case("a short burst after the line (the next line's first sound) is cut off", t_speech_span)


def t_silence_near():
    a = np.zeros(int(2.0 * SR), np.float32)
    place(a, 0.3, tone(0.3))
    place(a, 0.9, hiss(0.1))
    place(a, 1.0, tone(0.4))
    cut = voice.silence_near(a, SR, 1.0 - 0.03, -1)
    assert 0.6 < cut < 0.9, cut


case("a splice is cut in true silence, before the hiss the aligner missed", t_silence_near)


def t_splices():
    tl = {"voice": {"splices": [{"t": 1.0, "kept": "after"}, {"t": 2.5, "kept": "before"}, {"t": 4.0, "kept": "before"}]}}
    voice.record_splices(tl, [(2.0, "before"), (2.8, "after")], moved_after=2.0, shift=0.3, replaced=(2.0, 3.0))
    assert [x["t"] for x in tl["voice"]["splices"]] == [1.0, 2.0, 2.8, 4.3], tl


case("splice records inside a replaced span are dropped, later ones move", t_splices)


def paced_words():
    # Two segments; a sentence end with a 0.3 s pause, a comma with 0.2 s,
    # unpunctuated words 0.1 s apart,
    # a quoted sentence end ("word.”") with 0.4 s, and a section break of 0.5 s.
    spec = [("One", "a", 0.0, 0.3), ("two.", "a", 0.4, 0.7), ("Three,", "a", 1.0, 1.4), ("four", "a", 1.6, 1.9),
            ("“five.”", "a", 2.0, 2.3), ("Six", "a", 2.7, 3.0), ("seven.", "a", 3.1, 3.5), ("Eight", "b", 4.0, 4.3)]
    return [{"text": t, "seg": g, "start": s, "end": e} for t, g, s, e in spec]


def t_syllables():
    for word, n in (("Earth", 1), ("straight", 1), ("ocean", 2), ("little", 2), ("Antarctica", 4), ("named", 1),
                    ("wanted", 2), ("make", 1), ("the", 1), ("—", 0)):
        assert voice._syllables(word) == n, (word, voice._syllables(word), n)
    say = {"65%": "sixty-five percent"}
    assert voice.spoken_syllables("65%,", say) == 5 and voice.spoken_syllables("“Earth.”") == 1


case("syllables are counted by vowel groups, a number as it is read", t_syllables)


def t_pace_measure():
    w = paced_words()
    m = voice.pace_measure(w)
    # One two three four five six seven eight: 1+1+1+1+1+1+2+1 = 9.
    assert m["syllables"] == 9 and m["words_per_s"] == round(8 / 4.3, 2), m
    assert m["syllables_per_s"] == round(9 / 4.3, 2), m
    # Pauses over 0.12 s (0.3, 0.2, 0.4 and 0.5) come out of speech; the
    # 0.1 s gaps between words stay in it.
    assert m["speech_syllables_per_s"] == round(9 / (4.3 - 1.4), 2), m
    assert m["sentence_pause"] == 0.3 and m["section_pause"] == 0.5, m
    assert m["sentence_pause_median"] == 0.35, m
    # A short word read long counts as read.
    w[0]["text"] = "1,000"
    assert voice.pace_measure(w, {"1,000": "one thousand"})["syllables"] == 11
    lim = {"speech_syllables_per_s": [3.0, 3.4], "syllables_per_s": [2.2, 2.4], "sentence_pause_min": 0.4,
           "section_pause_min": 0.45}
    faults = voice.pace_faults(m, lim)
    assert len(faults) == 2 and "overall" in faults[0] and "sentence pause" in faults[1], faults
    ok = dict(m, speech_syllables_per_s=3.3, syllables_per_s=2.3, sentence_pause=0.42, section_pause=None)
    assert voice.pace_faults(ok, lim) == [], voice.pace_faults(ok, lim)
    # A limit that is not set is not checked.
    assert voice.pace_faults(m, {"syllables_per_s": [2.0, 2.2]}) == []


case("the pace is read in syllables, per sentence and section, past a closing quote", t_pace_measure)


def t_pace_plan():
    w = paced_words()
    tempo = 0.96
    ins = voice.pace_plan(w, tempo, sentence=0.78, section=0.92, comma=0.1)
    k = 1 / tempo
    want = {round((0.7 + 0.15) * k, 4): 0.78 - 0.3 * k, round((1.4 + 0.1) * k, 4): 0.1,
            round((2.3 + 0.2) * k, 4): 0.78 - 0.4 * k, round((3.5 + 0.25) * k, 4): 0.92 - 0.5 * k}
    got = {round(t, 4): e for t, e in ins}
    assert got.keys() == want.keys(), (sorted(got), sorted(want))
    for t in want:
        assert abs(got[t] - want[t]) < 1e-9, (t, got[t], want[t])
    # Every pause reaches its target in the paced take.
    def at(t):
        return voice.paced_time(t, tempo, ins)
    assert abs((at(1.0) - at(0.7)) - 0.78) < 0.002 and abs((at(4.0) - at(3.5)) - 0.92) < 0.002
    assert abs((at(1.6) - at(1.4)) - (0.2 * k + 0.1)) < 0.002
    # A pause between unpunctuated words gets nothing; a slow-down is
    # refused.
    assert all(abs(t - 0.35 * k) > 0.01 and abs(t - 3.05 * k) > 0.01 for t in got)
    try:
        voice.pace(Path("/nonexistent"), tempo=0.9)
        raise AssertionError("a slow-down was accepted")
    except SystemExit:
        pass


case("pace lengthens each short pause to its target, in its own silence, and never slows the words", t_pace_plan)


def t_pace_splices():
    tempo = 0.96
    ins = [(1.0, 0.5), (3.0, 0.25)]
    # A splice record before every insert is only stretched; one after both
    # moves by the stretch and both silences.
    assert voice.paced_time(0.48, tempo, ins) == round(0.5, 3)
    assert voice.paced_time(2.4, tempo, ins) == round(2.5 + 0.5, 3)
    assert voice.paced_time(3.84, tempo, ins) == round(4.0 + 0.75, 3)


case("pace moves the take's splice records with the stretch and every silence before them", t_pace_splices)


def grid_words(offset_steps=0):
    """Words timed as forced alignment times them, in 20 ms steps, most of
    them 0.12 s apart, two sentence ends 0.5 s long; the whole take starting
    `offset_steps` steps later."""
    lens = [11, 14, 9, 17, 12, 10, 15, 13, 9, 16, 12, 11]
    gaps = [6, 6, 25, 6, 6, 6, 3, 6, 25, 6, 6]
    out, k = [], 10 + offset_steps
    for i, n in enumerate(lens):
        out.append({"text": "word." if i in (2, 8) else "word", "seg": "a",
                    "start": round(k * 0.02, 3), "end": round((k + n) * 0.02, 3)})
        k += n + (gaps[i] if i < len(gaps) else 0)
    return out


def t_pace_grid():
    # Gaps of exactly 0.12 s are speech, wherever the take starts: on a
    # 0.12 line they fell either side by float rounding, and the same
    # timings shifted by whole steps read 3.41 to 3.95 syllables a second.
    reads = {voice.pace_measure(grid_words(j))["speech_syllables_per_s"] for j in range(0, 200, 7)}
    span = (sum([11, 14, 9, 17, 12, 10, 15, 13, 9, 16, 12, 11]) + sum([6, 6, 25, 6, 6, 6, 3, 6, 25, 6, 6])) * 0.02
    assert reads == {round(12 / (span - 1.0), 2)}, reads


case("a pause is a gap over 0.125 s, so 0.12 s gaps on the 20 ms grid read the same every time", t_pace_grid)


def t_pace_moves_words():
    with tempfile.TemporaryDirectory() as d:
        pub = Path(d)
        w = paced_words()
        a = np.zeros(int(4.6 * SR), np.float32)
        for x in w:
            place(a, x["start"], tone(x["end"] - x["start"]))
        sf.write(pub / "voice.wav", a, SR)
        segs = {"a": {"start": 0.0, "end": 3.5, "first": 0, "last": 6}, "b": {"start": 4.0, "end": 4.3, "first": 7, "last": 7}}
        tl = {"duration": 4.6, "words": w, "segments": segs, "voice": {"splices": [{"t": 3.75, "kept": "before"}]}}
        (pub / "timeline.json").write_text(json.dumps(tl))
        before = voice.pace_measure(w)
        ins = voice.pace_plan(w, 1.0, 0.78, 0.92, 0.1)
        length = voice.pace(pub, 1.0, sentence=0.78, section=0.92, comma=0.1)
        out = json.loads((pub / "timeline.json").read_text())
        b, sr = sf.read(pub / "voice.wav", dtype="float32")
        # Every word, segment and splice moved by the silence put in before
        # it, and the length is the new audio's.
        assert [(x["start"], x["end"]) for x in out["words"]] == \
            [(voice.paced_time(x["start"], 1.0, ins), voice.paced_time(x["end"], 1.0, ins)) for x in w], out["words"]
        assert out["segments"]["b"]["start"] == voice.paced_time(4.0, 1.0, ins) and out["voice"]["splices"][0]["t"] > 3.75
        assert out["duration"] == length == round(len(b) / sr, 3)
        # The moved timings still sit on the words' sound: each word is
        # loud inside its new span and the paused take is silent between.
        for x, n in zip(out["words"], out["words"][1:]):
            mid = b[int((x["start"] + 0.1) * sr):int((x["end"] - 0.1) * sr)]
            gap = b[int((x["end"] + 0.03) * sr):int((n["start"] - 0.03) * sr)]
            assert np.abs(mid).max() > 0.1 and (len(gap) == 0 or np.abs(gap).max() < 1e-3), x
        # Only pauses grew: the rate within speech is the same, overall slower.
        after = voice.pace_measure(out["words"])
        assert after["speech_syllables_per_s"] == before["speech_syllables_per_s"], (before, after)
        assert after["syllables_per_s"] < before["syllables_per_s"] and after["sentence_pause"] == 0.78, after


case("pace moves the word timings with the silence it puts in, so the paced take needs no re-alignment", t_pace_moves_words)


def t_join():
    assert build.check_parts([(0, 1011, 1012), (1012, 1623, 612)]) == 1624
    assert build.check_parts([(1012, 1623, 612), (0, 1011, 1012)]) == 1624
    for bad in ([(0, 1011, 1012), (1013, 1623, 611)],   # a frame missing at the seam
                [(0, 1011, 1012), (1000, 1623, 624)],   # overlapping parts
                [(0, 1011, 1010), (1012, 1623, 612)],   # a part short of frames
                [(5, 1011, 1007)],                       # not from frame 0
                []):
        try:
            build.check_parts(bad)
            raise AssertionError(f"accepted {bad}")
        except SystemExit:
            pass
    # Parts that meet but stop short of the composition's end (a range
    # briefed one frame short) are refused once the total is known.
    assert build.check_parts([(0, 1011, 1012), (1012, 1623, 612)], 1624) == 1624
    try:
        build.check_parts([(0, 1011, 1012), (1012, 1622, 611)], 1624)
        raise AssertionError("accepted parts one frame short of the composition")
    except SystemExit:
        pass
    tl = {"lead": 0.3, "duration": 52.2, "tail": 1.4}
    assert build.composition_frames(tl) == math.ceil((0.3 + 52.2 + 1.4) * config.brand()["frame"]["fps"])


case("join refuses parts that do not meet end to end, are short of frames, or stop short of the composition", t_join)


def chirp(f0, f1, dur=1.0):
    t = np.arange(int(dur * SR)) / SR
    f = f0 + (f1 - f0) * t / dur
    return (0.3 * np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32)


def t_pitch():
    with tempfile.TemporaryDirectory() as d:
        for f0, f1, sign in ((120, 240, 1), (240, 120, -1)):
            p = Path(d) / "c.wav"
            sf.write(p, chirp(f0, f1), SR)
            rep = voice.measure_span(p, 0.0, 1.0, transcribe=False)
            assert np.sign(rep["end_slope_hz_per_s"]) == sign, rep
            assert abs(rep["f0_start"] - f0) < 15 and abs(rep["f0_end"] - f1) < 20, rep


case("the pitch measure tells a rising ending from a falling one", t_pitch)

# ---------------------------------------------------------------- qa
print("qa: stray sounds, splices, clicks, transcript and the fact log")


def clean_take():
    a = np.zeros(int(3.0 * SR), np.float32)
    words = []
    for i, t in enumerate((0.3, 1.0, 1.8)):
        place(a, t, tone(0.4))
        words.append({"text": f"w{i}", "seg": "a", "start": t, "end": t + 0.4})
    return a, {"words": words, "voice": {"splices": []}}


def t_clean():
    a, tl = clean_take()
    assert qa.voice_flaws(a, SR, tl) == [], qa.voice_flaws(a, SR, tl)


case("a clean take has no flaws", t_clean)


def t_stray():
    a, tl = clean_take()
    place(a, 2.6, tone(0.1, f=200))
    out = qa.voice_flaws(a, SR, tl)
    assert any(o.startswith("stray sound 2.6") for o in out), out


case("a sound on no word is reported (the kept 'fo' of a next line)", t_stray)


def t_splice_cut():
    a, tl = clean_take()
    tl["voice"]["splices"] = [{"t": 1.2, "kept": "before"}]
    out = qa.voice_flaws(a, SR, tl)
    assert any("splice at 1.20 s cuts into sound" in o for o in out), out


case("a splice whose kept side is not silent is reported", t_splice_cut)


def t_click():
    a, tl = clean_take()
    a[int(1.6 * SR)] = 0.02
    out = qa.voice_flaws(a, SR, tl)
    assert any(o.startswith("click at 1.6") for o in out), out


case("a click in a pause is reported", t_click)


def t_wer():
    script = "It is 2,688 kilometres from the centre, about 87% of it."
    heard = "It is 2688 kilometers from the center, about 87 percent of it."
    wer, diffs = qa.word_errors(script, heard)
    assert wer == 0, diffs
    wer, diffs = qa.word_errors(script, heard.replace("center", "cellar"))
    assert diffs == [{"script": "center", "heard": "cellar"}], diffs


case("the transcript check reads British spelling and units alike, and lists a real error", t_wer)


def t_facts_logged():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "verification.md"
        p.write_text("| F01 | claim | source | Confirmed |\n")
        ep = {"facts": [{"id": "F01"}, {"id": "F02"}]}
        assert qa.facts_logged(ep, p) == ["F02"]


case("a fact with no row in verification.md is reported", t_facts_logged)

# ---------------------------------------------------------------- mix
print("mix: word cues and the sound-effect plan")
TL = {"duration": 10.0, "words": [{"text": w, "seg": s, "start": t, "end": t + 0.3} for w, s, t in
                                  (("Dig", "hook", 0.0), ("down.", "hook", 0.5), ("Where", "next", 2.0), ("now?", "next", 2.5))],
      "segments": {"hook": {"start": 0.0, "end": 0.8, "first": 0, "last": 1}, "next": {"start": 2.0, "end": 2.8, "first": 2, "last": 3}}}


def t_cues():
    assert mix.cue_time(TL, "next") == 2.0
    assert mix.cue_time(TL, "next@1") == 2.5
    assert mix.cue_time(TL, "hook$") == 0.8
    for bad in ("hook@2", "nope", "hook@"):
        try:
            mix.cue_time(TL, bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad} was accepted")


case("cues resolve by word, and a stale or unknown cue is refused", t_cues)


def t_sfx():
    ep = {"sfx": [{"cue": "hook", "name": "pop"}, {"cue": "hook@1", "name": "pop"}]}
    assert any("twice within" in p for p in mix.sfx_problems(ep, TL, takes={"pop": 1}))
    assert not any("twice within" in p for p in mix.sfx_problems(ep, TL, takes={"pop": 3}))
    dense = {"sfx": [{"cue": "hook", "name": f"e{i}"} for i in range(9)]}
    assert any("effects in" in p for p in mix.sfx_problems(dense, TL, takes={}))


case("the same sample back to back, and effects packed like a template, are flagged", t_sfx)

# ---------------------------------------------------------------- music
print("music: holes, the held ending and chunk edges")


def bed(dur=20.0):
    t = np.arange(int(dur * 44100)) / 44100
    return (0.1 * np.sin(2 * np.pi * 220 * t) * (1 + 0.2 * np.sin(2 * np.pi * 1.5 * t))).astype(np.float32)


def t_holes():
    x = bed()
    assert music.hole_db(x, 44100) > -3, music.hole_db(x, 44100)
    x[int(6 * 44100):int(9.5 * 44100)] *= 0.01
    assert music.hole_db(x, 44100) < -10, music.hole_db(x, 44100)


case("a bed that drops out for 3 s fails the hole test; a steady one passes", t_holes)


def t_hold():
    x = bed()
    assert music.hold_db(x, 44100, 15.0, 18.0) > -3
    x[int(15.5 * 44100):] *= 0.02
    assert music.hold_db(x, 44100, 15.0, 18.0) < -12


case("a bed cut off under the last words fails the hold test", t_hold)


def t_edges():
    tl = {"duration": 30.0, "segments": {"hook": {"start": 0.1}, "mid": {"start": 11.08}, "end": {"start": 24.0}}}
    assert music.chunk_edges(tl, ["hook", "mid", "end"], 3.5) == [0.0, 11.08, 24.0, 33.5]


case("chunk boundaries sit on segment starts and the last runs tail_s past the voice", t_edges)

# ---------------------------------------------------------------- recue
print("recue: cues follow their words after a wording change")


def t_recue():
    old = "Only about 800 square kilometres has land, almost all in Montana.".split()
    new = "Only about 800 km² has land, almost all in Montana.".split()
    m, moved = recue.mapping(old, new)
    assert m[10] == 9 and new[9] == "Montana.", (m, new)
    assert 3 in moved and 4 in moved
    src = 'cue("usa@10"); cue("usa@2"); cue("other@10")'
    assert recue.rewrite(src, "usa", m) == 'cue("usa@9"); cue("usa@2"); cue("other@10")'


case("a cue on 'Montana' moves from @10 to @9 when two words become one", t_recue)


def t_recue_quotes():
    m, _ = recue.mapping("Dig down now".split(), "Dig straight down now".split())
    assert recue.rewrite("at('hook@2'); at(\"hook@2\")", "hook", m) == "at('hook@3'); at(\"hook@3\")"


case("cues in single or double quotes are both moved", t_recue_quotes)

# ---------------------------------------------------------------- covers
print("covercheck: the cover design in the 3:4 grid tile")
CFG = config.brand()


def cover(d, title, subject):
    img = Image.new("RGB", (1080, 1920), CFG["palette"]["ink"])
    dr = ImageDraw.Draw(img)
    dr.rectangle(subject, fill=CFG["palette"]["accent"])
    png = Path(d) / "cover-01.png"
    img.save(png)
    png.with_suffix(".json").write_text(json.dumps({"title": title, "subject": subject}))
    return covercheck.problems(png, png.with_suffix(".json"), CFG)


def t_cover_ok():
    with tempfile.TemporaryDirectory() as d:
        assert cover(d, [100, 300, 700, 600], [300, 1000, 780, 1200]) == []


case("a subject centred in the tile under the title passes", t_cover_ok)


def t_cover_bunched():
    with tempfile.TemporaryDirectory() as d:
        out = cover(d, [100, 300, 700, 600], [300, 640, 780, 840])
        assert any("off centre" in p for p in out), out


case("a subject bunched under the title with an empty bottom fails", t_cover_bunched)


def t_cover_unsafe():
    with tempfile.TemporaryDirectory() as d:
        out = cover(d, [60, 300, 990, 600], [300, 1000, 780, 1200])
        assert any("outside the safe band" in p for p in out), out
        out = cover(d, [100, 200, 700, 600], [300, 1000, 780, 1200])
        assert any("outside the grid tile" in p for p in out), out


case("a title outside the safe band or the tile fails", t_cover_unsafe)


def t_cover_under():
    with tempfile.TemporaryDirectory() as d:
        out = cover(d, [100, 300, 700, 600], [300, 580, 780, 1200])
        assert any("under the title" in p for p in out), out


case("a subject that starts under the title fails", t_cover_under)

# ---------------------------------------------------------------- publish
print("publish: the release text lint")
GOOD = """# Release

## Caption

```text
Why do borders zigzag where rivers run?

Rivers move, and the treaties that followed them did not. The line stays where the water was.

Which border near you follows a river?

Sources: Natural Earth; national survey agencies.

#maps #geography #worldmap
```

## Pinned comment

```text
Part 2 is next: why do some countries have two capitals? Follow so it’s in your feed.
```

## Settings

- AI label: on.
- Audio name: "Why borders zigzag, Series"

## Hashtag checks

| Tag | Shown | Carry | Top posts | Used |
|---|---|---|---|---|
| #maps | 10M | 4 of 12 | map explainers | yes |
| #geography | 12M | 12 of 12 | explainers | yes |
| #worldmap | 2M | 6 of 12 | map explainers | yes |
"""


def lint(md):
    return publish.text_problems(md, cfg=CFG)


def t_good():
    assert lint(GOOD) == [], lint(GOOD)


case("a release text that keeps every rule passes", t_good)


def t_quotes():
    out = lint(GOOD.replace("it’s", "it's"))
    assert any("straight apostrophe" in p for p in out), out
    out = lint(GOOD.replace("it’s", "it‘s"))
    assert any("opening quote mark" in p for p in out), out


case("a straight apostrophe or an opening quote used as one is refused", t_quotes)


def t_audio():
    out = lint(GOOD.replace('"Why borders zigzag, Series"', '"' + "x" * 51 + '"'))
    assert any("audio name is 51" in p for p in out), out


case("an audio name over 50 characters is refused", t_audio)


def t_question():
    out = lint(GOOD.replace("Which border near you follows a river?", "Tell us which border follows a river."))
    assert any("not a question" in p for p in out), out


case("a caption whose last paragraph before the sources asks nothing fails", t_question)


def t_ai():
    out = lint(GOOD.replace("Rivers move", "Made with AI tools. Rivers move"))
    assert any("how it was made" in p for p in out), out


case("a caption that says how it was made fails", t_ai)


def t_ai_topics():
    for ok in ("Rivers move, and the revenue generated by tolls moved with them.",
               "Rivers move, and an AI company's filing says so.",
               "Rivers move, and machine learning maps them now."):
        out = lint(GOOD.replace("Rivers move, and the treaties that followed them did not.", ok))
        assert not any("how it was made" in p for p in out), (ok, out)
    for bad in ("Narrated by AI.", "An AI voice reads it.", "Voiced with text-to-speech."):
        out = lint(GOOD.replace("Rivers move", bad + " Rivers move"))
        assert any("how it was made" in p for p in out), (bad, out)


case("a caption about AI, or revenue generated, passes; one about how it was made fails", t_ai_topics)


def t_tags():
    out = lint(GOOD.replace("#worldmap\n```", "#worldmap #cartography\n```"))
    assert any("#cartography has no row" in p for p in out), out
    out = lint(GOOD.replace("#worldmap\n```", "#worldmap #a #b #c\n```"))
    assert any("6 hashtags" in p for p in out), out


case("an unchecked hashtag, or more than five, fails", t_tags)


def t_pin_label():
    out = lint(GOOD.replace("Follow so it’s in your feed.", "Stay tuned."))
    assert any("does not invite a follow" in p for p in out), out
    out = lint(GOOD.replace("- AI label: on.\n", ""))
    assert any("AI label: on" in p for p in out), out


case("a pinned comment without a follow, or no AI label setting, fails", t_pin_label)


def t_shortcode():
    ms = 1_760_000_000_000
    media_id = ((ms - publish.ID_EPOCH_MS) << 23) | 4242
    code = ""
    while media_id:
        media_id, r = divmod(media_id, 64)
        code = publish.ALPHABET[r] + code
    assert publish.shortcode_ms(f"https://www.instagram.com/reel/{code}/") == ms


case("a post's time is read back out of its shortcode", t_shortcode)

# ---------------------------------------------------------------- scaffold
print("scaffold: a new episode and release from the templates")


def t_scaffold():
    import contextlib
    import io

    with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
        scaffold.EPISODES, scaffold.WAITING = Path(d) / "episodes", Path(d) / "releases" / "to-post"
        scaffold.SCENES = Path(d) / "scenes"
        scaffold.SCENES.mkdir()
        out = scaffold.episode("07-shipping-containers", "Why are shipping containers all one size?")
        spec = json.loads((out / "episode.json").read_text())
        assert spec["number"] == 7 and spec["composition"] == "Ep07" and spec["id"] == "07-shipping-containers"
        for f in ("music-plan.json", "research.md", "verification.md", "picture-audit.md"):
            assert (out / f).exists(), f
        assert "{{" not in (out / "verification.md").read_text()
        scene = (scaffold.SCENES / "Ep07.tsx").read_text()
        assert "export const Ep07" in scene and "part={7}" in scene and "part={8}" in scene
        assert not re.search(r"\{\{[A-Z]+\}\}", scene), "a placeholder left in the scene"
        rel = scaffold.release("09-reel-shipping-containers", "07-shipping-containers")
        assert json.loads((rel / "release.json").read_text())["cover"] == "covers/cover-07.png"


case("the scaffold writes every file of an episode and a release, placeholders filled", t_scaffold)

# ---------------------------------------------------------------- rhythm
print("rhythm: the picture's movement and the reference parts' range")


def band_frames(moves, seconds=10, fps=30):
    """Grey frames, 192x108, of a still picture in which a bright square
    in the picture band travels 2 px a frame during each (first frame, last
    frame) in `moves`, while a caption below the band changes every third
    of a second."""
    n = seconds * fps + 1
    f = np.full((n, 192, 108), 128, np.uint8)
    x = 10
    for i in range(n):
        if any(a < i <= b for a, b in moves):
            x += 2
        f[i, 90:110, x % 80:x % 80 + 20] = 250
        if (i // 10) % 2:
            f[i, 165:180, 20:90] = 30
    return f


def t_motion():
    m = rhythm.motion(band_frames([(60, 90), (180, 195)]), 30)
    # Moves of 1.0 and 0.5 s in 10 s, holds of 2.0, 3.0 and 3.5 s; the
    # caption below the band is not the picture.
    assert m == {"moving_share": 0.15, "moves_per_10s": 2.0, "median_move_s": 0.75, "median_hold_s": 3.0}, m
    assert rhythm.motion(band_frames([]), 30)["moves_per_10s"] == 0.0
    # A one-frame flash in the middle of a hold is no movement anyone sees:
    # it neither counts nor cuts the hold in two (counted, the median hold
    # read 1.72 s for 3.0).
    flash = band_frames([(60, 90), (180, 195)])
    flash[135, 100:114, 60:74] = 250
    assert rhythm.motion(flash, 30) == m, rhythm.motion(flash, 30)
    # Four moves in 3 s, each on its word, with a third of a second
    # between them: no busier in moving share, but too many moves and no
    # hold to read.
    quick = [(30 + k * 22, 42 + k * 22) for k in range(4)]
    m = rhythm.motion(band_frames(quick), 30)
    assert m["moves_per_10s"] == 4.0 and m["median_hold_s"] < 0.5 and m["moving_share"] < 0.183, m
    lim = CFG["rhythm"]["limits"]
    v = {"speech_syllables_per_s": 5.0, "syllables_per_s": 3.7, "sentence_pause": 0.45, "section_pause": 0.6}
    out = rhythm.faults({"voice": v, "picture": m}, lim)
    assert len(out) == 2 and "movements per 10 s" in out[0] and "median hold" in out[1], out


case("the picture band's movements and holds are counted, the captions left out", t_motion)


def t_motion_listing():
    tl = {"lead": 0.3, "words": [{"text": "Dig", "start": 1.6}, {"text": "down", "start": 5.7}]}
    rows = rhythm.listing(band_frames([(60, 90), (180, 195)]), 30, tl)
    # The two movements and the three holds the measure counted, in order,
    # each with the word being spoken as it starts.
    kinds = [r.split()[0] for r in rows]
    assert kinds == ["hold", "move", "hold", "move", "hold"], rows
    assert '"Dig"' in rows[1] and '"down"' in rows[3] and "before the first word" in rows[0], rows


case("the picture measure lists every movement and hold it counted, with its word", t_motion_listing)


def t_rhythm_faults():
    lim = CFG["rhythm"]["limits"]
    # A part that felt rushed beside its reference parts, as measured: the
    # speech rate and all three picture measures out.
    rushed = {"voice": {"speech_syllables_per_s": 5.22, "syllables_per_s": 3.7, "sentence_pause": 0.45, "section_pause": None},
              "picture": {"moving_share": 0.29, "moves_per_10s": 2.81, "median_move_s": 0.6, "median_hold_s": 2.03}}
    out = rhythm.faults(rushed, lim)
    assert len(out) == 4 and "within speech" in out[0], out
    within = {"voice": {"speech_syllables_per_s": 5.0, "syllables_per_s": 3.7, "sentence_pause": 0.45, "section_pause": 0.6},
              "picture": {"moving_share": 0.15, "moves_per_10s": 1.5, "median_move_s": 1.2, "median_hold_s": 2.6}}
    assert rhythm.faults(within, lim) == [], rhythm.faults(within, lim)
    # Within speech, a take up to 0.05 outside the range is inside the
    # alignment's own noise; one past it is not.
    hi = lim["speech_syllables_per_s"][1]
    near = dict(within, voice=dict(within["voice"], speech_syllables_per_s=round(hi + 0.04, 2)))
    past = dict(within, voice=dict(within["voice"], speech_syllables_per_s=round(hi + 0.06, 2)))
    assert rhythm.faults(near, lim) == [] and len(rhythm.faults(past, lim)) == 1, (rhythm.faults(near, lim), rhythm.faults(past, lim))


case("a rushed part leaves the reference range on every measure; one inside it passes", t_rhythm_faults)


def t_limits_from():
    def row(speech, overall, pause, med, sec, sec_med, share, moves, hold):
        return {"voice": {"speech_syllables_per_s": speech, "syllables_per_s": overall, "sentence_pause": pause,
                          "sentence_pause_median": med, "section_pause": sec, "section_pause_median": sec_med},
                "picture": {"moving_share": share, "moves_per_10s": moves, "median_hold_s": hold}}
    rows = {"01": row(4.9, 3.6, 0.42, 0.5, 0.55, 0.6, 0.15, 1.6, 2.5),
            "02": row(5.1, 3.8, 0.40, 0.52, 0.5, 0.62, 0.18, 1.9, 2.3),
            "03": row(5.0, 3.7, 0.45, 0.48, 0.6, 0.58, 0.12, 1.2, 3.1)}
    lim, pauses = rhythm.limits_from(rows)
    assert lim == {"speech_syllables_per_s": [4.9, 5.1], "syllables_per_s": [3.6, 3.8], "sentence_pause_min": 0.40,
                   "moving_share_max": 0.18, "moves_per_10s_max": 1.9, "median_hold_s_min": 2.3,
                   "section_pause_min": 0.5}, lim
    assert pauses == {"sentence": 0.5, "section": 0.6}, pauses
    # Every reference part is inside the limits drawn from them.
    assert all(rhythm.faults(r, lim) == [] for r in rows.values())


case("the limits are the reference parts' own range, and every one of them is inside it", t_limits_from)


def t_standard_brand():
    text = (config.ROOT / "brand.json").read_text()
    assert rhythm.dump_brand(json.loads(text)) == text, "standard would rewrite brand.json beyond what it measured"
    with tempfile.TemporaryDirectory() as d:
        b = Path(d) / "brand.json"
        b.write_text(text)
        try:
            rhythm.standard(b)
            raise AssertionError("a standard with no reference parts was written")
        except SystemExit:
            pass
        assert b.read_text() == text


case("standard keeps brand.json as written and refuses to run with no reference parts", t_standard_brand)

# ---------------------------------------------------------------- tone
print("voicestyle: the narrator's tone against the reference parts")


def spoken(f, dur, amp):
    """A voiced word: a harmonic tone at `f` Hz, faded over 20 ms."""
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * k * f * t) / k for k in range(1, 9))
    return (amp * x * np.minimum(1, np.minimum(t, dur - t) / 0.02) / 2.7).astype(np.float32)


def tone_take(d, name, pitches, amps):
    """A take of four-word sentences, each word 0.3 s at its pitch and
    level, 0.1 s between words and 0.5 s between sentences; its path and
    word timings."""
    words, clips, t = [], [], 0.2
    for ps, am in zip(pitches, amps):
        for i, (f, amp) in enumerate(zip(ps, am)):
            words.append({"text": "word." if i == len(ps) - 1 else "word", "seg": "a", "start": round(t, 3), "end": round(t + 0.3, 3)})
            clips.append((t, spoken(f, 0.3, amp)))
            t += 0.3 + (0.5 if i == len(ps) - 1 else 0.1)
    a = np.zeros(int((t + 0.3) * SR), np.float32)
    for s, c in clips:
        place(a, s, c)
    path = Path(d) / f"{name}.wav"
    sf.write(path, a, SR)
    return path, words


PITCHES = [[130, 150, 175, 140], [125, 145, 160, 135], [135, 160, 150, 128], [130, 140, 170, 138]]
LEVELS = [[0.3, 0.25, 0.33, 0.27]] * 4


def semis(f):
    return 12 * np.log2(np.array(f) / 100.0)


def t_tone_measure():
    with tempfile.TemporaryDirectory() as d:
        m = voicestyle.measure(*tone_take(d, "ref", PITCHES, LEVELS), (60, 320))
    # As constructed: the median word pitch, each sentence's spread of
    # pitch, the spread of the words' levels.
    assert abs(m["pitch_median_hz"] - 140) < 1.5, m
    assert abs(m["pitch_movement_st"] - np.mean([np.std(semis(s)) for s in PITCHES])) < 0.2, m
    assert abs(m["hook_movement_st"] - np.std(semis(PITCHES[0]))) < 0.3, m
    assert abs(m["loudness_sd_db"] - np.std(20 * np.log10(sum(LEVELS, [])))) < 0.2, m


def t_tone_faults():
    with tempfile.TemporaryDirectory() as d:
        def take(name, pitches, levels):
            return voicestyle.measure(*tone_take(d, name, pitches, levels), (60, 320))
        # Three reference parts, a little apart in pitch and level.
        refs = {"r1": take("r1", PITCHES, LEVELS),
                "r2": take("r2", [[f * 1.02 for f in s] for s in PITCHES], LEVELS),
                "r3": take("r3", PITCHES, [[x * 1.05 for x in LEVELS[0]]] + LEVELS[1:])}
        lim = voicestyle.limits_from(refs)
        assert all(voicestyle.faults(r, lim, {}) == [] for r in refs.values())
        # A take that keeps the pace but opens 4.4 dB quieter (a listless
        # first sentence) fails on the hook's level.
        quiet = take("quiet", PITCHES, [[x * 0.6 for x in LEVELS[0]]] + LEVELS[1:])
        out = voicestyle.faults(quiet, lim, {})
        assert any("hook's level" in x for x in out), out
        # A flat opening line fails on the hook's pitch movement; a take a
        # semitone low, on its pitch.
        flat = voicestyle.faults(take("flat", [[150] * 4] + PITCHES[1:], LEVELS), lim, {})
        assert any("hook's pitch movement" in x for x in flat), flat
        low = voicestyle.faults(take("low", [[f * 0.94 for f in s] for s in PITCHES], LEVELS), lim, {})
        assert any(x.startswith("pitch median") for x in low), low
    # No standard written is a fault, never a pass.
    assert voicestyle.faults(refs["r1"], {}, {}) and "no tone standard" in voicestyle.faults(refs["r1"], {}, {})[0]


def t_tone_brand():
    tone = CFG["voice_tone"]
    assert set(tone["tolerance"]) <= set(tone["limits"]) == set(voicestyle.LABELS), tone
    assert all(lo <= hi for lo, hi in tone["limits"].values()) and tone["pitch_hz"][0] < tone["pitch_hz"][1]
    with tempfile.TemporaryDirectory() as d:
        b = Path(d) / "brand.json"
        text = (config.ROOT / "brand.json").read_text()
        b.write_text(text)
        try:
            voicestyle.standard(b)
            raise AssertionError("a tone standard with no reference parts was written")
        except SystemExit:
            pass
        assert b.read_text() == text


TONE = [("the tone is measured as constructed: pitch, its movement within sentences, the words' levels", t_tone_measure),
        ("a quiet opening fails on the hook's level, a flat one on its pitch, a low take on the median", t_tone_faults)]
for label, fn in TONE:
    if LIBROSA:
        case(label, fn)
    else:
        skip(label, "librosa is not installed (pip install -r toolkit/requirements.txt)")
case("brand.json's tone limits are consistent, and standard refuses with no reference parts", t_tone_brand)

# ---------------------------------------------------------------- brand
print("brand.json: the geometry every check relies on")


def t_brand():
    s, t, lay = CFG["safe"], CFG["tile"], CFG["layout"]
    assert 0 < s["left"] < s["right"] < 1080 and 0 < s["top"] < s["bottom"] < 1920
    assert s["left"] <= s["railX"] <= s["right"] and s["top"] < s["railY"] < s["bottom"]
    assert t["top"] == 240 and t["bottom"] == 1680, "the grid tile is the middle 3:4 of a 9:16 cover"
    assert s["top"] <= lay["badge"] < lay["top"] < lay["captions"] < s["bottom"]
    r = CFG["rhythm"]
    lo, hi = r["band"]
    assert lay["top"] / 1920 < lo < hi < lay["captions"] / 1920, "the picture band lies between the headline and the captions"
    for k in ("speech_syllables_per_s", "syllables_per_s"):
        assert r["limits"][k][0] <= r["limits"][k][1], k


case("the safe box, grid tile, layout and picture band are consistent", t_brand)

print(f"PY {passed} {failed} {skipped}")
sys.exit(1 if failed else 0)
