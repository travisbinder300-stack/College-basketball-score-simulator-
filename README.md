# College-basketball-score-simulator-
Basketball-simulator

---

## NBA Playtype Player Prop Generator

`nba_playtype_props.py` generates NBA player prop recommendations by comparing a
player's play-type tendencies against the opposing team's defensive efficiency for
each play type, and by surfacing similar players who share the same position and
offensive profile.

### How it works

| Step | What happens |
|------|-------------|
| 1 | Each player is described by a **play-type frequency vector** (e.g. 32 % isolation, 28 % pick-and-roll ball-handler, …) and per-type PPP. |
| 2 | Each team's defense is described by **PPP allowed per play type** (lower = better). |
| 3 | A **matchup multiplier** is computed as the frequency-weighted defensive PPP relative to league average. |
| 4 | Season averages for points, assists and rebounds are scaled by the multiplier to produce **projected lines**. |
| 5 | **Similar players** are found using a blend of position match (40 %) and cosine similarity of play-type vectors (60 %). |
| 6 | Each prop gets an **edge** (projection − bookmaker line) and a **confidence** rating (HIGH / MEDIUM / LOW). |

### Play types supported

`isolation`, `pnr_ball_handler`, `pnr_screener`, `post_up`, `spot_up`,
`off_screen`, `hand_off`, `cut`, `putback`, `misc`

### Quick start

```python
from nba_playtype_props import (
    build_sample_players, build_sample_defenses, analyze_matchup
)

players  = build_sample_players()
defenses = build_sample_defenses()

sga    = next(p for p in players  if "Gilgeous" in p.name)
mem_d  = next(d for d in defenses if d.team == "MEM")

result = analyze_matchup(sga, mem_d, players)
for rec in result["prop_recommendations"]:
    print(rec)
```

Or run the built-in demo:

```
python nba_playtype_props.py
```

### Running tests

```
python -m unittest test_nba_playtype_props -v
```
