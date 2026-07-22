"""Unit tests for the TeamRankings home-ranking output."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


_SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "fetch_rankings.py"
_SPEC = importlib.util.spec_from_file_location("fetch_rankings", _SCRIPT_PATH)
assert _SPEC and _SPEC.loader
fetch_rankings = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fetch_rankings)


class FetchHomeRankingsTests(unittest.TestCase):
    """Tests for parsing and displaying home-by-other rankings."""

    _HTML = """
    <table>
      <tr><th>Rank</th><th>Team</th><th>Home Win %</th></tr>
      <tr><td>1</td><td>New York Liberty</td><td>80.0%</td></tr>
      <tr><td>2</td><td>Minnesota Lynx</td><td>75.0%</td></tr>
    </table>
    """

    def test_fetch_home_rankings_uses_home_by_other_url(self) -> None:
        with patch.object(fetch_rankings, "_fetch_html", return_value=self._HTML) as fetch:
            rows = fetch_rankings.fetch_home_rankings("wnba")

        fetch.assert_called_once_with(
            "https://www.teamrankings.com/wnba/ranking/home-by-other/"
        )
        self.assertEqual(rows[0]["Team"], "New York Liberty")
        self.assertEqual(rows[1]["Home Win %"], "75.0%")

    def test_print_home_rankings_includes_team_values(self) -> None:
        rows = [{"Rank": "1", "Team": "New York Liberty", "Home Win %": "80.0%"}]
        with patch("builtins.print") as output:
            fetch_rankings.print_home_rankings(rows)

        printed = "\n".join(str(call.args[0]) for call in output.call_args_list)
        self.assertIn("Home-by-other rankings:", printed)
        self.assertIn("New York Liberty", printed)


class FetchAwayRankingsTests(unittest.TestCase):
    """Tests for parsing and displaying away-by-other rankings."""

    _HTML = """
    <table>
      <tr><th>Rank</th><th>Team</th><th>Away Win %</th></tr>
      <tr><td>1</td><td>Las Vegas Aces</td><td>70.0%</td></tr>
    </table>
    """

    def test_fetch_away_rankings_uses_away_by_other_url(self) -> None:
        with patch.object(fetch_rankings, "_fetch_html", return_value=self._HTML) as fetch:
            rows = fetch_rankings.fetch_away_rankings("wnba")

        fetch.assert_called_once_with(
            "https://www.teamrankings.com/wnba/ranking/away-by-other/"
        )
        self.assertEqual(rows[0]["Team"], "Las Vegas Aces")

    def test_print_away_rankings_includes_team_values(self) -> None:
        rows = [{"Rank": "1", "Team": "Las Vegas Aces", "Away Win %": "70.0%"}]
        with patch("builtins.print") as output:
            fetch_rankings.print_away_rankings(rows)

        printed = "\n".join(str(call.args[0]) for call in output.call_args_list)
        self.assertIn("Away-by-other rankings:", printed)
        self.assertIn("Las Vegas Aces", printed)


if __name__ == "__main__":
    unittest.main()
