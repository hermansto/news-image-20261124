# The World Ledger — 24 November 2026

[![Bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/hermansto/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/hermansto/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-page newspaper front page for Tuesday, 24 November 2026, drawn
entirely in code. No photographs, no downloaded pictures, no faces.

## The four stories

All four were checked against the Reuters world-news summary for
24 November 2026, and each one carries its source line on the page:

1. **Zelenskiy confirms Ukraine hit Russian ship in Gulf of Finland** —
   the Ukrainian president confirmed on Tuesday that Ukraine was behind
   a drone strike on a Russian cargo ship; Norway urged caution.
2. **Israeli strike kills Hamas security chief in Gaza** — Naeem Abu
   Nahel, director of Hamas' internal security apparatus, was killed
   with six others, including two police officers, medics and police said.
3. **Russian attack kills two in Zaporizhzhia** — an overnight attack
   killed two people and wounded 40, including four children, and struck
   an apartment building, the regional governor said.
4. **Houthis 60 km from Aden, Yemeni forces say city will hold** —
   Houthi fighters pushed to within 60 km of Aden, Yemen's military said,
   and the military said the city will not be captured.

Nothing unconfirmed is printed as fact. Details that could not be
verified are left out entirely.

## How it is made

`main.py` uses only the Python standard library and Pillow. Every
illustration — the ship at sea, the town blocks, the two bars for the
Zaporizhzhia figures, and the Aden coastline sketch — is drawn with
shapes. Text is wrapped by measuring it with the font first, so no
two text bands overlap.

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/news24-rebuild2-out python3 main.py
```

It writes only `entry.png` into that output directory, then reads the
file back and checks it is 1024x1024. Two runs give a byte-identical
file: there are no timestamps and no unseeded randomness in the image.

## Licence

MIT — see `LICENSE`.
