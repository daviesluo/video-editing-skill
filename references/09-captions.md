# 09: Captions

Most viewers watch with the sound off for the first seconds, so the
captions carry the hook. They are burned in, word by word, in exact sync
with the voice, and never leave a word stranded on a page.

## How they look and move (`kit/Captions.tsx`)

- **Word by word in place**: each word appears as it is spoken, in its
  final position, so the line never runs ahead of the voice and never
  reflows: the whole page is laid out from its first frame and the words
  not yet spoken are hidden, never left out (a page built from the words
  so far re-centres at every word and jumps lines when it wraps; a review
  measured "Yahoo" moving 72 px as "had" landed). A page shows two to
  three frames before its first word; each later word fades in over two
  frames, starting two to three frames before its start, so it is fully
  drawn by the time it is heard. A page does not scale, slide or pop in:
  it is simply there.
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

The lead is not optional. A story reel whose captions lit on the aligned
start, with no lead, and six words after a pause aligned 0.1 to 0.14 s
late, read to the owner as behind the voice ("make sure the captions and
the voice are in sync; the current version feels slightly slow"). So,
before every render: every word after a pause is checked against its
voiced onset (10 ms RMS rising over -30 dBFS after a dip under -45), any
start 0.07 s or more late is moved to the onset and recorded in the
timeline (redone after any re-alignment), and the captions lead by their
two to three frames on top of that. Subtitles under a real voice follow
the same rule against that voice.

Subtitles under a real voice are timed the same way, never by ear: each
line's first word is force-aligned on the bite's own cut and its onset
read on the waveform; the line shows the lead ahead of it and never
before its picture's cut. A film whose bite subtitles had been set by ear
had four lines 0.02 to 0.1 s late and one 0.24 s early, found only when
the owner asked for the check to be run on it: a sync rule set on one
film is measured on every film of the series the same day.

The sync is a script, not a look, run after every timing change: it
fails on a word shown after its start, a page that leaves before its last
word ends (beyond the lead when the next page takes over, past a frame
when the band empties), a narrated word said over an empty band that the
picture does not show, a page or subtitle outliving its picture's cut,
and a page that comes up on one picture and types its words onto the next
(a cut inside the page before its last word shows; a page landing within
a frame of the cut's lead counts as landing with it). A page lives on one
picture: split it at the cut, or move the cut to the page's first word.
A subtitle line leads its first word by no more than the captions' lead
plus the alignment's error, 0.2 s in all (lines 7 to 12 frames early once
passed a looser limit). It is trusted once it has failed on the faults it was written for (two
pages leaving early, "is worth" said over an empty band).

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
  and may run up to five words. Keep a page from reading as another
  phrase on its own: "that many maps" read as a quantity ("so many maps")
  until "map data that" was kept together.
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

## A bleeped word

When the voice bleeps a word (below and `05-music-and-sound.md`, "A
bleep"), its caption shows what is heard: the letters before the beep as
spoken, then a bar in the series' accent colour over the place of the
rest, swept in over two frames on the beep's first frame, as the
highlights on quote cards are. The hidden letters are never drawn, not
even for a frame before the bar (they are laid out transparent, so the
page does not reflow); the bar covers the letters from the cap height to
the baseline; the punctuation after the word lands as the bar completes,
held in its place till then, so the page reads the kept letters alone,
never the letters, a gap and a stray quote mark. The page breaks where
the voice pauses, so the bleeped word starts its page ("Bi▇▇” business
cards." after "its “I’m CEO,").

## Captions on light footage

White type never sits on near-white footage: a white caption on a white
web page read as nothing. It moves to the page's black or to the shot's
own dark area, with its shadow; on a white page it can be set dark
instead. Where nothing dark lies under the only free place (a white shirt
or scarf below a face), the words get a soft dark fall-off behind them: a
radial gradient about half black at its centre to nothing at its edge, of
one fixed size for every page on that picture, from the picture's first
frame; never a box. Check every caption on a still over its picture.

## Captions never cover a key label

Move the label, not the caption. And nothing is drawn over the captions:
see "Nothing over the captions" in `08-animation.md`.
