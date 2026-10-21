# Release {{RELEASE}}: <type>, <the hook>

Status: waiting for the owner’s approval. Nothing is posted without it.
Source: `episodes/{{EPISODE}}`. Every figure below is in its
`verification.md`; the text adds no new facts.

## Caption

```text
<The hook line, complete on its own in the two lines shown before “more”, in the words people search.>

<The explanation: what the video only shows, the exact figures and names, two to four short sentences.>

<One open question only the viewer can answer, ending on a question mark?>

Sources: <dataset, publisher and year, in the form each licence asks for>.

#<niche> #<niche> #<subject> #<subject> #<community>
```

## Pinned comment

```text
<Part N+1 is next: the next part’s question in full. Why follow, in one clause. Follow <Series name> so it’s in your feed.>
```

Ready replies (fact ids from `verification.md`):

- For “<the well-actually this post will draw>”: “<the answer, from facts already shown>” (F01.)

## Series-link comment

Posted and pinned on the previous part once this one is live.

```text
<Part N is up now on @<handle>: the question in full.>
```

## TikTok caption

```text
<Written for TikTok, not pasted: hook, two sentences, the question?>

Sources: <...>.

#<tag> #<tag> #<tag>
```

## YouTube title

```text
<The hook as a title, at most 100 characters>
```

## YouTube description

```text
<Two or three sentences with the figures, the question?>

Sources: <...>.

#<tag> #<tag> #<tag>
```

## TikTok and YouTube pinned comment

```text
<Part N+1 is next: the question. Follow so you catch it.>
```

## Short replies

```text
When: <a comment this post will draw>
Reply: <at most 150 characters, no link>
```

## Settings

- Video: `video.mp4`. Cover: `cover.png` (Edit cover, add from camera
  roll); check the 3:4 tile in the grid once it is up.
- Upload at highest quality, from the original file, not a draft (a draft
  is recompressed).
- AI label: on (the voice is synthetic). Closed captions: off (the video
  carries its own).
- Audio name: "<the hook, <Series name>>" (at most 50 characters; it can be
  set only once).
- Location, collaborators, people tags, mentions: none.

## Checklist

- [ ] Staged with `publish.py stage` (render and cover copied in, commit
      and SHA-256 recorded) and `check` passes.
- [ ] The owner has approved the video, cover and text.
- [ ] Posted from the original file; settings above; cover checked in
      the grid.
- [ ] Within minutes: pinned comment posted and pinned; early comments
      answered by hand.
- [ ] Series-link comment on the previous part.
- [ ] Read back the live post and compare it with this folder; then
      `python pipeline/publish.py done {{RELEASE}} <date> <url>`.

## Why

- The hook: <why this wording, and the search words in it>.
- The question: <why only the viewer can answer it>.
- The pinned comment: <what it promises and why that is a reason to follow>.

## Hashtag checks

Read on each tag’s public page on <YYYY-MM-DD> (“carry” is how many of the
top posts carry the tag in their caption):

| Tag | Shown | Carry | Top posts | Used |
|---|---|---|---|---|
| #<tag> | <count> | <n of 12> | <what the top posts are> | yes, <why> |
