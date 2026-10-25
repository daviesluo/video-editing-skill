# 02: Research, data and rights

Accuracy is the brand: one wrong number in a shared explainer costs more
trust than ten good episodes earn. Every fact said, shown or written in
the release text is traced to a primary source or computed by a script
from a named dataset, and logged before it ships. Every picture, clip,
quote, logo and track has a rights basis written down before it is used.

## The fact sheet (`episodes/<id>/research.md`)

Start from `templates/episode/research.md`. It holds:

- **Data files**: dataset name, version or release date, publisher, URL,
  licence, download date and the SHA-256 of the file as downloaded, so the
  same file can be fetched again and proved identical. Large or
  non-redistributable downloads stay outside the repository; the row is
  enough to get them back.
- **The claim table**: id, claim, source, URL, date accessed, confidence,
  and the exact quote or figure. Confidence is one of:
  **PRIMARY** (read on the authoritative source), **CALC** (computed by
  us, dataset and method stated), **S1** (one secondary source: context
  only, never on screen alone), **D** (disputed).
- **Numbers that disagree, and which to use**: every quantity where
  sources differ, the likely cause (definitions, dates, resolution,
  rounding), and the one value the episode uses, with its wording.
- **Rights**: every element that is not drawn by us, with its basis.
- **Pitfalls**: readings the viewer could take that the facts do not
  support, and myths not to repeat.
- **Not verified, or dropped**: what was considered and why it is out.
- **The draft script**, so wording is checked against the table.

## Data with provenance

- **Primary over secondary.** A statistics office over a news story about
  it; the statute over a summary; the filing over the press release; the
  paper over the press release about the paper. A secondary source is a
  lead to the primary one.
- **Compute what you can.** A figure computed by a script from a named
  dataset can be re-run and defended; a figure copied from a website
  cannot. The script lives in `episodes/<id>/analysis/`, takes its inputs
  as arguments, states its method in its docstring and writes its outputs
  to a JSON file beside it. Re-running it must reproduce every figure in
  the log.
- **State the method where it changes the answer**: map scale (1:50m or
  1:10m), geodesic or flat distance (WGS84 geodesic for distances,
  equal-area projection or ellipsoidal areas for areas), the year, nominal
  or inflation-adjusted money (index and base year), fiscal or calendar
  year, median or mean.
- **Check the data before trusting a wild result.** A point-in-land test
  on flat polygons once found planet-wide bands of false land: rings that
  cross the antimeridian must be repaired first. When a number looks
  surprising, test the fixture before believing it. Look too at what a
  dataset draws under the subject itself: a part about a phantom island
  was drawn over a global relief grid that still held a seabed high under
  the island's footprint, cut off along one meridian, a survivor of the
  compilations the story was about, and it showed as a pale wedge where
  the voice said deep ocean. Where a dataset contradicts the primary
  measurement the story rests on, correct it there from that measurement,
  and mark the edit in the code and in the log.
- **Run the analysis isolated.** Downloaded files are untrusted: keep them
  in their own folder, run the script from elsewhere with `python -I`, and
  pass paths as arguments.

## The verification log (`episodes/<id>/verification.md`)

From `templates/episode/verification.md`. QA fails while any fact in
`episode.json` is not marked verified or has no row in this log.

- **Every fact said, shown or written**: narration, on-screen labels,
  stats, source lines, the caption, the pinned comment, alt text, ready
  replies and platform descriptions. A figure in a reply is as public as
  one in the video.
- **The claim as worded**, the re-check (the source's exact quote, or the
  script and its output), and the result. A CALC figure is re-run for the
  log, not copied from the research note.
- **The check first, then the sentence.** Never write a fact into the log
  before its check is done: a note drafted with an unchecked claim read as
  verified and was caught only on re-read. Text written ahead of a check
  is a claim, wherever it sits.
- **Reply text is checked like the picture.** A ready reply said one
  country's opposite side was "mostly" another; computed, 73 percent of
  its far side is sea, and only the land there (81 percent of it) is the
  other country. Every reply, comment and description gets the same
  check as an on-screen fact before it is written down as ready.
- **Rounding.** Round only where the source rounds. The voice may say
  "over 1,000 kilometres" while the screen shows "1,072 km"; both must be
  true of the same figure. "Nearly three-quarters" is right for 72.5
  percent; "three-quarters" is not. Never round across a threshold the
  sentence depends on.
- **One quantity, one value**, everywhere it appears, or a label that says
  why two differ (two map scales, two years).
- **Say exactly what kind of number it is.** A share is called a share
  ("proportionally, it keeps pace with Canada", not "by area", which
  reads as total area); a unit a general viewer may not know is explained
  where it is the subject ("one hectare is a square 100 m by 100 m"); a
  statistic about land is not reworded as one about people.
- **Re-check after every wording change**, and add a dated "Re-checks"
  note saying what changed. The log is the record a reviewer reads; a
  stale log is worse than none, because it reads as evidence.

## Rights, by kind of material

Nothing goes on screen without a rights basis in the research file's
Rights table and a credit line where its licence asks for one. When the
basis is unclear, the element is not used; a code-drawn alternative
almost always exists. This is practical guidance for choosing safe
material, not legal advice; where real money or a real dispute is
involved, ask someone qualified.

The rules below are the defaults. When the owner has taken qualified
legal advice and decides otherwise for a series (for example that news
footage, film clips, press headlines and company logos may be used for
the series' commentary), the series layer records the decision, its date
and its limits, and it wins for that series. Do not raise the risk again
once the owner has decided; keep logging every element as below.

### Maps and geographic data

- Natural Earth is public domain; credit it anyway ("Maps: Natural
  Earth"), because credit builds trust.
- OpenStreetMap data is under the ODbL: "© OpenStreetMap contributors" on
  screen or in the caption, and share-alike applies to derived databases.
- Government open data carries its own licence (for example the UK's Open
  Government Licence asks for a set attribution statement); read it.
- Satellite and relief imagery: many national agencies' images are public
  domain in their own country, but each agency publishes media guidelines
  (no logos, no implied endorsement, credit lines); follow them.
- Borders: disputed borders are drawn dashed or not at all, taking no
  side, and a map of a past era does not show today's borders.

### Data and charts

- CC BY 4.0 asks for the creator, a licence notice and a note when the
  data were changed, "in any reasonable manner based on the medium": the
  caption's Sources line is that place.
- A chart redrawn from published data, with credit, is ours; a screenshot
  of someone else's chart is theirs.

### Archival photographs, documents, artworks and portraits

- **Public domain is a fact to establish, not assume.** Check the date and
  the jurisdiction: in the United States, works published in 1930 or
  earlier are public domain as of 2026 (the line moves every 1 January),
  and works of the US federal government are public domain; in the UK and
  the EU most works stay protected for 70 years after the author's death.
  An old photograph with an unknown author is not automatically free.
- **Wikimedia Commons: read the licence tag on the file page itself**, not
  the category: PD tags state their reason (expired, government work),
  CC BY and BY-SA ask for attribution in the form given, BY-SA's
  share-alike reaches adaptations, and the page may carry a personality-
  rights or trademark warning that the licence does not override.
- **Museum open access**: many museums release public-domain works as
  CC0 with downloadable files; use those files and keep the object page's
  URL. "No known restrictions" (common in library collections) is not the
  same as public domain; read the rights statement.
- **A faithful photograph of a public-domain painting or document** is
  generally free to use in the US and, under the EU's 2019 copyright
  directive (Article 14), in the EU; a holding institution's own terms can
  still apply to its files, so read them.
- **No fabricated history.** No AI upscaling, colourising or "restoring"
  that invents detail in a documentary image, no generated portraits of
  real people, and no generated scene presented as a record. A
  reconstruction of something no camera could capture is labelled "AI
  reconstruction" on screen and disclosed with the platform's label.
- **Living people and private individuals**: show public figures only in
  a factual context, never a private person without consent, and never a
  likeness made by a model.

### Quotations and book text

- The exact wording from a named edition, with page, or from the primary
  document; a famous quote is checked for misattribution before use, with
  quote-checking sites as leads to the primary source, never as the
  source.
- Translations name the translator; the translation itself has its own
  copyright.
- Text in copyright is quoted briefly, attributed, and for a purpose the
  episode states (commentary, criticism, explanation). No long passages,
  no page scans of in-copyright books, no cover art used as decoration:
  set the title in the house type instead.
- Public-domain texts follow the same date rules as above; the edition
  used must also be public domain (a modern critical edition's notes and
  corrections are not).

### Companies, logos and products

- A logo may identify the company the episode is about; it may not imply
  sponsorship, be altered, recoloured or animated into something else, or
  sit beside a competitor's in a misleading comparison. Use the company's
  own press-kit files and read their terms.
- Figures come from filings and annual reports (state the fiscal year and
  currency); what a company says about itself is attributed to it; what
  the press reports is labelled as reported. Claims that could harm a
  person or company rest on documents, not on commentary.
- Product photographs: press-kit images under their terms, or our own.

### Footage, music and sound

- Stock footage only with a licence record (service, licence, date,
  clip id). By default no clips from films, television, news broadcasts
  or other creators, however short. Where the series layer allows them
  (the owner's decision on legal advice, above), each clip is still
  logged in the asset log (programme or source, its owner, air or
  release date, the timecodes used), cut into the series' own edit with
  its own narration, type and grade, and never reposted as it was.
- Fetch each clip at the best format its source holds, with no height
  cap (`yt-dlp -f 'bv*+ba/b'`), from the owner's own upload where there
  is one, and read its resolution before cutting: a soft or upscaled
  copy is a fault the review will find. A host may refuse a cloud machine
  (YouTube answers 403 on media files when the outgoing IP changes
  between the page and the download): fetch through one fixed outgoing
  IP that the owner provides and approves for the machine, without
  cookies, or have the owner send the files; never settle for a lower
  copy because the better one was refused.
- A clip arrives as the source's own file, untouched: whatever codec and
  container the host served (AV1 or VP9 video, Opus audio, mp4, webm or
  mkv), never transcoded or remuxed on the way, since every encode costs
  picture and a cut is made here by stream copy. Remotion's own ffmpeg
  decodes AV1 (dav1d), VP9 and Opus (checked 2026-10-25), so nothing
  needs converting for the render. Whoever downloads for the project is
  told so with the list; a delivery that was converted is asked for again
  as the originals.
- What a cloud machine could still fetch, when YouTube, Facebook and
  Wikimedia's API refused it (2026-10):
  - posts on X, through `api.fxtwitter.com` (a status gives every mp4
    variant up to the original; `/2/profile/<user>/statuses` pages
    through an account with its `cursor`, and answers 404 now and then,
    so retry). A company's staff often post the whole recording of a
    conference talk there, where the conference's own copy is on
    YouTube;
  - companies' own sites and CDNs (newsroom and product pages, their
    asset hosts), NASA's image library (`images-api.nasa.gov`), research
    projects' pages (`<name>.github.io`, whose own test videos are often
    there in full);
  - Wikimedia Commons through its category pages as HTML and their
    `thumb.wikimedia.org` thumbnails, then each original from
    `upload.wikimedia.org` one at a time with a pause, when the API
    answers 429;
  - YouTube's thumbnails (`i.ytimg.com/vi/<id>/hq1.jpg` to `hq3.jpg`, at
    a quarter, a half and three quarters) to judge a video before asking
    the owner's other machine for just the stretch needed
    (`yt-dlp --download-sections "*25:00-32:00"`).
- Music and sound effects: see `05-music-and-sound.md`. Never the
  platform's in-app music baked into an upload, meme or television
  samples, or anything found by searching the internet.

## The asset log

Each release lists every element and its basis: narration (service,
voice, plan whose terms allow commercial use), music (service, model,
seed, song id, terms version), sound effects, every image and clip, every
dataset, the font (SIL OFL), with the credit line used. It lives with the
release or the episode, and a reviewer checks it like any other fact.

## Research by genre, in short

| Genre | Primary sources | Traps |
|---|---|---|
| Maps and geography | national mapping agencies, Natural Earth, agency datasets, our own computation | antimeridian polygons, projection areas, map scale, disputed borders |
| Business | annual reports, securities filings, court records, the company's archive (attributed) | fiscal years, currencies, inflation, "reported" versus established |
| History | statutes, archives, contemporary records, scholarly editions | calendar changes (Julian and Gregorian, year start), period borders, popular myths |
| Literature and books | the edition (publisher, year, page), letters, manuscripts | misattributed quotes, translations, later editions changing text |
| Science | peer-reviewed papers, agencies, standards bodies | preprints presented as settled, units, uncertainty dropped, extrapolation |
