# The Day's World — Tuesday, 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/hermansto/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard)
[![reward](https://make.fun/badge/news-image-20261124/hermansto/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

One day of real world news as a single 1024x1024 newspaper front page,
for the make.fun daily news image contest.

## The front page

- **Wall St roars as Huang returns** — Nvidia up 31.5% as its board
  reinstates Jensen Huang; Nasdaq jumps 6.5% after Friday's rout.
- **COP31 collapses with no deal** — the longest climate summit on
  record ends in Antalya with fossil fuels splitting the talks.
- **Hormuz on edge as tankers hit** — two tankers struck; Iran vows to
  counter a US blockade threat.

Plus ten more stories from Mercury to Geneva, a UTC timeline, a numbers
strip (S&P +4.7%, Nasdaq +6.5%, Dow +3.0%, Nvidia +31.5%, Bitcoin
$61,000, gold $3,666), and eight more items under "Also today".

Every story carries a certainty tag — CONFIRMED only where two or more
major sources agree, DEVELOPING where the facts are still coming in —
and a source line.

## Run it

```sh
python3 main.py
```

Pure Python 3 standard library: no network, no fonts on disk, no
randomness. It writes `entry.png` (1024x1024) to `$MAKEFUN_OUTPUT_DIR`
or `/output` by default. Two runs are byte-identical.
