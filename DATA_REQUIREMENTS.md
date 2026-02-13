# Data Requirements - 2025-26 Season Only

## ⚠️ CRITICAL: Current Data Only

**This system MUST use current 2025-26 season data.** Using outdated data from previous seasons (2023-24, 2024-25, etc.) will produce inaccurate predictions and poor betting decisions.

## Why Current Data Matters

1. **Team Composition Changes** - Rosters change every year due to:
   - Player graduation
   - Transfers (transfer portal)
   - NBA draft departures
   - Recruiting classes
   - Coaching changes

2. **Playing Style Evolution** - Teams evolve:
   - New offensive/defensive systems
   - Tempo changes
   - Strategic adjustments
   - Personnel-driven adaptations

3. **Strength of Schedule** - Varies by season:
   - Conference realignment
   - Non-conference scheduling
   - Tournament seeding
   - Head-to-head matchups

4. **Betting Markets** - Lines are set for current season:
   - Oddsmakers use current data
   - Public perception based on current performance
   - Value opportunities exist in current market only

## Required Data Sources (2025-26 Season)

### Primary Sources

**1. KenPom.com**
- Offensive/defensive efficiency ratings
- Tempo and pace statistics
- Adjusted efficiency metrics
- Four Factors
- **Update Frequency:** Daily

**2. TeamRankings.com**
- ATS records (overall, home/away, favorite/underdog)
- Team rankings and trends
- Schedule difficulty
- Statistical trends
- **Update Frequency:** Daily after games

**3. BartTorvik.com**
- Alternative efficiency metrics
- Player ratings
- Strength of schedule
- Tournament projections
- **Update Frequency:** Daily

**4. Sports-Reference.com (CBB-Reference)**
- Traditional statistics (PPG, RPG, APG)
- Team records and results
- Player statistics
- Historical game data
- **Update Frequency:** Daily

### Secondary Sources

- **ESPN.com** - Injury reports, news, game recaps
- **NCAA.com** - Official statistics and records
- **Conference websites** - Team news and updates
- **Team websites** - Injury reports, roster changes

## Data Update Schedule

### Daily Updates Required
- Game results and scores
- ATS records
- Efficiency ratings
- Team rankings
- Injury reports

### Weekly Updates Required
- Power ratings recalculation
- Strength of schedule adjustments
- Trend analysis
- Conference standings

### Monthly Updates Required
- Season-long statistics review
- Model calibration
- Historical performance analysis
- Database maintenance

## Data Validation Checklist

Before making predictions, verify:

- [ ] All team statistics are from 2025-26 season
- [ ] ATS records reflect current season games only
- [ ] Injury reports are up-to-date (within 24 hours)
- [ ] Recent form includes only current season games
- [ ] Power ratings calculated from current season data
- [ ] Strength of schedule based on current season opponents
- [ ] No data from 2024-25 or earlier seasons is being used

## Common Mistakes to Avoid

❌ **DO NOT:**
- Use last season's efficiency ratings
- Reference old ATS records
- Apply previous season's power ratings
- Use outdated roster information
- Rely on pre-season projections late in season
- Mix data from multiple seasons

✅ **DO:**
- Verify data date stamps
- Check for roster changes
- Update after every game day
- Cross-reference multiple sources
- Validate injury reports
- Use current season context only

## Sample Data Currency Check

When using the system, always verify:

```python
# Good - Current season reference
manhattan_stats = {
    "season": "2025-26",
    "last_updated": "2026-02-13",
    "source": "KenPom.com",
    "offensive_efficiency": 103.5
}

# Bad - Old season reference
manhattan_stats = {
    "season": "2023-24",  # ❌ OLD DATA
    "last_updated": "2024-03-15",  # ❌ OUTDATED
    "offensive_efficiency": 103.5
}
```

## Data Quality Standards

### Minimum Requirements
- **Timeliness:** Within 24 hours of latest games
- **Completeness:** All key statistics available
- **Accuracy:** Cross-referenced with multiple sources
- **Consistency:** Same season across all metrics

### Best Practices
- Record data source and timestamp
- Document any estimated or incomplete data
- Flag teams with limited game history
- Note significant recent changes (injuries, suspensions)
- Track data quality over time

## Emergency Procedures

**If Current Data Unavailable:**
1. Do NOT use old season data as substitute
2. Wait for current season data to become available
3. If urgent, clearly mark predictions as "incomplete data"
4. Reduce confidence level and bet sizing
5. Consider avoiding that game entirely

**If Data Conflicts:**
1. Use most recent source
2. Cross-reference with official NCAA statistics
3. Check team/conference official sources
4. Document discrepancy
5. Use conservative estimate

## Conclusion

**The accuracy of this system depends entirely on using current 2025-26 season data.** 

Old data produces old predictions. Current data produces actionable insights.

**Last Updated:** 2026-02-13
**Current Season:** 2025-26
**Next Review:** End of 2025-26 season
