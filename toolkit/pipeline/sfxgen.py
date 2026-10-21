"""Builds the sound-effect library in pipeline/sfx-lib/ with ElevenLabs
sound generation: several takes of each effect, so a cue that repeats in an
episode never plays the identical sample twice in a row.

    .venv/bin/python pipeline/sfxgen.py            # make what is missing
    .venv/bin/python pipeline/sfxgen.py --force    # remake everything

Each take is trimmed of leading silence, faded out, peak-normalised to
-3 dBFS and stored as 48 kHz mono WAV. Generate on a plan whose terms allow
commercial use of the output, and record the plan and date in the
episode's licence notes. The prompts below are the house set: soft,
close, dry and short, so the effects sit under the voice. Add your own
effects here rather than downloading clips of unknown licence.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voice import eleven  # noqa: E402

RATE = 48000
from config import SFX_LIB as OUT  # noqa: E402

# name: (prompt, seconds generated, seconds kept, takes)
EFFECTS = {
    "whoosh": ("Soft airy cinematic whoosh as a camera glides past, smooth and close, no music, no impact", 1.0, 0.9, 4),
    "tick": ("A single soft tick of a pencil tapping paper on a wooden desk, dry and close", 0.5, 0.18, 4),
    "pop": ("A small soft wooden click, like a pin pushed into cork, warm and subtle, dry", 0.5, 0.25, 4),
    "thud": ("A deep soft cinematic low boom with a short warm tail, subtle, no rumble at the end", 1.2, 1.0, 3),
    # A riser is an effect under a reveal, never part of the music bed.
    "riser": ("A subtle airy tension riser that swells for a second and a half and stops, no hit at the end", 1.6, 1.5, 2),
}


def make(name, prompt, gen_s, keep_s, take, api, auth):
    r = requests.post(
        f"{api}/sound-generation",
        params={"output_format": "mp3_44100_192"},
        headers={**auth, "Content-Type": "application/json"},
        json={"text": prompt, "duration_seconds": gen_s, "prompt_influence": 0.55},
        timeout=180,
    )
    if not r.ok:
        raise SystemExit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
        tmp.write(r.content)
        tmp.flush()
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", tmp.name, "-f", "f32le", "-ac", "1", "-ar", str(RATE), "-"],
                             capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    above = np.nonzero(np.abs(x) > 0.02 * np.abs(x).max())[0]
    x = x[max(0, above[0] - int(0.005 * RATE)):] if len(above) else x
    x = x[: int(keep_s * RATE)]
    fade = min(len(x), int(0.08 * RATE))
    x[-fade:] *= np.linspace(1, 0, fade) ** 2
    x *= 10 ** (-3 / 20) / (np.abs(x).max() + 1e-9)
    sf.write(OUT / f"{name}-{take}.wav", x, RATE, subtype="PCM_16")


def main(force=False):
    OUT.mkdir(exist_ok=True)
    api, auth = eleven()
    for name, (prompt, gen_s, keep_s, takes) in EFFECTS.items():
        for take in range(1, takes + 1):
            if force or not (OUT / f"{name}-{take}.wav").exists():
                make(name, prompt, gen_s, keep_s, take, api, auth)
                print("made", name, take, flush=True)


if __name__ == "__main__":
    main("--force" in sys.argv)
