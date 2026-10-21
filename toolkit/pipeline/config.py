"""Where things live, and the series' brand values, for every pipeline
script. The brand values are read from brand.json at the project root, the
one file a series edits to change its name, handle, palette, safe zone and
release limits; the studio reads the same file, so the checks here and the
picture there can never disagree.

Project layout (the toolkit folder is a template of it):

    brand.json            series name, handle, palette, safe zone, limits
    pipeline/             these scripts
    studio/               the Remotion project
    episodes/<NN-slug>/   episode.json, music-plan.json, verification.md,
                          picture-audit.md, research.md, out/ (gitignored)
    releases/to-post/     one folder per release waiting to be posted
    releases/posted/      the same folders once live
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio"
EPISODES = ROOT / "episodes"
RELEASES = ROOT / "releases"
WAITING = RELEASES / "to-post"
LIVE = RELEASES / "posted"
TEMPLATES = ROOT / "templates"
SFX_LIB = Path(__file__).resolve().parent / "sfx-lib"


def brand(path=None):
    """The series' brand values (brand.json)."""
    return json.loads(Path(path or ROOT / "brand.json").read_text())


def public_dir(episode):
    """Where an episode's committed narration, timeline and music live."""
    return STUDIO / "public" / "episodes" / episode["id"]


def readings(episode):
    """The `say` table for the narrator's accent. `say` is either a flat
    {script word: reading} map or keyed by accent ({"british": {...},
    "american": {...}}), and `voice.accent` picks one, so a British narrator
    never reads a number the American way."""
    say = episode.get("say", {})
    if "british" in say or "american" in say:
        return say.get(episode.get("voice", {}).get("accent", "british"), {})
    return say
