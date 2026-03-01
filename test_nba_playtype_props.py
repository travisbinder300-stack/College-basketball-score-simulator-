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
    OffensiveIsolationStats,
    OffensivePnrBallHandlerStats,
    OffensivePnrManStats,
    OffensivePostUpStats,
    OffensiveSpotUpStats,
    OffensiveHandoffStats,
    OffensiveOffScreenStats,
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
    build_offensive_isolation_stats,
    rank_players_by_offensive_isolation,
    find_isolation_scorers,
    find_isolation_beneficiaries,
    match_all_isolation_matchups,
    predict_isolation_matchup,
    build_offensive_pnr_ball_handler_stats,
    rank_players_by_offensive_pnr_ball_handler,
    find_pnr_ball_handler_scorers,
    predict_pnr_ball_handler_matchup,
    build_offensive_pnr_man_stats,
    rank_players_by_offensive_pnr_man,
    find_pnr_man_scorers,
    predict_pnr_man_matchup,
    build_offensive_post_up_stats,
    rank_players_by_offensive_post_up,
    find_post_up_scorers,
    predict_post_up_matchup,
    build_offensive_spot_up_stats,
    rank_players_by_offensive_spot_up,
    find_spot_up_player_scorers,
    predict_spot_up_matchup,
    build_offensive_handoff_stats,
    rank_players_by_offensive_handoff,
    find_handoff_player_scorers,
    predict_handoff_matchup,
    build_offensive_off_screen_stats,
    rank_players_by_offensive_off_screen,
    find_off_screen_player_scorers,
    predict_off_screen_matchup,
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


# ===========================================================================
# Offensive Isolation dataset tests
# ===========================================================================

class TestBuildOffensiveIsolationStats(unittest.TestCase):
    """Tests for build_offensive_isolation_stats()."""

    def setUp(self):
        self.stats = build_offensive_isolation_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_fifty_players_present(self):
        self.assertEqual(len(self.stats), 200)

    def test_all_items_are_offensive_isolation_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensiveIsolationStats)

    def test_known_players_present(self):
        names = {s.player for s in self.stats}
        for expected in ("James Harden", "Shai Gilgeous-Alexander",
                         "Anthony Edwards", "Victor Wembanyama"):
            self.assertIn(expected, names)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_harden_fields(self):
        harden = next(s for s in self.stats if s.player == "James Harden")
        self.assertEqual(harden.team, "CLE")
        self.assertEqual(harden.gp, 41)
        self.assertAlmostEqual(harden.freq_pct, 42.1)
        self.assertAlmostEqual(harden.ppp, 1.06)
        self.assertAlmostEqual(harden.percentile, 82.4)

    def test_batch3_players_present(self):
        """All 50 batch-3 isolation players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Jabari Smith Jr.", "Anthony Davis", "Ty Jerome",
            "Nickeil Alexander-Walker", "Bennedict Mathurin", "Toumani Camara",
            "Josh Giddey", "Jarace Walker", "Darius Garland", "Lauri Markkanen",
            "CJ McCollum", "Malik Monk", "Jalen Suggs", "Cedric Coward",
            "Marvin Bagley III", "Matas Buzelis", "De'Anthony Melton",
            "Dylan Harper", "Max Christie", "Derrick White", "Reed Sheppard",
            "Alex Sarr", "Jamal Shead", "Bub Carrington", "OG Anunoby",
            "Ryan Nembhard", "Collin Sexton", "Noah Clowney", "Anthony Black",
            "Kris Dunn", "Bobby Portis", "Tre Mann", "P.J. Washington",
            "Jonathan Kuminga", "Aaron Wiggins", "Dyson Daniels", "Franz Wagner",
            "Cam Thomas", "Kenrich Williams", "D'Angelo Russell", "Moses Moody",
            "Gui Santos", "Rui Hachimura", "Sharife Cooper", "Drake Powell",
            "Keldon Johnson", "Brice Sensabaugh", "Cason Wallace", "Ace Bailey",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_cam_thomas_mil_fields(self):
        """Cam Thomas (MIL, 8 GP) batch-3 entry has correct stats."""
        cam = next(
            s for s in self.stats if s.player == "Cam Thomas" and s.team == "MIL"
        )
        self.assertEqual(cam.gp, 8)
        self.assertAlmostEqual(cam.poss, 1.3)
        self.assertAlmostEqual(cam.freq_pct, 9.1)
        self.assertAlmostEqual(cam.ppp, 2.30)
        self.assertAlmostEqual(cam.percentile, 100.0)

    def test_gui_santos_fields(self):
        """Gui Santos (GSW) batch-3 entry has correct stats."""
        santos = next(s for s in self.stats if s.player == "Gui Santos")
        self.assertEqual(santos.team, "GSW")
        self.assertEqual(santos.gp, 48)
        self.assertAlmostEqual(santos.ppp, 1.47)
        self.assertAlmostEqual(santos.fg_pct, 90.0)
        self.assertAlmostEqual(santos.percentile, 98.8)

    def test_ace_bailey_fields(self):
        """Ace Bailey (UTA) batch-3 entry has correct stats."""
        ace = next(s for s in self.stats if s.player == "Ace Bailey")
        self.assertEqual(ace.team, "UTA")
        self.assertEqual(ace.gp, 51)
        self.assertAlmostEqual(ace.ppp, 0.67)
        self.assertAlmostEqual(ace.tov_freq_pct, 15.2)
        self.assertAlmostEqual(ace.percentile, 12.9)

    def test_batch4_players_present(self):
        """All 50 batch-4 isolation players are present in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Dennis Schröder", "Caris LeVert", "Day'Ron Sharpe", "Bruce Brown",
            "Marcus Smart", "Jaden McDaniels", "Jalen Green", "Will Riley",
            "Jaylen Wells", "Jordan Clarkson", "Collin Gillespie", "Oso Ighodaro",
            "Scoot Henderson", "Jose Alvarado", "Jaden Ivey", "Kobe Sanders",
            "Mikal Bridges", "Khris Middleton", "Naz Reid", "Bilal Coulibaly",
            "Anfernee Simons", "Tristan Vukcevic", "Ousmane Dieng", "Kyle Anderson",
            "Miles McBride", "Trae Young", "Tobias Harris", "Josh Hart",
            "Buddy Hield", "Jalen Pickett", "Devin Carter", "Rob Dillingham",
            "Kentavious Caldwell-Pope", "Isaac Okoro", "RJ Barrett", "Nolan Traore",
            "Herbert Jones", "T.J. McConnell", "Jonas Valančiūnas", "Onyeka Okongwu",
            "Ronald Holland II", "Nique Clifford", "Cole Anthony", "Cam Spencer",
            "Pat Spencer", "Ayo Dosunmu", "Myles Turner", "Jamaree Bouyea",
            "Jarrett Allen",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_scoot_henderson_fields(self):
        """Scoot Henderson (POR, 9 GP) batch-4 entry has correct stats."""
        scoot = next(s for s in self.stats if s.player == "Scoot Henderson")
        self.assertEqual(scoot.team, "POR")
        self.assertEqual(scoot.gp, 9)
        self.assertAlmostEqual(scoot.ppp, 1.42)
        self.assertAlmostEqual(scoot.ft_freq_pct, 33.3)
        self.assertAlmostEqual(scoot.percentile, 98.4)

    def test_collin_sexton_chi_fields(self):
        """Collin Sexton (CHI, 8 GP) batch-4 entry has correct stats."""
        sexton = next(
            s for s in self.stats if s.player == "Collin Sexton" and s.team == "CHI"
        )
        self.assertEqual(sexton.gp, 8)
        self.assertAlmostEqual(sexton.ppp, 1.50)
        self.assertAlmostEqual(sexton.fg_pct, 66.7)
        self.assertAlmostEqual(sexton.percentile, 99.6)

    def test_jarrett_allen_fields(self):
        """Jarrett Allen (CLE) batch-4 entry has correct stats."""
        allen = next(s for s in self.stats if s.player == "Jarrett Allen")
        self.assertEqual(allen.team, "CLE")
        self.assertEqual(allen.gp, 47)
        self.assertAlmostEqual(allen.ppp, 0.86)
        self.assertAlmostEqual(allen.tov_freq_pct, 28.6)
        self.assertAlmostEqual(allen.percentile, 47.7)


class TestRankPlayersByOffensiveIsolation(unittest.TestCase):
    """Tests for rank_players_by_offensive_isolation()."""

    def setUp(self):
        self.stats = build_offensive_isolation_stats()

    def test_returns_all_players(self):
        ranked = rank_players_by_offensive_isolation(self.stats)
        self.assertEqual(len(ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        ranked = rank_players_by_offensive_isolation(self.stats)
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(ranked[i].percentile, ranked[i + 1].percentile)

    def test_pritchard_at_top(self):
        ranked = rank_players_by_offensive_isolation(self.stats)
        self.assertEqual(ranked[0].player, "Cam Thomas")


class TestFindIsolationScorers(unittest.TestCase):
    """Tests for find_isolation_scorers()."""

    def setUp(self):
        self.iso_stats = build_offensive_isolation_stats()
        self.def_rankings = build_defensive_isolation_rankings()

    def test_returns_list(self):
        result = find_isolation_scorers(self.iso_stats)
        self.assertIsInstance(result, list)

    def test_all_meet_freq_threshold(self):
        result = find_isolation_scorers(self.iso_stats, min_freq_pct=15.0, min_ppp=1.00)
        for r in result:
            self.assertGreaterEqual(r["freq_pct"], 15.0)

    def test_all_meet_ppp_threshold(self):
        result = find_isolation_scorers(self.iso_stats, min_freq_pct=10.0, min_ppp=1.05)
        for r in result:
            self.assertGreater(r["ppp"], 1.05 - 1e-9)

    def test_sorted_by_freq_pct_descending(self):
        result = find_isolation_scorers(self.iso_stats, min_freq_pct=5.0, min_ppp=0.0)
        for i in range(len(result) - 1):
            self.assertGreaterEqual(result[i]["freq_pct"], result[i + 1]["freq_pct"])

    def test_def_fields_none_without_opponent(self):
        result = find_isolation_scorers(self.iso_stats, min_freq_pct=5.0, min_ppp=0.0)
        for r in result:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_fields_populated_with_opponent(self):
        result = find_isolation_scorers(
            self.iso_stats,
            opponent_team="SAS",
            isolation_defensive_rankings=self.def_rankings,
            min_freq_pct=5.0,
            min_ppp=0.0,
        )
        for r in result:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_harden_appears_with_low_thresholds(self):
        result = find_isolation_scorers(self.iso_stats, min_freq_pct=5.0, min_ppp=0.0)
        players = [r["player"] for r in result]
        self.assertIn("James Harden", players)


class TestFindIsolationBeneficiaries(unittest.TestCase):
    """Tests for find_isolation_beneficiaries()."""

    def setUp(self):
        self.iso_stats = build_offensive_isolation_stats()
        self.def_rankings = build_defensive_isolation_rankings()

    def test_returns_list(self):
        result = find_isolation_beneficiaries(
            self.iso_stats, "ATL", self.def_rankings,
            min_freq_pct=5.0, min_ppp=0.0,
        )
        self.assertIsInstance(result, list)

    def test_empty_for_unknown_team(self):
        result = find_isolation_beneficiaries(
            self.iso_stats, "ZZZ", self.def_rankings,
        )
        self.assertEqual(result, [])

    def test_empty_for_strong_defense(self):
        # PHX has isolation defensive percentile=100.0 → above any max_def_percentile<100
        result = find_isolation_beneficiaries(
            self.iso_stats, "PHX", self.def_rankings,
            min_freq_pct=5.0, min_ppp=0.0, max_def_percentile=40.0,
        )
        self.assertEqual(result, [])

    def test_edge_formula(self):
        # ATL has percentile=0.0 (weakest), so it should pass the filter
        result = find_isolation_beneficiaries(
            self.iso_stats, "ATL", self.def_rankings,
            min_freq_pct=5.0, min_ppp=0.0, max_def_percentile=40.0,
        )
        atl_ppp = self.def_rankings["ATL"].ppp
        for r in result:
            self.assertAlmostEqual(r["edge"], round(r["ppp"] - atl_ppp, 3))

    def test_sorted_by_freq_pct_descending(self):
        result = find_isolation_beneficiaries(
            self.iso_stats, "ATL", self.def_rankings,
            min_freq_pct=5.0, min_ppp=0.0, max_def_percentile=40.0,
        )
        for i in range(len(result) - 1):
            self.assertGreaterEqual(result[i]["freq_pct"], result[i + 1]["freq_pct"])

    def test_result_keys(self):
        result = find_isolation_beneficiaries(
            self.iso_stats, "ATL", self.def_rankings,
            min_freq_pct=5.0, min_ppp=0.0, max_def_percentile=40.0,
        )
        if result:
            self.assertIn("edge", result[0])
            self.assertIn("def_ppp", result[0])
            self.assertIn("def_percentile", result[0])


class TestMatchAllIsolationMatchups(unittest.TestCase):
    """Tests for match_all_isolation_matchups()."""

    def setUp(self):
        self.off_stats = build_offensive_isolation_stats()
        self.def_rankings = build_defensive_isolation_rankings()

    def test_returns_list(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=10
        )
        self.assertIsInstance(result, list)

    def test_top_n_respected(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=10
        )
        self.assertLessEqual(len(result), 10)

    def test_required_keys_present(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=5, max_def_percentile=100.0
        )
        for entry in result:
            for key in ("player", "team", "off_percentile", "ppp",
                        "freq_pct", "opponent", "def_ppp", "def_percentile", "edge"):
                self.assertIn(key, entry)

    def test_sorted_by_edge_descending(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=50, max_def_percentile=100.0
        )
        for i in range(len(result) - 1):
            self.assertGreaterEqual(result[i]["edge"], result[i + 1]["edge"])

    def test_player_not_matched_against_own_team(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=500, max_def_percentile=100.0
        )
        for entry in result:
            self.assertNotEqual(entry["team"], entry["opponent"])

    def test_max_def_percentile_filter(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=500, max_def_percentile=20.0
        )
        for entry in result:
            self.assertLessEqual(entry["def_percentile"], 20.0)

    def test_empty_when_no_weak_defenses(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=50, max_def_percentile=-1.0
        )
        self.assertEqual(result, [])

    def test_min_off_percentile_filter(self):
        result = match_all_isolation_matchups(
            self.off_stats, self.def_rankings, top_n=500,
            max_def_percentile=100.0, min_off_percentile=80.0
        )
        for entry in result:
            self.assertGreaterEqual(entry["off_percentile"], 80.0)


class TestPredictIsolationMatchup(unittest.TestCase):
    """Tests for predict_isolation_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_isolation_stats()
        self.def_rankings = build_defensive_isolation_rankings()

    # ------------------------------------------------------------------
    # Basic return structure
    # ------------------------------------------------------------------

    def test_returns_dict_for_valid_inputs(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsInstance(result, dict)

    def test_required_keys_present(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        expected_keys = {
            "player", "team", "gp", "freq_pct", "ppp", "pts",
            "off_percentile", "opponent", "def_ppp", "def_freq_pct",
            "def_percentile", "edge", "verdict",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    # ------------------------------------------------------------------
    # SGA vs SAS — high-volume iso scorer vs SAS defense
    # ------------------------------------------------------------------

    def test_sga_vs_sas_player_fields(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Shai Gilgeous-Alexander")
        self.assertEqual(result["team"], "OKC")
        self.assertAlmostEqual(result["ppp"], 1.17)
        self.assertAlmostEqual(result["off_percentile"], 91.4)

    def test_sga_vs_sas_opponent_fields(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["opponent"], "SAS")
        self.assertAlmostEqual(result["def_ppp"], 0.92)

    def test_sga_vs_sas_edge(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(result["edge"], round(1.17 - 0.92, 3))

    def test_sga_vs_sas_verdict_favorable(self):
        result = predict_isolation_matchup(
            "Shai Gilgeous-Alexander", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["verdict"], "FAVORABLE")

    # ------------------------------------------------------------------
    # Harden vs SAS — lower edge (~0.14) → NEUTRAL
    # ------------------------------------------------------------------

    def test_harden_vs_sas_verdict_neutral(self):
        result = predict_isolation_matchup(
            "James Harden", "SAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    # ------------------------------------------------------------------
    # Verdict thresholds
    # ------------------------------------------------------------------

    def test_verdict_tough_when_edge_below_minus_threshold(self):
        player = OffensiveIsolationStats(
            player="Tough Player", team="AAA", gp=50,
            poss=5.0, freq_pct=20.0, ppp=0.75, pts=5.0,
            fgm=1.0, fga=2.0, fg_pct=50.0, efg_pct=50.0,
            ft_freq_pct=10.0, tov_freq_pct=5.0, sf_freq_pct=5.0,
            and_one_freq_pct=0.0, score_freq_pct=50.0, percentile=20.0,
        )
        # PHX allows 0.81 PPP → edge = 0.75 - 0.81 = -0.06 → NEUTRAL
        # OKC allows 0.82 PPP → edge = 0.75 - 0.82 = -0.07 → NEUTRAL
        # PHX percentile=100, let's use ATL (ppp=1.05, poor defense)... no
        # Actually for TOUGH we need edge <= -0.15, so player ppp=0.75 vs
        # a team that allows 0.91+, like SAS (0.92) → edge = -0.17 → TOUGH
        result = predict_isolation_matchup(
            "Tough Player", "SAS", [player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        player = OffensiveIsolationStats(
            player="Neutral Player", team="BBB", gp=50,
            poss=5.0, freq_pct=15.0, ppp=0.95, pts=5.0,
            fgm=1.0, fga=2.0, fg_pct=50.0, efg_pct=50.0,
            ft_freq_pct=10.0, tov_freq_pct=5.0, sf_freq_pct=5.0,
            and_one_freq_pct=0.0, score_freq_pct=50.0, percentile=50.0,
        )
        # SAS allows 0.92 PPP → edge = 0.95 - 0.92 = 0.03 → NEUTRAL
        result = predict_isolation_matchup(
            "Neutral Player", "SAS", [player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    # ------------------------------------------------------------------
    # Not-found cases
    # ------------------------------------------------------------------

    def test_returns_none_for_unknown_player(self):
        result = predict_isolation_matchup(
            "Nobody Famous", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_isolation_matchup(
            "James Harden", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Case-insensitive player name lookup
    # ------------------------------------------------------------------

    def test_case_insensitive_player_name(self):
        result_lower = predict_isolation_matchup(
            "shai gilgeous-alexander", "SAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_isolation_matchup(
            "SHAI GILGEOUS-ALEXANDER", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    # ------------------------------------------------------------------
    # Edge formula
    # ------------------------------------------------------------------

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_isolation_matchup(
            "Anthony Edwards", "ATL", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )


# ===========================================================================
# Offensive PnR Ball Handler analytics tests
# ===========================================================================

class TestBuildOffensivePnrBallHandlerStats(unittest.TestCase):
    """Tests for build_offensive_pnr_ball_handler_stats()."""

    def setUp(self):
        self.stats = build_offensive_pnr_ball_handler_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 100)

    def test_all_items_are_offensive_pnr_ball_handler_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensivePnrBallHandlerStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_luka_fields(self):
        """Luka Dončić should be the highest-volume PnR ball handler."""
        luka = next(s for s in self.stats if s.player == "Luka Dončić")
        self.assertEqual(luka.team, "LAL")
        self.assertAlmostEqual(luka.freq_pct, 69.1)
        self.assertAlmostEqual(luka.ppp, 0.93)
        self.assertAlmostEqual(luka.percentile, 55.9)

    def test_curry_fields(self):
        """Stephen Curry spot-check."""
        curry = next(s for s in self.stats if s.player == "Stephen Curry")
        self.assertEqual(curry.team, "GSW")
        self.assertEqual(curry.gp, 36)
        self.assertAlmostEqual(curry.ppp, 1.01)
        self.assertAlmostEqual(curry.percentile, 72.8)

    def test_known_players_present(self):
        names = {s.player for s in self.stats}
        for expected in (
            "Luka Dončić", "Shai Gilgeous-Alexander", "Jalen Brunson",
            "James Harden", "LeBron James", "Stephen Curry",
        ):
            self.assertIn(expected, names)

    def test_batch2_players_present(self):
        """All batch-2 PnR ball handler players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Dillon Brooks", "Anfernee Simons", "Coby White", "Desmond Bane",
            "T.J. McConnell", "Ryan Rollins", "Scottie Barnes", "Jalen Suggs",
            "Tre Mann", "Stephon Castle", "Marcus Smart", "Kobe Sanders",
            "Cooper Flagg", "Amen Thompson", "Jimmy Butler III",
            "Norman Powell", "Dennis Schröder", "Payton Pritchard",
            "Davion Mitchell", "Jaime Jaquez Jr.", "Derik Queen",
            "Andrew Wiggins", "Jaylen Wells",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        """All batch-3 PnR ball handler players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Jaden McDaniels", "Franz Wagner", "Kentavious Caldwell-Pope",
            "Jalen Green", "Dru Smith", "Tobias Harris", "Jordan Clarkson",
            "Aaron Wiggins", "Jalen Pickett", "Caris LeVert",
            "P.J. Washington", "Cam Thomas", "Josh Hart", "Zach LaVine",
            "Aaron Gordon", "Bones Hyland", "Pelle Larsson", "Jordan Miller",
            "Naji Marshall", "Kyle Kuzma",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        """All batch-4 PnR ball handler players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Shaedon Sharpe", "Nolan Traore", "Michael Porter Jr.",
            "Miles Bridges", "Nikola Vučević", "Brice Sensabaugh",
            "De'Anthony Melton", "Bilal Coulibaly", "Ty Jerome",
            "Ousmane Dieng", "Quentin Grimes", "Rob Dillingham",
            "OG Anunoby", "Myles Turner", "Mikal Bridges",
            "Kevin Porter Jr.", "Collin Sexton", "Lauri Markkanen",
            "Derrick White", "Victor Wembanyama",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_batch5_players_present(self):
        """All batch-5 PnR ball handler players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Jeremiah Fears", "Jamal Shead", "Devin Carter", "VJ Edgecombe",
            "Dylan Harper", "Reed Sheppard", "Ace Bailey", "Bub Carrington",
            "Jaden Ivey", "Caleb Love", "Tremont Waters", "Tre Johnson",
            "Cason Wallace", "Daniss Jenkins", "Ajay Mitchell", "Will Riley",
            "Max Christie", "Saddiq Bey", "Gradey Dick", "Ryan Nembhard",
            "Jonathan Kuminga",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-5 players: {missing}")

    def test_payton_pritchard_fields(self):
        """Payton Pritchard spot-check (batch-2 high-ppp entry)."""
        pp = next(s for s in self.stats if s.player == "Payton Pritchard")
        self.assertEqual(pp.team, "BOS")
        self.assertEqual(pp.gp, 56)
        self.assertAlmostEqual(pp.ppp, 1.00)
        self.assertAlmostEqual(pp.percentile, 70.7)

    def test_ty_jerome_fields(self):
        """Ty Jerome (MEM, 8 GP) batch-3 spot-check."""
        tj = next(s for s in self.stats if s.player == "Ty Jerome")
        self.assertEqual(tj.team, "MEM")
        self.assertEqual(tj.gp, 8)
        self.assertAlmostEqual(tj.ppp, 0.98)
        self.assertAlmostEqual(tj.percentile, 64.9)

    def test_jonathan_kuminga_fields(self):
        """Jonathan Kuminga (GSW, batch-5 last entry) spot-check."""
        jk = next(s for s in self.stats if s.player == "Jonathan Kuminga")
        self.assertEqual(jk.team, "GSW")
        self.assertEqual(jk.gp, 20)
        self.assertAlmostEqual(jk.ppp, 0.83)
        self.assertAlmostEqual(jk.percentile, 23.5)


class TestRankPlayersByOffensivePnrBallHandler(unittest.TestCase):
    """Tests for rank_players_by_offensive_pnr_ball_handler()."""

    def setUp(self):
        self.stats = build_offensive_pnr_ball_handler_stats()
        self.ranked = rank_players_by_offensive_pnr_ball_handler(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_pnr_ball_handler()
        self.assertGreater(len(ranked_default), 0)


class TestFindPnrBallHandlerScorers(unittest.TestCase):
    """Tests for find_pnr_ball_handler_scorers()."""

    def setUp(self):
        self.pnr_stats = build_offensive_pnr_ball_handler_stats()
        self.def_rankings = build_pnr_ball_handler_defensive_rankings()

    def test_returns_list(self):
        results = find_pnr_ball_handler_scorers(self.pnr_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 20.0
        results = find_pnr_ball_handler_scorers(self.pnr_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 0.90
        results = find_pnr_ball_handler_scorers(self.pnr_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_pnr_ball_handler_scorers(self.pnr_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_pnr_ball_handler_scorers(self.pnr_stats)
        if results:
            keys = results[0].keys()
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, keys)

    def test_def_ppp_none_when_no_opponent(self):
        results = find_pnr_ball_handler_scorers(self.pnr_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_pnr_ball_handler_scorers(
            self.pnr_stats, "POR", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_luka_in_high_freq_scorers(self):
        results = find_pnr_ball_handler_scorers(
            self.pnr_stats, min_freq_pct=50.0, min_ppp=0.85
        )
        players = [r["player"] for r in results]
        self.assertIn("Luka Dončić", players)


class TestPredictPnrBallHandlerMatchup(unittest.TestCase):
    """Tests for predict_pnr_ball_handler_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_pnr_ball_handler_stats()
        self.def_rankings = build_pnr_ball_handler_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_pnr_ball_handler_matchup(
            "Luka Dončić", "POR", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_pnr_ball_handler_matchup(
            "Luka Dončić", "POR", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_luka_vs_det(self):
        """DET has 100.0 defensive percentile (best), but lowest PPP allowed (0.79),
        making Luka's edge (0.93 - 0.79 = 0.14) FAVORABLE."""
        result = predict_pnr_ball_handler_matchup(
            "Luka Dončić", "DET", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Luka Dončić")
        self.assertEqual(result["opponent"], "DET")
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A player with low PPP vs a weak PnR defense (high PPP allowed) should get TOUGH."""
        weak_player = OffensivePnrBallHandlerStats(
            player="Weak PnR", team="TST", gp=50,
            poss=5.0, freq_pct=25.0, ppp=0.75, pts=4.0,
            fgm=1.0, fga=3.5, fg_pct=28.6, efg_pct=28.6,
            ft_freq_pct=8.0, tov_freq_pct=18.0, sf_freq_pct=6.0,
            and_one_freq_pct=1.0, score_freq_pct=33.0, percentile=10.0,
        )
        # POR allows 0.96 PPP → edge = 0.75 - 0.96 = -0.21 → TOUGH
        result = predict_pnr_ball_handler_matchup(
            "Weak PnR", "POR", [weak_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensivePnrBallHandlerStats(
            player="Avg PnR", team="TST", gp=50,
            poss=8.0, freq_pct=35.0, ppp=0.92, pts=7.5,
            fgm=2.0, fga=6.5, fg_pct=30.8, efg_pct=36.0,
            ft_freq_pct=10.0, tov_freq_pct=14.0, sf_freq_pct=8.0,
            and_one_freq_pct=1.5, score_freq_pct=40.0, percentile=50.0,
        )
        # CLE allows 0.81 PPP → edge = 0.92 - 0.81 = 0.11 → FAVORABLE
        # Use PHI (0.84 PPP): edge = 0.92 - 0.84 = 0.08 → NEUTRAL
        result = predict_pnr_ball_handler_matchup(
            "Avg PnR", "PHI", [avg_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_pnr_ball_handler_matchup(
            "Nobody Famous", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_pnr_ball_handler_matchup(
            "Luka Dončić", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_pnr_ball_handler_matchup(
            "luka dončić", "SAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_pnr_ball_handler_matchup(
            "LUKA DONČIĆ", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_pnr_ball_handler_matchup(
            "Stephen Curry", "POR", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_pnr_ball_handler_matchup("Jalen Brunson", "SAS")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Jalen Brunson")


# ===========================================================================
# Offensive PnR roll man (screener) analytics tests
# ===========================================================================

class TestBuildOffensivePnrManStats(unittest.TestCase):
    """Tests for build_offensive_pnr_man_stats()."""

    def setUp(self):
        self.stats = build_offensive_pnr_man_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 100)

    def test_all_items_are_offensive_pnr_man_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensivePnrManStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_jokic_fields(self):
        """Nikola Jokić should be the top roll man by PPP."""
        jokic = next(s for s in self.stats if s.player == "Nikola Jokić")
        self.assertEqual(jokic.team, "DEN")
        self.assertAlmostEqual(jokic.ppp, 1.43)
        self.assertAlmostEqual(jokic.percentile, 79.3)

    def test_sengun_fields(self):
        """Alperen Sengun spot-check."""
        sengun = next(s for s in self.stats if s.player == "Alperen Sengun")
        self.assertEqual(sengun.team, "HOU")
        self.assertEqual(sengun.gp, 49)
        self.assertAlmostEqual(sengun.ppp, 1.38)
        self.assertAlmostEqual(sengun.percentile, 75.9)

    def test_known_players_present(self):
        names = {s.player for s in self.stats}
        for expected in (
            "Nikola Jokić", "Alperen Sengun", "Bam Adebayo",
            "Domantas Sabonis", "Karl-Anthony Towns", "Joel Embiid",
            "Jarrett Allen", "Chet Holmgren",
        ):
            self.assertIn(expected, names)

    def test_batch2_players_present(self):
        """All batch-2 roll man players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Wendell Carter Jr.", "Xavier Tillman", "Moritz Wagner", "Naz Reid",
            "Nick Richards", "Charles Bassey", "Keyonte George",
            "Maozinho Moreira", "Mo Bamba", "Kel'el Ware", "Paul Reed",
            "Trayce Jackson-Davis", "Duop Reath", "Bismack Biyombo",
            "Taj Gibson", "Aaron Nesmith", "Jericho Sims", "JaVale McGee",
            "Mason Plumlee", "Robin Lopez",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        """All batch-3 roll man players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Zach Collins", "Trey Lyles", "Udoka Azubuike",
            "Willy Hernangómez", "Santi Aldama", "Montrezl Harrell",
            "Boban Marjanović", "Goga Bitadze", "Mike Muscala",
            "Thomas Bryant", "Drew Eubanks", "Trendon Watford",
            "Luke Kornet", "Gary Clark", "JT Thor",
            "Marvin Bagley III", "Ariel Hukporti", "Jaxson Hayes",
            "Kai Jones",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        """All batch-4 roll man players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Damian Lillard", "Tony Bradley", "James Wiseman", "Killian Hayes",
            "Christian Wood", "Brice Sensabaugh", "Efe Abanda",
            "Moussa Diabate", "Kevon Looney", "Harry Giles III",
            "Dario Šarić", "Keaton Wallace", "Nerlens Noel", "Justin Patton",
            "Vit Krejci", "Usman Garuba", "Zeke Nnaji", "Saben Lee",
            "Daishen Nix", "Chris Boucher",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_batch5_players_present(self):
        """All batch-5 roll man players are in the dataset."""
        names = {s.player for s in self.stats}
        expected = {
            "Victor Wembanyama", "Derik Queen", "Zaccharie Risacher",
            "Isaiah Collier", "Stephon Castle", "Reed Sheppard",
            "Rob Dillingham", "Dylan Harper", "Ace Bailey", "Bub Carrington",
            "Jaden Ivey", "Caleb Love", "Cason Wallace", "Daniss Jenkins",
            "Ajay Mitchell", "Will Riley", "Max Christie", "Gradey Dick",
            "Ryan Nembhard", "Jonathan Kuminga",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-5 players: {missing}")

    def test_victor_wembanyama_fields(self):
        """Victor Wembanyama (batch-5 first entry) spot-check."""
        vw = next(s for s in self.stats if s.player == "Victor Wembanyama")
        self.assertEqual(vw.team, "SAS")
        self.assertEqual(vw.gp, 43)
        self.assertAlmostEqual(vw.ppp, 1.19)
        self.assertAlmostEqual(vw.percentile, 44.8)

    def test_luke_kornet_fields(self):
        """Luke Kornet (batch-3 high-GP entry) spot-check."""
        lk = next(s for s in self.stats if s.player == "Luke Kornet")
        self.assertEqual(lk.team, "BOS")
        self.assertEqual(lk.gp, 57)
        self.assertAlmostEqual(lk.ppp, 1.17)
        self.assertAlmostEqual(lk.percentile, 41.4)

    def test_jonathan_kuminga_fields(self):
        """Jonathan Kuminga (batch-5 last entry) spot-check."""
        jk = next(s for s in self.stats if s.player == "Jonathan Kuminga")
        self.assertEqual(jk.team, "GSW")
        self.assertEqual(jk.gp, 20)
        self.assertAlmostEqual(jk.ppp, 1.10)
        self.assertAlmostEqual(jk.percentile, 24.1)


class TestRankPlayersByOffensivePnrMan(unittest.TestCase):
    """Tests for rank_players_by_offensive_pnr_man()."""

    def setUp(self):
        self.stats = build_offensive_pnr_man_stats()
        self.ranked = rank_players_by_offensive_pnr_man(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_pnr_man()
        self.assertGreater(len(ranked_default), 0)


class TestFindPnrManScorers(unittest.TestCase):
    """Tests for find_pnr_man_scorers()."""

    def setUp(self):
        self.pnr_stats = build_offensive_pnr_man_stats()
        self.def_rankings = build_pnr_man_defensive_rankings()

    def test_returns_list(self):
        results = find_pnr_man_scorers(self.pnr_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 20.0
        results = find_pnr_man_scorers(self.pnr_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 1.15
        results = find_pnr_man_scorers(self.pnr_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_pnr_man_scorers(self.pnr_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_pnr_man_scorers(self.pnr_stats)
        if results:
            keys = results[0].keys()
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, keys)

    def test_def_ppp_none_when_no_opponent(self):
        results = find_pnr_man_scorers(self.pnr_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_pnr_man_scorers(
            self.pnr_stats, "LAL", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_jokic_in_high_freq_scorers(self):
        results = find_pnr_man_scorers(
            self.pnr_stats, min_freq_pct=25.0, min_ppp=1.20
        )
        players = [r["player"] for r in results]
        self.assertIn("Nikola Jokić", players)


class TestPredictPnrManMatchup(unittest.TestCase):
    """Tests for predict_pnr_man_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_pnr_man_stats()
        self.def_rankings = build_pnr_man_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_pnr_man_matchup(
            "Nikola Jokić", "LAL", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_pnr_man_matchup(
            "Nikola Jokić", "LAL", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_jokic_vs_lal(self):
        """LAL allows 1.27 PPP and Jokić has 1.43 → edge = 0.16 → FAVORABLE."""
        result = predict_pnr_man_matchup(
            "Nikola Jokić", "LAL", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Nikola Jokić")
        self.assertEqual(result["opponent"], "LAL")
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A weak roll man vs a strong PnR man defense should get TOUGH."""
        weak_player = OffensivePnrManStats(
            player="Weak Roll", team="TST", gp=50,
            poss=3.0, freq_pct=20.0, ppp=0.90, pts=2.7,
            fgm=1.0, fga=2.5, fg_pct=40.0, efg_pct=42.0,
            ft_freq_pct=8.0, tov_freq_pct=8.0, sf_freq_pct=7.0,
            and_one_freq_pct=1.0, score_freq_pct=43.0, percentile=5.0,
        )
        # HOU allows 0.96 PPP → edge = 0.90 - 0.96 = -0.06 → NEUTRAL
        # DEN allows 1.02 PPP → edge = 0.90 - 1.02 = -0.12 → TOUGH
        result = predict_pnr_man_matchup(
            "Weak Roll", "DEN", [weak_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensivePnrManStats(
            player="Avg Roll", team="TST", gp=50,
            poss=5.0, freq_pct=28.0, ppp=1.10, pts=5.5,
            fgm=2.0, fga=4.0, fg_pct=50.0, efg_pct=52.0,
            ft_freq_pct=10.0, tov_freq_pct=5.0, sf_freq_pct=9.0,
            and_one_freq_pct=2.0, score_freq_pct=53.0, percentile=50.0,
        )
        # HOU allows 0.96 PPP → edge = 1.10 - 0.96 = 0.14 → FAVORABLE
        # SAS allows 1.00 PPP → edge = 1.10 - 1.00 = 0.10 → FAVORABLE
        # MEM allows 1.01 PPP → edge = 1.10 - 1.01 = 0.09 → NEUTRAL
        result = predict_pnr_man_matchup(
            "Avg Roll", "MEM", [avg_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_pnr_man_matchup(
            "Nobody Famous", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_pnr_man_matchup(
            "Nikola Jokić", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_pnr_man_matchup(
            "nikola jokić", "SAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_pnr_man_matchup(
            "NIKOLA JOKIĆ", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_pnr_man_matchup(
            "Alperen Sengun", "SAS", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_pnr_man_matchup("Bam Adebayo", "SAS")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Bam Adebayo")


# ===========================================================================
# Offensive post-up analytics tests
# ===========================================================================

class TestBuildOffensivePostUpStats(unittest.TestCase):
    """Tests for build_offensive_post_up_stats()."""

    def setUp(self):
        self.stats = build_offensive_post_up_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 60)

    def test_all_items_are_offensive_post_up_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensivePostUpStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_embiid_fields(self):
        """Joel Embiid should be the top post-up scorer by freq × ppp."""
        embiid = next(s for s in self.stats if s.player == "Joel Embiid")
        self.assertEqual(embiid.team, "PHI")
        self.assertAlmostEqual(embiid.ppp, 1.10)
        self.assertAlmostEqual(embiid.percentile, 72.4)

    def test_jokic_fields(self):
        """Nikola Jokić spot-check."""
        jokic = next(s for s in self.stats if s.player == "Nikola Jokić")
        self.assertEqual(jokic.team, "DEN")
        self.assertEqual(jokic.gp, 42)
        self.assertAlmostEqual(jokic.ppp, 1.06)
        self.assertAlmostEqual(jokic.percentile, 62.1)

    def test_known_players_present(self):
        names = {s.player for s in self.stats}
        for expected in (
            "Joel Embiid", "Nikola Jokić", "Giannis Antetokounmpo",
            "LeBron James", "Domantas Sabonis", "Bam Adebayo",
            "Kevin Durant", "Jayson Tatum",
        ):
            self.assertIn(expected, names)

    def test_batch2_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Draymond Green", "Rudy Gobert", "DeMar DeRozan",
            "Andrew Wiggins", "Jaren Jackson Jr.", "Markelle Fultz",
            "Harrison Barnes", "Thaddeus Young", "Nic Claxton",
            "Wendell Carter Jr.", "Precious Achiuwa", "Marvin Bagley III",
            "Dario Šarić", "Ivica Zubac", "Montrezl Harrell",
            "Zach Collins", "JaVale McGee", "Moritz Wagner",
            "Mark Williams",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Jalen Duren", "Deandre Ayton", "Trey Lyles", "Jusuf Nurkić",
            "Xavier Tillman", "Steven Adams", "Goga Bitadze",
            "Willy Hernangómez", "Charles Bassey", "Taj Gibson",
            "Naz Reid", "Bismack Biyombo", "Robin Lopez",
            "Harry Giles III", "Udoka Azubuike", "Boban Marjanović",
            "Saben Lee", "Mason Plumlee",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Victor Wembanyama", "Derik Queen", "Zaccharie Risacher",
            "Stephon Castle", "Dylan Harper", "Ace Bailey",
            "Kel'el Ware", "Bub Carrington", "Jaden Ivey",
            "Gradey Dick", "Max Christie", "Cason Wallace",
            "Jonathan Kuminga", "Daniss Jenkins", "Ajay Mitchell",
            "Will Riley", "Ryan Nembhard", "Caleb Love", "Rob Dillingham",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_victor_wembanyama_fields(self):
        """Victor Wembanyama (batch-4 first entry) spot-check."""
        vw = next(s for s in self.stats if s.player == "Victor Wembanyama")
        self.assertEqual(vw.team, "SAS")
        self.assertEqual(vw.gp, 43)
        self.assertAlmostEqual(vw.ppp, 1.08)
        self.assertAlmostEqual(vw.percentile, 62.1)

    def test_demar_derozan_fields(self):
        """DeMar DeRozan (batch-2, high-usage) spot-check."""
        dd = next(s for s in self.stats if s.player == "DeMar DeRozan")
        self.assertEqual(dd.team, "SAC")
        self.assertAlmostEqual(dd.ppp, 0.99)
        self.assertAlmostEqual(dd.percentile, 31.0)


class TestRankPlayersByOffensivePostUp(unittest.TestCase):
    """Tests for rank_players_by_offensive_post_up()."""

    def setUp(self):
        self.stats = build_offensive_post_up_stats()
        self.ranked = rank_players_by_offensive_post_up(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_post_up()
        self.assertGreater(len(ranked_default), 0)


class TestFindPostUpScorers(unittest.TestCase):
    """Tests for find_post_up_scorers()."""

    def setUp(self):
        self.post_up_stats = build_offensive_post_up_stats()
        self.def_rankings = build_post_up_defensive_rankings()

    def test_returns_list(self):
        results = find_post_up_scorers(self.post_up_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 20.0
        results = find_post_up_scorers(self.post_up_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 1.05
        results = find_post_up_scorers(self.post_up_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_post_up_scorers(self.post_up_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_post_up_scorers(self.post_up_stats)
        if results:
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, results[0].keys())

    def test_def_ppp_none_when_no_opponent(self):
        results = find_post_up_scorers(self.post_up_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_post_up_scorers(
            self.post_up_stats, "SAC", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_embiid_in_high_freq_scorers(self):
        results = find_post_up_scorers(
            self.post_up_stats, min_freq_pct=30.0, min_ppp=1.05
        )
        players = [r["player"] for r in results]
        self.assertIn("Joel Embiid", players)


class TestPredictPostUpMatchup(unittest.TestCase):
    """Tests for predict_post_up_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_post_up_stats()
        self.def_rankings = build_post_up_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_post_up_matchup(
            "Joel Embiid", "SAC", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_post_up_matchup(
            "Joel Embiid", "SAC", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_embiid_vs_sac(self):
        """SAC allows 1.11 PPP and Embiid has 1.10 → edge ≈ -0.01 → NEUTRAL."""
        result = predict_post_up_matchup(
            "Joel Embiid", "SAC", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Joel Embiid")
        self.assertEqual(result["opponent"], "SAC")
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_verdict_favorable_for_large_positive_edge(self):
        """A strong post-up scorer vs a weak post-up defense → FAVORABLE."""
        strong_player = OffensivePostUpStats(
            player="Strong Post", team="TST", gp=50,
            poss=6.0, freq_pct=30.0, ppp=1.15, pts=6.9,
            fgm=2.5, fga=4.5, fg_pct=55.0, efg_pct=55.0,
            ft_freq_pct=20.0, tov_freq_pct=9.0, sf_freq_pct=18.0,
            and_one_freq_pct=4.0, score_freq_pct=55.0, percentile=70.0,
        )
        # MIN has 1.13 PPP allowed → edge = 1.15 - 1.13 = 0.02 → NEUTRAL
        # LAC has 1.11 PPP allowed → edge = 1.15 - 1.11 = 0.04 → NEUTRAL
        # IND has 1.10 PPP allowed → edge = 1.15 - 1.10 = 0.05 → NEUTRAL
        # SAC has 1.11 PPP allowed → edge = 1.15 - 1.11 = 0.04 → NEUTRAL
        # BKN has 1.10 PPP allowed → edge = 1.15 - 1.10 = 0.05 → NEUTRAL
        # MIL has 0.95 PPP allowed → edge = 1.15 - 0.95 = 0.20 → FAVORABLE
        result = predict_post_up_matchup(
            "Strong Post", "MIL", [strong_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A weak post-up scorer vs a strong post-up defense → TOUGH."""
        weak_player = OffensivePostUpStats(
            player="Weak Post", team="TST", gp=50,
            poss=3.0, freq_pct=15.0, ppp=0.70, pts=2.1,
            fgm=1.0, fga=2.8, fg_pct=36.0, efg_pct=36.0,
            ft_freq_pct=10.0, tov_freq_pct=14.0, sf_freq_pct=8.0,
            and_one_freq_pct=1.5, score_freq_pct=38.0, percentile=5.0,
        )
        # DET allows 0.74 PPP → edge = 0.70 - 0.74 = -0.04 → NEUTRAL
        # SAS allows 0.78 PPP → edge = 0.70 - 0.78 = -0.08 → NEUTRAL
        # LAL allows 0.93 PPP → edge = 0.70 - 0.93 = -0.23 → TOUGH
        result = predict_post_up_matchup(
            "Weak Post", "LAL", [weak_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensivePostUpStats(
            player="Avg Post", team="TST", gp=50,
            poss=4.0, freq_pct=18.0, ppp=1.00, pts=4.0,
            fgm=1.7, fga=3.8, fg_pct=45.0, efg_pct=45.0,
            ft_freq_pct=14.0, tov_freq_pct=10.0, sf_freq_pct=12.0,
            and_one_freq_pct=2.5, score_freq_pct=48.0, percentile=45.0,
        )
        # PHI allows 1.00 PPP → edge = 1.00 - 1.00 = 0.00 → NEUTRAL
        result = predict_post_up_matchup(
            "Avg Post", "PHI", [avg_player], self.def_rankings
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_post_up_matchup(
            "Nobody Famous", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_post_up_matchup(
            "Joel Embiid", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_post_up_matchup(
            "joel embiid", "SAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_post_up_matchup(
            "JOEL EMBIID", "SAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_post_up_matchup(
            "Nikola Jokić", "DET", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_post_up_matchup("Joel Embiid", "SAS")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Joel Embiid")


# ===========================================================================
# Offensive spot-up analytics tests
# ===========================================================================

class TestBuildOffensiveSpotUpStats(unittest.TestCase):
    """Tests for build_offensive_spot_up_stats()."""

    def setUp(self):
        self.stats = build_offensive_spot_up_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 60)

    def test_all_items_are_offensive_spot_up_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensiveSpotUpStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_curry_fields(self):
        """Stephen Curry should be the top spot-up scorer."""
        curry = next(s for s in self.stats if s.player == "Stephen Curry")
        self.assertEqual(curry.team, "GSW")
        self.assertAlmostEqual(curry.ppp, 1.29)
        self.assertAlmostEqual(curry.percentile, 99.0)

    def test_klay_fields(self):
        """Klay Thompson spot-check."""
        klay = next(s for s in self.stats if s.player == "Klay Thompson")
        self.assertEqual(klay.team, "GSW")
        self.assertEqual(klay.gp, 68)
        self.assertAlmostEqual(klay.ppp, 1.21)
        self.assertAlmostEqual(klay.percentile, 96.6)

    def test_known_players_present(self):
        names = {s.player for s in self.stats}
        for expected in (
            "Stephen Curry", "Klay Thompson", "Buddy Hield",
            "Duncan Robinson", "Desmond Bane", "Kevin Durant",
            "Jayson Tatum", "Mikal Bridges",
        ):
            self.assertIn(expected, names)

    def test_batch2_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "CJ McCollum", "OG Anunoby", "Dorian Finney-Smith",
            "Josh Hart", "Dillon Brooks", "Saddiq Bey",
            "Jalen McDaniels", "Reggie Bullock", "Josh Richardson",
            "Royce O'Neale", "Danny Green", "Pat Connaughton",
            "Gary Harris", "Max Strus", "Goga Bitadze",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Patrick Beverley", "Anfernee Simons", "Caris LeVert",
            "Marcus Morris Sr.", "Derrick White", "Jae'Sean Tate",
            "Terance Mann", "Miles Bridges", "Donte DiVincenzo",
            "Terrence Ross", "Kyle Kuzma", "Harrison Barnes",
            "Josh Green", "Jalen Green", "Keldon Johnson",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Zaccharie Risacher", "Stephon Castle", "Gradey Dick",
            "Victor Wembanyama", "Derik Queen", "Cason Wallace",
            "Dylan Harper", "Ace Bailey", "Bub Carrington",
            "Max Christie", "Jaden Ivey", "Ryan Nembhard",
            "Rob Dillingham", "Ajay Mitchell", "Will Riley",
            "Daniss Jenkins", "Caleb Love", "Kel'el Ware",
            "Jonathan Kuminga",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_victor_wembanyama_fields(self):
        """Victor Wembanyama (batch-4) spot-check."""
        vw = next(s for s in self.stats if s.player == "Victor Wembanyama")
        self.assertEqual(vw.team, "SAS")
        self.assertEqual(vw.gp, 43)
        self.assertAlmostEqual(vw.ppp, 1.06)
        self.assertAlmostEqual(vw.percentile, 37.9)

    def test_derrick_white_fields(self):
        """Derrick White (batch-3) spot-check."""
        dw = next(s for s in self.stats if s.player == "Derrick White")
        self.assertEqual(dw.team, "BOS")
        self.assertAlmostEqual(dw.ppp, 1.06)
        self.assertAlmostEqual(dw.percentile, 37.9)


class TestRankPlayersByOffensiveSpotUp(unittest.TestCase):
    """Tests for rank_players_by_offensive_spot_up()."""

    def setUp(self):
        self.stats = build_offensive_spot_up_stats()
        self.ranked = rank_players_by_offensive_spot_up(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_spot_up()
        self.assertGreater(len(ranked_default), 0)


class TestFindSpotUpPlayerScorers(unittest.TestCase):
    """Tests for find_spot_up_player_scorers()."""

    def setUp(self):
        self.spot_up_stats = build_offensive_spot_up_stats()
        self.def_rankings = build_spot_up_defensive_rankings()

    def test_returns_list(self):
        results = find_spot_up_player_scorers(self.spot_up_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 30.0
        results = find_spot_up_player_scorers(self.spot_up_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 1.15
        results = find_spot_up_player_scorers(self.spot_up_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_spot_up_player_scorers(self.spot_up_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_spot_up_player_scorers(self.spot_up_stats)
        if results:
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, results[0].keys())

    def test_def_ppp_none_when_no_opponent(self):
        results = find_spot_up_player_scorers(self.spot_up_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_spot_up_player_scorers(
            self.spot_up_stats, "OKC", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_curry_in_high_freq_scorers(self):
        results = find_spot_up_player_scorers(
            self.spot_up_stats, min_freq_pct=40.0, min_ppp=1.20
        )
        players = [r["player"] for r in results]
        self.assertIn("Stephen Curry", players)


class TestPredictSpotUpMatchup(unittest.TestCase):
    """Tests for predict_spot_up_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_spot_up_stats()
        self.def_rankings = build_spot_up_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_spot_up_matchup(
            "Stephen Curry", "OKC", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_spot_up_matchup(
            "Stephen Curry", "OKC", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_curry_player_and_opponent_fields(self):
        result = predict_spot_up_matchup(
            "Stephen Curry", "OKC", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Stephen Curry")
        self.assertEqual(result["opponent"], "OKC")

    def test_verdict_favorable_for_large_positive_edge(self):
        """A top shooter vs a weak spot-up defense → FAVORABLE."""
        strong_player = OffensiveSpotUpStats(
            player="Elite Shooter", team="TST", gp=55,
            poss=10.0, freq_pct=50.0, ppp=1.25, pts=12.5,
            fgm=4.5, fga=9.0, fg_pct=50.0, efg_pct=65.0,
            ft_freq_pct=5.0, tov_freq_pct=2.5, sf_freq_pct=3.8,
            and_one_freq_pct=0.5, score_freq_pct=56.0, percentile=90.0,
        )
        # find a team with relatively high def ppp allowed so we can test
        # FAVORABLE when edge >= 0.10.
        # Build a synthetic weak defense with ppp=1.00 → edge = 1.25-1.00 = 0.25
        from nba_playtype_props import DefensiveSpotUpStats
        weak_def = {"ZZZ": DefensiveSpotUpStats(
            team="ZZZ", gp=55, poss=8.0, freq_pct=20.0, ppp=1.00,
            pts=8.0, fgm=3.0, fga=6.5, fg_pct=46.0, efg_pct=58.0,
            ft_freq_pct=4.0, tov_freq_pct=3.5, sf_freq_pct=3.0,
            and_one_freq_pct=0.5, score_freq_pct=52.0, percentile=5.0,
        )}
        result = predict_spot_up_matchup(
            "Elite Shooter", "ZZZ", [strong_player], weak_def
        )
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A below-average shooter vs elite spot-up defense → TOUGH."""
        weak_player = OffensiveSpotUpStats(
            player="Cold Shooter", team="TST", gp=55,
            poss=5.0, freq_pct=22.0, ppp=0.85, pts=4.3,
            fgm=1.5, fga=4.5, fg_pct=34.0, efg_pct=44.0,
            ft_freq_pct=3.5, tov_freq_pct=4.5, sf_freq_pct=2.5,
            and_one_freq_pct=0.3, score_freq_pct=40.0, percentile=8.0,
        )
        from nba_playtype_props import DefensiveSpotUpStats
        elite_def = {"ZZZ": DefensiveSpotUpStats(
            team="ZZZ", gp=55, poss=6.5, freq_pct=15.0, ppp=1.10,
            pts=7.2, fgm=2.6, fga=5.5, fg_pct=47.0, efg_pct=60.0,
            ft_freq_pct=4.2, tov_freq_pct=3.0, sf_freq_pct=3.2,
            and_one_freq_pct=0.5, score_freq_pct=53.0, percentile=95.0,
        )}
        result = predict_spot_up_matchup(
            "Cold Shooter", "ZZZ", [weak_player], elite_def
        )
        # edge = 0.85 - 1.10 = -0.25 → TOUGH
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensiveSpotUpStats(
            player="Avg Shooter", team="TST", gp=55,
            poss=6.0, freq_pct=28.0, ppp=1.07, pts=6.4,
            fgm=2.3, fga=5.4, fg_pct=43.0, efg_pct=57.0,
            ft_freq_pct=4.0, tov_freq_pct=3.2, sf_freq_pct=3.0,
            and_one_freq_pct=0.5, score_freq_pct=48.0, percentile=40.0,
        )
        from nba_playtype_props import DefensiveSpotUpStats
        avg_def = {"ZZZ": DefensiveSpotUpStats(
            team="ZZZ", gp=55, poss=7.0, freq_pct=18.0, ppp=1.05,
            pts=7.4, fgm=2.7, fga=5.8, fg_pct=46.0, efg_pct=59.0,
            ft_freq_pct=4.1, tov_freq_pct=3.1, sf_freq_pct=3.1,
            and_one_freq_pct=0.5, score_freq_pct=52.0, percentile=45.0,
        )}
        # edge = 1.07 - 1.05 = 0.02 → NEUTRAL
        result = predict_spot_up_matchup(
            "Avg Shooter", "ZZZ", [avg_player], avg_def
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_spot_up_matchup(
            "Nobody Famous", "OKC", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_spot_up_matchup(
            "Stephen Curry", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_spot_up_matchup(
            "stephen curry", "OKC", self.off_stats, self.def_rankings
        )
        result_upper = predict_spot_up_matchup(
            "STEPHEN CURRY", "OKC", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_spot_up_matchup(
            "Klay Thompson", "OKC", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_spot_up_matchup("Stephen Curry", "OKC")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Stephen Curry")


# ===========================================================================
# Offensive hand-off analytics tests
# ===========================================================================

class TestBuildOffensiveHandoffStats(unittest.TestCase):
    """Tests for build_offensive_handoff_stats()."""

    def setUp(self):
        self.stats = build_offensive_handoff_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 55)

    def test_all_items_are_offensive_handoff_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensiveHandoffStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_haliburton_fields(self):
        """Tyrese Haliburton data validation."""
        hali = next(s for s in self.stats if s.player == "Tyrese Haliburton")
        self.assertEqual(hali.team, "IND")
        self.assertAlmostEqual(hali.ppp, 1.20)
        self.assertAlmostEqual(hali.percentile, 99.0)

    def test_lamelo_fields(self):
        """LaMelo Ball spot-check."""
        lamelo = next(s for s in self.stats if s.player == "LaMelo Ball")
        self.assertEqual(lamelo.team, "CHA")
        self.assertEqual(lamelo.gp, 56)
        self.assertAlmostEqual(lamelo.ppp, 1.18)
        self.assertAlmostEqual(lamelo.percentile, 96.6)

    def test_batch1_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Tyrese Haliburton", "LaMelo Ball", "Trae Young", "Kyrie Irving",
            "Donovan Mitchell", "Ja Morant", "De'Aaron Fox", "Jalen Brunson",
            "Cole Anthony", "Malcolm Brogdon", "Terry Rozier", "Darius Garland",
            "Fred VanVleet", "Immanuel Quickley", "Cade Cunningham",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-1 players: {missing}")

    def test_batch2_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Jordan Poole", "Josh Giddey", "Anfernee Simons", "Dejounte Murray",
            "Jordan Nwora", "Bruce Brown", "Tre Mann", "Scoot Henderson",
            "Tyus Jones", "Patty Mills", "Jalen Suggs", "RJ Barrett",
            "Markelle Fultz", "Killian Hayes", "Monte Morris",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Ben Simmons", "Cameron Thomas", "Keyonte George", "Jordan Hawkins",
            "Bones Hyland", "Kevin Porter Jr.", "Devin Vassell", "Isaiah Joe",
            "Coby White", "Shaedon Sharpe", "Naji Marshall", "Gary Payton II",
            "Ochai Agbaji", "Quentin Grimes", "Josh Christopher",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Stephon Castle", "Gradey Dick", "Zaccharie Risacher", "Dylan Harper",
            "Ace Bailey", "Bub Carrington", "Cason Wallace", "Max Christie",
            "Rob Dillingham", "Ajay Mitchell", "Ryan Nembhard", "Will Riley",
            "Daniss Jenkins", "Caleb Love", "Kel'el Ware",
            "Jonathan Kuminga", "Derik Queen", "Victor Wembanyama",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_victor_wembanyama_fields(self):
        """Victor Wembanyama (batch-4) spot-check."""
        vw = next(s for s in self.stats if s.player == "Victor Wembanyama")
        self.assertEqual(vw.team, "SAS")
        self.assertEqual(vw.gp, 43)
        self.assertAlmostEqual(vw.ppp, 1.03)
        self.assertAlmostEqual(vw.percentile, 20.7)

    def test_scoot_henderson_fields(self):
        """Scoot Henderson (batch-2) spot-check."""
        scoot = next(s for s in self.stats if s.player == "Scoot Henderson")
        self.assertEqual(scoot.team, "POR")
        self.assertAlmostEqual(scoot.ppp, 1.08)
        self.assertAlmostEqual(scoot.percentile, 41.4)


class TestRankPlayersByOffensiveHandoff(unittest.TestCase):
    """Tests for rank_players_by_offensive_handoff()."""

    def setUp(self):
        self.stats = build_offensive_handoff_stats()
        self.ranked = rank_players_by_offensive_handoff(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_handoff()
        self.assertGreater(len(ranked_default), 0)


class TestFindHandoffPlayerScorers(unittest.TestCase):
    """Tests for find_handoff_player_scorers()."""

    def setUp(self):
        self.handoff_stats = build_offensive_handoff_stats()
        self.def_rankings = build_handoff_defensive_rankings()

    def test_returns_list(self):
        results = find_handoff_player_scorers(self.handoff_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 20.0
        results = find_handoff_player_scorers(self.handoff_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 1.10
        results = find_handoff_player_scorers(self.handoff_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_handoff_player_scorers(self.handoff_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_handoff_player_scorers(self.handoff_stats)
        if results:
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, results[0].keys())

    def test_def_ppp_none_when_no_opponent(self):
        results = find_handoff_player_scorers(self.handoff_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_handoff_player_scorers(
            self.handoff_stats, "WAS", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_haliburton_in_top_scorers(self):
        results = find_handoff_player_scorers(
            self.handoff_stats, min_freq_pct=20.0, min_ppp=1.15
        )
        players = [r["player"] for r in results]
        self.assertIn("Tyrese Haliburton", players)


class TestPredictHandoffMatchup(unittest.TestCase):
    """Tests for predict_handoff_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_handoff_stats()
        self.def_rankings = build_handoff_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_handoff_matchup(
            "Tyrese Haliburton", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_handoff_matchup(
            "Tyrese Haliburton", "WAS", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_player_and_opponent_fields(self):
        result = predict_handoff_matchup(
            "Tyrese Haliburton", "WAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Tyrese Haliburton")
        self.assertEqual(result["opponent"], "WAS")

    def test_verdict_favorable_for_large_positive_edge(self):
        """A top hand-off scorer vs a weak hand-off defense → FAVORABLE."""
        strong_player = OffensiveHandoffStats(
            player="Elite Handler", team="TST", gp=55,
            poss=5.0, freq_pct=20.0, ppp=1.25, pts=6.3,
            fgm=2.5, fga=4.8, fg_pct=52.0, efg_pct=64.0,
            ft_freq_pct=7.0, tov_freq_pct=5.5, sf_freq_pct=5.2,
            and_one_freq_pct=0.9, score_freq_pct=55.0, percentile=92.0,
        )
        from nba_playtype_props import DefensiveHandoffStats
        weak_def = {"ZZZ": DefensiveHandoffStats(
            team="ZZZ", gp=55, poss=4.0, freq_pct=12.0, ppp=1.00,
            pts=4.0, fgm=1.5, fga=3.5, fg_pct=43.0, efg_pct=56.0,
            ft_freq_pct=5.5, tov_freq_pct=6.0, sf_freq_pct=4.5,
            and_one_freq_pct=0.6, score_freq_pct=49.0, percentile=5.0,
        )}
        result = predict_handoff_matchup(
            "Elite Handler", "ZZZ", [strong_player], weak_def
        )
        # edge = 1.25 - 1.00 = 0.25 → FAVORABLE
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A below-average hand-off scorer vs elite hand-off defense → TOUGH."""
        weak_player = OffensiveHandoffStats(
            player="Cold Handler", team="TST", gp=55,
            poss=2.5, freq_pct=14.0, ppp=0.85, pts=2.1,
            fgm=0.8, fga=2.5, fg_pct=32.0, efg_pct=42.0,
            ft_freq_pct=4.5, tov_freq_pct=9.0, sf_freq_pct=3.5,
            and_one_freq_pct=0.3, score_freq_pct=38.0, percentile=6.0,
        )
        from nba_playtype_props import DefensiveHandoffStats
        elite_def = {"ZZZ": DefensiveHandoffStats(
            team="ZZZ", gp=55, poss=3.0, freq_pct=8.0, ppp=1.10,
            pts=3.3, fgm=1.2, fga=2.8, fg_pct=43.0, efg_pct=57.0,
            ft_freq_pct=5.0, tov_freq_pct=5.5, sf_freq_pct=4.2,
            and_one_freq_pct=0.5, score_freq_pct=51.0, percentile=96.0,
        )}
        result = predict_handoff_matchup(
            "Cold Handler", "ZZZ", [weak_player], elite_def
        )
        # edge = 0.85 - 1.10 = -0.25 → TOUGH
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensiveHandoffStats(
            player="Avg Handler", team="TST", gp=55,
            poss=3.0, freq_pct=16.0, ppp=1.07, pts=3.2,
            fgm=1.3, fga=3.0, fg_pct=43.0, efg_pct=56.0,
            ft_freq_pct=5.5, tov_freq_pct=7.0, sf_freq_pct=4.0,
            and_one_freq_pct=0.6, score_freq_pct=49.0, percentile=40.0,
        )
        from nba_playtype_props import DefensiveHandoffStats
        avg_def = {"ZZZ": DefensiveHandoffStats(
            team="ZZZ", gp=55, poss=3.5, freq_pct=10.0, ppp=1.05,
            pts=3.7, fgm=1.4, fga=3.2, fg_pct=44.0, efg_pct=58.0,
            ft_freq_pct=5.3, tov_freq_pct=6.5, sf_freq_pct=4.1,
            and_one_freq_pct=0.6, score_freq_pct=51.0, percentile=45.0,
        )}
        # edge = 1.07 - 1.05 = 0.02 → NEUTRAL
        result = predict_handoff_matchup(
            "Avg Handler", "ZZZ", [avg_player], avg_def
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_handoff_matchup(
            "Nobody Famous", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_handoff_matchup(
            "Tyrese Haliburton", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_handoff_matchup(
            "tyrese haliburton", "WAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_handoff_matchup(
            "TYRESE HALIBURTON", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_handoff_matchup(
            "LaMelo Ball", "WAS", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_handoff_matchup("Tyrese Haliburton", "WAS")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Tyrese Haliburton")


# ===========================================================================
# Offensive off-screen analytics tests
# ===========================================================================

class TestBuildOffensiveOffScreenStats(unittest.TestCase):
    """Tests for build_offensive_off_screen_stats()."""

    def setUp(self):
        self.stats = build_offensive_off_screen_stats()

    def test_returns_list(self):
        self.assertIsInstance(self.stats, list)

    def test_minimum_count(self):
        self.assertGreaterEqual(len(self.stats), 55)

    def test_all_items_are_offensive_off_screen_stats(self):
        for s in self.stats:
            self.assertIsInstance(s, OffensiveOffScreenStats)

    def test_ppp_values_positive(self):
        for s in self.stats:
            self.assertGreater(s.ppp, 0)

    def test_percentile_in_range(self):
        for s in self.stats:
            self.assertGreaterEqual(s.percentile, 0.0)
            self.assertLessEqual(s.percentile, 100.0)

    def test_klay_thompson_fields(self):
        """Klay Thompson data validation."""
        klay = next(s for s in self.stats if s.player == "Klay Thompson")
        self.assertEqual(klay.team, "GSW")
        self.assertAlmostEqual(klay.ppp, 1.22)
        self.assertAlmostEqual(klay.percentile, 99.0)

    def test_stephen_curry_fields(self):
        """Stephen Curry spot-check."""
        curry = next(s for s in self.stats if s.player == "Stephen Curry")
        self.assertEqual(curry.team, "GSW")
        self.assertEqual(curry.gp, 55)
        self.assertAlmostEqual(curry.ppp, 1.20)
        self.assertAlmostEqual(curry.percentile, 96.6)

    def test_batch1_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Klay Thompson", "Stephen Curry", "Buddy Hield", "Duncan Robinson",
            "Joe Harris", "Luke Kennard", "Mike Muscala", "Bogdan Bogdanovic",
            "Seth Curry", "Sam Hauser", "Caleb Martin", "Donte DiVincenzo",
            "Alec Burks", "Jordan Nwora", "Ryan Arcidiacono",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-1 players: {missing}")

    def test_batch2_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Gary Trent Jr.", "Furkan Korkmaz", "Jevon Carter",
            "Kentavious Caldwell-Pope", "Josh Richardson", "Devin Vassell",
            "Isaiah Joe", "Patty Mills", "Grayson Allen", "Khris Middleton",
            "Luguentz Dort", "Jalen McDaniels", "Malik Beasley",
            "Joe Ingles", "Reggie Jackson",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-2 players: {missing}")

    def test_batch3_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Jordan Hawkins", "Ochai Agbaji", "Gradey Dick", "Max Christie",
            "Ryan Nembhard", "Cam Whitmore", "Darius Garland", "Terry Rozier",
            "Cade Cunningham", "Anfernee Simons", "RJ Barrett", "Jordan Poole",
            "Quentin Grimes", "Scoot Henderson",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-3 players: {missing}")

    def test_batch4_players_present(self):
        names = {s.player for s in self.stats}
        expected = {
            "Zaccharie Risacher", "Stephon Castle", "Ace Bailey", "Dylan Harper",
            "Bub Carrington", "Will Riley", "Ajay Mitchell", "Cason Wallace",
            "Rob Dillingham", "Daniss Jenkins", "Kel'el Ware", "Caleb Love",
            "Jonathan Kuminga", "Derik Queen", "Victor Wembanyama",
        }
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing batch-4 players: {missing}")

    def test_victor_wembanyama_fields(self):
        """Victor Wembanyama (batch-4) spot-check."""
        vw = next(s for s in self.stats if s.player == "Victor Wembanyama")
        self.assertEqual(vw.team, "SAS")
        self.assertEqual(vw.gp, 43)
        self.assertAlmostEqual(vw.ppp, 1.05)
        self.assertAlmostEqual(vw.percentile, 20.7)

    def test_sam_hauser_fields(self):
        """Sam Hauser (batch-1) spot-check."""
        hauser = next(s for s in self.stats if s.player == "Sam Hauser")
        self.assertEqual(hauser.team, "BOS")
        self.assertAlmostEqual(hauser.ppp, 1.15)
        self.assertAlmostEqual(hauser.percentile, 75.9)


class TestRankPlayersByOffensiveOffScreen(unittest.TestCase):
    """Tests for rank_players_by_offensive_off_screen()."""

    def setUp(self):
        self.stats = build_offensive_off_screen_stats()
        self.ranked = rank_players_by_offensive_off_screen(self.stats)

    def test_returns_list(self):
        self.assertIsInstance(self.ranked, list)

    def test_same_length_as_input(self):
        self.assertEqual(len(self.ranked), len(self.stats))

    def test_sorted_descending_by_percentile(self):
        for i in range(len(self.ranked) - 1):
            self.assertGreaterEqual(
                self.ranked[i].percentile, self.ranked[i + 1].percentile
            )

    def test_first_has_highest_percentile(self):
        max_pct = max(s.percentile for s in self.stats)
        self.assertAlmostEqual(self.ranked[0].percentile, max_pct)

    def test_default_dataset_used_when_none(self):
        ranked_default = rank_players_by_offensive_off_screen()
        self.assertGreater(len(ranked_default), 0)


class TestFindOffScreenPlayerScorers(unittest.TestCase):
    """Tests for find_off_screen_player_scorers()."""

    def setUp(self):
        self.off_screen_stats = build_offensive_off_screen_stats()
        self.def_rankings = build_off_screen_defensive_rankings()

    def test_returns_list(self):
        results = find_off_screen_player_scorers(self.off_screen_stats)
        self.assertIsInstance(results, list)

    def test_all_pass_freq_threshold(self):
        min_freq = 25.0
        results = find_off_screen_player_scorers(self.off_screen_stats, min_freq_pct=min_freq)
        for r in results:
            self.assertGreaterEqual(r["freq_pct"], min_freq)

    def test_all_pass_ppp_threshold(self):
        min_ppp = 1.15
        results = find_off_screen_player_scorers(self.off_screen_stats, min_ppp=min_ppp)
        for r in results:
            self.assertGreaterEqual(r["ppp"], min_ppp)

    def test_sorted_by_freq_pct_descending(self):
        results = find_off_screen_player_scorers(self.off_screen_stats)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]["freq_pct"], results[i + 1]["freq_pct"])

    def test_result_has_required_keys(self):
        results = find_off_screen_player_scorers(self.off_screen_stats)
        if results:
            for k in ("player", "team", "freq_pct", "ppp", "pts",
                      "percentile", "def_ppp", "def_percentile"):
                self.assertIn(k, results[0].keys())

    def test_def_ppp_none_when_no_opponent(self):
        results = find_off_screen_player_scorers(self.off_screen_stats)
        for r in results:
            self.assertIsNone(r["def_ppp"])
            self.assertIsNone(r["def_percentile"])

    def test_def_ppp_populated_with_opponent(self):
        results = find_off_screen_player_scorers(
            self.off_screen_stats, "WAS", self.def_rankings
        )
        for r in results:
            self.assertIsNotNone(r["def_ppp"])
            self.assertIsNotNone(r["def_percentile"])

    def test_klay_in_top_scorers(self):
        results = find_off_screen_player_scorers(
            self.off_screen_stats, min_freq_pct=25.0, min_ppp=1.15
        )
        players = [r["player"] for r in results]
        self.assertIn("Klay Thompson", players)


class TestPredictOffScreenMatchup(unittest.TestCase):
    """Tests for predict_off_screen_matchup()."""

    def setUp(self):
        self.off_stats = build_offensive_off_screen_stats()
        self.def_rankings = build_off_screen_defensive_rankings()

    def test_returns_dict_for_known_player_and_team(self):
        result = predict_off_screen_matchup(
            "Klay Thompson", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_result_has_required_keys(self):
        result = predict_off_screen_matchup(
            "Klay Thompson", "WAS", self.off_stats, self.def_rankings
        )
        for k in ("player", "team", "gp", "freq_pct", "ppp", "pts",
                  "off_percentile", "opponent", "def_ppp", "def_freq_pct",
                  "def_percentile", "edge", "verdict"):
            self.assertIn(k, result)

    def test_player_and_opponent_fields(self):
        result = predict_off_screen_matchup(
            "Klay Thompson", "WAS", self.off_stats, self.def_rankings
        )
        self.assertEqual(result["player"], "Klay Thompson")
        self.assertEqual(result["opponent"], "WAS")

    def test_verdict_favorable_for_large_positive_edge(self):
        """A top off-screen scorer vs a weak off-screen defense → FAVORABLE."""
        strong_player = OffensiveOffScreenStats(
            player="Elite Shooter", team="TST", gp=55,
            poss=5.5, freq_pct=28.0, ppp=1.28, pts=7.0,
            fgm=2.8, fga=5.5, fg_pct=51.0, efg_pct=66.0,
            ft_freq_pct=5.5, tov_freq_pct=4.0, sf_freq_pct=4.5,
            and_one_freq_pct=0.7, score_freq_pct=60.0, percentile=95.0,
        )
        from nba_playtype_props import DefensiveOffScreenStats
        weak_def = {"ZZZ": DefensiveOffScreenStats(
            team="ZZZ", gp=55, poss=5.0, freq_pct=14.0, ppp=1.00,
            pts=5.0, fgm=2.0, fga=4.0, fg_pct=50.0, efg_pct=64.0,
            ft_freq_pct=5.0, tov_freq_pct=5.0, sf_freq_pct=4.0,
            and_one_freq_pct=0.5, score_freq_pct=56.0, percentile=4.0,
        )}
        result = predict_off_screen_matchup(
            "Elite Shooter", "ZZZ", [strong_player], weak_def
        )
        # edge = 1.28 - 1.00 = 0.28 → FAVORABLE
        self.assertEqual(result["verdict"], "FAVORABLE")

    def test_verdict_tough_for_large_negative_edge(self):
        """A below-average off-screen scorer vs elite off-screen defense → TOUGH."""
        weak_player = OffensiveOffScreenStats(
            player="Cold Shooter", team="TST", gp=55,
            poss=2.5, freq_pct=16.0, ppp=0.88, pts=2.2,
            fgm=0.9, fga=2.6, fg_pct=34.0, efg_pct=44.0,
            ft_freq_pct=4.0, tov_freq_pct=8.0, sf_freq_pct=3.2,
            and_one_freq_pct=0.3, score_freq_pct=40.0, percentile=8.0,
        )
        from nba_playtype_props import DefensiveOffScreenStats
        elite_def = {"ZZZ": DefensiveOffScreenStats(
            team="ZZZ", gp=55, poss=4.0, freq_pct=10.0, ppp=1.12,
            pts=4.5, fgm=1.8, fga=3.6, fg_pct=50.0, efg_pct=65.0,
            ft_freq_pct=5.0, tov_freq_pct=4.5, sf_freq_pct=3.9,
            and_one_freq_pct=0.5, score_freq_pct=58.0, percentile=97.0,
        )}
        result = predict_off_screen_matchup(
            "Cold Shooter", "ZZZ", [weak_player], elite_def
        )
        # edge = 0.88 - 1.12 = -0.24 → TOUGH
        self.assertEqual(result["verdict"], "TOUGH")

    def test_verdict_neutral_for_small_edge(self):
        avg_player = OffensiveOffScreenStats(
            player="Avg Shooter", team="TST", gp=55,
            poss=4.0, freq_pct=22.0, ppp=1.10, pts=4.4,
            fgm=1.8, fga=3.8, fg_pct=47.0, efg_pct=61.0,
            ft_freq_pct=5.0, tov_freq_pct=5.0, sf_freq_pct=4.0,
            and_one_freq_pct=0.5, score_freq_pct=54.0, percentile=48.0,
        )
        from nba_playtype_props import DefensiveOffScreenStats
        avg_def = {"ZZZ": DefensiveOffScreenStats(
            team="ZZZ", gp=55, poss=4.5, freq_pct=12.0, ppp=1.08,
            pts=4.9, fgm=1.9, fga=3.8, fg_pct=50.0, efg_pct=64.0,
            ft_freq_pct=5.2, tov_freq_pct=4.8, sf_freq_pct=4.1,
            and_one_freq_pct=0.5, score_freq_pct=57.0, percentile=45.0,
        )}
        # edge = 1.10 - 1.08 = 0.02 → NEUTRAL
        result = predict_off_screen_matchup(
            "Avg Shooter", "ZZZ", [avg_player], avg_def
        )
        self.assertEqual(result["verdict"], "NEUTRAL")

    def test_returns_none_for_unknown_player(self):
        result = predict_off_screen_matchup(
            "Nobody Famous", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_returns_none_for_unknown_team(self):
        result = predict_off_screen_matchup(
            "Klay Thompson", "ZZZ", self.off_stats, self.def_rankings
        )
        self.assertIsNone(result)

    def test_case_insensitive_player_name(self):
        result_lower = predict_off_screen_matchup(
            "klay thompson", "WAS", self.off_stats, self.def_rankings
        )
        result_upper = predict_off_screen_matchup(
            "KLAY THOMPSON", "WAS", self.off_stats, self.def_rankings
        )
        self.assertIsNotNone(result_lower)
        self.assertIsNotNone(result_upper)
        self.assertEqual(result_lower["player"], result_upper["player"])

    def test_edge_equals_ppp_minus_def_ppp(self):
        result = predict_off_screen_matchup(
            "Stephen Curry", "WAS", self.off_stats, self.def_rankings
        )
        self.assertAlmostEqual(
            result["edge"], round(result["ppp"] - result["def_ppp"], 3)
        )

    def test_default_datasets_used_when_none(self):
        result = predict_off_screen_matchup("Klay Thompson", "WAS")
        self.assertIsNotNone(result)
        self.assertEqual(result["player"], "Klay Thompson")


if __name__ == "__main__":
    unittest.main()
