# 14: Release, posting and the read-back

A release is a folder holding exactly what is posted, at full quality,
with text that has been linted and reviewed. Nothing is posted without
the owner's approval, and every post is read back once it is live.

## The release folder (`releases/to-post/<release>/`)

`python pipeline/scaffold.py release 09-reel-<slug> <episode id>` writes
it from `templates/release/`. Releases are numbered in posting order
(`07-reel-...`).

| File | What |
|---|---|
| `release.json` | type and source, the cover path, the commit the video was rendered from and its SHA-256 (written by `stage`); once live, the date and link |
| `post.md` | the single home of the text: fenced `text` blocks under fixed headings, then the settings, the checklist, the reasons for each choice and the hashtag check table |
| `video.mp4`, `cover.png` | the masters |
| `caption.txt`, `pinned-comment.txt`, `series-link-comment.txt`, `tiktok-caption.txt`, `youtube-title.txt`, `youtube-description.txt`, `pinned-comment-tiktok-youtube.txt`, `replies.txt` | the blocks written out by `stage` and `text`, so what is pasted is what was reviewed |

```sh
python pipeline/publish.py stage <release> <full commit hash>   # media in, hash recorded, .txt written, check
python pipeline/publish.py text  <release>                      # rewrite the .txt files from post.md, then check
python pipeline/publish.py check <release>                      # lint text and cover again
python pipeline/publish.py done  <release> <YYYY-MM-DD> <url>   # moves it to releases/posted/
python pipeline/publish.py when  <url or shortcode>             # the post time, for the read-back
```

Stage before the review, so the reviewer checks the staged folder and
`check` has run on it: a release once reached review unstaged, and its
apostrophes, audio name and cover had never been checked.

## What `publish.py check` enforces, and why

| Rule | Why |
|---|---|
| apostrophes typed ’ (U+2019); no straight ' and no ‘ used as one | on the way from a pack to the app, straight apostrophes turned into alternating ‘ and ’ in about half the words of two live captions ("world‘s", "It‘s") |
| no middle dots, em or en dashes, arrows | typographic tells of generated text |
| the text never says how it was made (a topic about AI is fine) | the platform's own label does the disclosure; a caption line about it reads as an apology and costs reach |
| 3 to 5 hashtags, none repeated, each with a row in the Hashtag checks table | the platform allows at most five, caption and comments together; each tag must have been checked on its public page |
| the caption's last paragraph before Sources is a question | one open question is what earns comments |
| a Sources line | credit, as the data licences ask, and trust |
| the pinned comment invites a follow and carries no hashtag | its one job is follows; tags in comments count against the five |
| the audio name at most 50 characters | the platform refuses a longer one, and it can be set only once |
| the settings say "AI label: on" | a realistic synthetic voice requires the platform's label |
| TikTok and YouTube limits (caption 4,000; title 100; description 5,000, no < or >; replies 150, no links) | each platform's own limits, read October 2026 |
| the cover passes `covercheck.py`; the staged video matches its recorded SHA-256 | the folder is the master |

## The caption

- **The hook line, complete on its own** in the two lines shown before
  "more" (under about 90 characters), echoing the video's question or
  answer, in the words people search ("antipode", "Greenland",
  "Mercator").
- **The explanation**: what the video only shows (exact figures, names,
  the method), 45 to 90 words above the sources in two to four short
  paragraphs. Every figure is in `verification.md`; the text adds no new
  facts.
- **One open question** only the viewer can answer (their route, their
  country, their guess), ending on "?". Never "comment YES", "tag a
  friend" or "send this to": platforms hold back engagement bait.
- **Sources**: dataset, publisher and year, in the form each licence
  asks, then the hashtags.
- **No mention of how it was made.** The bio does not mention it either.

## Hashtags, researched per release

Three to five: the niche (the series' field), the exact subject, the
community that shares this kind of post. Hashtags label a post; they do
not add reach. Check each on its public topic page before using it and
fill the table in `post.md`: what is shown, how many of the top 12 posts
carry the tag, what the top posts are, and the decision. Tags that look
right can belong to something else entirely (one subject's own tag was a
skincare brand, another a home-renovation community); country tags
usually open on travel reels and are used only where the country is the
answer.

## The pinned comment and the series links

- **One job each**: the caption's question gets comments, the pinned
  comment gets follows.
- **The pinned comment names the next part's question in full and the
  reason to follow** ("Part 6 is next: is Reno, Nevada, east or west of
  Los Angeles? Follow <series name> so it’s in your feed."). A vague
  teaser ("then the same test on South America") fails the cold read.
- **Series links**: once the next part is live, add and pin a second
  comment on the previous part ("Part 6 is up now on @<handle>: <the
  question>"). If the platform offers a series or linked-video feature,
  use it too, but never depend on it: such features come and go.
- **Ready replies** in `post.md`: the "well, actually" comments the post
  will draw, each answered with facts already verified and re-checked as
  worded (a ready reply once said one country's far side was "mostly"
  another, when most of it was sea; `02-research-and-rights.md`), each citing its
  fact id. Short versions (at most 150 characters, no links) for TikTok.

## Other platforms

The same release goes to TikTok and YouTube Shorts after the first
platform, with text written for each, not pasted: a TikTok caption with
its own first line; a YouTube title (the hook, at most 100 characters)
and a description with the sources.

- **YouTube only through the official YouTube Data API**, under the
  owner's one-time OAuth consent: its Terms forbid accessing the service
  "using any automated means", so a browser agent driving YouTube Studio
  breaks them however human it looks. Upload the staged file (check its
  SHA-256 against `release.json`), category Education, the language
  set, "made for kids" No, the synthetic-content question answered, then
  the first comment. The API cannot pin comments.
- **TikTok** has no comment API for replies and its Content Posting API
  needs an audited app; anything that works the website for the owner goes
  slowly, by hand-like steps, and stops and calls the owner at any
  verification prompt, CAPTCHA or warning. Replies are at most 150
  characters.
- Replies, on any platform, at most one every 45 s and 40 a day.
- Any automation that runs an account never holds a password it does not
  need, does nothing that looks automated, and posts nothing the owner
  has not approved (a release the owner already posted on the first
  platform counts as approved, as does a reply from its ready replies).
- Read each platform's current rules and disclosure policy before the
  first post, and date them in the release.

## The posting guide

Each release that is ready goes to the owner as one pack: the guide, the
video and cover as files, and the caption, audio name and pinned comment
in the message itself, copied from the release's `.txt` files, and the
reviewer's listening times. Resend the
whole pack when any part changes. The guide may be translated for the
person who posts; the English below is the source.

```text
Posting guide: release <release>, <series name> part <N>

Before you start
0. Listen once, end to end, on headphones: above all <times from the
   review's "could not check" list>. Tell me anything you hear before
   posting.
1. Download video.mp4 and cover.png from the release folder to the phone.
   Use these files, not a saved draft: a draft is recompressed (one went
   from 2 MB to 800 KB).
2. In Settings, Media quality: upload at highest quality, on.

Post
3. Create, Reel, choose video.mp4.
4. Next. Edit cover, Add from camera roll, choose cover.png. Check the 3:4
   preview: title and picture inside it.
5. Caption: paste caption.txt exactly. Check the apostrophes are ’.
6. Audio: rename the original audio to: <audio name> (it can be set once).
7. More options: Add AI label, on. Closed captions, off (the video has its
   own). No location, no tagged people, no collaborators. Share to a
   linked Page only as you have set it, never to a personal profile.
8. Share.

In the first minutes
9. Paste pinned-comment.txt as a comment, then pin it.
10. On the previous part: paste series-link-comment.txt and pin it.
10a. Profile: open the post's menu and choose Pin to main grid, so the
     parts sit in order on the profile.
11. Answer early comments by hand; ready replies are in post.md.

Then
12. Send the link of the live post, so it can be read back and recorded.
```

## After posting: the read-back

- **Read the live post back** from its public page and embed
  (`/reel/<code>/embed/captioned/` gives the caption, audio name, cover
  and a 720p copy without a login) and compare it with the release
  folder: every 0.5 s frame against the master, audio in sync, loudness,
  the caption character for character (apostrophes), the audio name, the
  cover in the grid. `publish.py when <url>` reads the posting time out of
  the shortcode. Report what differs; comments and the profile usually
  need a login and are checked on the owner's screenshots.
- **Record it**: `publish.py done <release> <date> <url>` moves the folder
  to `releases/posted/`.
- **Performance notes** after 24 to 48 hours: the skip rate (viewers who
  leave in the first three seconds), the retention graph and where it
  drops, sends per reach, follows, and the account's recommendation
  status. Compare with the series' own history, not vendor benchmarks,
  and write what to change in the next topic or hook.
- **Leave a posted video alone**: no deleting and reposting a slow one, no
  engagement groups or second accounts; reply to comments by hand.

## Cadence and profile

- Parts of a series go up as soon as each is ready, at most one release a
  day, so the teaser pays off while it is remembered.
- The bio never mentions how the videos are made and gives a concrete
  reason to follow: what the account posts, two of its real questions as
  examples, and how often, in short grammatical lines.
- The avatar is simple, bold and stylised, striking at 110 px. Its figure
  fills about half to two thirds of the circle, not more (an owner found a
  grid filling 59 percent of the width too big), and is centred by its
  visual weight, never by the bounding box: an asymmetric figure (a grid
  with one square pushed out) centred by its box sits visibly off to one
  side. Show it to the owner at full size and as the app shows it, a
  circle at about 160, 44 and 28 px on light and dark, and send the
  1080x1080 originals so they can upload and look before choosing.
- In the bio, "every day" (adverb) not "everyday" (adjective).
