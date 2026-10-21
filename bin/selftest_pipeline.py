# Copyright 2026 The video-editing-skill authors. Licensed under the Apache
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
# Needs numpy, soundfile and Pillow (toolkit/requirements.txt). No network,
# no ffmpeg, no API key. Writes only inside a temporary directory.

import json
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit" / "pipeline"))

import config  # noqa: E402
import covercheck  # noqa: E402
import mix  # noqa: E402
import music  # noqa: E402
import publish  # noqa: E402
import qa  # noqa: E402
import recue  # noqa: E402
import scaffold  # noqa: E402
import voice  # noqa: E402

SR = 48000
RNG = np.random.default_rng(7)
passed = failed = 0


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
    return publish.text_problems(md, "reel", cfg=CFG)


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


case("a caption that mentions how it was made fails", t_ai)


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
        out = scaffold.episode("07-shipping-containers", "Why are shipping containers all one size?")
        spec = json.loads((out / "episode.json").read_text())
        assert spec["number"] == 7 and spec["composition"] == "Ep07" and spec["id"] == "07-shipping-containers"
        for f in ("music-plan.json", "research.md", "verification.md", "picture-audit.md"):
            assert (out / f).exists(), f
        assert "{{" not in (out / "verification.md").read_text()
        rel = scaffold.release("09-reel-shipping-containers", "07-shipping-containers")
        assert json.loads((rel / "release.json").read_text())["cover"] == "covers/cover-07.png"


case("the scaffold writes every file of an episode and a release, placeholders filled", t_scaffold)

# ---------------------------------------------------------------- brand
print("brand.json: the geometry every check relies on")


def t_brand():
    s, t, lay = CFG["safe"], CFG["tile"], CFG["layout"]
    assert 0 < s["left"] < s["right"] < 1080 and 0 < s["top"] < s["bottom"] < 1920
    assert s["left"] <= s["railX"] <= s["right"] and s["top"] < s["railY"] < s["bottom"]
    assert t["top"] == 240 and t["bottom"] == 1680, "the grid tile is the middle 3:4 of a 9:16 cover"
    assert s["top"] <= lay["badge"] < lay["top"] < lay["captions"] < s["bottom"]


case("the safe box, grid tile and layout are consistent", t_brand)

print(f"PY {passed} {failed}")
sys.exit(1 if failed else 0)
