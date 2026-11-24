# Stat per possible game (XPPG)

How much is a great player worth if he is often unavailable?

Points per game only counts the games a player plays. This project counts the games he **could** have played. A player who scores 30 a game but misses half the season gives his team fewer points than his average suggests, and his team still has to play those games without him.

## The metric

**XPPG** = season total of a stat ÷ possible games, where X is any counting stat (points, rebounds, assists and so on).

- **Possible games** start at the player's NBA debut. After that, every missed game counts, whatever the reason.
- **PPPG** (points per possible game) = PPG × the share of possible games he played.
- **PPM** = points per minute played. **PPPM** = points per possible minute, with 48 possible minutes per possible game.

Every methodological choice is recorded in [docs/DECISIONS.md](docs/DECISIONS.md).

## Thesis

Not every all-star is worth keeping. A star who is often unavailable, or who takes up so many minutes that teammates lose opportunities, may cost his team wins even while averaging 27+ points.

## Status

Set-up done. Model 1 (points only: PPG against PPPG, PPM against PPPM, whole league, per season) is next.

## Reproducing

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

Then run the notebooks in `notebooks/` in order. Data comes from NBA.com through [nba_api](https://github.com/swar/nba_api) and is cached under `data/raw/`, which is not in git.
