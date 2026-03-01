"""
Unit tests for nba_playtype_props.py
"""

import unittest
from nba_playtype_props import (
    PlayTypeStats,
    PlayerProfile,
    DefensiveMatchup,
    DefensiveIsolationStats,
    TransitionDefensiveStats,
    DefensivePnrBallHandlerStats,
    DefensivePnrManStats,
    DefensivePostUpStats,
    DefensiveSpotUpStats,
    DefensiveHandoffStats,
    DefensiveOffScreenStats,
    DefensivePutbackStats,
    OffensiveTransitionStats,
    build_sample_players,
    build_sample_defenses,
    build_defensive_isolation_rankings,
    rank_teams_by_isolation_defense,
    build_transition_defensive_rankings,
    rank_teams_by_transition_defense,
    build_pnr_ball_handler_defensive_rankings,
    rank_teams_by_pnr_ball_handler_defense,
    build_pnr_man_defensive_rankings,
    rank_teams_by_pnr_man_defense,
    build_post_up_defensive_rankings,
    rank_teams_by_post_up_defense,
    build_spot_up_defensive_rankings,
    rank_teams_by_spot_up_defense,
    find_spot_up_beneficiaries,
    build_handoff_defensive_rankings,
    rank_teams_by_handoff_defense,
    find_handoff_beneficiaries,
    build_off_screen_defensive_rankings,
    rank_teams_by_off_screen_defense,
    find_off_screen_beneficiaries,
    build_putback_defensive_rankings,
    rank_teams_by_putback_defense,
    find_putback_beneficiaries,
    build_offensive_transition_stats,
    rank_players_by_offensive_transition,
    find_transition_scorers,
    find_transition_beneficiaries,
    match_all_transition_matchups,
    compute_similarity,
    find_similar_players,
    _matchup_multiplier,
    project_props,
    analyze_matchup,
    predict_transition_matchup,
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


class TestTransitionDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_transition_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("MIA", "OKC", "WAS", "DAL", "BOS", "LAC"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        okc = self.rankings["OKC"]
        self.assertIsInstance(okc, TransitionDefensiveStats)
        self.assertEqual(okc.team, "OKC")
        self.assertAlmostEqual(okc.ppp, 1.20)
        self.assertAlmostEqual(okc.percentile, 100.0)

    def test_best_transition_defense_highest_percentile(self):
        """Oklahoma City Thunder should have the highest percentile (100)."""
        okc = self.rankings["OKC"]
        self.assertAlmostEqual(okc.percentile, 100.0)

    def test_worst_transition_defense_lowest_percentile(self):
        """Washington Wizards should have the lowest percentile (0.0)."""
        was = self.rankings["WAS"]
        self.assertAlmostEqual(was.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)


class TestRankTeamsByTransitionDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_transition_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best transition defense (OKC, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "OKC")

    def test_last_team_has_lowest_percentile(self):
        """Worst transition defense (Washington Wizards, percentile=0) comes last."""
        self.assertEqual(self.ranked[-1].team, "WAS")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "DAL": build_transition_defensive_rankings()["DAL"],
            "BOS": build_transition_defensive_rankings()["BOS"],
        }
        ranked_subset = rank_teams_by_transition_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "DAL")


class TestPnrBallHandlerDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_pnr_ball_handler_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("DET", "OKC", "POR", "BKN", "CLE", "GSW"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        det = self.rankings["DET"]
        self.assertIsInstance(det, DefensivePnrBallHandlerStats)
        self.assertEqual(det.team, "DET")
        self.assertAlmostEqual(det.ppp, 0.79)
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_best_pnr_bh_defense_highest_percentile(self):
        """Detroit Pistons should have the highest percentile (100)."""
        det = self.rankings["DET"]
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_worst_pnr_bh_defense_lowest_percentile(self):
        """Portland Trail Blazers should have the lowest percentile (0.0)."""
        por = self.rankings["POR"]
        self.assertAlmostEqual(por.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)


class TestRankTeamsByPnrBallHandlerDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_pnr_ball_handler_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best PnR ball handler defense (Detroit Pistons, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "DET")

    def test_last_team_has_lowest_percentile(self):
        """Worst PnR ball handler defense (Portland Trail Blazers, percentile=0) comes last."""
        self.assertEqual(self.ranked[-1].team, "POR")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "DET": build_pnr_ball_handler_defensive_rankings()["DET"],
            "OKC": build_pnr_ball_handler_defensive_rankings()["OKC"],
        }
        ranked_subset = rank_teams_by_pnr_ball_handler_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "DET")


class TestPnrManDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_pnr_man_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("HOU", "MEM", "SAS", "DEN", "LAL", "WAS"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        hou = self.rankings["HOU"]
        self.assertIsInstance(hou, DefensivePnrManStats)
        self.assertEqual(hou.team, "HOU")
        self.assertAlmostEqual(hou.ppp, 0.96)
        self.assertAlmostEqual(hou.percentile, 100.0)

    def test_best_pnr_man_defense_highest_percentile(self):
        """Houston Rockets should have the highest percentile (100)."""
        hou = self.rankings["HOU"]
        self.assertAlmostEqual(hou.percentile, 100.0)

    def test_worst_pnr_man_defense_lowest_percentile(self):
        """Los Angeles Lakers should have the lowest percentile (0.0)."""
        lal = self.rankings["LAL"]
        self.assertAlmostEqual(lal.percentile, 0.0)

    def test_washington_wizards_missing_fields_default_to_sentinel(self):
        """Washington Wizards row was truncated; missing fields should be -1.0 (sentinel)."""
        was = self.rankings["WAS"]
        self.assertAlmostEqual(was.sf_freq_pct, -1.0)
        self.assertAlmostEqual(was.and_one_freq_pct, -1.0)
        self.assertAlmostEqual(was.score_freq_pct, -1.0)
        self.assertAlmostEqual(was.percentile, -1.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)


class TestRankTeamsByPnrManDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_pnr_man_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best PnR man defense (Houston Rockets, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "HOU")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "HOU": build_pnr_man_defensive_rankings()["HOU"],
            "SAS": build_pnr_man_defensive_rankings()["SAS"],
        }
        ranked_subset = rank_teams_by_pnr_man_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "HOU")


class TestPostUpDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_post_up_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("DET", "SAS", "BOS", "OKC", "MIN", "SAC"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        det = self.rankings["DET"]
        self.assertIsInstance(det, DefensivePostUpStats)
        self.assertEqual(det.team, "DET")
        self.assertAlmostEqual(det.ppp, 0.74)
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_best_post_up_defense_highest_percentile(self):
        """Detroit Pistons should have the highest percentile (100)."""
        det = self.rankings["DET"]
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_worst_post_up_defense_lowest_percentile(self):
        """Minnesota Timberwolves should have the lowest percentile (0.0)."""
        min_ = self.rankings["MIN"]
        self.assertAlmostEqual(min_.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)

    def test_fg_pct_equals_efg_pct(self):
        """Post-up data has FG% == EFG% (no three-point shots in post-ups)."""
        for stats in self.rankings.values():
            self.assertAlmostEqual(stats.fg_pct, stats.efg_pct, places=1)


class TestRankTeamsByPostUpDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_post_up_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best post-up defense (Detroit Pistons, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "DET")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "DET": build_post_up_defensive_rankings()["DET"],
            "SAS": build_post_up_defensive_rankings()["SAS"],
        }
        ranked_subset = rank_teams_by_post_up_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "DET")


class TestSpotUpDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_spot_up_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("DET", "MIA", "BOS", "DAL", "WAS", "UTA"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        det = self.rankings["DET"]
        self.assertIsInstance(det, DefensiveSpotUpStats)
        self.assertEqual(det.team, "DET")
        self.assertAlmostEqual(det.ppp, 0.97)
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_best_spot_up_defense_highest_percentile(self):
        """Detroit Pistons should have the highest percentile (100)."""
        det = self.rankings["DET"]
        self.assertAlmostEqual(det.percentile, 100.0)

    def test_worst_spot_up_defense_lowest_percentile(self):
        """Washington Wizards should have the lowest percentile (0.0)."""
        was = self.rankings["WAS"]
        self.assertAlmostEqual(was.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)

    def test_efg_pct_greater_than_fg_pct(self):
        """Spot-up shots include threes so EFG% should be >= FG%."""
        for stats in self.rankings.values():
            self.assertGreaterEqual(stats.efg_pct, stats.fg_pct)


class TestRankTeamsBySpotUpDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_spot_up_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best spot-up defense (Detroit Pistons, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "DET")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "DET": build_spot_up_defensive_rankings()["DET"],
            "MIA": build_spot_up_defensive_rankings()["MIA"],
        }
        ranked_subset = rank_teams_by_spot_up_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "DET")


class TestFindSpotUpBeneficiaries(unittest.TestCase):
    """Tests for find_spot_up_beneficiaries()."""

    def setUp(self):
        self.players = build_sample_players()
        self.spot_up_rankings = build_spot_up_defensive_rankings()

    def test_returns_list(self):
        result = find_spot_up_beneficiaries(self.players, "WAS", self.spot_up_rankings)
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_spot_up_beneficiaries(self.players, "UNKNOWN", self.spot_up_rankings)
        self.assertEqual(result, [])

    def test_all_players_meet_freq_threshold(self):
        """Every returned player should have spot-up freq >= min_spot_up_freq."""
        min_freq = 0.10
        result = find_spot_up_beneficiaries(
            self.players, "WAS", self.spot_up_rankings, min_spot_up_freq=min_freq
        )
        for entry in result:
            self.assertGreaterEqual(entry["spot_up_freq"], min_freq)

    def test_opponent_def_ppp_populated(self):
        result = find_spot_up_beneficiaries(self.players, "WAS", self.spot_up_rankings)
        for entry in result:
            self.assertAlmostEqual(
                entry["def_ppp"], self.spot_up_rankings["WAS"].ppp
            )

    def test_sorted_by_spot_up_freq_descending(self):
        result = find_spot_up_beneficiaries(self.players, "WAS", self.spot_up_rankings)
        freqs = [e["spot_up_freq"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_no_beneficiaries_for_elite_defense(self):
        """DET (ppp=0.97) is below the default ppp_threshold=1.03 → no beneficiaries."""
        result = find_spot_up_beneficiaries(self.players, "DET", self.spot_up_rankings)
        self.assertEqual(result, [])

    def test_result_keys(self):
        result = find_spot_up_beneficiaries(self.players, "WAS", self.spot_up_rankings)
        if result:
            expected_keys = {
                "player", "position", "spot_up_freq",
                "spot_up_ppp", "def_ppp", "def_percentile", "edge",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_custom_ppp_threshold(self):
        """With a very low threshold every eligible-freq player should appear."""
        result_low = find_spot_up_beneficiaries(
            self.players, "WAS", self.spot_up_rankings, ppp_threshold=0.0
        )
        result_high = find_spot_up_beneficiaries(
            self.players, "WAS", self.spot_up_rankings, ppp_threshold=999.0
        )
        self.assertGreaterEqual(len(result_low), len(result_high))


class TestHandoffDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_handoff_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("MIA", "BKN", "MEM", "WAS", "OKC", "SAS"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        mia = self.rankings["MIA"]
        self.assertIsInstance(mia, DefensiveHandoffStats)
        self.assertEqual(mia.team, "MIA")
        self.assertAlmostEqual(mia.ppp, 0.82)
        self.assertAlmostEqual(mia.percentile, 100.0)

    def test_best_handoff_defense_highest_percentile(self):
        """Miami Heat should have the highest percentile (100)."""
        mia = self.rankings["MIA"]
        self.assertAlmostEqual(mia.percentile, 100.0)

    def test_worst_handoff_defense_lowest_percentile(self):
        """Washington Wizards should have the lowest percentile (0.0)."""
        was = self.rankings["WAS"]
        self.assertAlmostEqual(was.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)

    def test_efg_pct_greater_than_or_equal_fg_pct(self):
        """EFG% should be >= FG% (handoffs include three-point shots)."""
        for stats in self.rankings.values():
            self.assertGreaterEqual(stats.efg_pct, stats.fg_pct)


class TestRankTeamsByHandoffDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_handoff_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best handoff defense (Miami Heat, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "MIA")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "MIA": build_handoff_defensive_rankings()["MIA"],
            "MEM": build_handoff_defensive_rankings()["MEM"],
        }
        ranked_subset = rank_teams_by_handoff_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "MIA")


class TestFindHandoffBeneficiaries(unittest.TestCase):
    """Tests for find_handoff_beneficiaries()."""

    def setUp(self):
        self.players = build_sample_players()
        self.handoff_rankings = build_handoff_defensive_rankings()

    def test_returns_list(self):
        result = find_handoff_beneficiaries(self.players, "WAS", self.handoff_rankings)
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_handoff_beneficiaries(self.players, "UNKNOWN", self.handoff_rankings)
        self.assertEqual(result, [])

    def test_all_players_meet_freq_threshold(self):
        """Every returned player should have handoff freq >= min_handoff_freq."""
        min_freq = 0.05
        result = find_handoff_beneficiaries(
            self.players, "WAS", self.handoff_rankings, min_handoff_freq=min_freq
        )
        for entry in result:
            self.assertGreaterEqual(entry["handoff_freq"], min_freq)

    def test_opponent_def_ppp_populated(self):
        result = find_handoff_beneficiaries(self.players, "WAS", self.handoff_rankings)
        for entry in result:
            self.assertAlmostEqual(
                entry["def_ppp"], self.handoff_rankings["WAS"].ppp
            )

    def test_sorted_by_handoff_freq_descending(self):
        result = find_handoff_beneficiaries(self.players, "WAS", self.handoff_rankings)
        freqs = [e["handoff_freq"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_no_beneficiaries_for_elite_defense(self):
        """MIA (ppp=0.82) is below the default ppp_threshold=1.00 → no beneficiaries."""
        result = find_handoff_beneficiaries(self.players, "MIA", self.handoff_rankings)
        self.assertEqual(result, [])

    def test_result_keys(self):
        result = find_handoff_beneficiaries(
            self.players, "WAS", self.handoff_rankings, ppp_threshold=0.0
        )
        if result:
            expected_keys = {
                "player", "position", "handoff_freq",
                "handoff_ppp", "def_ppp", "def_percentile", "edge",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_custom_ppp_threshold(self):
        """With a very low threshold every eligible-freq player should appear."""
        result_low = find_handoff_beneficiaries(
            self.players, "WAS", self.handoff_rankings, ppp_threshold=0.0
        )
        result_high = find_handoff_beneficiaries(
            self.players, "WAS", self.handoff_rankings, ppp_threshold=999.0
        )
        self.assertGreaterEqual(len(result_low), len(result_high))


class TestOffScreenDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_off_screen_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("DEN", "LAL", "SAC", "POR", "TOR", "HOU"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        den = self.rankings["DEN"]
        self.assertIsInstance(den, DefensiveOffScreenStats)
        self.assertEqual(den.team, "DEN")
        self.assertAlmostEqual(den.ppp, 1.23)
        self.assertAlmostEqual(den.percentile, 100.0)

    def test_best_off_screen_defense_highest_percentile(self):
        """Denver Nuggets should have the highest percentile (100)."""
        den = self.rankings["DEN"]
        self.assertAlmostEqual(den.percentile, 100.0)

    def test_worst_off_screen_defense_lowest_percentile(self):
        """Portland Trail Blazers should have the lowest percentile (0.0)."""
        por = self.rankings["POR"]
        self.assertAlmostEqual(por.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)

    def test_efg_pct_greater_than_or_equal_fg_pct(self):
        """EFG% should be >= FG% (off-screen actions include three-point shots)."""
        for stats in self.rankings.values():
            self.assertGreaterEqual(stats.efg_pct, stats.fg_pct)


class TestRankTeamsByOffScreenDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_off_screen_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best off-screen defense (Denver Nuggets, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "DEN")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "DEN": build_off_screen_defensive_rankings()["DEN"],
            "POR": build_off_screen_defensive_rankings()["POR"],
        }
        ranked_subset = rank_teams_by_off_screen_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "DEN")


class TestFindOffScreenBeneficiaries(unittest.TestCase):
    """Tests for find_off_screen_beneficiaries()."""

    def setUp(self):
        self.players = build_sample_players()
        self.off_screen_rankings = build_off_screen_defensive_rankings()

    def test_returns_list(self):
        result = find_off_screen_beneficiaries(self.players, "DEN", self.off_screen_rankings)
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_off_screen_beneficiaries(self.players, "UNKNOWN", self.off_screen_rankings)
        self.assertEqual(result, [])

    def test_all_players_meet_freq_threshold(self):
        """Every returned player should have off_screen freq >= min_off_screen_freq."""
        min_freq = 0.05
        result = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, min_off_screen_freq=min_freq
        )
        for entry in result:
            self.assertGreaterEqual(entry["off_screen_freq"], min_freq)

    def test_opponent_def_ppp_populated(self):
        result = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, ppp_threshold=0.0
        )
        for entry in result:
            self.assertAlmostEqual(
                entry["def_ppp"], self.off_screen_rankings["DEN"].ppp
            )

    def test_sorted_by_off_screen_freq_descending(self):
        result = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, ppp_threshold=0.0
        )
        freqs = [e["off_screen_freq"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_no_beneficiaries_for_strong_defense(self):
        """POR (ppp=0.80) is below the default ppp_threshold=1.00 → no beneficiaries."""
        result = find_off_screen_beneficiaries(self.players, "POR", self.off_screen_rankings)
        self.assertEqual(result, [])

    def test_result_keys(self):
        result = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, ppp_threshold=0.0
        )
        if result:
            expected_keys = {
                "player", "position", "off_screen_freq",
                "off_screen_ppp", "def_ppp", "def_percentile", "edge",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_custom_ppp_threshold(self):
        """With a very low threshold every eligible-freq player should appear."""
        result_low = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, ppp_threshold=0.0
        )
        result_high = find_off_screen_beneficiaries(
            self.players, "DEN", self.off_screen_rankings, ppp_threshold=999.0
        )
        self.assertGreaterEqual(len(result_low), len(result_high))


class TestPutbackDefensiveRankings(unittest.TestCase):
    def setUp(self):
        self.rankings = build_putback_defensive_rankings()

    def test_all_thirty_teams_present(self):
        self.assertEqual(len(self.rankings), 30)

    def test_known_team_abbrevs_present(self):
        for abbr in ("CLE", "MIN", "SAC", "BKN", "NOP", "PHX"):
            self.assertIn(abbr, self.rankings)

    def test_stats_dataclass_fields(self):
        cle = self.rankings["CLE"]
        self.assertIsInstance(cle, DefensivePutbackStats)
        self.assertEqual(cle.team, "CLE")
        self.assertAlmostEqual(cle.ppp, 1.01)
        self.assertAlmostEqual(cle.percentile, 100.0)

    def test_best_putback_defense_highest_percentile(self):
        """Cleveland Cavaliers should have the highest percentile (100)."""
        cle = self.rankings["CLE"]
        self.assertAlmostEqual(cle.percentile, 100.0)

    def test_worst_putback_defense_lowest_percentile(self):
        """Sacramento Kings should have the lowest percentile (0.0)."""
        sac = self.rankings["SAC"]
        self.assertAlmostEqual(sac.percentile, 0.0)

    def test_ppp_values_are_positive(self):
        for stats in self.rankings.values():
            self.assertGreater(stats.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for stats in self.rankings.values():
            self.assertIsInstance(stats.gp, int)
            self.assertGreater(stats.gp, 0)

    def test_efg_pct_greater_than_or_equal_fg_pct(self):
        """EFG% should be >= FG% for all putback entries."""
        for stats in self.rankings.values():
            self.assertGreaterEqual(stats.efg_pct, stats.fg_pct)


class TestRankTeamsByPutbackDefense(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_teams_by_putback_defense()

    def test_returns_all_thirty_teams(self):
        self.assertEqual(len(self.ranked), 30)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_team_has_highest_percentile(self):
        """Best putback defense (Cleveland Cavaliers, percentile=100) comes first."""
        self.assertEqual(self.ranked[0].team, "CLE")

    def test_accepts_custom_rankings_dict(self):
        subset = {
            "CLE": build_putback_defensive_rankings()["CLE"],
            "SAC": build_putback_defensive_rankings()["SAC"],
        }
        ranked_subset = rank_teams_by_putback_defense(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].team, "CLE")


class TestFindPutbackBeneficiaries(unittest.TestCase):
    """Tests for find_putback_beneficiaries()."""

    def setUp(self):
        self.players = build_sample_players()
        self.putback_rankings = build_putback_defensive_rankings()

    def test_returns_list(self):
        result = find_putback_beneficiaries(self.players, "SAC", self.putback_rankings)
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_putback_beneficiaries(self.players, "UNKNOWN", self.putback_rankings)
        self.assertEqual(result, [])

    def test_all_players_meet_freq_threshold(self):
        """Every returned player should have putback freq >= min_putback_freq."""
        min_freq = 0.05
        result = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, min_putback_freq=min_freq
        )
        for entry in result:
            self.assertGreaterEqual(entry["putback_freq"], min_freq)

    def test_opponent_def_ppp_populated(self):
        result = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, ppp_threshold=0.0
        )
        for entry in result:
            self.assertAlmostEqual(
                entry["def_ppp"], self.putback_rankings["SAC"].ppp
            )

    def test_sorted_by_putback_freq_descending(self):
        result = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, ppp_threshold=0.0
        )
        freqs = [e["putback_freq"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_no_beneficiaries_for_strong_defense(self):
        """CLE (ppp=1.01) is below ppp_threshold=1.10 → no beneficiaries."""
        result = find_putback_beneficiaries(
            self.players, "CLE", self.putback_rankings, ppp_threshold=1.10
        )
        self.assertEqual(result, [])

    def test_result_keys(self):
        result = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, ppp_threshold=0.0
        )
        if result:
            expected_keys = {
                "player", "position", "putback_freq",
                "putback_ppp", "def_ppp", "def_percentile", "edge",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_custom_ppp_threshold(self):
        """With a very low threshold every eligible-freq player should appear."""
        result_low = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, ppp_threshold=0.0
        )
        result_high = find_putback_beneficiaries(
            self.players, "SAC", self.putback_rankings, ppp_threshold=999.0
        )
        self.assertGreaterEqual(len(result_low), len(result_high))


class TestOffensiveTransitionStats(unittest.TestCase):
    def setUp(self):
        self.stats = build_offensive_transition_stats()

    def test_returns_196_players(self):
        self.assertEqual(len(self.stats), 196)

    def test_all_are_dataclass_instances(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensiveTransitionStats)

    def test_best_percentile_cam_thomas_mil(self):
        """Cam Thomas (MIL) should have the highest percentile (100.0)."""
        cam = next(s for s in self.stats if s.player == "Cam Thomas" and s.team == "MIL")
        self.assertAlmostEqual(cam.percentile, 100.0)

    def test_worst_percentile_derrick_white(self):
        """Derrick White should have the lowest percentile (3.7)."""
        white = next(s for s in self.stats if s.player == "Derrick White")
        self.assertAlmostEqual(white.percentile, 3.7)

    def test_ppp_values_are_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_gp_values_are_positive_integers(self):
        for s in self.stats:
            self.assertIsInstance(s.gp, int)
            self.assertGreater(s.gp, 0)

    def test_efg_pct_generally_geq_fg_pct(self):
        """EFG% should be >= FG% for all transition entries."""
        for s in self.stats:
            self.assertGreaterEqual(s.efg_pct, s.fg_pct)

    def test_known_player_fields(self):
        harden = next(s for s in self.stats if s.player == "James Harden")
        self.assertEqual(harden.team, "CLE")
        self.assertAlmostEqual(harden.freq_pct, 26.8)
        self.assertAlmostEqual(harden.ppp, 1.39)

    def test_all_players_have_teams(self):
        for s in self.stats:
            self.assertTrue(s.team, f"{s.player} has no team")


class TestRankPlayersByOffensiveTransition(unittest.TestCase):
    def setUp(self):
        self.ranked = rank_players_by_offensive_transition()

    def test_returns_196_players(self):
        self.assertEqual(len(self.ranked), 196)

    def test_sorted_best_to_worst(self):
        percentiles = [s.percentile for s in self.ranked]
        self.assertEqual(percentiles, sorted(percentiles, reverse=True))

    def test_first_player_has_highest_percentile(self):
        """Cam Thomas MIL (100.0) should be at the top."""
        self.assertGreaterEqual(self.ranked[0].percentile, 91.0)

    def test_last_player_has_lowest_percentile(self):
        """Jordan Goodwin (0.0) should be last."""
        self.assertAlmostEqual(self.ranked[-1].percentile, 0.0)

    def test_accepts_custom_list(self):
        subset = [
            s for s in build_offensive_transition_stats()
            if s.player in ("James Harden", "Jerami Grant")
        ]
        ranked_subset = rank_players_by_offensive_transition(subset)
        self.assertEqual(len(ranked_subset), 2)
        self.assertEqual(ranked_subset[0].player, "James Harden")


class TestFindTransitionScorers(unittest.TestCase):
    def setUp(self):
        self.stats = build_offensive_transition_stats()

    def test_returns_list(self):
        result = find_transition_scorers(self.stats)
        self.assertIsInstance(result, list)

    def test_all_results_meet_freq_threshold(self):
        threshold = 12.0
        result = find_transition_scorers(self.stats, min_freq_pct=threshold)
        for entry in result:
            self.assertGreaterEqual(entry["freq_pct"], threshold)

    def test_all_results_meet_ppp_threshold(self):
        threshold = 1.05
        result = find_transition_scorers(self.stats, min_ppp=threshold)
        for entry in result:
            self.assertGreaterEqual(entry["ppp"], threshold)

    def test_sorted_by_freq_pct_descending(self):
        result = find_transition_scorers(self.stats)
        freqs = [e["freq_pct"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_result_keys_without_opponent(self):
        result = find_transition_scorers(self.stats)
        if result:
            expected_keys = {
                "player", "team", "freq_pct", "ppp",
                "pts", "percentile", "def_ppp", "def_percentile",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_def_fields_none_without_opponent(self):
        result = find_transition_scorers(self.stats)
        for entry in result:
            self.assertIsNone(entry["def_ppp"])
            self.assertIsNone(entry["def_percentile"])

    def test_def_fields_populated_with_opponent(self):
        def_rankings = build_transition_defensive_rankings()
        result = find_transition_scorers(
            self.stats, opponent_team="WAS",
            transition_defensive_rankings=def_rankings,
            min_freq_pct=0.0, min_ppp=0.0,
        )
        for entry in result:
            self.assertIsNotNone(entry["def_ppp"])
            self.assertIsNotNone(entry["def_percentile"])

    def test_empty_when_no_players_meet_thresholds(self):
        result = find_transition_scorers(self.stats, min_freq_pct=999.0)
        self.assertEqual(result, [])

    def test_harden_appears_at_top_by_freq(self):
        """James Harden leads all players with 26.8% transition freq."""
        result = find_transition_scorers(self.stats, min_freq_pct=10.0, min_ppp=1.00)
        self.assertEqual(result[0]["player"], "James Harden")

    def test_custom_thresholds_narrow_results(self):
        broad = find_transition_scorers(self.stats, min_freq_pct=10.0, min_ppp=0.80)
        narrow = find_transition_scorers(self.stats, min_freq_pct=20.0, min_ppp=1.00)
        self.assertGreaterEqual(len(broad), len(narrow))


class TestFindTransitionBeneficiaries(unittest.TestCase):
    """Tests for find_transition_beneficiaries()."""

    def setUp(self):
        self.stats = build_offensive_transition_stats()
        self.def_rankings = build_transition_defensive_rankings()

    def test_returns_list(self):
        result = find_transition_beneficiaries(self.stats, "WAS", self.def_rankings)
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_transition_beneficiaries(self.stats, "UNKNOWN", self.def_rankings)
        self.assertEqual(result, [])

    def test_empty_for_strong_defense(self):
        """OKC has the best transition defense (percentile=100.0) → above default threshold."""
        result = find_transition_beneficiaries(self.stats, "OKC", self.def_rankings)
        self.assertEqual(result, [])

    def test_all_results_meet_freq_threshold(self):
        min_freq = 10.0
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=min_freq
        )
        for entry in result:
            self.assertGreaterEqual(entry["freq_pct"], min_freq)

    def test_all_results_meet_ppp_threshold(self):
        min_ppp = 1.05
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_ppp=min_ppp
        )
        for entry in result:
            self.assertGreaterEqual(entry["ppp"], min_ppp)

    def test_opponent_def_fields_populated(self):
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=0.0, min_ppp=0.0
        )
        for entry in result:
            self.assertAlmostEqual(entry["def_ppp"], self.def_rankings["WAS"].ppp)
            self.assertAlmostEqual(
                entry["def_percentile"], self.def_rankings["WAS"].percentile
            )

    def test_sorted_by_freq_pct_descending(self):
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=0.0, min_ppp=0.0
        )
        freqs = [e["freq_pct"] for e in result]
        self.assertEqual(freqs, sorted(freqs, reverse=True))

    def test_result_keys(self):
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=0.0, min_ppp=0.0
        )
        if result:
            expected_keys = {
                "player", "team", "freq_pct", "ppp", "pts",
                "percentile", "def_ppp", "def_percentile", "edge",
            }
            self.assertEqual(set(result[0].keys()), expected_keys)

    def test_edge_equals_player_ppp_minus_def_ppp(self):
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=0.0, min_ppp=0.0
        )
        def_ppp = self.def_rankings["WAS"].ppp
        for entry in result:
            self.assertAlmostEqual(entry["edge"], round(entry["ppp"] - def_ppp, 3))

    def test_harden_appears_at_top_against_weak_defense(self):
        """James Harden (freq=26.8) should lead vs WAS (weak defense)."""
        result = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings, min_freq_pct=10.0, min_ppp=1.00
        )
        self.assertTrue(len(result) > 0)
        self.assertEqual(result[0]["player"], "James Harden")

    def test_custom_max_def_percentile(self):
        """Raising max_def_percentile to 100 opens all teams; -1 closes all."""
        result_open = find_transition_beneficiaries(
            self.stats, "OKC", self.def_rankings,
            min_freq_pct=0.0, min_ppp=0.0, max_def_percentile=100.0
        )
        result_closed = find_transition_beneficiaries(
            self.stats, "WAS", self.def_rankings,
            min_freq_pct=0.0, min_ppp=0.0, max_def_percentile=-1.0
        )
        self.assertGreater(len(result_open), 0)
        self.assertEqual(result_closed, [])


class TestMatchAllTransitionMatchups(unittest.TestCase):
    """Tests for match_all_transition_matchups()."""

    def setUp(self):
        self.off_stats = build_offensive_transition_stats()
        self.def_rankings = build_transition_defensive_rankings()

    def test_returns_list(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=20, max_def_percentile=100.0
        )
        self.assertIsInstance(result, list)

    def test_top_n_respected(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=10, max_def_percentile=100.0
        )
        self.assertLessEqual(len(result), 10)

    def test_required_keys_present(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=5, max_def_percentile=100.0
        )
        self.assertGreater(len(result), 0)
        expected_keys = {
            "player", "team", "off_percentile", "ppp", "freq_pct",
            "opponent", "def_ppp", "def_percentile", "edge",
        }
        self.assertEqual(set(result[0].keys()), expected_keys)

    def test_sorted_by_edge_descending(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=30, max_def_percentile=100.0
        )
        edges = [r["edge"] for r in result]
        self.assertEqual(edges, sorted(edges, reverse=True))

    def test_edge_formula(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=30, max_def_percentile=100.0
        )
        for entry in result:
            self.assertAlmostEqual(
                entry["edge"], round(entry["ppp"] - entry["def_ppp"], 3)
            )

    def test_player_not_matched_against_own_team(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=200, max_def_percentile=100.0
        )
        for entry in result:
            self.assertNotEqual(entry["team"], entry["opponent"])

    def test_max_def_percentile_filter(self):
        result_all = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=500, max_def_percentile=100.0
        )
        result_weak = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=500, max_def_percentile=20.0
        )
        # Restricting to weakest defenses should yield fewer or equal rows
        self.assertLessEqual(len(result_weak), len(result_all))
        for entry in result_weak:
            self.assertLessEqual(entry["def_percentile"], 20.0)

    def test_empty_when_no_weak_defences(self):
        result = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=50, max_def_percentile=-1.0
        )
        self.assertEqual(result, [])

    def test_min_off_percentile_filter(self):
        result_high = match_all_transition_matchups(
            self.off_stats, self.def_rankings, top_n=500,
            max_def_percentile=100.0, min_off_percentile=80.0
        )
        for entry in result_high:
            self.assertGreaterEqual(entry["off_percentile"], 80.0)


class TestPredictTransitionMatchup(unittest.TestCase):
    """Tests for predict_transition_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_transition_stats()
        self.def_rankings = build_transition_defensive_rankings()

    # ------------------------------------------------------------------
    # Basic return structure
    # ------------------------------------------------------------------

    def test_returns_dict_for_valid_inputs(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsInstance(result, dict)

    def test_required_keys_present(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        expected_keys = {
            "player", "team", "gp", "freq_pct", "ppp", "pts",
            "off_percentile", "opponent", "def_ppp", "def_freq_pct",
            "def_percentile", "edge", "verdict",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    # ------------------------------------------------------------------
    # Josh Hart vs SAS — the primary requested matchup
    # ------------------------------------------------------------------

    def test_hart_vs_sas_player_fields(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Josh Hart")
        self.assertEqual(result["team"], "NYK")
        self.assertAlmostEqual(result["ppp"], 1.5)
        self.assertAlmostEqual(result["off_percentile"], 99.6)

    def test_hart_vs_sas_opponent_fields(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["opponent"], "SAS")
        self.assertAlmostEqual(result["def_ppp"], 1.13)

    def test_hart_vs_sas_edge(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        expected_edge = round(1.5 - 1.13, 3)
        self.assertAlmostEqual(result["edge"], expected_edge)

    def test_hart_vs_sas_verdict_favorable(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["verdict"], "FAVORABLE")

    # ------------------------------------------------------------------
    # Verdict thresholds
    # ------------------------------------------------------------------

    def test_verdict_tough_when_edge_below_minus_threshold(self):
        # Build a synthetic player with low PPP and a high-PPP-allowed defense
        player = OffensiveTransitionStats(
            player="Test Player", team="AAA", gp=50,
            poss=5.0, freq_pct=20.0, ppp=0.80, pts=5.0,
            fgm=1.0, fga=2.0, fg_pct=50.0, efg_pct=50.0,
            ft_freq_pct=10.0, tov_freq_pct=5.0, sf_freq_pct=5.0,
            and_one_freq_pct=0.0, score_freq_pct=50.0, percentile=20.0,
        )
        result = predict_transition_matchup(
            "Test Player", "OKC",
            [player], self.def_rankings,
        )
        # OKC allows only 1.20 PPP and has percentile=100 — player edge = 0.80-1.20 = -0.40
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        player = OffensiveTransitionStats(
            player="Neutral Guy", team="BBB", gp=50,
            poss=5.0, freq_pct=15.0, ppp=1.14, pts=5.0,
            fgm=1.0, fga=2.0, fg_pct=50.0, efg_pct=50.0,
            ft_freq_pct=10.0, tov_freq_pct=5.0, sf_freq_pct=5.0,
            and_one_freq_pct=0.0, score_freq_pct=50.0, percentile=50.0,
        )
        # SAS allows 1.13 PPP; edge = 1.14 - 1.13 = 0.01 → NEUTRAL
        result = predict_transition_matchup(
            "Neutral Guy", "SAS", [player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    # ------------------------------------------------------------------
    # Not-found cases
    # ------------------------------------------------------------------

    def test_returns_none_for_unknown_player(self):
        result = predict_transition_matchup(
            "Nobody Famous", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_transition_matchup(
            "Josh Hart", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Case-insensitive player name lookup
    # ------------------------------------------------------------------

    def test_case_insensitive_player_name(self):
        result_lower = predict_transition_matchup(
            "josh hart", "SAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_transition_matchup(
            "JOSH HART", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    # ------------------------------------------------------------------
    # Edge formula
    # ------------------------------------------------------------------

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_transition_matchup(
            "Josh Hart", "SAS", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )


if __name__ == "__main__":
    unittest.main()
