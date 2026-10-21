"""Stages releases: one folder per release, holding exactly what is posted,
at full quality, so what is pasted is what was reviewed.

    python pipeline/publish.py stage <release> <commit rendered from>
    python pipeline/publish.py text  <release>
    python pipeline/publish.py check <release>
    python pipeline/publish.py done  <release> <YYYY-MM-DD> <post url>
    python pipeline/publish.py when  <post url or shortcode>

A release waits in releases/to-post/<release>/ until the owner approves and
posts it; `done` then moves it to releases/posted/<YYYY-MM-DD>-<release>/
and records the date and link. Nothing is posted without the owner's
approval.

Each release folder holds release.json, naming its source:

    {"type": "reel", "source": "episodes/01-slug", "cover": "covers/cover-01.png"}
    {"type": "carousel", "source": "carousels/01-slug", "slides": 7}

and post.md (templates/release/post.md), the single home of the text to
post: fenced ```text blocks under the headings below, then the settings,
the checklist, the reasons for each choice and the hashtag check table.

`stage` copies the media in (a reel's final.mp4 and cover; a carousel's
slides), records for a reel the commit its video was rendered from and the
video's SHA-256, writes the .txt files from post.md and runs `check`.
`check` lints the text against the rules in references/14-release-and-
publishing.md and each platform's limits, and the cover against the cover
design. `when` reads a post's time out of its shortcode, for the read-back.
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from config import LIVE, ROOT, WAITING, brand

BLOCKS = {
    "Caption": "caption.txt",
    "Pinned comment": "pinned-comment.txt",
    "Alt text": "alt-text.txt",
    "Series-link comment": "series-link-comment.txt",
    "TikTok caption": "tiktok-caption.txt",
    "TikTok title": "tiktok-title.txt",
    "YouTube title": "youtube-title.txt",
    "YouTube description": "youtube-description.txt",
    "Short replies": "replies.txt",
    "TikTok and YouTube pinned comment": "pinned-comment-tiktok-youtube.txt",
}
# Platform limits as read in October 2026 (references/14-release-and-
# publishing.md cites the pages): TikTok captions 4,000 characters,
# photo-post titles 90, comment replies 150; YouTube titles 100 and
# descriptions 5,000, with no < or >.
MAX_TIKTOK_CAPTION = 4000
MAX_TIKTOK_TITLE = 90
MAX_YT_TITLE = 100
MAX_YT_DESCRIPTION = 5000
# Typographic tells and ornaments the text never uses.
BANNED = {"·": "middle dot", "—": "em dash", "–": "en dash", "→": "arrow", "←": "arrow", "->": "arrow"}
# The text never mentions how the video was made; the platform's own label
# setting does the disclosure.
NO_AI = re.compile(r"\bA\.?I\b|artificial intelligence|machine.learning|generated", re.I)
# Apostrophes are typed as ’ (U+2019). On the way from a pack to the app a
# straight ' became an opening quote ‘ in about half the words of two live
# captions ("world‘s", "It‘s"); a ’ arrives untouched.
QUOTES = {"'": "straight apostrophe ('), write ’", "‘": "opening quote mark (‘) used as an apostrophe, write ’"}
TAG = re.compile(r"(?<!\w)#\w+")


def release_dir(release):
    """A release waiting in releases/to-post/, or one already posted."""
    for base in (WAITING, LIVE):
        if (base / release / "release.json").exists():
            return base / release
    raise SystemExit(f"no release {release} in {WAITING} or {LIVE}")


def blocks_of(md):
    """The fenced text blocks of a post.md, by heading."""
    out = {}
    for title in BLOCKS:
        m = re.search(rf"^## {re.escape(title)}[ \t]*\n(?:(?!## |```).*\n)*?```text\n([\s\S]*?)\n```", md, re.M)
        if m:
            out[title] = m.group(1)
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage(release, rendered_from=None):
    folder = WAITING / release
    spec = json.loads((folder / "release.json").read_text())
    src = ROOT / spec["source"]
    if spec["type"] == "reel":
        if not rendered_from:
            raise SystemExit("name the commit the video was rendered from")
        from PIL import Image

        video = src / "out" / "final.mp4"
        shutil.copy(video, folder / "video.mp4")
        Image.open(ROOT / spec["cover"]).convert("RGB").save(folder / "cover.png", optimize=True)
        commit = subprocess.run(["git", "rev-parse", "--verify", rendered_from + "^{commit}"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        spec.update({"rendered_from": commit, "video_sha256": sha256(folder / "video.mp4")})
        (folder / "release.json").write_text(json.dumps(spec, indent=2) + "\n")
        print(f"video.mp4 {spec['video_sha256'][:12]}..., rendered from {commit}")
    elif spec["type"] == "carousel":
        for k in range(1, spec["slides"] + 1):
            shutil.copy(src / "out" / f"slide-{k}.png", folder / f"slide-{k:02d}.png")
        print(f"{spec['slides']} slides")
    else:
        raise SystemExit(f"unknown release type {spec['type']}")
    text(release)


def text(release):
    """Rewrites the .txt files from post.md, leaving the media as staged."""
    here = release_dir(release)
    for title, body in blocks_of((here / "post.md").read_text()).items():
        (here / BLOCKS[title]).write_text(body + "\n")
    check(release)


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def text_problems(md, kind="reel", live=False, cfg=None):
    """Every rule the text of a post.md breaks, as readable lines. `live`
    skips the rules for text already posted on the first platform, which is
    a record and is not linted again."""
    cfg = (cfg or brand())["release"]
    found = blocks_of(md)
    out = []
    needed = ["Caption", "Pinned comment"] + (["Alt text"] if kind == "carousel" else [])
    for title in needed:
        if title not in found:
            out.append(f"post.md has no {title} block")
    first = {"Caption", "Pinned comment", "Alt text", "Series-link comment"}
    cap = found.get("Caption", "")
    tags = TAG.findall(cap)
    for title, body in found.items():
        if live and title in first:
            continue
        for ch, name in BANNED.items():
            if ch in body:
                out.append(f"{title} contains a {name} ({ch})")
        for ch, name in QUOTES.items():
            if ch in body:
                out.append(f"{title} contains a {name}")
        if title != "Alt text" and NO_AI.search(body):
            out.append(f"{title} mentions how it was made ({NO_AI.search(body).group(0)})")
    if not live and cap:
        if len(cap) > cfg["maxCaption"]:
            out.append(f"caption is {len(cap)} characters, over {cfg['maxCaption']}")
        if not cfg["minHashtags"] <= len(tags) <= cfg["maxHashtags"]:
            out.append(f"{len(tags)} hashtags; use {cfg['minHashtags']} to {cfg['maxHashtags']}")
        if len({t.lower() for t in tags}) != len(tags):
            out.append("a hashtag repeats")
        table = md.split("## Hashtag checks", 1)[1] if "## Hashtag checks" in md else ""
        for t in tags:
            if not re.search(rf"\|\s*{re.escape(t)}\s*\|", table, re.I):
                out.append(f"{t} has no row in the Hashtag checks table: check each tag's public page before using it")
        paras = paragraphs(TAG.sub("", cap))
        src = next((i for i, p in enumerate(paras) if re.match(r"Sources?:", p)), None)
        if src is None:
            out.append("the caption has no Sources line")
        elif src == 0 or not paras[src - 1].rstrip().endswith("?"):
            out.append("the caption's last paragraph before the sources is not a question")
    pin = found.get("Pinned comment")
    if pin is not None and not live:
        if not re.search(r"\bfollow", pin, re.I):
            out.append("the pinned comment does not invite a follow")
        if TAG.search(pin):
            out.append("the pinned comment carries a hashtag (they count against the post's limit)")
    if kind == "reel" and not live:
        audio = re.search(r'Audio name: "([^"]+)"', md)
        if not audio:
            out.append("post.md names no audio (a line 'Audio name: \"...\"')")
        else:
            if len(audio.group(1)) > cfg["maxAudioName"]:
                out.append(f"audio name is {len(audio.group(1))} characters, over {cfg['maxAudioName']}")
            if any(ch in audio.group(1) for ch in QUOTES):
                out.append("audio name contains a straight apostrophe or an opening quote mark; write ’")
        if not re.search(r"AI label: on\b", md):
            out.append("post.md's settings do not say 'AI label: on' (the voice is synthetic)")
    if kind == "carousel" and "Alt text" in found:
        n = re.search(r'"slides":\s*(\d+)', md)
        lines = [ln for ln in found["Alt text"].splitlines() if ln.strip()]
        if n and len(lines) != int(n.group(1)):
            out.append(f"alt text has {len(lines)} lines for {n.group(1)} slides")
    out += platform_problems(found, cfg)
    return out


def platform_problems(found, cfg):
    """TikTok's and YouTube's limits, for the blocks a release carries."""
    out = []
    tiktok = found.get("TikTok caption")
    if tiktok is not None:
        tags = TAG.findall(tiktok)
        if len(tiktok) > MAX_TIKTOK_CAPTION:
            out.append(f"TikTok caption is {len(tiktok)} characters, over {MAX_TIKTOK_CAPTION}")
        if not cfg["minHashtags"] <= len(tags) <= cfg["maxHashtags"]:
            out.append(f"TikTok caption has {len(tags)} hashtags; use {cfg['minHashtags']} to {cfg['maxHashtags']}")
        if "?" not in tiktok.split("#", 1)[0]:
            out.append("the TikTok caption asks no question")
        if tiktok.strip() == found.get("Caption", "").strip():
            out.append("the TikTok caption is the first platform's caption unchanged; write it for TikTok")
    if "TikTok title" in found and len(found["TikTok title"]) > MAX_TIKTOK_TITLE:
        out.append(f"TikTok title is {len(found['TikTok title'])} characters, over {MAX_TIKTOK_TITLE}")
    title = found.get("YouTube title")
    if title is not None and ("\n" in title or len(title) > MAX_YT_TITLE):
        out.append(f"YouTube title must be one line of at most {MAX_YT_TITLE} characters")
    description = found.get("YouTube description")
    if description is not None:
        if len(description) > MAX_YT_DESCRIPTION:
            out.append(f"YouTube description is {len(description)} characters, over {MAX_YT_DESCRIPTION}")
        if "Sources" not in description:
            out.append("the YouTube description names no sources")
    for name in ("YouTube title", "YouTube description"):
        if name in found and re.search(r"[<>]", found[name]):
            out.append(f"{name} contains < or >, which YouTube refuses")
    pin = found.get("TikTok and YouTube pinned comment")
    if pin is not None and len(pin) > cfg["maxReply"]:
        out.append(f"the TikTok and YouTube pinned comment is {len(pin)} characters, over {cfg['maxReply']}")
    replies = found.get("Short replies")
    if replies is not None:
        for e in [e.strip() for e in replies.split("\n\n") if e.strip()]:
            m = re.fullmatch(r"When: (.+)\nReply: (.+)", e)
            if not m:
                out.append(f"a short reply is not 'When: ...' then 'Reply: ...': {e[:50]}")
            elif len(m.group(2)) > cfg["maxReply"]:
                out.append(f"reply is {len(m.group(2))} characters, over {cfg['maxReply']}: {m.group(2)[:50]}")
            elif re.search(r"https?://|www\.", m.group(2)):
                out.append(f"a reply carries a link: {m.group(2)[:50]}")
    return out


def check(release):
    import covercheck

    here = release_dir(release)
    spec = json.loads((here / "release.json").read_text())
    md = (here / "post.md").read_text()
    if spec["type"] == "carousel":
        md += f'\n<!-- "slides": {spec["slides"]} -->\n'
    problems = text_problems(md, spec["type"], live=here.parent == LIVE)
    if spec["type"] == "reel":
        cover = ROOT / spec["cover"]
        if (here / "cover.png").exists():
            problems += [f"cover: {p}" for p in covercheck.problems(here / "cover.png", cover.with_suffix(".json"))]
        else:
            problems.append("not staged: no cover.png (run stage)")
        if not (here / "video.mp4").exists():
            problems.append("not staged: no video.mp4 (run stage)")
        elif spec.get("video_sha256") and sha256(here / "video.mp4") != spec["video_sha256"]:
            problems.append("video.mp4 does not match the SHA-256 recorded when it was staged")
    cap = blocks_of(md).get("Caption", "")
    print(f"{release}: caption {len(cap)} characters, {len(TAG.findall(cap))} hashtags {' '.join(TAG.findall(cap))}")
    for p in problems:
        print("FAIL", p)
    if problems:
        raise SystemExit(1)
    print("text and cover OK" if spec["type"] == "reel" else "text OK")


def done(release, date, url):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise SystemExit("date must be YYYY-MM-DD")
    folder = WAITING / release
    spec = json.loads((folder / "release.json").read_text())
    spec["published"] = {"date": date, "url": url}
    (folder / "release.json").write_text(json.dumps(spec, indent=2) + "\n")
    LIVE.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(folder), str(LIVE / f"{date}-{release}")], cwd=ROOT, check=True)
    print("moved to", LIVE / f"{date}-{release}")


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
# Milliseconds since 1970 at which the platform's media ids start counting.
ID_EPOCH_MS = 1314220021721


def shortcode_ms(code):
    """The posting time, in milliseconds since 1970, encoded in a reel or
    post shortcode: the code is the media id in base 64 (A-Z a-z 0-9 - _),
    and the id's bits above the lowest 23 count milliseconds from
    ID_EPOCH_MS. Used in the read-back to confirm which post is which."""
    code = re.sub(r".*/(?:reel|p|tv)/([A-Za-z0-9_-]+).*", r"\1", code)[:11]
    media_id = 0
    for ch in code:
        media_id = media_id * 64 + ALPHABET.index(ch)
    return (media_id >> 23) + ID_EPOCH_MS


def when(code):
    import datetime as dt

    ms = shortcode_ms(code)
    print(dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, *args = sys.argv[1:]
    {"stage": stage, "text": text, "check": check, "done": done, "when": when}[cmd](*args)
