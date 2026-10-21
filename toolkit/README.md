# toolkit

The project template the skill works in: copy this folder's contents into
a new repository, run `sh setup.sh`, and edit `brand.json` and `.env`.
`references/00-setup.md` in the skill repository has the full setup and
the layout.

| Path | What |
|---|---|
| `brand.json` | the series' name, handle, avatar, palette, safe zone, layout, cover tile, release limits and music licence; read by the studio and by every check |
| `pipeline/` | the Python steps: `build.py` (voice, realign, captions, mix, render, mux, qa, remux), `voice.py`, `mix.py`, `music.py`, `sfx.py`, `sfxgen.py`, `qa.py`, `covercheck.py`, `publish.py`, `recue.py`, `scaffold.py`, `audition.py`, `fontwidths.py`, `config.py`; `textures.py fetch` downloads the public-domain relief and Natural Earth layers, records their SHA-256 in `studio/public/textures/SOURCES.md` and builds the globe textures (`globetex.py`) and map plates (`reproject.py`), none of them committed |
| `studio/` | the Remotion project: `src/brand/` (tokens, font, cover, avatar), `src/kit/` (captions and their pagination, kinetic type, stats, bars, `MapView` on a relief plate, `GlobeView` with its lit relief, clipping and scene objects, `Sheet` for the printed-sheet pull-back, `CutAway3D` for an object opened in the 3D scene, `Document`, `Quote`, `Timeline`, `Logo`, the orphan and cover probes, the follow beat, the film finish), `src/lib/` (eases, word cues, geography, projections, plates and their look, the globe's geometry and overlays), `src/episodes/` (one file per episode; `Example.tsx` shows the grammar), `scripts/` (stills, covers, caption pages, design variants on stills, plate grids) |
| `episodes/00-example/` | the example episode's spec; its timeline, with even word timings and no voice, is in `studio/public/episodes/00-example/`, so it renders with no key |
| `templates/` | what `pipeline/scaffold.py` copies for a new episode (spec, music plan, research, verification log, picture audit, and `scene/EpNN.tsx`, its scene file) or release (`release.json`, `post.md`) |
| `setup.sh`, `requirements.txt`, `studio/package.json`, `.env.example` | the machine setup, every version pinned; keys only in `.env` or the environment |
