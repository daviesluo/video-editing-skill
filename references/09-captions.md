# 09: Captions

Most viewers watch with the sound off for the first seconds, so the
captions carry the hook. They are burned in, word by word, in exact sync
with the voice, and never leave a word stranded on a page.

## How they look and move (`kit/Captions.tsx`)

- **Word by word in place**: each word appears as it is spoken, in its
  final position, so the line never runs ahead of the voice and never
  reflows. A page shows two frames before its first word; each later word
  fades in over 0.07 s from two frames before its start. A page does not
  scale, slide or pop in: it is simply there.
- **The spoken word in the accent colour**, the rest in the type colour,
  both with the tight halo, so a caption reads even over a tint of its own
  colour.
- **A page's first word shows at once**, so the band never empties for a
  frame at a page change; a page with no page straight after it fades over
  0.15 s rather than vanishing.
- **Position**: `LAYOUT.captions` y 1450, centred in a box from x 200 to
  880, at 76 px, weight 800, just above the platform's own text.
- **Turn the platform's automatic captions off** for these videos, or a
  viewer with captions on gets two sets on top of each other.

## In sync, by measurement

The timings come from forced alignment of the finished take
(`build.py <id> realign`) plus the fricative-onset correction
(`04-voice.md`), never from the synthesis timings alone, which run up to
250 ms late after pauses. Measure disputed words on a spectrogram. A word
lights within 0.1 s of its voiced onset; later than that is a finding
(0.13 s on "65%" was visible, 0.07 s on "km²" was not).

## Pages (`kit/paginate.ts`)

The pagination is a small search for the fewest pages that break no rule:

- **Hard breaks only at punctuation**; within a phrase, pages follow the
  voice's phrasing rather than an even split, preferring a break where the
  voice pauses.
- **At most three words a page, on one line**: a page must fit 660 px of
  the 680 px box, measured with the caption face's own advance widths
  (`kit/archivo800.ts`, written by `pipeline/fontwidths.py`), because a
  page that wraps leaves one word alone on a line.
- **Never a word alone on a page** unless it is its whole phrase. "Follow
  for part" then "2." is the failure this exists for.
- **A number stays with the word after it**, and **a page never ends on a
  word that belongs to the next**: "a", "an" and "no" cost almost as much
  as a lone word ("eleven dates no" / "one in Britain" split "no one");
  articles and prepositions tip a tie.
- **Smaller rather than stranded**: a page may be set at 92, 86 or 80
  percent size to keep two words together.
- **Kept phrases** (`caption_keep` in `episode.json`, copied into the
  timeline by `build.py <id> captions`) never split across pages: "a new
  one", "South Pacific", "the 2nd". A kept phrase runs across a comma
  ("Reno, Nevada," is one page; without the keep, "Nevada," stood alone),
  and may run up to five words.
- **Split compounds** (`caption_split`): a hyphenated word too long to
  share a line ("gauge-changing") may break after its hyphen into two
  caption words, its time shared by letters.

## List the pages and read every one

```sh
cd studio && node --experimental-strip-types scripts/caption-pages.ts <id>
```

prints every page with its start, width and scale, and flags a page of
one word after an unfinished page. Read all of them before any render,
and again after every wording change: a page that splits what the eye
reads as one unit ("in the" / "South Pacific,") goes into `caption_keep`
even when no rule fails. A spelled-out number too wide to share a line
with its neighbour at any size cannot be kept whole; accept it and say so
in the picture audit.

## Captions never cover a key label

Move the label, not the caption. And nothing is drawn over the captions:
see "Nothing over the captions" in `08-animation.md`.
