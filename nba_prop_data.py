"""
NBA Prop Betting Data Model
Based on PropMadness.com interfuture data structure

This module defines the data structures for NBA prop betting,
including player props, game information, and betting lines.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class PropType(Enum):
    """Types of prop bets available"""
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    THREE_POINTERS = "three_pointers"
    STEALS = "steals"
    BLOCKS = "blocks"
    TURNOVERS = "turnovers"
    PRA = "points_rebounds_assists"  # Combined stat
    DOUBLE_DOUBLE = "double_double"
    TRIPLE_DOUBLE = "triple_double"


class OddsFormat(Enum):
    """Odds format types"""
    AMERICAN = "american"
    DECIMAL = "decimal"
    FRACTIONAL = "fractional"


@dataclass
class Player:
    """NBA Player information"""
    player_id: str
    name: str
    team: str
    position: str
    jersey_number: Optional[int] = None
    
    def __str__(self):
        return f"{self.name} - {self.team} ({self.position})"


@dataclass
class Game:
    """NBA Game information"""
    game_id: str
    home_team: str
    away_team: str
    scheduled_time: datetime
    venue: str
    season: str
    status: str = "scheduled"  # scheduled, live, completed
    
    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"


@dataclass
class PropLine:
    """Prop betting line with odds"""
    line_value: float  # e.g., 25.5 points
    over_odds: float  # American odds for over (e.g., -110)
    under_odds: float  # American odds for under (e.g., -110)
    bookmaker: str
    last_updated: datetime
    
    def get_decimal_odds(self, is_over: bool) -> float:
        """Convert American odds to decimal odds"""
        odds = self.over_odds if is_over else self.under_odds
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1
    
    def get_implied_probability(self, is_over: bool) -> float:
        """Calculate implied probability from odds"""
        decimal_odds = self.get_decimal_odds(is_over)
        return 1 / decimal_odds


@dataclass
class PlayerProp:
    """Player prop bet"""
    prop_id: str
    player: Player
    game: Game
    prop_type: PropType
    prop_line: PropLine
    player_season_avg: Optional[float] = None
    player_last_5_avg: Optional[float] = None
    vs_opponent_avg: Optional[float] = None
    injury_status: str = "healthy"  # healthy, questionable, doubtful, out
    minutes_projection: Optional[float] = None
    
    def __str__(self):
        return f"{self.player.name} {self.prop_type.value} O/U {self.prop_line.line_value}"
    
    def get_context_data(self) -> Dict:
        """Get contextual data for the prop"""
        return {
            "player": str(self.player),
            "game": str(self.game),
            "prop_type": self.prop_type.value,
            "line": self.prop_line.line_value,
            "season_avg": self.player_season_avg,
            "last_5_avg": self.player_last_5_avg,
            "vs_opponent_avg": self.vs_opponent_avg,
            "injury_status": self.injury_status,
            "minutes_projection": self.minutes_projection,
            "over_odds": self.prop_line.over_odds,
            "under_odds": self.prop_line.under_odds,
            "over_probability": f"{self.prop_line.get_implied_probability(True):.2%}",
            "under_probability": f"{self.prop_line.get_implied_probability(False):.2%}"
        }


@dataclass
class PropBetSlip:
    """A bet slip containing one or more props"""
    slip_id: str
    props: List[PlayerProp]
    stake: float
    bet_type: str = "single"  # single, parlay, round_robin
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def calculate_parlay_odds(self) -> float:
        """Calculate combined decimal odds for parlay"""
        if self.bet_type != "parlay":
            return 1.0
        
        total_odds = 1.0
        for prop in self.props:
            # Assuming all props are "over" for simplicity
            total_odds *= prop.prop_line.get_decimal_odds(True)
        return total_odds
    
    def calculate_potential_payout(self) -> float:
        """Calculate potential payout"""
        if self.bet_type == "single" and len(self.props) == 1:
            decimal_odds = self.props[0].prop_line.get_decimal_odds(True)
            return self.stake * decimal_odds
        elif self.bet_type == "parlay":
            parlay_odds = self.calculate_parlay_odds()
            return self.stake * parlay_odds
        return 0.0


# Sample data generator
def generate_sample_props() -> List[PlayerProp]:
    """Generate sample NBA prop data based on PropMadness.com structure"""
    
    # Sample games
    game1 = Game(
        game_id="NBA_2024_LAL_GSW_001",
        home_team="Golden State Warriors",
        away_team="Los Angeles Lakers",
        scheduled_time=datetime(2024, 3, 15, 19, 30),
        venue="Chase Center",
        season="2023-24"
    )
    
    game2 = Game(
        game_id="NBA_2024_BOS_MIA_001",
        home_team="Miami Heat",
        away_team="Boston Celtics",
        scheduled_time=datetime(2024, 3, 15, 20, 0),
        venue="Kaseya Center",
        season="2023-24"
    )
    
    # Sample players
    lebron = Player("2544", "LeBron James", "Los Angeles Lakers", "SF", 23)
    curry = Player("201939", "Stephen Curry", "Golden State Warriors", "PG", 30)
    tatum = Player("1628369", "Jayson Tatum", "Boston Celtics", "SF", 0)
    butler = Player("202710", "Jimmy Butler", "Miami Heat", "SF", 22)
    
    # Sample props
    props = [
        PlayerProp(
            prop_id="PROP_001",
            player=lebron,
            game=game1,
            prop_type=PropType.POINTS,
            prop_line=PropLine(25.5, -110, -110, "DraftKings", datetime.now()),
            player_season_avg=27.3,
            player_last_5_avg=29.8,
            vs_opponent_avg=28.5,
            injury_status="healthy",
            minutes_projection=35.0
        ),
        PlayerProp(
            prop_id="PROP_002",
            player=curry,
            game=game1,
            prop_type=PropType.THREE_POINTERS,
            prop_line=PropLine(4.5, -115, -105, "FanDuel", datetime.now()),
            player_season_avg=4.8,
            player_last_5_avg=5.2,
            vs_opponent_avg=4.3,
            injury_status="healthy",
            minutes_projection=34.0
        ),
        PlayerProp(
            prop_id="PROP_003",
            player=tatum,
            game=game2,
            prop_type=PropType.PRA,
            prop_line=PropLine(40.5, -120, +100, "BetMGM", datetime.now()),
            player_season_avg=41.2,
            player_last_5_avg=43.5,
            vs_opponent_avg=39.8,
            injury_status="healthy",
            minutes_projection=36.0
        ),
        PlayerProp(
            prop_id="PROP_004",
            player=butler,
            game=game2,
            prop_type=PropType.REBOUNDS,
            prop_line=PropLine(5.5, -110, -110, "Caesars", datetime.now()),
            player_season_avg=6.1,
            player_last_5_avg=7.0,
            vs_opponent_avg=5.8,
            injury_status="healthy",
            minutes_projection=33.0
        ),
        PlayerProp(
            prop_id="PROP_005",
            player=lebron,
            game=game1,
            prop_type=PropType.ASSISTS,
            prop_line=PropLine(7.5, -105, -115, "DraftKings", datetime.now()),
            player_season_avg=8.2,
            player_last_5_avg=9.0,
            vs_opponent_avg=7.8,
            injury_status="healthy",
            minutes_projection=35.0
        ),
    ]
    
    return props


if __name__ == "__main__":
    # Example usage
    print("NBA Prop Betting Data - Sample Props\n")
    print("=" * 80)
    
    sample_props = generate_sample_props()
    
    for prop in sample_props:
        print(f"\n{prop}")
        print("-" * 80)
        context = prop.get_context_data()
        for key, value in context.items():
            print(f"  {key}: {value}")
