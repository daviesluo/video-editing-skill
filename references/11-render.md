# 11: Render

Render stills first, look at them, fix, and only then render the video.
On four cores with no GPU, the example (54 s, a map plate and a 5 s globe
beat) renders in about 9 minutes, and an episode with a 3D globe on screen
for most of 60 s took about 27 minutes; a still takes seconds.

## Settings

`build.py episodes/<id> render` runs:

```
npx remotion render <Composition> out/video.mp4 --gl=swangle --concurrency=2 \
  --codec=h264 --crf=16 --x264-preset=slow --pixel-format=yuv420p \
  --color-space=bt709 --muted --props='{"id":..., "lead":..., "tail":..., "qa":false}'
```

- **`--gl=swangle`** always: cloud containers have no GPU, and WebGL
  without it draws nothing.
- **Concurrency 1 or 2**: the software renderer already uses every core;
  more tabs only thrash.
- **H.264 High, yuv420p, CRF 16, preset slow, BT.709, 30 fps**: the
  platform re-encodes everything, so give it a clean master. `mux` adds
  AAC 256 kbps at 48 kHz and `+faststart`.
- **The picture renders muted**; the mix is muxed afterwards, so a music
  change never needs a new picture.
- **Never open the studio UI in a cloud session**: nobody can see it.
  Render stills and look at them.
- **Vendor every asset** under `studio/public/` (fonts, images, data) and
  pin every package (`npm i --save-exact`); a render fetches nothing.

## Stills first

```sh
cd studio
node scripts/stills.mjs Ep07 /tmp/s 0,1.5,3.2,6.8          # chosen moments
node scripts/stills.mjs Ep07 /tmp/s every:0.5               # a contact run
ORPHANS=1 node scripts/stills.mjs Ep07 /tmp/scan every:0.5  # the text scan
```

Look at a still at each key word (the picture audit's rows) and at every
scene change and camera move in 0.1 s steps before rendering. Stills
render from one bundle and the bundle is deleted afterwards; delete the
stills themselves once their report is written (`00-setup.md`,
"Housekeeping"). `build.py render` prints the narration's pace before it
starts; a take outside the series' pace is fixed first (`04-voice.md`).

Stills, covers and the render time the episode the same way: the lead-in
and tail are read from the timeline, which `build.py` (`voice`, `realign`
or `captions`) writes from `episode.json`'s `audio_lead` and `tail`, never
from numbers in `Root.tsx`. After changing either in `episode.json`, run
`build.py episodes/<id> captions` before taking stills.

## Render helper sessions

To render several episodes at once, or while this session keeps working,
send renders to standing helper sessions, each its own machine with
identical settings, so its frames are the same frames.

- **Two standing helpers, named "video render helper - 1" and "video
  render helper - 2"**, created once and reused for every render by
  message. Never spawn a new helper per render: a fresh one has to set up
  its machine again, costs a new context, and leaves another session to
  track. Record their session ids in the project's ledger.
- **Creating them**, once per project: on a platform with remote sessions,
  start two sessions on this repository titled exactly "video render
  helper - 1" and "video render helper - 2", give each the machine setup
  from the ledger as its first message, and record both session ids in the
  ledger. Reuse them by message (the platform's send-message tool). Where
  there are no remote sessions, a helper is a second machine or terminal
  with the same checkout and setup, run with the same brief; and when no
  helper is free, render here with the same `build.py` steps: the settings
  are identical, so the frames are too.
- **Brief by the full commit hash**, pushed first, never by a branch name
  that can move.
- **The helper pushes its result to an orphan branch** named
  `render/<NN>-<short hash>` holding only `final.mp4`, so a video never
  enters the main history, and reports the SHA-256. This session fetches
  that branch and checks the hash. Some sessions cannot delete remote
  branches; superseded render branches are then left for the owner to
  delete.

The brief, sent as a message to an idle helper:

```text
Render request <NN> for <repository>.

1. If this container is fresh, run the machine setup in the ledger
   (setup.sh, which also builds the textures; the browser; the key in .env).
2. git fetch origin && git checkout --detach <full 40-character commit hash>
3. .venv/bin/python pipeline/build.py episodes/<id> mix
   .venv/bin/python pipeline/build.py episodes/<id> render
   .venv/bin/python pipeline/build.py episodes/<id> mux
4. Push episodes/<id>/out/final.mp4 alone to a new orphan branch
   render/<NN>-<first 7 of the hash>:
     git checkout --orphan render/<NN>-<short>
     git rm -rq --cached . && git add -f episodes/<id>/out/final.mp4
     git commit -qm "Render <NN> at <short>" && git push -u origin render/<NN>-<short>
     git checkout -qf --detach <full hash>     # back to a clean tree
5. Reply with: the branch, the commit rendered, sha256sum of final.mp4,
   its duration, and any warning the render printed. Do not run QA, do
   not change any file, do not push anywhere else.
```

### One episode across both helpers

When an episode is wanted sooner than one helper renders it, split it:
every frame depends on its number alone, so the parts are the frames a
whole render makes.

- Each helper renders half at the same full commit hash, with
  `RENDER_FRAMES=<first>-<last> .venv/bin/python pipeline/build.py
  episodes/<id> render` (frames from 0; the last frame is the
  composition's length less one), which writes `out/video-<first>-<last>.mp4`,
  and pushes that file to its orphan branch in place of `final.mp4`.
- Fetch both parts into `episodes/<id>/out/`, then `build.py episodes/<id>
  join`: it checks that the parts meet end to end (the first starts at
  frame 0, each later one the frame after the last ended, each file holds
  every frame of its range) and concatenates them without re-encoding,
  then prints the seam's frame numbers.
- Look at the frames either side of each seam at full size, then `mix`,
  `mux` and every QA gate as for a whole render.

## Shortcuts that save a render

- **Only the music or the effects changed** (code, voice and timeline
  identical to the render): `build.py episodes/<id> remux` remixes and lays
  the new mix under the existing picture, stream-copied. Then all the QA
  gates again.
- **Only the picture changed after the narration is final**: render the
  picture at the new commit, check that its audio matches the staged
  audio sample for sample, then remux the new video stream with the staged
  audio (`ffmpeg -i new.mp4 -i staged.mp4 -map 0:v -map 1:a -c copy`).
  Then every QA gate, and compare every 0.5 s frame with the previous
  release: only the intended region may change.

## After the render

`build.py episodes/<id> qa` on the delivered `final.mp4`, then the rest of
the gates in `12-qa-gates.md`, then the independent review of this exact
file (its SHA-256 in the review's header).
