# 04: Voice

The narration is the spine of the episode: captions, cues, sound and the
music's sections all hang off its word timings. It must sound like one
calm, confident documentary narrator reading a script they understand,
with no stray sound anywhere, and every word timed to its voiced onset.

## Choosing the narrator

- The most human-sounding voice available, chosen by the owner by ear
  from three or four candidates: `pipeline/audition.py <dir>
  <voice_id>:<label> ...` renders the same passage in each, loudness
  matched, so the choice is about the voice. Use a passage with a number,
  a name and a question in it.
- The same voice in every episode of a series. Record the voice id, its
  library name and the accent in `episode.json` (`voice`).
- Library voices may need a paid plan; generate only on a plan whose
  terms allow commercial use, and log it.

## Settings

| Field | Value | Why |
|---|---|---|
| `model` | `eleven_v4` | the most natural delivery available; takes no `style`, `speed` or SSML |
| `stability` | 0.5 ("natural") | lower drifts in character, higher reads flat |
| `similarity_boost` | 0.75 | |
| `seed` | fixed per take | a take can be reproduced, and seeds can be compared |
| `format` | `mp3_44100_192` | converted to 48 kHz WAV on arrival |
| `language_code` | `en` | |

Pace with punctuation and sentence length, not with settings. At most one
or two direction tags such as `[curious]` in a script; they are stripped
from captions and alignment automatically.

## One request per episode

`build.py episodes/<id> voice` sends the whole narration in one request to
`/with-timestamps`, which returns the audio and per-character timings of
the text as sent. One request keeps the prosody whole: separate requests
per sentence sound like separate readings. The take goes to
`studio/public/episodes/<id>/voice.wav` and its timeline to
`timeline.json`; commit both (`git add -f voice.wav` for the shipping
take only), so a re-render never needs a new request.

## Re-time every take by forced alignment

Synthesis timings run 150 to 250 ms late on words after a pause.
`build.py episodes/<id> realign` sends the finished audio and the text as
spoken to forced alignment, which lands within about 85 ms of the voiced
onsets, and rewrites the timeline (the audio is unchanged). Then
`voice.fricative_onsets` corrects the one case forced alignment gets
wrong: a word that starts with a hiss after a pause ("Spain", "So",
"65%" read "sixty-five") is placed at its next sound, up to 0.2 s late; its
start is moved back over the hiss. A hiss that runs on unbroken from a
word ending in a hiss or burst ("straight south") stays with that word.
Spot-check disputed words on a spectrogram.

## Choosing among seeds, by measurement

A take can sound different on every seed. Generate three to six, then
keep the one that measures best, not the one that happened first:

- **The transcript reads as written.** A recogniser hears the take; a
  question meant as one must be heard as one ("Where would you come out
  on the other side?", not "…come out? On the other side?").
- **Pitch does what the sentence needs.** `python pipeline/voice.py
  measure <wav> <start> <end>` prints the pitch at the start and end and
  the slope over the last 0.4 s: a statement or a whole question falls at
  its end; a rise mid-line is a second question.
- **Length suits the cut.** A hook spoken too fast is lost; "Where … side?"
  needed at least 1.6 s.
- **Key words are clear.** Check proper nouns and numbers with the
  largest recogniser the machine can hold: a small model once passed a
  misread name that a larger one caught. `build.py qa` and `voice.py
  measure` use `medium.en` by default; set `QA_WHISPER_MODEL=large-v3`
  (or `qa.model` in `episode.json`) where the machine holds it. Coined names go in
  `qa.hotwords`, and a person still listens to them.

## Changing a finished take

Never re-take a whole approved narration for one changed sentence: the
new take changes every timing and every delivery around it.

- **`python pipeline/voice.py replace episodes/<id> <seg> <first> <last>
  [seed]`** (`voice.replace_words`) re-voices one changed phrase, words
  `first` to `last` of the segment, after the new wording is in `episode.json`:
  only that phrase is synthesised, with the narration before and after as
  context, trimmed to its sound, matched in loudness to the segment, and
  spliced in with 15 ms ramps. The extra length comes out of the pause
  after it. Then `realign`, `recue.py`, the music retime and the caption
  pages.
- **Replace whole sentences, from a pause.** A start inside connected
  speech is refused, because the nearest silence can be words earlier and
  the cut would silently drop them; this once dropped "plans to bring
  down the" from a line.
- **Cuts are made only in true silence** (`silence_near`: 30 ms of frames
  over 55 dB under the take's peak), never at the aligned times: an
  aligned start can be 0.1 s after a word's "S" or "T" begins, and a cut
  there once kept the hiss of a replaced "So" and the "T" of a replaced
  "Tokyo".
- **A short burst after the new line is dropped** (`speech_span`): given
  the next line as context, the model can start voicing it, and a
  re-voiced ending once kept the "fo" of the "Follow" that came next.
- **Every splice is recorded** in the timeline (time, and which side is
  old audio), and QA fails a splice whose old side is not silent. Records
  inside a span that a later re-voice replaced are dropped.
- **`python pipeline/voice.py add-line episodes/<id> <seg> [seed]`**
  (`voice.add_line`) appends a new last
  segment (a call to action added after approval) the same way, placed
  after a pause.
- Pass a seed to try several seeds of a replacement; copy `voice.wav`
  and `timeline.json` aside first and keep the best by the measures above.

## The take's QA

`build.py episodes/<id> qa` runs `qa.voice_flaws` on every take, and it
must print nothing:

- no sound within 40 dB of the take's peak that belongs to no word;
- no splice whose old side holds sound;
- no sample jump over 0.01 inside a pause (a click);
- the first and last samples silent and the last 50 ms empty (a take that
  ended on a cut-off fragment clicked on the quiet end card; `mix.py` also
  fades both ends over 10 ms).

And the transcript must match the script (word error rate at or under 3
percent, every difference read by eye, digits forbidden in a check of the
`say` readings). Before calling a voice fix done, run every check over
every take, not only the spot that was reported.

## Test voice

`VOICE_PROVIDER=kokoro` gives a local voice with word timings, for
pipeline tests with no key. It never ships.
