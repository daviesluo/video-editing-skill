# 05: Music and sound effects

The music is felt more than heard: it carries pace and warmth, never
fights the voice, never stops abruptly, and sounds like the same
composer every episode. Sound effects mark cuts and reveals, sparingly,
under the voice. Every sound has a licence record.

## The house sound: "Paper and Wood"

Felt upright piano (low register, sparse dyads and open fifths, never
the melody), pizzicato cello and viola (soft, short, warm), a quiet bowed
cello pedal at the lifts, in a dry chamber room. 88 to 100 BPM, one
tempo per episode, a major key with a Lydian colour, one chord every two
bars, pianissimo to mezzo piano.

It was chosen on measurement against a marimba pulse and cinematic
strings: of the three it left the most room for the voice (the least
energy in the 1 to 4 kHz speech-clarity band), had the fewest note onsets
per second and the steadiest loudness. Marimba beds fight speech and read
as corporate stock; swelling strings carry too much top end and range.

**Never**: vocals, choir or humming, drums, synthesisers, brass, mallets,
risers or impacts, swells, long reverb tails, fade-outs or cut endings,
and no artist or song names in prompts.

## One composed bed per episode

`episodes/<id>/music-plan.json` (from `templates/episode/music-plan.json`)
is a composition plan for Eleven Music:

- **Chunk boundaries sit on segment starts**, so the music lifts where
  the story turns. `python pipeline/music.py retime episodes/<id> <seg>
  <seg> ...` puts them back after any new take of the voice.
- **A continuous pulse from the very first beat**, and a single low note
  at its final level on the first beat: a bed that started sparse sat
  near silence under the hook for three seconds, then came in at once.
- **The same loudness and density in every chunk** ("the same loudness
  and density as the previous section", in each chunk's styles).
- **A held final chord through the end card.** The last chunk asks for "a
  held final chord… that keeps sounding softly under the last spoken
  question and through the end card, fading only in the last second",
  `tail_s` (3 to 4 s) makes the plan run that far past the narration, and
  `music.end_fade_s` 1.0 in `episode.json` makes the mixer fade only the
  last second. A bed that decayed under the last word left a silent end
  card.

Then:

```sh
python pipeline/music.py make  episodes/<id> 101     # and 102, 103 ...
python pipeline/music.py check episodes/<id> episodes/<id>/out/music/take-music_v2_5-101.mp3
python pipeline/music.py use   episodes/<id> <the best take that passed>
```

`use` copies the take to `studio/public/episodes/<id>/music.mp3`
(committed) and records model, seed, song id, generation time and the
licence (from `brand.json`) in `episode.json`. Output is 128 kbps MP3 on
plans without high-quality downloads, which is inaudible under a voice.

## The checks a take must pass (`music.py check`)

Measured after the mixer's own clean-up and levelling, which is what the
viewer hears:

| Check | Pass | The failure it exists for |
|---|---|---|
| length | within 0.6 s of the plan | a bed that ends before the video |
| loudness range | at most 9 LU | swells that fight the voice |
| 1 to 4 kHz share | at most -20 dB | a bed in the voice's clarity band |
| onsets | at most 4 a second | a busy pulse that competes with speech |
| seams | short-term loudness changes at most 4 LU across each chunk boundary | a section that lands louder |
| holes | the quietest 3 s of the body at most 10 dB under its median | near-silence under the hook (one take scored -13.9) |
| hold | under the last words and the end card, at most 12 dB under the median | the chord cut off under the last word |
| ending | the last 1.5 s decays by over 6 dB, no click | a cut ending |
| vocals | a recogniser with voice-activity detection finds no speech | a hummed or sung line |

Make two seeds at least; takes of one plan differ a lot. Then listen to
the opening, each lift and the ending of the mix; measurement finds the
failures above, not taste.

## Levels and ducking (`mix.py`)

- Voice levelled to -16 LUFS first.
- The bed 8 LU under the voice where nobody speaks; ducked 7 dB under
  speech, driven by the word alignment (pauses under 0.5 s bridged so it
  does not pump; down over 250 ms ending 80 ms before each word, back over
  750 ms); while the voice runs, 250 to 400 Hz dipped 3 dB and 1.5 to
  4 kHz dipped 4 dB. That puts the bed about 15 to 16 LU under the voice
  while it speaks; broadcast practice keeps commentary at least 10 LU over
  music, and listeners prefer more.
- The bed is high-passed at 110 Hz, low-passed at 14.5 kHz and levelled
  at 2:1 with slow attack and release, so sections step rather than jump.
- A bed made for a slightly shorter narration is slowed (pitch kept) to
  fit, up to 5 percent; more needs a new composition.
- Final: -14 LUFS integrated and true peak at or under -1 dBTP, measured
  on the delivered AAC file. The mix is limited 3 dB under full scale
  before linear normalisation, or a punchy voice settles a dB or two low.

## Sound effects

- **Few, under the voice, on meaning**: a whoosh on a camera move, a tick
  on a label, a pop on a marker landing, a low thud on the payoff. One
  effect every 1.5 s or more densely reads as a template, and
  `mix.sfx_problems` says so.
- **Never the same sample back to back.** `pipeline/sfxgen.py` generates
  several takes of each effect into `pipeline/sfx-lib/`, and the mixer
  cycles through them; the synthesised effects in `sfx.py` are the
  fallback.
- **Cues are word cues** in `episode.json` (`{"cue": "payoff@1", "offset":
  -0.2, "name": "thud", "gain_db": -14}`), so they move with the words.
- Prompts for generated effects stay soft, close, dry and short; keep the
  plan and date of every generated take.

## Never, and the licence record

- Never the platform's in-app music baked into an upload (it is licensed
  for that platform's own use, and a claim follows the file elsewhere),
  meme, film or television samples, or anything found by searching the
  internet.
- Every bed and effect has a record: service, model or library, seed or
  clip id, plan and terms version with date, and what use the terms allow.
  Generate only on a plan whose terms allow commercial use, and while on
  it: output usually stays under the terms in force when it was made.
