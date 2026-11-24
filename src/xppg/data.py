"""Download and tidy the raw tables Model 1 needs (D13, D14).

Everything goes through the cache in raw.py, so each request is made once.
The season in progress is re-downloaded on request (refresh=True), because
its cached copy goes out of date every day.
"""

import gzip
import json
from datetime import datetime, timezone

import pandas as pd
import requests
from nba_api.stats.endpoints import commonteamroster, leaguegamelog
from nba_api.stats.static import teams as static_teams

from xppg.raw import RAW_DIR, fetch

FEED_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nba.com/"}

COMPLETE_SEASONS = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]  # D14
IN_PROGRESS = "2026-27"  # shown separately, never mixed into complete seasons
SEASONS = COMPLETE_SEASONS + [IN_PROGRESS]


def _game_log(season, who, refresh):
    df = fetch(
        leaguegamelog.LeagueGameLog,
        refresh=refresh,
        season=season,
        season_type_all_star="Regular Season",  # D13
        player_or_team_abbreviation=who,
    )["LeagueGameLog"]
    df.columns = df.columns.str.lower()
    df["game_date"] = pd.to_datetime(df["game_date"])
    df.insert(0, "season", season)
    return df


def player_games(season, refresh=False):
    """One row per player per game he appeared in (players who did not play have no row)."""
    return _game_log(season, "P", refresh)


def team_games(season, refresh=False):
    """One row per team per game played."""
    return _game_log(season, "T", refresh)


def season_label(start_year):
    """1996 -> "1996-97"."""
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def debuts(first_year=1996):
    """Each player's NBA debut (first regular-season game), for D1.

    Uses game logs back to 1996-97 plus the study seasons. NBA.com's FROM_YEAR
    is the draft season, not the debut (Embiid: 2014, debut 2016), so it is not used.
    Every player in the study's pool debuted after 1996.
    """
    seasons = [season_label(y) for y in range(first_year, 2020)] + SEASONS
    frames = [player_games(s)[["player_id", "game_date"]] for s in seasons]
    return pd.concat(frames).groupby("player_id").game_date.min().rename("debut")


MOVEMENT_URL = "https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json"
MOVEMENT_CACHE = RAW_DIR / "PlayerMovement" / "NBA_Player_Movement.json.gz"


def player_movement(refresh=False):
    """Dated trades, waivers and signings since July 2015 (D16).

    NBA.com's transactions feed, which nba_api does not wrap. It is a single
    living file, so it is cached once and downloaded again only on request.
    """
    if refresh or not MOVEMENT_CACHE.exists():
        response = requests.get(MOVEMENT_URL, headers=FEED_HEADERS, timeout=60)
        response.raise_for_status()
        record = {"url": MOVEMENT_URL, "fetched_at": datetime.now(timezone.utc).isoformat(),
                  "response": response.json()}
        MOVEMENT_CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = MOVEMENT_CACHE.with_suffix(".tmp")
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            json.dump(record, f)
        tmp.replace(MOVEMENT_CACHE)
    with gzip.open(MOVEMENT_CACHE, "rt", encoding="utf-8") as f:
        record = json.load(f)

    df = pd.DataFrame(record["response"]["NBA_Player_Movement"]["rows"])
    df = df[df.PLAYER_ID.notna() & (df.PLAYER_ID > 0)]  # drops draft-pick and cash rows
    desc = df.TRANSACTION_DESCRIPTION
    out = pd.DataFrame({
        "date": pd.to_datetime(df.TRANSACTION_DATE),
        "type": df.Transaction_Type,
        "player_id": df.PLAYER_ID.astype(int),
        "team_id": df.TEAM_ID.astype("Int64"),
        # contract named in a signing or conversion, e.g. "Two-Way Contract", "10-Day Contract"
        "contract": desc.str.extract(r" to an? ([A-Za-z0-9\- ]*Contract)")[0],
        # for trades, the team the player came from
        "from_team": desc.where(df.Transaction_Type == "Trade").str.extract(r" from (.+?)\.?$")[0],
        "description": desc,
    })
    names = {t["full_name"]: t["id"] for t in static_teams.get_teams()}
    names["LA Clippers"] = names["Los Angeles Clippers"]
    out["from_team_id"] = out.from_team.map(names).astype("Int64")
    out.attrs["fetched_at"] = record["fetched_at"]
    return out.sort_values(["date", "player_id"]).reset_index(drop=True)


def rosters(season, team_ids, refresh=False):
    """Roster snapshot for each team. NBA.com gives no join or leave dates (D12 caveat)."""
    frames = []
    for team_id in team_ids:
        df = fetch(commonteamroster.CommonTeamRoster, refresh=refresh, team_id=int(team_id), season=season)[
            "CommonTeamRoster"
        ]
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df.columns = df.columns.str.lower()
    df = df.rename(columns={"teamid": "team_id", "player": "player_name"})
    df = df.drop(columns="season")  # NBA.com gives "2020"; use the project's "2020-21" form
    df.insert(0, "season", season)
    return df
