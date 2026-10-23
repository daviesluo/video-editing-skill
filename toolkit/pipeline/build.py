"""Build an episode end to end, or one step of it.

    python pipeline/build.py episodes/<id> [step]

Steps, in order (`all` runs voice, realign, mix, render, mux, qa):
  voice     one synthesis request for the whole narration
            (studio/public/episodes/<id>/voice.wav and timeline.json)
  realign   re-time the committed take by forced alignment, audio unchanged
  captions  copy caption_keep and caption_split into the timeline
  mix       voice, sound effects and music to out/mix.wav
  render    the picture, muted, to out/video.mp4 (no GPU: --gl=swangle);
            RENDER_FRAMES=a-b renders frames a to b only, to out/video-a-b.mp4
  join      the parts rendered with RENDER_FRAMES into out/video.mp4,
            stream-copied, once their frame counts are checked to meet
            and to add up to the composition's length
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
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import mix  # noqa: E402
import qa  # noqa: E402
import voice  # noqa: E402
from config import STUDIO, brand, public_dir, readings  # noqa: E402

RENDER_FLAGS = ["--gl=swangle", "--concurrency=2", "--codec=h264", "--crf=16", "--x264-preset=slow",
                "--pixel-format=yuv420p", "--color-space=bt709", "--muted"]


def load(ep_dir):
    ep_dir = Path(ep_dir).resolve()
    episode = json.loads((ep_dir / "episode.json").read_text())
    out = ep_dir / "out"
    out.mkdir(exist_ok=True)
    return episode, public_dir(episode), out, ep_dir


def render_range():
    """RENDER_FRAMES=a-b, as (a, b), or None for the whole episode."""
    frames = os.environ.get("RENDER_FRAMES")
    if not frames:
        return None
    m = re.fullmatch(r"(\d+)-(\d+)", frames)
    if not m or int(m[1]) > int(m[2]):
        raise SystemExit(f"RENDER_FRAMES={frames}: give the first and last frame, such as 0-1012")
    return int(m[1]), int(m[2])


def step_render(episode, out, public):
    # The voice's pace is measured against the reference parts before the
    # render is spent; QA gates it again with the picture's rhythm.
    m = voice.pace_measure(json.loads((public / "timeline.json").read_text())["words"], readings(episode))
    slow = voice.pace_faults(m)
    print("pace:", m, ("; OUTSIDE THE REFERENCE PARTS' PACE: " + "; ".join(slow)) if slow else "")
    # The composition reads the timeline itself (calculateMetadata), so the
    # props only pin what the mix also used: the lead-in and the tail.
    props = json.dumps({"id": episode["id"], "lead": episode.get("audio_lead", 0.0),
                        "tail": episode.get("tail", 1.2), "qa": False})
    # A frame range renders one part, so two helpers can each render half an
    # episode at the same commit and `join` puts them together. Every frame
    # depends on its number alone, so the parts are the frames a whole
    # render makes.
    rng = render_range()
    target = out / (f"video-{rng[0]}-{rng[1]}.mp4" if rng else "video.mp4")
    subprocess.run(["npx", "remotion", "render", episode["composition"], str(target), *RENDER_FLAGS,
                    f"--props={props}"] + ([f"--frames={rng[0]}-{rng[1]}"] if rng else []), cwd=STUDIO, check=True)


def check_parts(parts, total=None):
    """Checks that rendered parts, as (first frame, last frame, frames in
    the file), meet end to end: the first starts at frame 0, each later one
    the frame after the last ended, each file holds every frame of its
    range, and, given the composition's `total`, the last ends on its last
    frame. Returns the frame count of the whole."""
    if not parts:
        raise SystemExit("join: no parts (out/video-<a>-<b>.mp4); render them with RENDER_FRAMES=a-b")
    nxt = 0
    for a, b, n in sorted(parts):
        if a != nxt or n != b - a + 1:
            raise SystemExit(f"join: the part for frames {a}-{b} has {n} frames from {a}; expected {b - a + 1} from {nxt}")
        nxt = b + 1
    if total is not None and nxt != total:
        raise SystemExit(f"join: the parts hold frames 0-{nxt - 1}; the composition has {total} frames (0-{total - 1})")
    return nxt


def composition_frames(timeline):
    """The episode composition's length in frames, as the studio works it
    out (lib/episode.ts): lead-in, narration and tail, rounded up."""
    fps = brand()["frame"]["fps"]
    return math.ceil((timeline.get("lead", 0.0) + timeline["duration"] + timeline.get("tail", 0.0)) * fps)


def step_join(out, total=None):
    """Joins the parts rendered with RENDER_FRAMES into out/video.mp4 in
    frame order, without re-encoding, after `check_parts`. Prints the seam
    frames, which are looked at either side before the join is trusted."""
    files = {}
    for p in out.glob("video-*-*.mp4"):
        m = re.fullmatch(r"video-(\d+)-(\d+)", p.stem)
        if m:
            files[(int(m[1]), int(m[2]))] = p
    parts = []
    for (a, b), p in sorted(files.items()):
        n = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout
        parts.append((a, b, int(n)))
    total = check_parts(parts, total)
    lst = out / "parts.txt"
    lst.write_text("".join(f"file '{files[(a, b)].name}'\n" for a, b, _ in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst.name, "-c", "copy", "video.mp4"],
                   check=True, cwd=out)
    lst.unlink()
    seams = [b for _, b, _ in parts[:-1]]
    print(f"join: {len(parts)} parts, {total} frames; check frames {', '.join(f'{s} and {s + 1}' for s in seams)}")


def frame_count(video):
    """The number of video frames in a file, counted from its packets, and
    its frame rate."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                        "-show_entries", "stream=nb_read_packets,avg_frame_rate", "-of", "json", str(video)],
                       capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]
    num, den = (int(x) for x in s["avg_frame_rate"].split("/"))
    return int(s["nb_read_packets"]), num / den


def step_mux(out, video=None):
    # Every rendered frame is kept: the mix is padded or trimmed to exactly
    # the picture's length (`-shortest` with a stream copy cut the last one
    # to four frames).
    video = video or out / "video.mp4"
    frames, fps = frame_count(video)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(out / "mix.wav"),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", "apad", "-t", f"{frames / fps:.6f}",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(out / "final.mp4")],
                   check=True)
    got, _ = frame_count(out / "final.mp4")
    if got != frames:
        raise SystemExit(f"mux: final.mp4 has {got} frames, the render {frames}")


def step_remux(out):
    """Only the music or the effects changed (code, voice and timeline the
    same as the render): keep the rendered picture, stream-copied, and lay
    the new mix under it. Saves a full render."""
    prev = out / "final-prev.mp4"
    shutil.copy(out / "final.mp4", prev)
    step_mux(out, video=prev)


def keep_phrases(episode, public):
    """Copies episode.json's `caption_keep` (phrases a caption page must not
    split, such as "a new one" or "Reno, Nevada"), `caption_split`
    (hyphenated words the captions may break after the hyphen), and the
    lead-in and tail into timeline.json, where the studio reads them."""
    path = public / "timeline.json"
    tl = json.loads(path.read_text())
    tl["keep"] = episode.get("caption_keep", [])
    tl["split"] = episode.get("caption_split", [])
    # The lead-in and tail too, so stills and covers time the picture
    # exactly as the render does.
    tl["lead"] = episode.get("audio_lead", 0.0)
    tl["tail"] = episode.get("tail", 1.2)
    path.write_text(json.dumps(tl, indent=1, ensure_ascii=False) + "\n")


STEPS = ("all", "voice", "realign", "captions", "mix", "render", "join", "mux", "qa", "remux")


def main(ep_dir, step="all"):
    if step not in STEPS:
        raise SystemExit(f"unknown step {step!r}; the steps are {', '.join(STEPS)}")
    if render_range() and step != "render":
        raise SystemExit("RENDER_FRAMES renders one part, with the render step alone; then join, mux and qa")
    episode, public, out, ep_dir = load(ep_dir)
    steps = ["voice", "realign", "mix", "render", "mux", "qa"] if step == "all" else [step]
    timeline = None
    if "voice" in steps:
        timeline = voice.make(episode, public)
        print("voice:", timeline["voice"], f"{timeline['duration']} s")
    if "realign" in steps and episode["voice"].get("provider", "elevenlabs") == "elevenlabs":
        moved = voice.realign(episode, public)
        timeline = None
        if moved is None:
            print("realign: the word count changed, so no per-word shift is reported")
        else:
            shift = sorted(abs(d) for d in moved)
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
        step_render(episode, out, public)
    if step == "join":
        step_join(out, composition_frames(timeline))
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
