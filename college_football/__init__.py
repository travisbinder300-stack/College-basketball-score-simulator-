"""
College Football Score Simulator Package
=========================================

A comprehensive college football simulation system with spread analysis tools.

Usage:
    from college_football import FootballTeam, FootballSimulator
    from college_football import FootballSpreadAnalyzer
    from college_football import analyze_matchup
"""

from .football_simulator import FootballTeam, FootballSimulator
from .football_spread_analyzer import FootballSpreadAnalyzer
from .football_find_picks import analyze_matchup, print_quick_analysis

__all__ = [
    'FootballTeam',
    'FootballSimulator',
    'FootballSpreadAnalyzer',
    'analyze_matchup',
    'print_quick_analysis'
]
