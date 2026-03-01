"""
Unit tests for nba_playtype_props.py
"""

import unittest
from nba_playtype_props import (
    PlayTypeStats,
    PlayerProfile,
    DefensiveMatchup,
    DefensiveIsolationStats,
    build_sample_players,
    build_sample_defenses,
    build_defensive_isolation_rankings,
    rank_teams_by_isolation_defense,
    compute_similarity,
    find_similar_players,
    _matchup_multiplier,
    project_props,
    analyze_matchup,
)


class TestPlayTypeStats(unittest.TestCase):
    def test_defaults(self):
        pts = PlayTypeStats()
        self.assertEqual(pts.frequency, 0.0)
        self.assertEqual(pts.ppp, 0.0)
        self.assertEqual(pts.percentile, 50.0)

    def test_custom_values(self):
        pts = PlayTypeStats(frequency=0.3, ppp=1.1, percentile=80.0)
        self.assertAlmostEqual(pts.frequency, 0.3)
        self.assertAlmostEqual(pts.ppp, 1.1)
        self.assertAlmostEqual(pts.percentile, 80.0)


class TestPlayerProfile(unittest.TestCase):
    def setUp(self):
        self.player = PlayerProfile(
            name="Test Player",
            position="PG",
            team="TST",
            avg_points=20.0,
            avg_assists=5.0,
            avg_rebounds=4.0,
            play_types={
                "isolation":        PlayTypeStats(frequency=0.40, ppp=1.10, percentile=80),
                "pnr_ball_handler": PlayTypeStats(frequency=0.30, ppp=1.00, percentile=65),
                "spot_up":          PlayTypeStats(frequency=0.20, ppp=1.05, percentile=70),
                "misc":             PlayTypeStats(frequency=0.10, ppp=0.90, percentile=50),
            },
        )

    def test_dominant_play_types_order(self):
        dom = self.player.dominant_play_types(top_n=2)
        self.assertEqual(dom[0], "isolation")
        self.assertEqual(dom[1], "pnr_ball_handler")

    def test_dominant_play_types_top_n(self):
        dom = self.player.dominant_play_types(top_n=3)
        self.assertEqual(len(dom), 3)

    def test_dominant_play_types_empty(self):
        empty_player = PlayerProfile(name="Empty", position="C", team="TST")
        dom = empty_player.dominant_play_types()
        self.assertEqual(dom, [])


class TestSampleData(unittest.TestCase):
    def test_sample_players_not_empty(self):
        players = build_sample_players()
        self.assertGreater(len(players), 0)

    def test_sample_players_have_play_types(self):
        players = build_sample_players()
        for p in players:
            self.assertGreater(len(p.play_types), 0)

    def test_sample_defenses_not_empty(self):
        defenses = build_sample_defenses()
        self.assertGreater(len(defenses), 0)

    def test_sample_defenses_have_play_types(self):
        defenses = build_sample_defenses()
        for d in defenses:
            self.assertGreater(len(d.play_types), 0)


class TestSimilarity(unittest.TestCase):
    def setUp(self):
        self.players = build_sample_players()

    def _get_player(self, name_fragment: str) -> PlayerProfile:
        return next(p for p in self.players if name_fragment in p.name)

    def test_self_similarity_is_high(self):
        sga = self._get_player("Gilgeous")
        score = compute_similarity(sga, sga)
        self.assertGreater(score, 0.9)

    def test_similar_position_scores_higher_than_different(self):
        sga = self._get_player("Gilgeous")   # PG
        luka = self._get_player("Doncic")    # PG
        jokic = self._get_player("Jokic")    # C
        pg_score = compute_similarity(sga, luka)
        c_score = compute_similarity(sga, jokic)
        self.assertGreater(pg_score, c_score)

    def test_find_similar_excludes_self(self):
        sga = self._get_player("Gilgeous")
        similar = find_similar_players(sga, self.players, top_n=3)
        names = [p.name for p, _ in similar]
        self.assertNotIn(sga.name, names)

    def test_find_similar_returns_correct_count(self):
        sga = self._get_player("Gilgeous")
        similar = find_similar_players(sga, self.players, top_n=2)
        self.assertEqual(len(similar), 2)

    def test_find_similar_sorted_descending(self):
        sga = self._get_player("Gilgeous")
        similar = find_similar_players(sga, self.players, top_n=5)
        scores = [s for _, s in similar]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestMatchupMultiplier(unittest.TestCase):
    def setUp(self):
        self.players = build_sample_players()
        self.defenses = build_sample_defenses()

    def _get_player(self, name_fragment: str) -> PlayerProfile:
        return next(p for p in self.players if name_fragment in p.name)

    def _get_defense(self, team: str) -> DefensiveMatchup:
        return next(d for d in self.defenses if d.team == team)

    def test_weak_defense_multiplier_above_one(self):
        """Memphis allows high PPP → multiplier > 1 for an offensive player."""
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        mult = _matchup_multiplier(sga, mem)
        self.assertGreater(mult, 1.0)

    def test_strong_defense_multiplier_below_one(self):
        """OKC/BOS allow low PPP → multiplier < 1 for an offensive player."""
        sga = self._get_player("Gilgeous")
        okc = self._get_defense("OKC")
        mult = _matchup_multiplier(sga, okc)
        self.assertLess(mult, 1.0)

    def test_empty_player_play_types_returns_one(self):
        empty_player = PlayerProfile(name="Empty", position="C", team="TST")
        mem = self._get_defense("MEM")
        mult = _matchup_multiplier(empty_player, mem)
        self.assertAlmostEqual(mult, 1.0)


class TestProjectProps(unittest.TestCase):
    def setUp(self):
        self.players = build_sample_players()
        self.defenses = build_sample_defenses()

    def _get_player(self, name_fragment: str) -> PlayerProfile:
        return next(p for p in self.players if name_fragment in p.name)

    def _get_defense(self, team: str) -> DefensiveMatchup:
        return next(d for d in self.defenses if d.team == team)

    def test_returns_three_props(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        props = project_props(sga, mem)
        self.assertEqual(len(props), 3)
        prop_types = {r.prop_type for r in props}
        self.assertEqual(prop_types, {"points", "assists", "rebounds"})

    def test_positive_edge_against_weak_defense(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        # Use season avg as lines so edge reflects pure matchup multiplier
        lines = {
            "points": sga.avg_points,
            "assists": sga.avg_assists,
            "rebounds": sga.avg_rebounds,
        }
        props = project_props(sga, mem, lines=lines)
        pts_prop = next(r for r in props if r.prop_type == "points")
        self.assertGreater(pts_prop.edge, 0)

    def test_confidence_levels_are_valid(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        props = project_props(sga, mem)
        valid = {"HIGH", "MEDIUM", "LOW"}
        for rec in props:
            self.assertIn(rec.confidence, valid)

    def test_custom_lines_affect_edge(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        high_line = {"points": 50.0}
        props = project_props(sga, mem, lines=high_line)
        pts_prop = next(r for r in props if r.prop_type == "points")
        self.assertLess(pts_prop.edge, 0)


class TestAnalyzeMatchup(unittest.TestCase):
    def setUp(self):
        self.players = build_sample_players()
        self.defenses = build_sample_defenses()

    def _get_player(self, name_fragment: str) -> PlayerProfile:
        return next(p for p in self.players if name_fragment in p.name)

    def _get_defense(self, team: str) -> DefensiveMatchup:
        return next(d for d in self.defenses if d.team == team)

    def test_result_keys(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        result = analyze_matchup(sga, mem, self.players)
        for key in ("player", "position", "opponent", "dominant_play_types",
                    "similar_players", "prop_recommendations"):
            self.assertIn(key, result)

    def test_result_player_name(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        result = analyze_matchup(sga, mem, self.players)
        self.assertEqual(result["player"], sga.name)

    def test_similar_players_count(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        result = analyze_matchup(sga, mem, self.players)
        self.assertLessEqual(len(result["similar_players"]), 3)

    def test_prop_recommendations_count(self):
        sga = self._get_player("Gilgeous")
        mem = self._get_defense("MEM")
        result = analyze_matchup(sga, mem, self.players)
        self.assertEqual(len(result["prop_recommendations"]), 3)


class TestDefensiveIsolationRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_defensive_isolation_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("ATL", "BOS", "OKC", "PHX", "LAL", "LAC"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        okc = self.rankings["OKC"]
        self.assertIsInstance(okc, DefensiveIsolationStats)
        self.assertEqual(okc.team, "OKC")
        self.assertAlmostEqual(okc.ppp, 0.82)
        self.assertAlmostEqual(okc.percentile, 96.6)

    def test_best_isolation_defense_highest_percentile(self):
        """Phoenix Suns should have the highest percentile (100)."""
        phx = self.rankings["PHX"]
        self.assertAlmostEqual(phx.percentile, 100.0)

    def test_worst_isolation_defense_lowest_percentile(self):
        """Atlanta Hawks should have the lowest percentile (0.0)."""
        atl = self.rankings["ATL"]
        self.assertAlmostEqual(atl.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)


class TestRankTeamsByIsolationDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_isolation_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best isolation defense (Phoenix Suns, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "PHX")

    def test_last_team_has_lowest_percentile(self):
        """Worst isolation defense (Atlanta Hawks, percentile=0) comes last."""
        self.assertEqual(self.ranked[-1].team, "ATL")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "OKC": build_defensive_isolation_rankings()["OKC"],
            "BOS": build_defensive_isolation_rankings()["BOS"],
        }
        ranked_subset = rank_teams_by_isolation_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "OKC")


if __name__ == "__main__":
    unittest.main()
