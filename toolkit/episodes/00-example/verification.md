# 00-example: verification log

Every fact said, shown or written in the example, checked against its
source. The example is a demonstration of the grammar, not an episode, so
its figures are few; they are still checked the way an episode's are.
Sources checked 2026-10-21.

| Source | File | SHA-256 |
|---|---|---|
| Project Gutenberg eBook #1342, Jane Austen, *Pride and Prejudice* (released June 1, 1998) | `https://www.gutenberg.org/cache/epub/1342/pg1342.txt` | 3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75 |
| Project Gutenberg eBook #1228, Charles Darwin, *On the Origin of Species*, the 1859 first edition (released March 1, 1998) | `https://www.gutenberg.org/cache/epub/1228/pg1228.txt` | 362142cb7c6f90850477520cfe2a62fe423ae92ea8eb6d9cd8b30ddb39de60b9 |
| Dziewonski and Anderson, "Preliminary reference Earth model", *Physics of the Earth and Planetary Interiors* 25 (1981), 297 to 356 | the paper's Table 1 | |

## Narration

| Fact | Claim used (as worded) | Re-check (source, quote, recomputation) | Result |
|---|---|---|---|
| F01 | "1813 sits well before 1859" (the novel's year) | #1342, the 1894 edition's preface: "was not published till 1813, only four years before her death" | Confirmed; said "1813", shown "1813" |
| F02 | "1813 sits well before 1859" (the Origin's year) | #1228, title page: "LONDON: JOHN MURRAY, ALBEMARLE STREET. 1859."; the file is the 1859 first edition ("1228    1859, First Edition") | Confirmed; said "1859", shown "1859" |
| F04 | "there is grandeur in this view of life" | #1228, final paragraph: "There is grandeur in this view of life, with its several powers, having been originally breathed into a few forms or into one" | Confirmed; read as written, the sentence cut with an ellipsis after "life", which keeps its meaning |
| F06 | "Watch this shape slide to the equator" (it keeps its true size) | CALC: `slide` in `studio/src/lib/geo.ts` rotates the shape on the sphere; a rotation preserves area, and the re-projected shape shrinks on Mercator as it nears the equator | Confirmed |

## On screen only

| Text | Check | Result |
|---|---|---|
| The page: "It is a truth universally acknowledged, that a single man in possession of a good fortune must be in want of a wife." and the paragraph after it | F03: #1342, Chapter I, the first two paragraphs, word for word (no comma after "fortune") | Confirmed; the heading "Chapter I" as the edition prints it |
| "Jane Austen, Pride and Prejudice, 1813 (Project Gutenberg)" | F01 | Confirmed |
| "Charles Darwin, On the Origin of Species, 1859" | F02 | Confirmed |
| Timeline: "Pride and Prejudice" at 1813, "On the Origin of Species" at 1859, on a scale from 1800 to 1900 | F01, F02; positions are proportional to the year | Confirmed |
| The globe's cut-away layers: inner core, outer core, lower and upper mantle, crust | F05: PREM, inner core radius 1,221.5 km, core-mantle boundary 3,480 km, the 660 km discontinuity, mean radius 6,371 km; the crust is drawn 51 km thick (continental crust runs about 30 to 70 km) | Confirmed; no figure is said or labelled |
| "Earth’s centre", "New York", "Greenland", "Equator" | labels at their places: New York at 40.75° N, 73.98° W; the centre at radius 0 | Confirmed |
| Bars at 40, 75 and 100 | illustrative values, labelled "First", "Second", "Third"; no claim | Not a fact |
| "Example Company" and its mark | a placeholder, credited on screen "A placeholder mark, not a real company" | Not a fact |

## Release text

The example has no release.

Not said: the novel's and the Origin's later editions; PREM's figures.

## Re-checks

2026-10-21: written with the example's beats; every row above checked
against the files whose SHA-256 is recorded.
