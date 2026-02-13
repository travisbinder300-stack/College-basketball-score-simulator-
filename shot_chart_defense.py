"""
Shot Chart and Defensive Matchup Analysis
Player vs Defense ranking with similar player matching and defender hit rate tracking
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum
from datetime import datetime


class ShotZone(Enum):
    """Basketball court shot zones"""
    PAINT = "paint"
    MID_RANGE = "mid_range"
    THREE_POINT_CORNER = "three_point_corner"
    THREE_POINT_WING = "three_point_wing"
    THREE_POINT_TOP = "three_point_top"
    FREE_THROW_LINE = "free_throw_line"


class PlayStyle(Enum):
    """Player play style categories"""
    VOLUME_SCORER = "volume_scorer"  # High usage, high shot attempts
    EFFICIENT_SCORER = "efficient_scorer"  # High FG%, selective shooting
    THREE_POINT_SPECIALIST = "three_point_specialist"  # High 3PA
    PLAYMAKER = "playmaker"  # High assists, distributes ball
    TWO_WAY_PLAYER = "two_way_player"  # Balanced offense and defense
    POST_PLAYER = "post_player"  # Paint-focused, high post-ups
    SLASHER = "slasher"  # Drives to basket, high paint FGA
    STRETCH_BIG = "stretch_big"  # Big man who shoots 3s


class DefenseType(Enum):
    """Team defensive schemes"""
    SWITCH_HEAVY = "switch_heavy"  # Switches most screens
    DROP_COVERAGE = "drop_coverage"  # Big drops back on screens
    AGGRESSIVE_TRAP = "aggressive_trap"  # Traps ball handlers
    ZONE_DEFENSE = "zone_defense"  # Plays zone frequently
    MAN_TO_MAN = "man_to_man"  # Traditional man defense
    HELP_ROTATION = "help_rotation"  # Strong help defense


@dataclass
class ShotChartData:
    """Shot chart statistics by zone"""
    zone: ShotZone
    attempts: int
    makes: int
    fg_percentage: float
    points_per_shot: float
    frequency: float  # % of total shots from this zone
    
    def __str__(self):
        return f"{self.zone.value}: {self.makes}/{self.attempts} ({self.fg_percentage:.1%})"


@dataclass
class PlayerShotChart:
    """Complete shot chart for a player"""
    player_id: str
    player_name: str
    season: str
    shot_zones: List[ShotChartData]
    total_fga: int
    total_fgm: int
    overall_fg_pct: float
    
    def get_zone_stats(self, zone: ShotZone) -> Optional[ShotChartData]:
        """Get stats for a specific zone"""
        for shot_data in self.shot_zones:
            if shot_data.zone == zone:
                return shot_data
        return None
    
    def get_strongest_zones(self, min_frequency: float = 0.1) -> List[ShotChartData]:
        """Get zones where player is most efficient (with minimum frequency)"""
        filtered = [z for z in self.shot_zones if z.frequency >= min_frequency]
        return sorted(filtered, key=lambda x: x.fg_percentage, reverse=True)
    
    def get_most_frequent_zones(self) -> List[ShotChartData]:
        """Get zones by shot frequency"""
        return sorted(self.shot_zones, key=lambda x: x.frequency, reverse=True)


@dataclass
class DefenderStats:
    """Individual defender statistics"""
    player_id: str
    player_name: str
    team: str
    position: str
    
    # Defensive metrics
    defensive_rating: float  # Points allowed per 100 possessions
    steal_rate: float
    block_rate: float
    deflections_per_game: float
    
    # Matchup data
    contests_per_game: float
    opponent_fg_pct_allowed: float  # FG% when defending
    opponent_3pt_pct_allowed: float
    
    # Zone defense
    paint_fg_pct_allowed: float
    mid_range_fg_pct_allowed: float
    three_pt_fg_pct_allowed: float
    
    def get_hit_rate_vs_defender(self, zone: ShotZone) -> float:
        """Get opponent hit rate when this defender contests in a zone"""
        zone_map = {
            ShotZone.PAINT: self.paint_fg_pct_allowed,
            ShotZone.MID_RANGE: self.mid_range_fg_pct_allowed,
            ShotZone.FREE_THROW_LINE: self.mid_range_fg_pct_allowed,
            ShotZone.THREE_POINT_CORNER: self.three_pt_fg_pct_allowed,
            ShotZone.THREE_POINT_WING: self.three_pt_fg_pct_allowed,
            ShotZone.THREE_POINT_TOP: self.three_pt_fg_pct_allowed,
        }
        return zone_map.get(zone, self.opponent_fg_pct_allowed)


@dataclass
class TeamDefenseRanking:
    """Team defensive statistics and rankings"""
    team: str
    season: str
    
    # Overall defensive metrics
    defensive_rating: float  # League rank
    points_allowed_per_game: float
    opponent_fg_pct: float
    opponent_3pt_pct: float
    
    # Defense type and scheme
    primary_defense_type: DefenseType
    switch_rate: float  # % of screens switched
    
    # Zone-specific defense
    paint_defense_rank: int  # 1-30 ranking
    mid_range_defense_rank: int
    three_pt_defense_rank: int
    
    # Matchup weaknesses
    weak_zones: List[ShotZone]  # Zones where defense is weakest
    strong_zones: List[ShotZone]  # Zones where defense is strongest
    
    # Player type struggles
    struggles_against: List[PlayStyle]  # Play styles this defense struggles with
    
    def is_vulnerable_to(self, play_style: PlayStyle) -> bool:
        """Check if defense is vulnerable to a play style"""
        return play_style in self.struggles_against
    
    def get_zone_rank(self, zone: ShotZone) -> int:
        """Get defensive ranking for a specific zone"""
        zone_rank_map = {
            ShotZone.PAINT: self.paint_defense_rank,
            ShotZone.MID_RANGE: self.mid_range_defense_rank,
            ShotZone.FREE_THROW_LINE: self.mid_range_defense_rank,
            ShotZone.THREE_POINT_CORNER: self.three_pt_defense_rank,
            ShotZone.THREE_POINT_WING: self.three_pt_defense_rank,
            ShotZone.THREE_POINT_TOP: self.three_pt_defense_rank,
        }
        return zone_rank_map.get(zone, 15)  # Default to middle rank


@dataclass
class PlayerProfile:
    """Player profile with play style and shot tendencies"""
    player_id: str
    player_name: str
    team: str
    position: str
    
    # Play style classification
    primary_play_style: PlayStyle
    secondary_play_style: Optional[PlayStyle]
    
    # Shot tendencies
    shot_chart: PlayerShotChart
    
    # Usage and efficiency
    usage_rate: float
    true_shooting_pct: float
    effective_fg_pct: float
    
    # Matchup preferences
    preferred_zones: List[ShotZone]  # Where they like to shoot
    avoids_zones: List[ShotZone]  # Where they avoid shooting
    
    def calculate_similarity_score(self, other: 'PlayerProfile') -> float:
        """
        Calculate similarity score with another player (0-1 scale)
        Based on play style and shot distribution
        """
        score = 0.0
        
        # Play style match (40% weight)
        if self.primary_play_style == other.primary_play_style:
            score += 0.4
        elif self.primary_play_style == other.secondary_play_style or \
             self.secondary_play_style == other.primary_play_style:
            score += 0.2
        
        # Shot distribution similarity (40% weight)
        zone_similarity = 0.0
        for zone in ShotZone:
            self_zone = self.shot_chart.get_zone_stats(zone)
            other_zone = other.shot_chart.get_zone_stats(zone)
            if self_zone and other_zone:
                # Compare frequency distribution
                freq_diff = abs(self_zone.frequency - other_zone.frequency)
                zone_similarity += (1.0 - freq_diff)
        
        zone_similarity /= len(ShotZone)
        score += 0.4 * zone_similarity
        
        # Efficiency similarity (20% weight)
        eff_diff = abs(self.true_shooting_pct - other.true_shooting_pct)
        score += 0.2 * (1.0 - min(eff_diff, 0.3) / 0.3)
        
        return score


@dataclass
class DefensiveMatchup:
    """Matchup analysis between player and defense"""
    player_profile: PlayerProfile
    team_defense: TeamDefenseRanking
    primary_defender: Optional[DefenderStats]
    
    # Matchup analysis results
    favorable_zones: List[Tuple[ShotZone, float]]  # (zone, advantage_pct)
    unfavorable_zones: List[Tuple[ShotZone, float]]
    
    overall_matchup_rating: float  # -1.0 (bad) to 1.0 (good)
    expected_fg_boost: float  # Expected FG% change vs league average
    
    hit_rate_projection: Dict[ShotZone, float]  # Projected FG% by zone
    
    def get_matchup_summary(self) -> Dict:
        """Get comprehensive matchup summary"""
        return {
            "player": self.player_profile.player_name,
            "opponent": self.team_defense.team,
            "matchup_rating": f"{self.overall_matchup_rating:+.2f}",
            "expected_fg_boost": f"{self.expected_fg_boost:+.2%}",
            "favorable_zones": [z.value for z, _ in self.favorable_zones[:3]],
            "unfavorable_zones": [z.value for z, _ in self.unfavorable_zones[:3]],
            "defense_type": self.team_defense.primary_defense_type.value,
            "vulnerable_to_style": self.team_defense.is_vulnerable_to(
                self.player_profile.primary_play_style
            )
        }


class DefensiveMatchupAnalyzer:
    """Analyze matchups between players and defenses"""
    
    def __init__(self):
        self.matchup_cache = {}
    
    def analyze_matchup(
        self,
        player_profile: PlayerProfile,
        team_defense: TeamDefenseRanking,
        primary_defender: Optional[DefenderStats] = None
    ) -> DefensiveMatchup:
        """
        Analyze a player vs defense matchup
        Returns matchup with favorable/unfavorable zones and projections
        """
        favorable_zones = []
        unfavorable_zones = []
        hit_rate_projection = {}
        
        # Analyze each zone
        for zone_data in player_profile.shot_chart.shot_zones:
            zone = zone_data.zone
            player_fg_pct = zone_data.fg_percentage
            
            # Get defense stats for this zone
            defense_rank = team_defense.get_zone_rank(zone)
            
            # Calculate advantage (lower defense rank = better defense)
            # Defense rank 1-10 = elite, 11-20 = average, 21-30 = poor
            defense_multiplier = 1.0 + (defense_rank - 15) * 0.01
            
            # Factor in defender if available
            if primary_defender:
                defender_allowed_pct = primary_defender.get_hit_rate_vs_defender(zone)
                defense_multiplier *= (defender_allowed_pct / 0.45)  # Normalize to league avg
            
            # Project hit rate for this zone
            projected_fg_pct = player_fg_pct * defense_multiplier
            hit_rate_projection[zone] = projected_fg_pct
            
            # Calculate advantage
            advantage = projected_fg_pct - player_fg_pct
            
            if advantage > 0.02:  # More than 2% boost
                favorable_zones.append((zone, advantage))
            elif advantage < -0.02:  # More than 2% drop
                unfavorable_zones.append((zone, abs(advantage)))
        
        # Sort zones by advantage
        favorable_zones.sort(key=lambda x: x[1], reverse=True)
        unfavorable_zones.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate overall matchup rating
        play_style_bonus = 0.2 if team_defense.is_vulnerable_to(
            player_profile.primary_play_style
        ) else 0.0
        
        # Weight by shot frequency
        weighted_advantage = 0.0
        for zone_data in player_profile.shot_chart.shot_zones:
            zone = zone_data.zone
            projected = hit_rate_projection[zone]
            actual = zone_data.fg_percentage
            weighted_advantage += (projected - actual) * zone_data.frequency
        
        overall_rating = weighted_advantage * 10 + play_style_bonus
        
        return DefensiveMatchup(
            player_profile=player_profile,
            team_defense=team_defense,
            primary_defender=primary_defender,
            favorable_zones=favorable_zones,
            unfavorable_zones=unfavorable_zones,
            overall_matchup_rating=overall_rating,
            expected_fg_boost=weighted_advantage,
            hit_rate_projection=hit_rate_projection
        )
    
    def find_similar_players(
        self,
        player_profile: PlayerProfile,
        all_players: List[PlayerProfile],
        min_similarity: float = 0.6,
        max_results: int = 5
    ) -> List[Tuple[PlayerProfile, float]]:
        """
        Find similar players based on play style and shot chart
        Returns list of (player, similarity_score) tuples
        """
        similar_players = []
        
        for other_player in all_players:
            if other_player.player_id == player_profile.player_id:
                continue  # Skip self
            
            similarity = player_profile.calculate_similarity_score(other_player)
            
            if similarity >= min_similarity:
                similar_players.append((other_player, similarity))
        
        # Sort by similarity score
        similar_players.sort(key=lambda x: x[1], reverse=True)
        
        return similar_players[:max_results]
    
    def get_historical_performance(
        self,
        similar_players: List[Tuple[PlayerProfile, float]],
        team_defense: TeamDefenseRanking
    ) -> Dict:
        """
        Analyze how similar players performed against this defense
        Returns aggregate statistics
        """
        if not similar_players:
            return {}
        
        total_games = 0
        total_fg_pct = 0.0
        total_points = 0.0
        
        for player, similarity in similar_players:
            # In real implementation, would query historical game data
            # For now, use projected values weighted by similarity
            weight = similarity
            total_fg_pct += player.effective_fg_pct * weight
            total_games += weight
        
        if total_games > 0:
            avg_fg_pct = total_fg_pct / total_games
        else:
            avg_fg_pct = 0.45
        
        return {
            "num_similar_players": len(similar_players),
            "avg_similarity": sum(s for _, s in similar_players) / len(similar_players),
            "historical_fg_pct": avg_fg_pct,
            "historical_confidence": min(total_games, 1.0)
        }


def generate_sample_shot_charts() -> List[PlayerShotChart]:
    """Generate sample shot chart data"""
    
    # LeBron James - Balanced scorer
    lebron_zones = [
        ShotChartData(ShotZone.PAINT, 450, 270, 0.60, 1.20, 0.35),
        ShotChartData(ShotZone.MID_RANGE, 200, 85, 0.425, 0.85, 0.15),
        ShotChartData(ShotZone.THREE_POINT_CORNER, 100, 42, 0.42, 1.26, 0.08),
        ShotChartData(ShotZone.THREE_POINT_WING, 200, 74, 0.37, 1.11, 0.15),
        ShotChartData(ShotZone.THREE_POINT_TOP, 250, 90, 0.36, 1.08, 0.19),
        ShotChartData(ShotZone.FREE_THROW_LINE, 100, 43, 0.43, 0.86, 0.08),
    ]
    lebron_chart = PlayerShotChart(
        "2544", "LeBron James", "2023-24",
        lebron_zones, 1300, 604, 0.464
    )
    
    # Stephen Curry - Three-point specialist
    curry_zones = [
        ShotChartData(ShotZone.PAINT, 200, 130, 0.65, 1.30, 0.15),
        ShotChartData(ShotZone.MID_RANGE, 150, 66, 0.44, 0.88, 0.11),
        ShotChartData(ShotZone.THREE_POINT_CORNER, 120, 54, 0.45, 1.35, 0.09),
        ShotChartData(ShotZone.THREE_POINT_WING, 350, 161, 0.46, 1.38, 0.26),
        ShotChartData(ShotZone.THREE_POINT_TOP, 450, 189, 0.42, 1.26, 0.34),
        ShotChartData(ShotZone.FREE_THROW_LINE, 80, 36, 0.45, 0.90, 0.06),
    ]
    curry_chart = PlayerShotChart(
        "201939", "Stephen Curry", "2023-24",
        curry_zones, 1350, 636, 0.471
    )
    
    # Jayson Tatum - Versatile scorer
    tatum_zones = [
        ShotChartData(ShotZone.PAINT, 350, 196, 0.56, 1.12, 0.28),
        ShotChartData(ShotZone.MID_RANGE, 250, 105, 0.42, 0.84, 0.20),
        ShotChartData(ShotZone.THREE_POINT_CORNER, 90, 36, 0.40, 1.20, 0.07),
        ShotChartData(ShotZone.THREE_POINT_WING, 280, 112, 0.40, 1.20, 0.22),
        ShotChartData(ShotZone.THREE_POINT_TOP, 230, 88, 0.383, 1.15, 0.18),
        ShotChartData(ShotZone.FREE_THROW_LINE, 50, 21, 0.42, 0.84, 0.04),
    ]
    tatum_chart = PlayerShotChart(
        "1628369", "Jayson Tatum", "2023-24",
        tatum_zones, 1250, 558, 0.446
    )
    
    return [lebron_chart, curry_chart, tatum_chart]


def generate_sample_defenders() -> List[DefenderStats]:
    """Generate sample defender statistics"""
    
    defenders = [
        DefenderStats(
            "203507", "Giannis Antetokounmpo", "Milwaukee Bucks", "PF",
            defensive_rating=106.5, steal_rate=0.012, block_rate=0.028,
            deflections_per_game=3.2, contests_per_game=12.5,
            opponent_fg_pct_allowed=0.412, opponent_3pt_pct_allowed=0.334,
            paint_fg_pct_allowed=0.48, mid_range_fg_pct_allowed=0.39,
            three_pt_fg_pct_allowed=0.334
        ),
        DefenderStats(
            "1629029", "Bam Adebayo", "Miami Heat", "C",
            defensive_rating=108.2, steal_rate=0.011, block_rate=0.022,
            deflections_per_game=2.8, contests_per_game=14.2,
            opponent_fg_pct_allowed=0.435, opponent_3pt_pct_allowed=0.352,
            paint_fg_pct_allowed=0.51, mid_range_fg_pct_allowed=0.42,
            three_pt_fg_pct_allowed=0.352
        ),
        DefenderStats(
            "203954", "Rudy Gobert", "Minnesota Timberwolves", "C",
            defensive_rating=104.8, steal_rate=0.008, block_rate=0.032,
            deflections_per_game=2.1, contests_per_game=15.8,
            opponent_fg_pct_allowed=0.398, opponent_3pt_pct_allowed=0.345,
            paint_fg_pct_allowed=0.45, mid_range_fg_pct_allowed=0.40,
            three_pt_fg_pct_allowed=0.345
        ),
    ]
    
    return defenders


def generate_sample_team_defenses() -> List[TeamDefenseRanking]:
    """Generate sample team defensive rankings"""
    
    defenses = [
        TeamDefenseRanking(
            team="Boston Celtics", season="2023-24",
            defensive_rating=110.5, points_allowed_per_game=108.2,
            opponent_fg_pct=0.446, opponent_3pt_pct=0.351,
            primary_defense_type=DefenseType.SWITCH_HEAVY, switch_rate=0.68,
            paint_defense_rank=5, mid_range_defense_rank=3,
            three_pt_defense_rank=8,
            weak_zones=[ShotZone.THREE_POINT_CORNER],
            strong_zones=[ShotZone.PAINT, ShotZone.MID_RANGE],
            struggles_against=[PlayStyle.THREE_POINT_SPECIALIST, PlayStyle.STRETCH_BIG]
        ),
        TeamDefenseRanking(
            team="Miami Heat", season="2023-24",
            defensive_rating=109.2, points_allowed_per_game=106.8,
            opponent_fg_pct=0.442, opponent_3pt_pct=0.347,
            primary_defense_type=DefenseType.AGGRESSIVE_TRAP, switch_rate=0.45,
            paint_defense_rank=8, mid_range_defense_rank=6,
            three_pt_defense_rank=4,
            weak_zones=[ShotZone.PAINT],
            strong_zones=[ShotZone.THREE_POINT_WING, ShotZone.THREE_POINT_TOP],
            struggles_against=[PlayStyle.SLASHER, PlayStyle.POST_PLAYER]
        ),
        TeamDefenseRanking(
            team="Golden State Warriors", season="2023-24",
            defensive_rating=112.8, points_allowed_per_game=111.5,
            opponent_fg_pct=0.458, opponent_3pt_pct=0.365,
            primary_defense_type=DefenseType.HELP_ROTATION, switch_rate=0.52,
            paint_defense_rank=15, mid_range_defense_rank=12,
            three_pt_defense_rank=22,
            weak_zones=[ShotZone.THREE_POINT_TOP, ShotZone.THREE_POINT_WING],
            strong_zones=[ShotZone.MID_RANGE],
            struggles_against=[PlayStyle.THREE_POINT_SPECIALIST, PlayStyle.VOLUME_SCORER]
        ),
    ]
    
    return defenses


def main():
    """Demonstrate shot chart and defensive matchup analysis"""
    print("=" * 80)
    print("SHOT CHART & DEFENSIVE MATCHUP ANALYSIS")
    print("=" * 80)
    print()
    
    # Load sample data
    shot_charts = generate_sample_shot_charts()
    defenders = generate_sample_defenders()
    team_defenses = generate_sample_team_defenses()
    
    # Create player profiles
    lebron_profile = PlayerProfile(
        "2544", "LeBron James", "Los Angeles Lakers", "SF",
        primary_play_style=PlayStyle.VOLUME_SCORER,
        secondary_play_style=PlayStyle.PLAYMAKER,
        shot_chart=shot_charts[0],
        usage_rate=0.312, true_shooting_pct=0.605, effective_fg_pct=0.564,
        preferred_zones=[ShotZone.PAINT, ShotZone.THREE_POINT_TOP],
        avoids_zones=[ShotZone.MID_RANGE]
    )
    
    curry_profile = PlayerProfile(
        "201939", "Stephen Curry", "Golden State Warriors", "PG",
        primary_play_style=PlayStyle.THREE_POINT_SPECIALIST,
        secondary_play_style=PlayStyle.VOLUME_SCORER,
        shot_chart=shot_charts[1],
        usage_rate=0.298, true_shooting_pct=0.670, effective_fg_pct=0.620,
        preferred_zones=[ShotZone.THREE_POINT_TOP, ShotZone.THREE_POINT_WING],
        avoids_zones=[ShotZone.MID_RANGE]
    )
    
    tatum_profile = PlayerProfile(
        "1628369", "Jayson Tatum", "Boston Celtics", "SF",
        primary_play_style=PlayStyle.VOLUME_SCORER,
        secondary_play_style=PlayStyle.EFFICIENT_SCORER,
        shot_chart=shot_charts[2],
        usage_rate=0.325, true_shooting_pct=0.598, effective_fg_pct=0.554,
        preferred_zones=[ShotZone.PAINT, ShotZone.THREE_POINT_WING],
        avoids_zones=[ShotZone.FREE_THROW_LINE]
    )
    
    all_profiles = [lebron_profile, curry_profile, tatum_profile]
    
    # Initialize analyzer
    analyzer = DefensiveMatchupAnalyzer()
    
    # Analyze matchup: LeBron vs Warriors
    print("MATCHUP ANALYSIS: LeBron James vs Golden State Warriors")
    print("-" * 80)
    matchup = analyzer.analyze_matchup(
        lebron_profile,
        team_defenses[2],  # Warriors
        None
    )
    
    summary = matchup.get_matchup_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n  Favorable Zones:")
    for zone, advantage in matchup.favorable_zones[:3]:
        print(f"    • {zone.value}: +{advantage:.1%} advantage")
    
    print("\n  Projected Hit Rates by Zone:")
    for zone, hit_rate in matchup.hit_rate_projection.items():
        player_zone = lebron_profile.shot_chart.get_zone_stats(zone)
        if player_zone:
            change = hit_rate - player_zone.fg_percentage
            print(f"    • {zone.value}: {hit_rate:.1%} ({change:+.1%})")
    
    # Find similar players
    print("\n" + "=" * 80)
    print("SIMILAR PLAYER ANALYSIS")
    print("-" * 80)
    
    similar_to_lebron = analyzer.find_similar_players(
        lebron_profile, all_profiles, min_similarity=0.4
    )
    
    print(f"\nPlayers similar to {lebron_profile.player_name}:")
    for player, similarity in similar_to_lebron:
        print(f"  • {player.player_name}: {similarity:.1%} similarity")
        print(f"    Play style: {player.primary_play_style.value}")
        print(f"    TS%: {player.true_shooting_pct:.1%}")
    
    # Historical performance
    if similar_to_lebron:
        print("\n" + "-" * 80)
        print("Historical Performance vs Warriors (Similar Players):")
        hist_perf = analyzer.get_historical_performance(
            similar_to_lebron, team_defenses[2]
        )
        for key, value in hist_perf.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.1%}")
            else:
                print(f"  {key}: {value}")
    
    # Analyze defender impact
    print("\n" + "=" * 80)
    print("DEFENDER ANALYSIS")
    print("-" * 80)
    
    for defender in defenders:
        print(f"\n{defender.player_name} ({defender.team}):")
        print(f"  Defensive Rating: {defender.defensive_rating}")
        print(f"  Opponent FG% Allowed: {defender.opponent_fg_pct_allowed:.1%}")
        print(f"  Paint FG% Allowed: {defender.paint_fg_pct_allowed:.1%}")
        print(f"  3PT FG% Allowed: {defender.three_pt_fg_pct_allowed:.1%}")
        print(f"  Contests per Game: {defender.contests_per_game:.1f}")
    
    # Matchup with specific defender
    print("\n" + "=" * 80)
    print("MATCHUP WITH DEFENDER: Curry vs Bam Adebayo")
    print("-" * 80)
    
    matchup_with_defender = analyzer.analyze_matchup(
        curry_profile,
        team_defenses[1],  # Heat
        defenders[1]  # Bam Adebayo
    )
    
    summary = matchup_with_defender.get_matchup_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Shot chart and defensive matchup analysis complete!")


if __name__ == "__main__":
    main()
