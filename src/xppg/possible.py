"""Roster stints and possible games (D1, D2, D12, D16, D17).

A stint is a spell on one team within one season: [start, end), in dates.
Possible games for a stint = that team's games dated inside the stint.

How stint boundaries are set, in order of preference:
- Start: the latest joining transaction (signing, trade, waiver claim) with that
  team after the previous stint's end (or the season start) and on or before his
  first game for it; otherwise the season start. Never before his debut (D1).
- End: the first leaving transaction (waived, or traded away) after his last
  game for the team; otherwise 10 days after a 10-day contract signing; otherwise
  the season end if he is on the team's end-of-season roster; otherwise the day
  after his last game, and the stint is flagged as undated (D16).
- A player traded before ever playing for his old team that season (for
  example, injured all season) gets a stint on the old team up to the trade.
- A player on an end-of-season roster with no games that season, who has
  already debuted, gets a stint with zero games played (D12).
- Two-way stints are flagged (D17): his latest contract with that team is a
  two-way contract.
"""

import pandas as pd

JOIN = ["Signing", "Trade", "AwardOnWaivers"]
DAY = pd.Timedelta(days=1)


def _latest_contract(moves, team_id, by):
    signed = moves[(moves.team_id == team_id) & moves.contract.notna() & (moves.date <= by)]
    return signed.iloc[-1] if len(signed) else None


def player_stints(season, games, team_dates, roster_team, moves, debut, season_start, season_end):
    """Stints for one player in one season.

    games: his game rows that season (may be empty); team_dates: {team_id: sorted dates};
    roster_team: team id on the end-of-season roster or None; moves: his transactions.
    """
    in_season = moves[(moves.date > season_start) & (moves.date <= season_end)]
    spans = (games.groupby("team_id").game_date.agg(["min", "max"]).sort_values("min")
             if len(games) else pd.DataFrame(columns=["min", "max"]))
    teams = list(spans.index)
    if roster_team is not None and roster_team not in teams:
        teams.append(roster_team)  # on the end roster without a game for that team

    stints, prev_end = [], season_start
    for i, team in enumerate(teams):
        first = spans.loc[team, "min"] if team in spans.index else None
        last = spans.loc[team, "max"] if team in spans.index else None
        upper = first if first is not None else season_end

        joins = in_season[(in_season.team_id == team) & in_season.type.isin(JOIN)
                          & (in_season.date >= prev_end) & (in_season.date <= upper)]
        start, start_dated = (joins.date.iloc[-1], True) if len(joins) else (prev_end, i == 0)

        # traded here before ever playing for the old team this season
        if i == 0 and len(joins) and joins.iloc[-1].type == "Trade" and pd.notna(joins.iloc[-1].from_team_id):
            stints.append(dict(team_id=int(joins.iloc[-1].from_team_id), start=season_start, end=start,
                               dated=True, ten_day=False))

        end, dated, ten_day = None, True, False
        if last is not None:
            nxt = spans.loc[teams[i + 1], "min"] if i + 1 < len(teams) and teams[i + 1] in spans.index else season_end
            leaves = in_season[(in_season.date > last) & (in_season.date <= nxt)
                               & (((in_season.type == "Waive") & (in_season.team_id == team))
                                  | ((in_season.type == "Trade") & (in_season.from_team_id == team)))]
            contract = _latest_contract(moves, team, last)
            if len(leaves):
                end = leaves.date.iloc[0]
            elif contract is not None and contract.contract == "10-Day Contract":
                end, ten_day = max(contract.date + pd.Timedelta(days=10), last + DAY), True
            elif team == roster_team and i == len(teams) - 1:
                end = season_end + DAY
            else:
                end, dated = last + DAY, False
        else:
            end = season_end + DAY  # end-roster team with no games: there to the end

        stints.append(dict(team_id=team, start=start, end=end, dated=dated and start_dated, ten_day=ten_day))
        prev_end = end

    out = []
    for s in stints:
        s["start"] = max(s["start"], debut)  # D1: nothing counts before his debut
        dates = team_dates.get(s["team_id"], [])
        s["possible"] = sum(s["start"] <= d < s["end"] for d in dates)
        s["played"] = int((games.team_id == s["team_id"]).sum()) if len(games) else 0
        c = _latest_contract(moves, s["team_id"], s["end"])
        s["two_way"] = bool(c is not None and c.contract == "Two-Way Contract")
        s["season"] = season
        out.append(s)
    return out


def build_stints(P, T, R, M, debut):
    """All stints for every player in the pool, every season in P."""
    rows = []
    for season, games_s in P.groupby("season"):
        T_s = T[T.season == season]
        start, end = T_s.game_date.min(), T_s.game_date.max()
        team_dates = {t: sorted(d) for t, d in T_s.groupby("team_id").game_date}
        roster = R[R.season == season].drop_duplicates("player_id").set_index("player_id").team_id
        played = set(games_s.player_id)
        zero = [p for p in roster.index if p not in played and debut.get(p, pd.Timestamp.max) < start]
        by_player = dict(tuple(games_s.groupby("player_id")))
        empty = games_s.iloc[0:0]
        moves = dict(tuple(M.groupby("player_id")))
        no_moves = M.iloc[0:0]
        for pid in list(by_player) + zero:
            g = by_player.get(pid, empty)
            for s in player_stints(season, g, team_dates, roster.get(pid), moves.get(pid, no_moves),
                                   debut.get(pid, g.game_date.min()), start, end):
                rows.append(dict(player_id=pid, **s))
    st = pd.DataFrame(rows)
    st = st[st.possible > 0].reset_index(drop=True)  # drop zero-length leftovers
    assert (st.played <= st.possible).all(), "a stint has more games played than possible"
    return st


def player_seasons(stints, P, R):
    """One row per player-season: games, possible games, points, minutes and the four measures."""
    agg = stints.groupby(["season", "player_id"]).agg(
        possible_games=("possible", "sum"), teams=("team_id", "nunique"),
        undated=("dated", lambda x: not x.all()), two_way=("two_way", "any"), ten_day=("ten_day", "any"))
    box = P.groupby(["season", "player_id"]).agg(gp=("game_id", "nunique"), pts=("pts", "sum"), min=("min", "sum"))
    df = agg.join(box).fillna({"gp": 0, "pts": 0, "min": 0}).reset_index()
    names = pd.concat([P[["player_id", "player_name"]], R[["player_id", "player_name"]]]).drop_duplicates("player_id")
    df = df.merge(names, on="player_id", how="left")
    df[["gp", "pts", "min"]] = df[["gp", "pts", "min"]].astype(int)
    df["ppg"] = df.pts / df.gp.where(df.gp > 0)
    df["pppg"] = df.pts / df.possible_games
    df["ppm"] = df.pts / df["min"].where(df["min"] > 0)
    df["pppm"] = df.pts / (48 * df.possible_games)  # D3
    df["availability"] = df.gp / df.possible_games
    return df
