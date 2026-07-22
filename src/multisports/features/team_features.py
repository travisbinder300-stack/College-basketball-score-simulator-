"""Team-based leak-safe rolling features."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from multisports.config.base import SportConfig

from .base import FeatureGenerator


@dataclass(slots=True)
class TeamFeatureGenerator(FeatureGenerator):
    """Generate rolling team and opponent-strength features for game totals."""

    config: SportConfig

    def feature_names(self) -> list[str]:
        """Return the configured feature columns."""
        return list(self.config.feature_columns)

    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate leak-safe rolling features using only past games."""
        if df.empty:
            enriched = df.copy()
            for feature in self.feature_names():
                if feature not in enriched.columns:
                    enriched[feature] = pd.Series(dtype=float)
            return enriched

        window = self.config.rolling_window
        feature_df = df.copy()
        feature_df = feature_df.sort_values(["date", "id"]).reset_index(drop=True)
        feature_df["is_neutral_site"] = feature_df["is_neutral_site"].astype(int)
        feature_df["home_rest_days"] = feature_df["home_rest_days"].clip(upper=self.config.rest_cap)
        feature_df["away_rest_days"] = feature_df["away_rest_days"].clip(upper=self.config.rest_cap)

        home_rows = pd.DataFrame(
            {
                "game_id": feature_df["id"],
                "date": feature_df["date"],
                "team_id": feature_df["home_team_id"],
                "opp_team_id": feature_df["away_team_id"],
                "team_side": "home",
                "total_score": feature_df["total_score"],
                "team_score": feature_df["home_score"],
                "opp_score": feature_df["away_score"],
                "win": (feature_df["home_score"] > feature_df["away_score"]).astype(int),
            }
        )
        away_rows = pd.DataFrame(
            {
                "game_id": feature_df["id"],
                "date": feature_df["date"],
                "team_id": feature_df["away_team_id"],
                "opp_team_id": feature_df["home_team_id"],
                "team_side": "away",
                "total_score": feature_df["total_score"],
                "team_score": feature_df["away_score"],
                "opp_score": feature_df["home_score"],
                "win": (feature_df["away_score"] > feature_df["home_score"]).astype(int),
            }
        )
        long_df = pd.concat([home_rows, away_rows], ignore_index=True)
        long_df = long_df.sort_values(["date", "game_id", "team_side"]).reset_index(drop=True)

        total_col = f"rolling_total_{window}"
        win_col = f"win_pct_{window}"
        opp_strength_source_col = f"opp_source_strength_{window}"
        opp_strength_col = f"opp_strength_{window}"

        long_df[total_col] = (
            long_df.groupby("team_id", group_keys=False)["total_score"]
            .apply(lambda s: s.shift(1).rolling(window=window, min_periods=1).mean())
        )
        long_df[win_col] = (
            long_df.groupby("team_id", group_keys=False)["win"]
            .apply(lambda s: s.shift(1).rolling(window=window, min_periods=1).mean())
        )

        lookup = long_df[["game_id", "team_id", total_col]].rename(
            columns={"team_id": "opp_team_id", total_col: opp_strength_source_col}
        )
        long_df = long_df.merge(lookup, on=["game_id", "opp_team_id"], how="left")
        long_df[opp_strength_col] = (
            long_df.groupby("team_id", group_keys=False)[opp_strength_source_col]
            .apply(lambda s: s.shift(1).rolling(window=window, min_periods=1).mean())
        )

        default_total = float(feature_df["total_score"].mean())
        long_df[total_col] = long_df[total_col].fillna(default_total)
        long_df[win_col] = long_df[win_col].fillna(0.5)
        long_df[opp_strength_col] = long_df[opp_strength_col].fillna(default_total)

        home_features = long_df[long_df["team_side"] == "home"][["game_id", total_col, win_col, opp_strength_col]].rename(
            columns={
                total_col: f"home_rolling_total_{window}",
                win_col: f"home_win_pct_{window}",
                opp_strength_col: f"home_opp_strength_{window}",
            }
        )
        away_features = long_df[long_df["team_side"] == "away"][["game_id", total_col, win_col, opp_strength_col]].rename(
            columns={
                total_col: f"away_rolling_total_{window}",
                win_col: f"away_win_pct_{window}",
                opp_strength_col: f"away_opp_strength_{window}",
            }
        )

        enriched = feature_df.merge(home_features, left_on="id", right_on="game_id", how="left")
        enriched = enriched.merge(away_features, left_on="id", right_on="game_id", how="left", suffixes=("", "_away"))
        enriched = enriched.drop(columns=[col for col in ["game_id", "game_id_away"] if col in enriched.columns])

        for feature_name, fill_value in {
            f"home_rolling_total_{window}": default_total,
            f"away_rolling_total_{window}": default_total,
            f"home_win_pct_{window}": 0.5,
            f"away_win_pct_{window}": 0.5,
            f"home_opp_strength_{window}": default_total,
            f"away_opp_strength_{window}": default_total,
        }.items():
            enriched[feature_name] = enriched[feature_name].fillna(fill_value)

        return enriched
