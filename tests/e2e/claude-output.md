I couldn't write the rewrite to a file, so I didn't run the script on it. I checked the rewrite against the table by hand.

Draft check: `check.py` ran on `tests/e2e/draft.txt` and exited 1 with 5 blocks and 2 warns. Reader: founders hiring their first salesperson. Posted today: no.

## Scorecard

| # | Result | Reason |
|---|---|---|
| 1 | pass | The reader is named in line 1 of the draft. |
| 2 | warn | Line 1 is 26 words (limit 18). |
| 3 | **BLOCK** | "Comment HIRE and I'll send you my checklist" is a comment-to-get ask. "Thoughts?" is also bait. |
| 4 | **BLOCK** | "In today's fast-paced world" and "game-changer" read as machine-written. |
| 5 | pass | Written for one group, founders. |
| 6 | **BLOCK** | 4 tags: @Amy, @Bob, @Cat, @Dan. None appear in the post body. |
| 7 | warn | "Thoughts?" is generic. The close needs two sides. |
| 8 | n/a | Advice only. Connect with founders and sales leaders. |
| 9 | pass | The topic matches your headline. |
| 10 | pass | No other post today. |
| link | **BLOCK** | `example.com/hiring` is in the body. |

## Rewrite

===REWRITE===
Founders hiring a first salesperson: stop hiring for the pitch.

Most founders get it wrong. They hire for the pitch. The good hires come with a list of accounts they already know how to work.

Free access to my first-sales-hire checklist and full guide is in the comments.

Pitch or account list: which would you hire first?
===END===

Put `example.com/hiring` in the first comment.

## What changed
- **Vector 4:** cut "In today's fast-paced world", "game-changer" and "I wanted to share some thoughts". Kept your two real sentences about the pitch and the account list.
- **Vector 2:** line 1 is now 10 words, down from 26. It names the reader and gives a take.
- **Vector 3:** removed "Comment HIRE". The text now says "Free access … in the comments". If you want a comment-to-get ask, put it on an image, not in the text.
- **Vector 6:** dropped all 4 tags. Re-add one only if that person is in the post.
- **Link:** moved the URL out of the body into the first comment.
- **Vector 7:** replaced "Thoughts?" with a two-sided question, "Pitch or account list?".

I assumed the checklist and the full guide are the same free resource, both at that link. Fix the third line if they aren't.

## Posting note
Pick one time slot and keep it every day. Reply to every comment in the first hour. Post the link comment yourself right after publishing.
