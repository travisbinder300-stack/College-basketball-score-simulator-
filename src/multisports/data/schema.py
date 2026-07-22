"""Core schema definitions for sports data."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, Dict


@dataclass(slots=True)
class Team:
    """Represents a team in a sports league."""

    id: str
    name: str
    abbreviation: str
    sport: str
    conference: str
    division: str


@dataclass(slots=True)
class Player:
    """Represents a player belonging to a team."""

    id: str
    name: str
    team_id: str
    sport: str
    position: str


@dataclass(slots=True)
class Game:
    """Represents one completed sporting event."""

    id: str
    sport: str
    date: date
    season: str
    home_team_id: str
    away_team_id: str
    home_score: int
    away_score: int
    venue: str
    is_neutral_site: bool
    home_rest_days: int
    away_rest_days: int

    def __post_init__(self) -> None:
        """Validate game values after initialization."""
        if not isinstance(self.date, date):
            raise TypeError("date must be a datetime.date instance")
        if self.home_score < 0 or self.away_score < 0:
            raise ValueError("scores must be non-negative")
        if self.home_rest_days < 0 or self.away_rest_days < 0:
            raise ValueError("rest days must be non-negative")

    @property
    def total_score(self) -> int:
        """Return the sum of both teams' scores."""
        return self.home_score + self.away_score


@dataclass(slots=True)
class TrainingRow:
    """Flat training representation built from a game and model features."""

    game_id: str
    sport: str
    date: date
    season: str
    total_score: float
    features: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the training row contents."""
        if not isinstance(self.date, date):
            raise TypeError("date must be a datetime.date instance")
        if self.total_score < 0:
            raise ValueError("total_score must be non-negative")

    @classmethod
    def from_game_and_features(cls, game: Game, features: Dict[str, float]) -> "TrainingRow":
        """Create a training row from a game and computed features."""
        return cls(
            game_id=game.id,
            sport=game.sport,
            date=game.date,
            season=game.season,
            total_score=float(game.total_score),
            features=dict(features),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the training row to a flat dictionary."""
        payload = asdict(self)
        features = payload.pop("features")
        return {**payload, **features}
