"""Tests for nba_projections package."""

import pytest

from nba_projections.player_data import (
    PLAYERS,
    OPPONENT_DEF_RATINGS,
    get_player,
    get_all_players,
)
from nba_projections.projections import PlayerProjection, STAT_KEYS
from nba_projections.props import PropAnalyzer, PropResult


# ---------------------------------------------------------------------------
# player_data tests
# ---------------------------------------------------------------------------

class TestPlayerData:
    def test_players_not_empty(self):
        assert len(PLAYERS) > 0

    def test_all_players_have_required_fields(self):
        required = {"name", "team", "position", "season_avg", "game_log"}
        for pid, data in PLAYERS.items():
            assert required.issubset(data.keys()), f"{pid} missing fields"

    def test_season_avg_has_all_stats(self):
        for pid, data in PLAYERS.items():
            for stat in ("pts", "reb", "ast", "stl", "blk", "min", "fg_pct", "ft_pct"):
                assert stat in data["season_avg"], f"{pid} missing season_avg.{stat}"

    def test_game_log_entries_have_all_stats(self):
        for pid, data in PLAYERS.items():
            for game in data["game_log"]:
                for stat in ("pts", "reb", "ast", "stl", "blk", "min", "fg_pct", "ft_pct", "opponent", "home"):
                    assert stat in game, f"{pid} game log entry missing {stat}"

    def test_get_player_returns_correct_data(self):
        player = get_player("luka_doncic")
        assert player["name"] == "Luka Doncic"
        assert player["team"] == "DAL"

    def test_get_player_raises_on_unknown(self):
        with pytest.raises(KeyError):
            get_player("unknown_player_xyz")

    def test_get_all_players_returns_list(self):
        players = get_all_players()
        assert isinstance(players, list)
        assert "luka_doncic" in players

    def test_opponent_def_ratings_not_empty(self):
        assert len(OPPONENT_DEF_RATINGS) > 0

    def test_opponent_def_ratings_are_positive(self):
        for team, rating in OPPONENT_DEF_RATINGS.items():
            assert rating > 0, f"{team} has non-positive rating"


# ---------------------------------------------------------------------------
# projections tests
# ---------------------------------------------------------------------------

class TestPlayerProjection:
    def test_projection_returns_all_stat_keys(self):
        proj = PlayerProjection("luka_doncic", "GSW")
        result = proj.project()
        for stat in STAT_KEYS:
            assert stat in result
        assert "pts_reb_ast" in result

    def test_projection_values_are_positive(self):
        proj = PlayerProjection("nikola_jokic", "LAL")
        result = proj.project()
        for stat in STAT_KEYS:
            assert result[stat] > 0, f"{stat} projection is non-positive"

    def test_pts_reb_ast_equals_sum(self):
        proj = PlayerProjection("stephen_curry", "OKC")
        result = proj.project()
        expected = round(result["pts"] + result["reb"] + result["ast"], 1)
        assert result["pts_reb_ast"] == expected

    def test_home_projection_higher_than_away(self):
        home_proj = PlayerProjection("giannis_antetokounmpo", "CHI", home=True).project()
        away_proj = PlayerProjection("giannis_antetokounmpo", "CHI", home=False).project()
        assert home_proj["pts"] > away_proj["pts"]

    def test_easy_opponent_gives_higher_projection(self):
        # DET has the worst defense (1.08) vs MEM has good defense (0.94)
        easy_proj = PlayerProjection("jayson_tatum", "DET", home=True).project()
        hard_proj = PlayerProjection("jayson_tatum", "MEM", home=True).project()
        assert easy_proj["pts"] > hard_proj["pts"]

    def test_unknown_opponent_raises(self):
        with pytest.raises(ValueError):
            PlayerProjection("luka_doncic", "XYZ")

    def test_standard_deviation_returns_all_stats(self):
        proj = PlayerProjection("joel_embiid", "BOS")
        std = proj.standard_deviation()
        for stat in STAT_KEYS:
            assert stat in std
            assert std[stat] >= 0

    def test_projection_is_cached(self):
        proj = PlayerProjection("kevin_durant", "LAL")
        result1 = proj.project()
        result2 = proj.project()
        assert result1 is result2  # same object (cached)

    def test_summary_contains_expected_keys(self):
        proj = PlayerProjection("lebron_james", "GSW")
        summary = proj.summary()
        assert "player" in summary
        assert "team" in summary
        assert "opponent" in summary
        assert "home" in summary
        assert "projections" in summary
        assert "std_dev" in summary

    def test_all_players_project_without_error(self):
        for pid in get_all_players():
            proj = PlayerProjection(pid, "LAL")
            result = proj.project()
            assert result["pts"] > 0


# ---------------------------------------------------------------------------
# props tests
# ---------------------------------------------------------------------------

class TestPropAnalyzer:
    def _analyzer(self, player_id="luka_doncic", opponent="OKC", home=True):
        return PropAnalyzer(player_id, opponent, home=home)

    def test_evaluate_prop_returns_prop_result(self):
        analyzer = self._analyzer()
        result = analyzer.evaluate_prop("pts", 28.5)
        assert isinstance(result, PropResult)

    def test_over_recommendation_when_projection_higher(self):
        # Force a situation where projection should clearly beat the line
        analyzer = PropAnalyzer("joel_embiid", "DET", home=True)
        result = analyzer.evaluate_prop("pts", 10.0)
        assert result.recommendation == "OVER"
        assert result.edge > 0

    def test_under_recommendation_when_projection_lower(self):
        analyzer = PropAnalyzer("stephen_curry", "BOS", home=False)
        result = analyzer.evaluate_prop("pts", 99.0)
        assert result.recommendation == "UNDER"
        assert result.edge < 0

    def test_evaluate_all_returns_list(self):
        analyzer = self._analyzer()
        prop_lines = {"pts": 28.5, "reb": 8.5, "ast": 9.5}
        results = analyzer.evaluate_all(prop_lines)
        assert len(results) == 3
        for r in results:
            assert isinstance(r, PropResult)

    def test_evaluate_invalid_stat_raises(self):
        analyzer = self._analyzer()
        with pytest.raises(ValueError):
            analyzer.evaluate_prop("turnovers", 3.5)

    def test_hit_rate_between_0_and_1(self):
        analyzer = self._analyzer()
        result = analyzer.evaluate_prop("pts", 20.0)
        assert 0.0 <= result.hit_rate <= 1.0

    def test_pts_reb_ast_prop(self):
        analyzer = self._analyzer()
        result = analyzer.evaluate_prop("pts_reb_ast", 45.0)
        assert isinstance(result, PropResult)
        assert result.stat == "pts_reb_ast"

    def test_display_report_returns_string(self):
        analyzer = self._analyzer()
        report = analyzer.display_report()
        assert isinstance(report, str)
        assert "Luka Doncic" in report

    def test_display_report_with_props_contains_rec(self):
        analyzer = self._analyzer()
        report = analyzer.display_report({"pts": 28.5, "reb": 8.5})
        assert "OVER" in report or "UNDER" in report

    def test_confidence_high_on_large_edge(self):
        analyzer = PropAnalyzer("joel_embiid", "DET", home=True)
        result = analyzer.evaluate_prop("pts", 5.0)
        assert result.confidence == "High"

    def test_confidence_low_on_small_edge(self):
        analyzer = PropAnalyzer("luka_doncic", "GSW", home=True)
        proj_pts = analyzer._proj_values["pts"]
        # Set line very close to projection
        result = analyzer.evaluate_prop("pts", round(proj_pts - 0.5, 1))
        assert result.confidence == "Low"

    def test_prop_result_repr(self):
        result = PropResult("Luka Doncic", "pts", 28.5, 31.2, 0.7)
        r = repr(result)
        assert "PropResult" in r
        assert "OVER" in r

    def test_historical_hit_rate_all_games(self):
        """Player who scores 22-45 pts every game should have 100% hit rate vs line=5."""
        analyzer = PropAnalyzer("joel_embiid", "BOS")
        result = analyzer.evaluate_prop("pts", 5.0)
        assert result.hit_rate == 1.0
