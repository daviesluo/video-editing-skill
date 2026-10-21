# toolkit

The project template the skill works in: copy this folder's contents into
a new repository, run `sh setup.sh`, and edit `brand.json` and `.env`.
`../references/00-setup.md` has the full setup and the layout.

| Path | What |
|---|---|
| `brand.json` | the series' name, handle, avatar, palette, safe zone, layout, cover tile, release limits and music licence; read by the studio and by every check |
| `pipeline/` | the Python steps: `build.py` (voice, realign, captions, mix, render, mux, qa, remux), `voice.py`, `mix.py`, `music.py`, `sfx.py`, `sfxgen.py`, `qa.py`, `covercheck.py`, `publish.py`, `recue.py`, `scaffold.py`, `audition.py`, `fontwidths.py`, `config.py` |
| `studio/` | the Remotion project: `src/brand/` (tokens, font, cover, avatar), `src/kit/` (captions and their pagination, kinetic type, stats, bars, the orphan and cover probes, the follow beat, the film finish), `src/lib/` (eases, word cues, geography), `src/episodes/` (one file per episode; `Example.tsx` shows the grammar), `scripts/` (stills, covers, caption pages) |
| `episodes/00-example/` | the example episode's spec; its timeline, with even word timings and no voice, is in `studio/public/episodes/00-example/`, so it renders with no key |
| `templates/` | what `pipeline/scaffold.py` copies for a new episode (spec, music plan, research, verification log, picture audit) or release (`release.json`, `post.md`) |
| `setup.sh`, `requirements.txt`, `studio/package.json`, `.env.example` | the machine setup, every version pinned; keys only in `.env` or the environment |
