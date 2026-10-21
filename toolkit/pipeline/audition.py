"""Renders one passage in several ElevenLabs voices, so the person who
commissions the series can pick the narrator by ear.

    python pipeline/audition.py <out_dir> <voice_id>:<label> [...] [--text "<passage>"]

Each take is loudness-matched to -16 LUFS, so the choice is about the
voice, not the level, and the same seed is used for every voice. Use a
passage from the series itself, with a number, a name and a question in
it: those are where synthetic voices give themselves away. Writes
<label>.mp3 and takes.json.
"""

import json
import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voice import eleven  # noqa: E402

PASSAGE = ("Picture 1,248 towns on one page. Now shrink the page by half. "
           "Where does the line fall, and why does almost everyone guess wrong?")


def take(api, auth, voice_id, out, passage, model, seed):
    r = requests.post(f"{api}/text-to-speech/{voice_id}", params={"output_format": "mp3_44100_128"},
                      headers={**auth, "Content-Type": "application/json"},
                      json={"text": passage, "model_id": model, "language_code": "en", "seed": seed,
                            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}, timeout=180)
    if not r.ok:
        return {"error": f"{r.status_code} {r.text[:300]}"}
    raw = out.with_suffix(".raw.mp3")
    raw.write_bytes(r.content)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-b:a", "192k", str(out)], check=True)
    raw.unlink()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                               capture_output=True, text=True, check=True).stdout)
    return {"seconds": round(dur, 2), "words_per_minute": round(len(passage.split()) / dur * 60)}


def main(argv):
    passage = PASSAGE
    if "--text" in argv:
        i = argv.index("--text")
        passage = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    out_dir, *voices = argv
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    api, auth = eleven()
    model, seed = "eleven_v4", 104
    takes = {}
    for v in voices:
        voice_id, _, label = v.partition(":")
        takes[label] = {"voice_id": voice_id, **take(api, auth, voice_id, out_dir / f"{label}.mp3", passage, model, seed)}
        print(label, takes[label])
    (out_dir / "takes.json").write_text(json.dumps({"passage": passage, "model": model, "seed": seed, "takes": takes}, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
