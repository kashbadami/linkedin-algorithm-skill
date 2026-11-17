# LinkedIn algorithm check: a free skill for Claude (and ChatGPT)

LinkedIn now reads every post with a large language model before anyone sees it. The model decides what your post is about, who it's for, and whether it's bait. This skill checks your draft against the ten things that decide reach, then rewrites it to pass in your voice.

Paste a draft and you get back:
- **a scorecard:** pass, warn or block on each of the ten vectors, with the reason
- **a rewrite** that clears every block, keeping your facts and words
- **a list of what changed**, each change tied to a vector
- **a posting note:** the time slot to keep, and the first hour of replies

## The ten vectors

| # | What LinkedIn does | What the skill enforces |
|---|---|---|
| 1 | An LLM reads the post and matches it to readers | Topic and reader plain in the first 3 lines |
| 2 | Skip model: a fast scroll-past lowers the score | Line 1 of 18 words or fewer, payoff held for later, carousel past ~1,800 characters |
| 3 | Engagement bait is filtered | No "comment X and I'll send it", "Agree?" or "tag a friend"; the giveaway ask goes on the image |
| 4 | A quality classifier tags the post before ranking | No machine-written phrasing |
| 5 | No reward for reaching everyone | Written for one professional group |
| 6 | Excessive tagging is a low-quality trigger | Tag only people in the post |
| 7 | Comment weight is tuned live | Close on a question with two sides |
| 8 | Your network caps in-network reach | Connect inside your topic (advice) |
| 9 | Your profile tells LinkedIn who you write for | The post matches your headline |
| 10 | Posting too often competes with yourself | One post a day, same time, reply for the first hour |

It also blocks a link in the post body.

## How we tested it

**1. Every vector has a test case: 16 of 16 pass.** `tests/cases.json` holds one clean post that must pass with zero findings, plus 15 broken posts. Each broken post must trip its exact vector at the exact severity. Run it with `python3 tests/run_tests.py`:

```
ok    vector all   expect pass   clean post passes
ok    vector 1+5   expect block  no reader named in first 3 lines
ok    vector 2     expect warn   long first line
ok    vector 2     expect warn   over 1,800 characters
ok    vector 3     expect block  comment-a-keyword ask
ok    vector 3     expect block  capitalized keyword ask
ok    vector 3     expect block  one-word bait question
ok    vector 3     expect block  tag-a-friend bait
ok    vector 4     expect block  machine-written phrasing
ok    vector 6     expect block  four tags
ok    vector 6     expect warn   two tags
ok    vector 7     expect warn   no closing question
ok    vector 7     expect warn   generic closing question
ok    vector 9     expect warn   off-headline topic
ok    vector 10    expect block  second post today
ok    vector link  expect block  link in body

16/16 passed
```

**2. End to end: Claude ran the skill on a bad draft, and the checker graded the rewrite.** We wrote a draft that breaks seven rules ([`tests/e2e/draft.txt`](tests/e2e/draft.txt)). It has an AI opener, a "Comment HIRE and I'll send" ask, four tags, a link in the body and a "Thoughts?" close. Claude (Sonnet) loaded the skill, scored the draft and rewrote it. Its full output is in [`tests/e2e/claude-output.md`](tests/e2e/claude-output.md). We then ran the checker on the rewrite independently, so the model wasn't grading its own work.

| | Blocks | Warns | Result |
|---|---|---|---|
| Draft | 5 | 2 | FAIL |
| Claude's rewrite | 0 | 0 | PASS |

The rewrite:

```
Founders hiring a first salesperson: stop hiring for the pitch.

Most founders get it wrong. They hire for the pitch. The good hires come with a list of accounts they already know how to work.

Free access to my first-sales-hire checklist and full guide is in the comments.

Pitch or account list: which would you hire first?
```

**3. On our own posts.** The same checker gates every LinkedIn post we publish before it goes out.

## Install

**Claude (desktop app or claude.ai)**
1. Download [`dist/linkedin-algorithm.zip`](dist/linkedin-algorithm.zip).
2. In Claude, open Settings → Capabilities → Skills and upload the zip.
3. Start a chat: "Check this LinkedIn post" and paste your draft.

**Claude Code:** tell Claude "install the skill from github.com/kashbadami/linkedin-algorithm-skill".

**ChatGPT:** create a custom GPT or a project. Paste [`chatgpt/instructions.md`](chatgpt/instructions.md) into its instructions, upload [`chatgpt/check.py`](chatgpt/check.py) as a file, and turn on code.

## Sources
- LinkedIn, ["How LinkedIn Is Improving the Feed"](https://news.linkedin.com/2026/ImprovingTheFeed) (2026). Confirms LLM-based ranking and less engagement bait, with "comment to agree" prompts as an example.
- Vedika Bhaia's [2027 LinkedIn algorithm update](https://lnkd.in/p/gsGPGytd). The ten vectors come from her post. The skip model, the classifier tags, the tagging and frequency triggers, and profile matching come from her post and are not yet confirmed by LinkedIn.

## License
MIT. Use it, fork it, ship it.

Built by [Kash Badami](https://www.linkedin.com/in/kashbadami/). More GTM playbooks at [gtm.gobridgehead.ai](https://gtm.gobridgehead.ai).
