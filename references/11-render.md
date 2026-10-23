# 11: Render

Render stills first, look at them, fix, and only then render the video.
On four cores with no GPU, the example (54 s, a map plate and a 5 s globe
beat) renders in about 9 minutes, and an episode with a 3D globe on screen
for most of 60 s took about 27 minutes; a still takes seconds. So every
fault that can be found without a render is found before one, all of them
in one pass ("Before the full render", below), and the video is rendered
once.

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
"Housekeeping"). `build.py render` prints the narration's pace against
the reference parts before it starts; a take outside their range is fixed
first (`04-voice.md`).

Stills, covers and the render time the episode the same way: the lead-in
and tail are read from the timeline, which `build.py` (`voice`, `realign`
or `captions`) writes from `episode.json`'s `audio_lead` and `tail`, never
from numbers in `Root.tsx`. After changing either in `episode.json`, run
`build.py episodes/<id> captions` before taking stills.

## Before the full render: one pass

Every check that can run on stills, on the timeline or on the audio runs
before the first full render, and every fault they find is fixed in the
same round. One part went through five partial re-renders, each one
finding the next fault in the picture's rhythm (two short moves at a scene
change, then a second move in a second after the first, then a slide that
started late, then a 0.3 s hold before a profile), and the owner asked for
it to be got right in one pass, without lowering the bar. All of these
were in the code and the timeline before the first render. The pass:

1. **The script and the take**: the cold read (`03-script.md`); the take
   against the reference parts' pace and tone (`voice.py pace-report`,
   `voicestyle.py report`); the transcript; every caption page listed and
   read (`09-captions.md`).
2. **Stills at every key word** of the picture audit, and every scene
   change and camera move in 0.1 s steps (above).
3. **The text scan and the covers**: the orphan and safe-zone scan over the
   whole episode, `covers.mjs`, each cover looked at.
4. **The picture's rhythm from the code**: list every camera move with
   its start, its end and how far it goes, and every scene change with
   the moves it is made of. Compare each move's speed with its sibling
   moves (`08-animation.md`, "Speed, not only duration"); make each scene
   change one continuous move; leave a beat to read after each. Then
   count: a part whose list already has more movements per 10 s than the
   reference parts, or holds shorter than theirs, fails the rhythm check
   once rendered.
5. **The code's own faults by search**: every fade written as one
   element's window against another's (`on × (1 − other)`), every element
   drawn outside its scene's window, every flat map view whose span at
   its scale passes its plate or ±180°, every detail plate whose edge can
   enter the frame (`07-visual-grammars.md`, "Maps and globes";
   `08-animation.md`, "Designed, not drawn the quick way").
6. **The sound**: `music.py check` on the take in use, the effects plan.
7. **The release**: staged and `publish.py check`.

A quick low-resolution render of the whole episode on this machine may
follow as a first look at the rhythm, but it is not the gate: one
quarter-size, fast-encoded preview read a median hold of 4.1 s where the
full render of the same commit read 2.92 s, although the measure scales
both to the same small frame. The gate is `rhythm.py report` on the
delivered file. Then render the whole episode once, and run every gate in
`12-qa-gates.md` on it. If the rhythm check fails there, list what it
counted (`rhythm.py moves episodes/<id>`: every movement and hold, with
the word being spoken) and fix every entry the list shows at once, not the
first one found.

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
- **A smaller model at low effort.** A helper only runs the brief's
  commands; nothing it decides changes a frame, and what it returns is
  checked here (SHA-256, frame count, seam stills). Start every new helper
  on a smaller model (Sonnet) at low effort, set when the session is
  created (the owner, 2026-10-23). Where the platform's session tool sets
  the model but not the effort, ask the owner to set the effort in the
  app.
- **Brief by the full commit hash**, pushed first, never by a branch name
  that can move.
- **An interrupt sent by mistake is followed at once by a message.** The
  render the helper started in the background survives the interrupt, but
  the helper's turn has ended, so nothing pushes or reports the result
  until it is told to carry on with its brief.
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

- Each helper renders its part at the same full commit hash, with
  `RENDER_FRAMES=<first>-<last> .venv/bin/python pipeline/build.py
  episodes/<id> render` (frames from 0; the last frame is the
  composition's length less one), which writes `out/video-<first>-<last>.mp4`,
  and pushes that file to its orphan branch in place of `final.mp4`.
- **The brief names** the full hash, the part's frame range, the frame
  count the file must hold, and the composition's total, and the helper
  replies with the part's SHA-256. Each part fetched is checked against
  its hash before the join.
- Fetch every part into `episodes/<id>/out/`, then `build.py episodes/<id>
  join`: it checks that the parts meet end to end (the first starts at
  frame 0, each later one the frame after the last ended, each file holds
  every frame of its range, the last ends on the composition's last
  frame) and concatenates them without re-encoding, then prints the
  seams' frame numbers.
- **Check every seam against reference stills.** Render stills of the two
  frames either side of each seam at the same commit and compare: the
  step between them in the joined video should match the step between
  the stills (one seam read 1.13 in the video and 1.22 in the stills,
  the step being a fill in progress) and the encoder's keyframe step
  elsewhere in the video. Then `mix`, `mux` and every QA gate as for a
  whole render.

### Re-rendering only some parts

After a fix, the parts whose frames it does not touch can be kept and the
others re-rendered at the new commit, then all joined. Keep a part only
when the change provably leaves every one of its frames as they were:
diff the commits, and for every value that changed (a cue, a start, an
end, a duration, a shared component) work out the frames it reaches. A
move whose end time changed reaches every frame up to that end: one fix
moved a slide's end by a fraction of a second into the next part, which
would have left eight frames of the kept part out of step with the new
code at the seam, and the part had to be re-rendered too. When in doubt,
re-render it. The seam check above then runs on every seam, kept parts'
included, and the ledger records which commit each part was rendered at.
A round of partial re-renders is still a round: find everything first
(above).

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
