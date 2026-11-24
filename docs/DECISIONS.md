# Methodological decisions

Every significant choice made in the project, with the reason or the caveat behind it. Add new decisions at the bottom; never rewrite history. A revised decision is struck through and dated, with the new rule beside it.

Decided on 24 November 2026 unless dated otherwise.

## Decided

| # | Decision | Rationale / caveat |
|---|---|---|
| D1 | **Possible games start at the player's first possibly healthy game,** taken as his NBA debut | A false start should not be held against a young player (for example, Embiid missed 2014-15 and 2015-16 after the draft). From the debut on, every missed game counts. Counting from the draft is kept as a later variant (TODO). |
| D2 | **Every missed game after the start counts against the player, whatever the reason:** injury, rest, suspension or coach's decision | Suspensions and coach's punishments are self-inflicted; availability is the player's responsibility. Consequence: Model 1 does not need the reasons for absences, so no per-game box-score downloads are needed. |
| D3 | **A possible minute = 48 per possible game.** Every healthy player could play 48 minutes, even though none does | Caveat: PPPM = PPPG ÷ 48, so PPPM and PPPG rank players identically. PPM (points per minute played) still differs from both. Overtime is ignored for now. |
| D4 | **XPPG is general:** X is any counting stat (PPPG, RPPG, APPG, SPPG and so on). XPPG = season total of X ÷ possible games | One definition serves every stat. Model 1 uses points only (D6). Note: XPPG = X per game played × availability rate (games played ÷ possible games). |
| D5 | **Unit of analysis = one player-season** | Per-season keeps the first model simple. Careers and rolling windows can come later. |
| D6 | **Value means wins in the end. Model 1 is points only and deliberately as simple as possible:** PPG against PPPG, plus PPM and PPPM | Points are what every reader knows. The step from points to wins belongs to a later model. |
| D7 | **The thesis mechanism is minute dominance** (a star taking minutes from teammates), not usage | Note: NBA.com does publish usage rate (USG%) through `LeagueDashPlayerStats` with the Advanced measure type, so usage could be added later if wanted. |
| D8 | **The "efficient team" is tested by simulating a season.** Design deferred | Not needed until Model 1 is done. Note: building a team "knowing what we know now" is a hindsight exercise and must be described as one. |
| D9 | **Pool = the whole league:** no minimum games or minutes filter | We need to see everyone. Thresholds can be added later as toggles, for display only. |
| D10 | **Finances (salaries) deferred** | nba_api has no salary data. A second source will be needed (Basketball Reference, Spotrac or HoopsHype). |
| D11 | **Publication: the GitHub README first, a Substack write-up later** | The README is the public record of findings. The repository is public. |
| D12 | **A season's possible games = the games his team(s) played while he was on the roster** (was O1). Covers traded players, mid-season signings and players waived mid-season. A player on a roster for a whole season without playing counts at zero games played | Caveat: NBA.com has no roster dates. Stints will be worked out from game logs and roster snapshots; how gaps around trades are split is an implementation choice to be shown to the user before use. |
| D13 | **Regular season only** (was O2) | Playoffs are a different question and are left out of Model 1. |
| D14 | **Seasons: 2020-21 onwards,** six complete seasons to 2025-26; 2026-27 shown separately as a season in progress (was O3) | Start small. Skips 2019-20, when the season was suspended, only 22 teams entered the bubble and teams played 63 to 75 games. 2020-21 was still 72 games, which possible games handle. For players who debuted earlier, possible games simply start at 2020-21. |
| D15 | **COVID health and safety protocol absences count against the player** (2020-21, 2021-22), as D2 requires | Keeps Model 1 simple: no absence reasons needed. On the revisit list: a sensitivity check without protocol games, and a caveat in the README. |

## Open (to be decided before the numbers are run)

| # | Question | Recommendation |
|---|---|---|
| | None at present | |
