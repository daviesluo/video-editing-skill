"""Build an episode end to end, or one step of it.

    python pipeline/build.py episodes/<id> [step]

Steps, in order (`all` runs voice, realign, mix, render, mux, qa):
  voice     one synthesis request for the whole narration
            (studio/public/episodes/<id>/voice.wav and timeline.json)
  realign   re-time the committed take by forced alignment, audio unchanged
  captions  copy caption_keep and caption_split into the timeline
  mix       voice, sound effects and music to out/mix.wav
  render    the picture, muted, to out/video.mp4 (no GPU: --gl=swangle)
  mux       picture and mix to out/final.mp4
  qa        every automated check, out/qa.json and out/contact-sheet.png
  remux     audio-only change: the new mix onto the picture of an existing
            final.mp4 (out/final.mp4 is replaced; the old one is kept as
            out/final-prev.mp4)

Commit the shipping voice.wav (git add -f) and timeline.json, so a
re-render never needs a new voice request and every frame can be traced
to a commit.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import mix  # noqa: E402
import qa  # noqa: E402
import voice  # noqa: E402
from config import STUDIO, public_dir  # noqa: E402

RENDER_FLAGS = ["--gl=swangle", "--concurrency=2", "--codec=h264", "--crf=16", "--x264-preset=slow",
                "--pixel-format=yuv420p", "--color-space=bt709", "--muted"]


def load(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    episode = json.loads((ep_dir / "episode.json").read_text())
    out = ep_dir / "out"
    out.mkdir(exist_ok=True)
    return episode, public_dir(episode), out, ep_dir


def step_render(episode, out):
    # The composition reads the timeline itself (calculateMetadata), so the
    # props only pin what the mix also used: the lead-in and the tail.
    props = json.dumps({"id": episode["id"], "lead": episode.get("audio_lead", 0.0),
                        "tail": episode.get("tail", 1.2), "qa": False})
    subprocess.run(["npx", "remotion", "render", episode["composition"], str(out / "video.mp4"), *RENDER_FLAGS,
                    f"--props={props}"], cwd=STUDIO, check=True)


def step_mux(out, video=None):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video or out / "video.mp4"), "-i", str(out / "mix.wav"),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                    "-movflags", "+faststart", "-shortest", str(out / "final.mp4")], check=True)


def step_remux(out):
    """Only the music or the effects changed (code, voice and timeline the
    same as the render): keep the rendered picture, stream-copied, and lay
    the new mix under it. Saves a full render."""
    prev = out / "final-prev.mp4"
    shutil.copy(out / "final.mp4", prev)
    step_mux(out, video=prev)


def keep_phrases(episode, public):
    """Copies episode.json's `caption_keep` (phrases a caption page must not
    split, such as "a new one" or "Reno, Nevada") and `caption_split`
    (hyphenated words the captions may break after the hyphen) into
    timeline.json, where the captions read them."""
    path = public / "timeline.json"
    tl = json.loads(path.read_text())
    tl["keep"] = episode.get("caption_keep", [])
    tl["split"] = episode.get("caption_split", [])
    path.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")


def main(ep_dir, step="all"):
    episode, public, out, ep_dir = load(ep_dir)
    steps = ["voice", "realign", "mix", "render", "mux", "qa"] if step == "all" else [step]
    timeline = None
    if "voice" in steps:
        timeline = voice.make(episode, public)
        print("voice:", timeline["voice"], f"{timeline['duration']} s")
    if "realign" in steps and episode["voice"].get("provider", "elevenlabs") == "elevenlabs":
        shift = sorted(abs(d) for d in voice.realign(episode, public))
        timeline = None
        print(f"realign: {len(shift)} words, start moved median {shift[len(shift) // 2] * 1000:.0f} ms, "
              f"max {shift[-1] * 1000:.0f} ms")
    if "voice" in steps or "realign" in steps or step == "captions":
        keep_phrases(episode, public)
    if step == "captions":
        print("captions: keep", episode.get("caption_keep", []))
        return
    timeline = timeline or json.loads((public / "timeline.json").read_text())
    if "mix" in steps or step == "remux":
        print("mix:", mix.build(episode, timeline, public / "voice.wav", out / "mix.wav", out / "work"))
    if "render" in steps:
        step_render(episode, out)
    if "mux" in steps:
        step_mux(out)
    if step == "remux":
        step_remux(out)
        steps.append("qa")
    if "qa" in steps:
        report = qa.run(episode, timeline, out / "final.mp4", out, ep_dir)
        for c in report["checks"]:
            print(("PASS " if c["pass"] else "FAIL ") + c["check"], c["value"] if not c["pass"] else "")
        print("QA", "PASSED" if report["passed"] else "FAILED")
        if not report["passed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
