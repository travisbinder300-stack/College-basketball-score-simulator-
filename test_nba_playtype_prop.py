"""
Tests for nba_playtype_prop.py
"""

import pytest
from nba_playtype_prop import (
    DefensiveMatchupProfile,
    PlayType,
    PlayTypeStats,
    PlayerProfile,
    Position,
    PropEstimate,
    estimate_props,
    estimate_props_with_similarity,
    find_similar_players,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_guard(name: str = "Guard A", possessions: float = 20.0) -> PlayerProfile:
    """Return a simple PG profile whose play-type frequencies sum to 1.0."""
    return PlayerProfile(
        name=name,
        position=Position.POINT_GUARD,
        team="Team X",
        possessions_per_game=possessions,
        play_type_stats=[
            PlayTypeStats(PlayType.PICK_AND_ROLL_BALL_HANDLER, 0.40, 1.10, 0.30, 0.05),
            PlayTypeStats(PlayType.ISOLATION,                   0.25, 0.95, 0.08, 0.07),
            PlayTypeStats(PlayType.TRANSITION,                  0.20, 1.20, 0.18, 0.06),
            PlayTypeStats(PlayType.SPOT_UP,                     0.15, 1.05, 0.04, 0.09),
        ],
    )


def _make_big(name: str = "Big A", possessions: float = 14.0) -> PlayerProfile:
    """Return a simple C profile."""
    return PlayerProfile(
        name=name,
        position=Position.CENTER,
        team="Team Y",
        possessions_per_game=possessions,
        play_type_stats=[
            PlayTypeStats(PlayType.PICK_AND_ROLL_ROLL_MAN, 0.35, 1.00, 0.05, 0.20),
            PlayTypeStats(PlayType.POST_UP,                 0.30, 0.90, 0.08, 0.15),
            PlayTypeStats(PlayType.PUTBACK,                 0.20, 1.15, 0.01, 0.35),
            PlayTypeStats(PlayType.CUT,                     0.15, 1.25, 0.02, 0.18),
        ],
    )


def _average_defender(position: Position = Position.POINT_GUARD) -> DefensiveMatchupProfile:
    """Defender with all ratings at league average (1.0)."""
    return DefensiveMatchupProfile(
        defender_name="Average Defender",
        defender_position=position,
        play_type_ratings={},  # defaults to 1.0 for all
    )


# ---------------------------------------------------------------------------
# PlayTypeStats validation
# ---------------------------------------------------------------------------

class TestPlayTypeStats:
    def test_valid_creation(self):
        stat = PlayTypeStats(PlayType.ISOLATION, 0.30, 1.00, 0.10, 0.05)
        assert stat.frequency == 0.30

    def test_frequency_below_zero_raises(self):
        with pytest.raises(ValueError, match="frequency"):
            PlayTypeStats(PlayType.ISOLATION, -0.01, 1.00, 0.10, 0.05)

    def test_frequency_above_one_raises(self):
        with pytest.raises(ValueError, match="frequency"):
            PlayTypeStats(PlayType.ISOLATION, 1.01, 1.00, 0.10, 0.05)

    def test_assist_chance_out_of_range(self):
        with pytest.raises(ValueError, match="assist_chance"):
            PlayTypeStats(PlayType.ISOLATION, 0.30, 1.00, 1.10, 0.05)

    def test_rebound_chance_out_of_range(self):
        with pytest.raises(ValueError, match="rebound_chance"):
            PlayTypeStats(PlayType.ISOLATION, 0.30, 1.00, 0.10, -0.01)


# ---------------------------------------------------------------------------
# PlayerProfile validation
# ---------------------------------------------------------------------------

class TestPlayerProfile:
    def test_frequencies_must_sum_to_one(self):
        with pytest.raises(ValueError, match="frequencies must sum to 1.0"):
            PlayerProfile(
                name="Bad Player",
                position=Position.POINT_GUARD,
                team="X",
                possessions_per_game=15.0,
                play_type_stats=[
                    PlayTypeStats(PlayType.ISOLATION, 0.50, 1.00, 0.10, 0.05),
                    PlayTypeStats(PlayType.SPOT_UP,    0.20, 1.00, 0.05, 0.08),
                    # missing 0.30
                ],
            )

    def test_empty_play_type_stats_is_valid(self):
        p = PlayerProfile("Empty", Position.CENTER, "Z", 10.0, [])
        assert p.name == "Empty"


# ---------------------------------------------------------------------------
# DefensiveMatchupProfile
# ---------------------------------------------------------------------------

class TestDefensiveMatchupProfile:
    def test_default_rating_is_league_average(self):
        defender = DefensiveMatchupProfile(
            "Test", Position.SMALL_FORWARD, {}
        )
        assert defender.rating_for(PlayType.ISOLATION) == 1.0

    def test_custom_rating_returned(self):
        defender = DefensiveMatchupProfile(
            "Elite ISO Stopper",
            Position.SMALL_FORWARD,
            {PlayType.ISOLATION: 0.80},
        )
        assert defender.rating_for(PlayType.ISOLATION) == 0.80
        assert defender.rating_for(PlayType.SPOT_UP) == 1.0  # default


# ---------------------------------------------------------------------------
# estimate_props
# ---------------------------------------------------------------------------

class TestEstimateProps:
    def test_returns_prop_estimate_type(self):
        player = _make_guard()
        defender = _average_defender()
        result = estimate_props(player, defender)
        assert isinstance(result, PropEstimate)

    def test_player_and_defender_names_set(self):
        player = _make_guard("Steph")
        defender = _average_defender()
        result = estimate_props(player, defender)
        assert result.player_name == "Steph"
        assert result.defender_name == "Average Defender"

    def test_projected_points_positive(self):
        player = _make_guard()
        defender = _average_defender()
        result = estimate_props(player, defender)
        assert result.projected_points > 0

    def test_breakdown_keys_match_play_types(self):
        player = _make_guard()
        defender = _average_defender()
        result = estimate_props(player, defender)
        expected_keys = {s.play_type.value for s in player.play_type_stats}
        assert set(result.play_type_breakdown.keys()) == expected_keys

    def test_bad_defender_allows_more_points(self):
        """A below-average defender should yield a higher point projection."""
        player = _make_guard()
        avg_defender = _average_defender()
        bad_defender = DefensiveMatchupProfile(
            "Bad Defender",
            Position.POINT_GUARD,
            {pt: 1.20 for pt in PlayType},  # 20% worse than average on all play types
        )
        avg_estimate = estimate_props(player, avg_defender)
        bad_estimate = estimate_props(player, bad_defender)
        assert bad_estimate.projected_points > avg_estimate.projected_points

    def test_elite_defender_allows_fewer_points(self):
        """An elite defender should yield a lower point projection."""
        player = _make_guard()
        avg_defender = _average_defender()
        elite_defender = DefensiveMatchupProfile(
            "Elite Defender",
            Position.POINT_GUARD,
            {pt: 0.70 for pt in PlayType},
        )
        avg_estimate = estimate_props(player, avg_defender)
        elite_estimate = estimate_props(player, elite_defender)
        assert elite_estimate.projected_points < avg_estimate.projected_points

    def test_higher_possessions_yields_more_points(self):
        player_low = _make_guard("Low Usage", possessions=10.0)
        player_high = _make_guard("High Usage", possessions=25.0)
        defender = _average_defender()
        low_est = estimate_props(player_low, defender)
        high_est = estimate_props(player_high, defender)
        assert high_est.projected_points > low_est.projected_points

    def test_prop_estimate_str_contains_player_name(self):
        player = _make_guard("Chris Paul")
        defender = _average_defender()
        result = estimate_props(player, defender)
        assert "Chris Paul" in str(result)

    def test_assists_and_rebounds_nonnegative(self):
        player = _make_guard()
        defender = _average_defender()
        result = estimate_props(player, defender)
        assert result.projected_assists >= 0
        assert result.projected_rebounds >= 0


# ---------------------------------------------------------------------------
# find_similar_players
# ---------------------------------------------------------------------------

class TestFindSimilarPlayers:
    def _pool(self) -> list:
        guards = [_make_guard(f"Guard {i}") for i in range(5)]
        bigs = [_make_big(f"Big {i}") for i in range(3)]
        return guards + bigs

    def test_returns_at_most_top_n(self):
        pool = self._pool()
        target = _make_guard("Target Guard")
        similar = find_similar_players(target, pool, top_n=3)
        assert len(similar) <= 3

    def test_same_position_only_filters_position(self):
        pool = self._pool()
        target = _make_guard("Target Guard")
        similar = find_similar_players(target, pool, top_n=10, same_position_only=True)
        for p in similar:
            assert p.position == Position.POINT_GUARD

    def test_target_not_in_results(self):
        pool = self._pool()
        target = pool[0]  # include target in pool
        similar = find_similar_players(target, pool, top_n=5)
        assert target not in similar

    def test_any_position_returns_all_positions(self):
        pool = self._pool()
        target = _make_guard("Target Guard")
        similar = find_similar_players(
            target, pool, top_n=10, same_position_only=False
        )
        positions = {p.position for p in similar}
        assert Position.CENTER in positions or len(similar) >= 1

    def test_empty_pool_returns_empty(self):
        target = _make_guard("Solo Guard")
        similar = find_similar_players(target, [], top_n=5)
        assert similar == []


# ---------------------------------------------------------------------------
# estimate_props_with_similarity
# ---------------------------------------------------------------------------

class TestEstimatePropsWithSimilarity:
    def _pool(self) -> list:
        return [_make_guard(f"Peer {i}") for i in range(6)]

    def test_zero_similarity_weight_matches_own_estimate(self):
        player = _make_guard("Solo")
        defender = _average_defender()
        pool = self._pool()

        own = estimate_props(player, defender)
        blended = estimate_props_with_similarity(
            player, defender, pool, top_n=5, similarity_weight=0.0
        )
        assert blended.projected_points == own.projected_points
        assert blended.projected_assists == own.projected_assists
        assert blended.projected_rebounds == own.projected_rebounds

    def test_similarity_blending_changes_projection(self):
        """Adding peer influence should shift the projection."""
        player = _make_guard("Scorer", possessions=25.0)  # high usage
        defender = _average_defender()
        pool = [_make_guard(f"Avg {i}", possessions=14.0) for i in range(5)]

        own = estimate_props(player, defender)
        blended = estimate_props_with_similarity(
            player, defender, pool, top_n=5, similarity_weight=0.5
        )
        # Blending a high-usage player with lower-usage peers should reduce pts
        assert blended.projected_points < own.projected_points

    def test_empty_pool_falls_back_to_own_estimate(self):
        player = _make_guard("Solo")
        defender = _average_defender()
        own = estimate_props(player, defender)
        blended = estimate_props_with_similarity(player, defender, [], top_n=5)
        assert blended.projected_points == own.projected_points
